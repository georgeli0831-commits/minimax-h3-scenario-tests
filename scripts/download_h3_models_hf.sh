#!/usr/bin/env bash
# Official hf CLI route via AutoDL network turbo and hf-mirror.
set -euo pipefail

task_root="${1:?usage: download_h3_models_hf.sh /absolute/task/root}"
if [[ "$(cat "$HOME/TASK_MARKER")" != "minimax-h3-scenario-tests" ]]; then
  echo "TASK_MARKER_MISMATCH" >&2
  exit 44
fi
if [[ ! -r /etc/network_turbo ]]; then
  echo "NETWORK_TURBO_UNAVAILABLE" >&2
  exit 45
fi

source /etc/network_turbo
export HF_ENDPOINT="https://hf-mirror.com"
# hf-mirror supplies its own signed HTTP downloads.  Letting the Hub CLI use
# hf-xet bypasses the mirror and currently yields a CAS 401 on this host.
export HF_HUB_DISABLE_XET=1
unset HF_XET_HIGH_PERFORMANCE || true

models_root="$task_root/ComfyUI/models"
log_dir="$task_root/logs"
mkdir -p "$models_root" "$log_dir"
printf '%s START hf-cli endpoint=%s network_turbo=on\n' "$(date -Iseconds)" "$HF_ENDPOINT" | tee -a "$log_dir/h3-hf-download.log"

"$task_root/.venv/bin/hf" download Comfy-Org/MiniMax-H3 \
  diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors \
  diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors \
  text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors \
  vae/minimax_h3_video_vae_fp16.safetensors \
  vae/minimax_h3_audio_vae_fp32.safetensors \
  --local-dir "$models_root"

"$task_root/.venv/bin/python" "$task_root/scripts/verify_h3_models.py" \
  "$models_root" --report "$log_dir/h3-model-verification.json"
printf '%s DONE hf-cli exact-five-files-verified\n' "$(date -Iseconds)" | tee -a "$log_dir/h3-hf-download.log"
