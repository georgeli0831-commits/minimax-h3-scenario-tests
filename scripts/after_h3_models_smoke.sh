#!/usr/bin/env bash
# Wait for the verified ModelScope download, then run the required T2V smoke.
set -euo pipefail

task_root="${1:?usage: after_h3_models_smoke.sh /absolute/task/root}"
if [[ "$(cat "$HOME/TASK_MARKER")" != "minimax-h3-scenario-tests" ]]; then
  echo "TASK_MARKER_MISMATCH" >&2
  exit 44
fi

log="$task_root/logs/post-model-smoke.log"
note() { printf '%s %s\n' "$(date -Iseconds)" "$*" | tee -a "$log"; }
active_download_regex="^/bin/bash $task_root/scripts/download_h3_models_modelscope.sh $task_root$"

note "WAIT_MODEL_DOWNLOAD"
while pgrep -f "$active_download_regex" >/dev/null; do
  sleep 60
done

if ! grep -q 'DONE modelscope exact-five-files-verified' "$task_root/logs/h3-modelscope-download.log"; then
  note "STOP model download ended without verified completion"
  exit 46
fi
if ! "$task_root/.venv/bin/python" -c "import json; assert json.load(open('$task_root/logs/h3-model-verification.json'))['status'] == 'PASS'"; then
  note "STOP model verification report is not PASS"
  exit 47
fi
note "MODEL_VERIFIED"

# Restart only the task-owned ComfyUI instance so it discovers the newly placed weights.
mapfile -t comfy_pids < <(ps -eo pid=,args= | awk '$0 ~ /main.py --listen 127.0.0.1 --port 8188/ {print $1}')
for pid in "${comfy_pids[@]:-}"; do
  # The process may exit between ps and kill; that is already the desired state.
  if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
    kill -TERM "$pid" 2>/dev/null || true
  fi
done
for _ in $(seq 1 30); do
  any_alive=0
  for pid in "${comfy_pids[@]:-}"; do
    kill -0 "$pid" 2>/dev/null && any_alive=1
  done
  (( any_alive == 0 )) && break
  sleep 2
done

cd "$task_root/ComfyUI"
setsid -f "$task_root/.venv/bin/python" main.py --listen 127.0.0.1 --port 8188 \
  > "$task_root/logs/comfyui-8188.log" 2>&1 < /dev/null
for _ in $(seq 1 90); do
  if curl --fail --silent --max-time 5 http://127.0.0.1:8188/object_info >/dev/null; then
    break
  fi
  sleep 2
done
curl --fail --silent --max-time 5 http://127.0.0.1:8188/object_info >/dev/null
note "COMFYUI_RESTARTED"

api_payload="$task_root/logs/smoke-t2v-api.json"
"$task_root/.venv/bin/python" "$task_root/scripts/export_h3_t2v_api.py" \
  "$task_root/workflows/minimax_h3文生视频.json" \
  --output "$api_payload" --validate-url http://127.0.0.1:8188/object_info
"$task_root/.venv/bin/python" "$task_root/scripts/run_comfy_prompt.py" "$api_payload" \
  --timeout 7200 \
  --monitor-log "$task_root/logs/smoke-t2v-gpu.csv" \
  --report "$task_root/logs/smoke-t2v-report.json"

find "$task_root/ComfyUI/output" -type f -newer "$api_payload" -print0 \
  | while IFS= read -r -d '' output; do
      case "$output" in
        *.mp4|*.mov|*.webm|*.mkv)
          ffprobe -v error -show_entries stream=codec_type,codec_name,duration \
            -of default=noprint_wrappers=1 "$output" | tee -a "$log"
          ;;
      esac
    done
note "SMOKE_COMPLETE"
