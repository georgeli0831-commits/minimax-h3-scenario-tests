#!/usr/bin/env bash
# Resumable MiniMax H3 model download. Run only on the designated H3 test host.
set -euo pipefail

task_root="${1:?usage: download_h3_models.sh /absolute/task/root}"
marker="$(cat "$HOME/TASK_MARKER")"
if [[ "$marker" != "minimax-h3-scenario-tests" ]]; then
  echo "TASK_MARKER_MISMATCH: $marker" >&2
  exit 44
fi

log_dir="$task_root/logs"
log_file="$log_dir/h3-model-download.log"
mkdir -p "$log_dir"

# relative path|expected bytes
models=(
  "diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors|20970379616"
  "diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors|20970379616"
  "text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors|15687142551"
  "vae/minimax_h3_video_vae_fp16.safetensors|5207808496"
  "vae/minimax_h3_audio_vae_fp32.safetensors|605254808"
)

base_url="https://hf-mirror.com/Comfy-Org/MiniMax-H3/resolve/main"
segment_count="${H3_SEGMENT_COUNT:-8}"

log() {
  printf '%s %s\n' "$(date -Iseconds)" "$*" | tee -a "$log_file"
}

for record in "${models[@]}"; do
  relative="${record%%|*}"
  expected_bytes="${record##*|}"
  target="$task_root/ComfyUI/models/$relative"
  mkdir -p "$(dirname "$target")"

  if [[ -f "$target" ]] && [[ "$(stat -c%s "$target")" == "$expected_bytes" ]]; then
    log "SKIP verified-size $relative bytes=$expected_bytes"
    continue
  fi

  segments_dir="${target}.segments"
  mkdir -p "$segments_dir"
  chunk_bytes=$(( (expected_bytes + segment_count - 1) / segment_count ))
  log "START $relative expected_bytes=$expected_bytes segments=$segment_count"

  download_segment() {
    local index="$1"
    local start=$(( index * chunk_bytes ))
    local end=$(( start + chunk_bytes - 1 ))
    local segment_expected
    local part="$segments_dir/part-$index"
    local incoming="$part.incoming"
    local have=0

    if (( end >= expected_bytes )); then
      end=$(( expected_bytes - 1 ))
    fi
    segment_expected=$(( end - start + 1 ))

    # A signal can interrupt curl after it writes part of its temporary file.
    # Fold that exact byte range into the segment before asking the mirror for
    # a newly signed remaining range.
    if [[ -f "$incoming" ]]; then
      cat "$incoming" >> "$part"
      rm -f "$incoming"
    fi
    [[ -f "$part" ]] && have="$(stat -c%s "$part")"
    if (( have > segment_expected )); then
      log "ERROR oversized segment $relative index=$index have=$have expected=$segment_expected"
      return 46
    fi
    while (( have < segment_expected )); do
      local absolute_start=$(( start + have ))
      log "SEGMENT_START $relative index=$index range=$absolute_start-$end"
      curl --fail --location --silent --show-error \
        --retry 8 --retry-all-errors --connect-timeout 20 \
        --speed-time 120 --speed-limit 1 \
        --range "$absolute_start-$end" \
        --output "$incoming" "$base_url/$relative"
      cat "$incoming" >> "$part"
      rm -f "$incoming"
      have="$(stat -c%s "$part")"
    done
    log "SEGMENT_DONE $relative index=$index bytes=$have"
  }

  pids=()
  for (( index=0; index<segment_count; index++ )); do
    download_segment "$index" &
    pids+=("$!")
  done
  for pid in "${pids[@]}"; do
    wait "$pid"
  done

  tmp_target="${target}.assembled"
  rm -f "$tmp_target"
  for (( index=0; index<segment_count; index++ )); do
    cat "$segments_dir/part-$index" >> "$tmp_target"
  done
  mv "$tmp_target" "$target"

  actual_bytes="$(stat -c%s "$target")"
  if [[ "$actual_bytes" != "$expected_bytes" ]]; then
    log "ERROR size-mismatch $relative actual_bytes=$actual_bytes expected_bytes=$expected_bytes"
    exit 45
  fi
  log "DONE verified-size $relative bytes=$actual_bytes"
  rm -rf "$segments_dir"
done

log "ALL_MODELS_DOWNLOADED"
