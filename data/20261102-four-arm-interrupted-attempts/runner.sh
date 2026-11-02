#!/bin/sh
set -u
ROOT='/Users/lili/Desktop/test/FormSy-SOP消融实验-新仓库-20261102/正式-4组3seed'
PY='/Users/lili/Desktop/test/formsy-local-kit-test-20261029/isolated/config/sop-runtimes/bca1b2cf88bb7a6b28c97c10dbfc8a8a13f4d90ba4994707642704493b50d804/venv/bin/python'
MODEL='/Users/lili/Desktop/test/FormSy-SOP离线强模型-20261030/运行环境/Qwen3-14B-Q4_K_M.gguf'
BIN='/Users/lili/Desktop/test/FormSy-SOP真实需求对照-20261029/运行环境/llama-b11960'
cd "$ROOT" || exit 1
mkdir -p logs runs

for group in "$@"; do
  for seed in 42 43 44; do
    out="$ROOT/runs/${group}-s${seed}"
    if [ -e "$out" ]; then
      echo "SKIP existing $group $seed" >> "$ROOT/logs/runner.log"
      continue
    fi
    echo "START $group $seed $(date -u +%FT%TZ)" >> "$ROOT/logs/runner.log"
    "$PY" -u "$ROOT/ablation_host.py" \
      --config "$ROOT/configs/${group}-${seed}.json" \
      --output "$out" \
      --model "$MODEL" \
      --bin-dir "$BIN" \
      > "$ROOT/logs/${group}-s${seed}.log" 2>&1
    code=$?
    echo "END $group $seed exit=$code $(date -u +%FT%TZ)" >> "$ROOT/logs/runner.log"
  done
done
echo "ALLDONE $(date -u +%FT%TZ)" >> "$ROOT/logs/runner.log"
