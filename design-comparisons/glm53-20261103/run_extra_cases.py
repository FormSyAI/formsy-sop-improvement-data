#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import subprocess
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOP_REPO = Path("/Users/lili/Desktop/work/FormSyAI/formsy-sop")
ENDPOINT = "https://api.aurinova.cn/v1/chat/completions"
MODEL = "glm-5.3"
SEED = 5204
MAX_TOKENS = 5000
SOP_PATHS = [
    "skills/formsy-development-kit/SKILL.md",
    "skills/formsy-sop-product/SKILL.md",
    "skills/formsy-sop-product/references/PC规则.md",
    "skills/formsy-sop-technical/SKILL.md",
    "skills/formsy-sop-technical/references/TC规则.md",
    "skills/formsy-sop-technical/references/模块接口与数据.md",
    "skills/formsy-sop-selfcheck/SKILL.md",
]
BASE = """你是资深产品与项目 SOP 设计专家。为需求制定中文产品 SOP 与实施前计划，说明范围、角色权限、流程、状态、异常、数据、验收和未知。区分事实与建议，不要进入代码实现。"""
SOP = BASE + """\n\n你正在应用 FormSy SOP。以下是固定版本加载的完整相关规范。\n"""


def call(system, user):
    key = os.environ["API_KEY"]
    payload = {
        "model": MODEL,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "temperature": 0.2,
        "top_p": 0.95,
        "max_tokens": MAX_TOKENS,
        "seed": SEED,
        "reasoning_effort": "low",
    }
    body = json.dumps(payload, ensure_ascii=False).encode()
    req = urllib.request.Request(
        ENDPOINT,
        data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    started = time.monotonic()
    with urllib.request.urlopen(req, timeout=240) as response:
        result = json.load(response)
    return result, time.monotonic() - started


def main():
    sop_parts = []
    for path in SOP_PATHS:
        content = subprocess.check_output(["git", "show", f"origin/main:{path}"], cwd=SOP_REPO, text=True)
        sop_parts.append(f"\n=== {path} ===\n{content}\n")
    sop_text = "".join(sop_parts)
    cases = json.loads((ROOT / "extra_cases.json").read_text(encoding="utf-8"))
    for case in cases:
        for arm in ("baseline", "sop"):
            outdir = ROOT / "runs" / "extra-seed-5204" / case["id"] / arm
            outdir.mkdir(parents=True, exist_ok=True)
            system = BASE if arm == "baseline" else SOP + sop_text
            (outdir / "prompt.txt").write_text(f"SYSTEM\n{system}\n\nUSER\n{case['prompt']}\n", encoding="utf-8")
            result, duration = call(system, case["prompt"])
            (outdir / "response.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            answer = result["choices"][0]["message"].get("content", "")
            (outdir / "answer.md").write_text(answer.strip() + "\n", encoding="utf-8")
            print(json.dumps({
                "case": case["id"],
                "arm": arm,
                "seconds": round(duration, 3),
                "finish_reason": result["choices"][0].get("finish_reason"),
                "usage": result.get("usage"),
                "chars": len(answer),
            }, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
