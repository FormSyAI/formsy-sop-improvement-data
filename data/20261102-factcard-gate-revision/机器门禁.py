#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import json
import re
from pathlib import Path


FACT_PATTERNS = {
    "F01_auto_publish": r"(审核通过|审核.*通过).{0,30}(自动发布|即.*发布)|自动发布",
    "F02_old_readonly": r"(旧版本|历史版本|旧版).{0,30}(只读|不可修改|不可操作)|只读",
    "F03_latest_only": r"(意见|确认).{0,30}(仅|只).{0,20}(最新|当前)(发布)?版本|最新发布版.{0,20}(开放|允许|有效)|仅对最新发布版开放",
    "F04_history": r"(历史|旧版本|旧意见).{0,30}(保留|完整保存|完整保留)|完整保留",
    "F05_project_scope": r"(自己项目|本项目|所属项目).{0,30}已发布版本|客户.{0,30}(只能|仅能).{0,20}(查看|访问).{0,20}(自己项目|本项目|所属项目)",
    "F06_comment_binding": r"(意见|反馈).{0,40}(绑定|关联).{0,30}(设计稿.{0,20}版本|version_id|版本ID|版本号)",
    "F07_no_inherit": r"(新版本确认|确认状态|旧版本确认|v1\.0确认|确认记录).{0,60}(不继承|不能继承|不等同|不能直接算作|不视为|不自动继承|独立)",
    "F08_process_before_confirm": r"(先处理|处理完成|处理完|意见处理前置|意见处理状态).{0,60}(意见|反馈)?.{0,40}(确认|允许确认)|意见.{0,40}(未处理|处理完成|处理完).{0,40}(不能|无法|才允许|允许|阻止).{0,30}确认",
    "F09_single_confirmer": r"(指定一名|唯一|一名|指定1名|指定 1 名).{0,20}客户确认人|(客户确认人|确认人).{0,40}(其他客户|非确认人).{0,30}(只能|仅可|可以).{0,10}(提意见|提出意见)",
    "F10_downloaded_copy": r"(撤销访问|撤销.{0,10}访问).{0,150}(不影响|不能|无法|不可|仍可|仍能).{0,150}(收回|撤回|删除|影响|查看|保留|访问|已下载|下载|副本|文件).{0,100}(已下载|下载|副本|文件).{0,50}(副本|文件)?|已下载副本.{0,80}(仍|保留|可访问|不影响)",
}

FORBIDDEN_SCOPE = [
    "管理员", "通知模块", "自动通知", "云存储", "云端存储", "归档",
    "备份恢复", "数据备份", "邀请链接", "链接生成", "版本对比", "批量上传",
    "匿名意见", "大文件上传", "多语言",
]


def check(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    # Candidate suggestions can mention forbidden capabilities only inside a clearly non-scope section.
    candidate_section = ""
    for marker in ("候选建议", "候选建议（不进入本期范围）", "后续建议", "建议（非本期范围）", "未进入本期范围"):
        if marker in text:
            candidate_section = text[text.index(marker):]
            break
    enforce_text = text[: len(text) - len(candidate_section)] if candidate_section else text
    facts = {key: bool(re.search(pattern, text, re.I | re.S)) for key, pattern in FACT_PATTERNS.items()}
    scope_hits = [term for term in FORBIDDEN_SCOPE if term in enforce_text and not (term == "归档" and "不归档" in enforce_text)]
    facts_missing = [key for key, hit in facts.items() if not hit]
    gate_passed = not facts_missing and not scope_hits
    return {
        "path": str(path),
        "facts": facts,
        "facts_missing": facts_missing,
        "scope_hits": scope_hits,
        "gate_passed": gate_passed,
        "failure_reasons": (
            [f"missing fact {key}" for key in facts_missing]
            + [f"forbidden scope hit: {term}" for term in scope_hits]
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = check(args.input)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
