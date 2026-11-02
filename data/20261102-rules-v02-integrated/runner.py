#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent
PROMPTS = json.loads((BASE / "prompt-freeze.json").read_text(encoding="utf-8"))["prompts"]
MODEL = Path("/Users/lili/Desktop/test/FormSy-SOP离线强模型-20261030/运行环境/Qwen3-14B-Q4_K_M.gguf")
CLI = Path("/Users/lili/Desktop/test/FormSy-SOP真实需求对照-20261029/运行环境/llama-b11960/llama-completion")
ORDER = [f"integrated-rules-seed{seed}" for seed in (42, 43, 44)]
ENV = {
    "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
    "HOME": "/homeless",
    "TMPDIR": "/tmp",
    "LANG": "en_US.UTF-8",
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_CONFIG_NOSYSTEM": "1",
    "PYTHONDONTWRITEBYTECODE": "1",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    runs = BASE / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    for name in ORDER:
        outdir = runs / name
        if outdir.exists():
            print(f"SKIP existing {name}", flush=True)
            continue
        outdir.mkdir()
        prompt = Path(PROMPTS[name]["path"])
        stdout_path = outdir / "stdout.txt"
        stderr_path = outdir / "stderr.txt"
        cmd = [
            str(CLI),
            "-m", str(MODEL),
            "-f", str(prompt),
            "-no-cnv",
            "--no-display-prompt",
            "--no-escape",
            "--no-context-shift",
            "--offline",
            "--simple-io",
            "--perf",
            "-c", "32768",
            "-n", "4096",
            "-s", name.split("seed")[1],
            "--temp", "0.6",
            "--top-p", "0.95",
            "--top-k", "20",
            "--min-p", "0",
            "-ngl", "all",
            "-b", "256",
            "-ub", "128",
            "-ctk", "q8_0",
            "-ctv", "q8_0",
            "-fa", "on",
            "-t", "4",
        ]
        started = time.monotonic()
        with stdout_path.open("xb") as so, stderr_path.open("xb") as se:
            try:
                returncode = subprocess.run(cmd, stdout=so, stderr=se, timeout=2400, env=ENV, stdin=subprocess.DEVNULL).returncode
            except subprocess.TimeoutExpired:
                returncode = 124
        duration = time.monotonic() - started
        output_text = stdout_path.read_text(encoding="utf-8", errors="strict")
        stderr_text = stderr_path.read_text(encoding="utf-8", errors="replace")
        generated = re.search(r"(?m)^.*(?<!prompt )eval time\s*=.*?/\s*(\d+)\s*(?:runs|tokens)", stderr_text)
        meta = {
            "name": name,
            "runtime_profile": "fullgpu-lowbatch-context32768-output4096",
            "command": cmd,
            "exit_code": returncode,
            "timeout": returncode == 124,
            "duration_seconds": round(duration, 3),
            "generated_tokens_reported": int(generated.group(1)) if generated else None,
            "eog_marker_present": bool(re.search(r" \[end of text\]\n(?:\n)*\Z", output_text)),
            "output_chars": len(output_text),
            "output_sha256": sha256(stdout_path),
            "prompt_sha256": sha256(prompt),
        }
        (outdir / "inference.json").write_text(json.dumps(meta, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"name": name, "exit_code": returncode, "eog": meta["eog_marker_present"], "tokens": meta["generated_tokens_reported"], "chars": meta["output_chars"], "seconds": meta["duration_seconds"]}, ensure_ascii=False), flush=True)
        if returncode != 0 or not meta["eog_marker_present"]:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
