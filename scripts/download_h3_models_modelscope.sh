#!/usr/bin/env bash
# Exact MiniMax H3 files from the verified Comfy-Org ModelScope mirror.
set -euo pipefail

task_root="${1:?usage: download_h3_models_modelscope.sh /absolute/task/root}"
if [[ "$(cat "$HOME/TASK_MARKER")" != "minimax-h3-scenario-tests" ]]; then
  echo "TASK_MARKER_MISMATCH" >&2
  exit 44
fi

models_root="$task_root/ComfyUI/models"
log_dir="$task_root/logs"
mkdir -p "$models_root" "$log_dir"

# ModelScope's official Hub client verifies and resumes byte ranges itself.
export MODELSCOPE_DOWNLOAD_PARALLEL_WORKERS=4
export MODELSCOPE_DOWNLOAD_PARALLEL_THRESHOLD_MB=50
export MODELSCOPE_DOWNLOAD_PART_SIZE_MB=160

printf '%s START modelscope exact-five-files\n' "$(date -Iseconds)" | tee -a "$log_dir/h3-modelscope-download.log"
"$task_root/.venv/bin/ms-hub" download Comfy-Org/MiniMax-H3 \
  --include \
    diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors \
    diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors \
    text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors \
    vae/minimax_h3_video_vae_fp16.safetensors \
    vae/minimax_h3_audio_vae_fp32.safetensors \
  --max-workers 5 --local-dir "$models_root"

"$task_root/.venv/bin/python" "$task_root/scripts/verify_h3_models.py" \
  "$models_root" --report "$log_dir/h3-model-verification.json"
printf '%s DONE modelscope exact-five-files-verified\n' "$(date -Iseconds)" | tee -a "$log_dir/h3-modelscope-download.log"
