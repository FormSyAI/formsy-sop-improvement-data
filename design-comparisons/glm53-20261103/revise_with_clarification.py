#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import hashlib
import json
import os
import subprocess
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOP_REPO = Path("/Users/lili/Desktop/work/FormSyAI/formsy-sop")
SOP_REF = "origin/main"
ENDPOINT = "https://api.aurinova.cn/v1/chat/completions"
MODEL = "glm-5.3"
SOP_PATHS = [
    "skills/formsy-development-kit/SKILL.md",
    "skills/formsy-sop-product/SKILL.md",
    "skills/formsy-sop-product/references/PC规则.md",
    "skills/formsy-sop-technical/SKILL.md",
    "skills/formsy-sop-technical/references/TC规则.md",
    "skills/formsy-sop-technical/references/模块接口与数据.md",
    "skills/formsy-sop-selfcheck/SKILL.md",
]
BASE_SYSTEM = """你是资深产品与项目 SOP 设计专家。根据用户需求撰写一份中文产品 SOP。必须区分已明确事实、建议和未知，不要把建议写成已确认。只输出设计，不进入代码实现。"""
SOP_SYSTEM = BASE_SYSTEM + """

你正在应用 FormSy SOP。以下是从固定版本加载的完整相关规范，请用于规划与自检。

"""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sop_text() -> tuple[str, list[dict]]:
    parts = []
    manifest = []
    for path in SOP_PATHS:
        content = subprocess.check_output(
            ["git", "show", f"{SOP_REF}:{path}"],
            cwd=SOP_REPO,
            text=True,
        )
        parts.append(f"\n\n=== FormSy SOP 资源：{path} ===\n{content}\n=== 资源结束 ===\n")
        manifest.append({
            "path": path,
            "chars": len(content),
            "sha256": sha256(content.encode("utf-8")),
        })
    return "".join(parts), manifest


def call(system: str, user: str, seed: int, max_tokens: int) -> tuple[dict, float]:
    key = os.environ.get("API_KEY")
    if not key:
        raise RuntimeError("API_KEY is required")
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.2,
        "top_p": 0.95,
        "max_tokens": max_tokens,
        "seed": seed,
        "reasoning_effort": "low",
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    started = time.monotonic()
    for attempt in range(1, 4):
        req = urllib.request.Request(
            ENDPOINT,
            data=body,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=240) as response:
                result = json.load(response)
            elapsed = time.monotonic() - started
            result["_experiment"] = {
                "attempt": attempt,
                "duration_seconds": round(elapsed, 3),
                "request_sha256": sha256(body),
            }
            return result, elapsed
        except Exception:
            if attempt == 3:
                raise
            time.sleep(attempt * 2)
    raise RuntimeError("unreachable")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--max-tokens", type=int, default=7000)
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()
    case = (ROOT / "case.md").read_text(encoding="utf-8")
    clarification = (ROOT / "clarification.md").read_text(encoding="utf-8")
    sop, resources = sop_text()
    commit = subprocess.check_output(["git", "rev-parse", SOP_REF], cwd=SOP_REPO, text=True).strip()
    (ROOT / f"manifest-final-seed-{args.seed}.json").write_text(
        json.dumps({
            "model": MODEL,
            "endpoint": ENDPOINT,
            "sop_ref": SOP_REF,
            "sop_commit": commit,
            "sop_resources": resources,
            "seed": args.seed,
            "temperature": 0.2,
            "top_p": 0.95,
            "reasoning_effort": "low",
            "max_tokens": args.max_tokens,
        }, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    for arm in ("baseline", "sop"):
        initial_dir = ROOT / "runs" / f"seed-{args.seed}" / "initial" / arm
        initial = (initial_dir / "answer.md").read_text(encoding="utf-8")
        user = (
            case
            + "\n\n【你在上一轮产出的初始设计】\n"
            + initial
            + "\n\n【需求方对未决问题的补充答复】\n"
            + clarification
            + "\n\n请基于上述答复更新并输出最终产品 SOP，明确已确认行为、状态与上下文、异常、验收和剩余未知。"
        )
        outdir = ROOT / "runs" / f"seed-{args.seed}" / "final" / arm
        if args.skip_existing and (outdir / "response.json").exists():
            print(f"SKIP final {args.seed} {arm}", flush=True)
            continue
        outdir.mkdir(parents=True, exist_ok=True)
        system = BASE_SYSTEM if arm == "baseline" else SOP_SYSTEM + sop
        (outdir / "prompt.txt").write_text(f"SYSTEM\n{system}\n\nUSER\n{user}\n", encoding="utf-8")
        response, duration = call(system, user, args.seed, args.max_tokens)
        (outdir / "response.json").write_text(json.dumps(response, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        content = response["choices"][0]["message"].get("content", "")
        (outdir / "answer.md").write_text(content.strip() + "\n", encoding="utf-8")
        print(json.dumps({
            "phase": "final",
            "arm": arm,
            "seed": args.seed,
            "seconds": round(duration, 3),
            "finish_reason": response["choices"][0].get("finish_reason"),
            "usage": response.get("usage"),
            "answer_chars": len(content),
        }, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
