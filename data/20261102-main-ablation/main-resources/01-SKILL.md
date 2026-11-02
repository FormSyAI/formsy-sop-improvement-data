---
name: formsy-development-kit
description: "FormSy 开发统一入口：处理已授权新增、修改、修复和既有开发流程的继续；读取项目规范、架构与知识，记录采集里程碑，按需生成产品、技术、自检、知识及汇总文档。普通问答和只读解释不创建流程。"
---

# FormSy development kit

本包是唯一对外 Skill 入口。下列模块是同一 Skill 的按需参考资料，不需要分别安装或调用其他 SOP Skill。

## 选择当前工作

- 工程工作开始、切换独立目标或恢复暂停目标时，先读[原生采集与任务记录](references/progress-recording.md)，解析当前宿主会话并实际记录任务。用户不执行开发流程时仍适用；普通问答不创建任务。
- 新开发或继续既有流程：读取 [开发流程](modules/formsy-sop-workflow/GUIDE.md)，再只读取当前阶段需要的模块；沿用用户已有授权。
- 产品、技术、自检、知识治理与汇总文档：按下表读取对应模块；单独整理文档不创建开发 run。
- 真实采集进展与交接：使用下文进度合同，先核对实际来源和业务任务；流程 run 不代替采集身份。
- 报告：使用下文固定渲染器与真实输入。

项目配置了 `.formsy-sop/runtime.json` 时使用其 `cli_argv`；独立 CLI 的入口是 `formsy flow` 和 `formsy sop engine`。仅在显式兼容旧项目时使用旧入口。统一入口不更改登录凭据或批准范围。

- [文档汇总](modules/formsy-sop-assemble/GUIDE.md)
- [知识治理](modules/formsy-sop-knowledge/GUIDE.md)
- [产品设计](modules/formsy-sop-product/GUIDE.md)
- [自检](modules/formsy-sop-selfcheck/GUIDE.md)
- [技术设计](modules/formsy-sop-technical/GUIDE.md)
- [审计参考](modules/formsy-sop-traceaudit/GUIDE.md)
- [开发流程](modules/formsy-sop-workflow/GUIDE.md)
- [SOP 文档整理](modules/formsy-sop/GUIDE.md)

## 项目规范、采集与报告

FormSy SOP owns the complete local development workflow. Start or continue the
workflow module under the user's existing authorization; the Server contributes
only Birdview, project SOP, and knowledge with Verifier. Their absence does not
disable built-in clarification, templates, planning, consistency, self-check,
implementation, repair or completion checks.

Use `formsy project connect --worktree ABSOLUTE --json` to prepare local resources
and attempt verified Server matching. A unique authorized match may bind;
ambiguous matches need an actual choice. Keep each repository's identity and
authorization independent. Read project_context/sop_get only for optional project
SOP, preserving its actual binding revision and published pin. Missing content
or a failed read remains a gap, never zero-rule success or fabricated permission.

The workflow module's optional-project-context reference owns source status,
adoption and local Verifier acceptance semantics. Raw JSON stays in files and
collapsed details; display brief progress, unresolved questions and the workbench.

## Apply shared Birdview guidance

Server supplies three optional project supplements: Birdview, project SOP, and
knowledge with Verifier definitions. Follow
[the source and acceptance contract](modules/formsy-sop-workflow/references/optional-project-context.md).
The workflow module owns their reads and local impact preview. Missing login,
binding, publication or connectivity does not disable the built-in SOP workflow.
Keep actual source identity, fixed versions and coverage gaps; availability is
not adoption, execution or acceptance. Applicable adopted Verifier failures
still hold acceptance; authorized result synchronization is tracked separately.

When MCP is not connected, describe the missing integration. If the user asks
for CLI diagnostics, discover the installed command through `formsy --help` before using it. The preview launch path is `formsy mcp serve`.

Report separately what the server returned, what remains unavailable, and what
was actually tested. Normal clarifications can remain in the current conversation.

## Record engineering milestones

Before engineering work, resolve the current session through the installed capture
configuration as described in the progress contract. A project/SOP lookup does not
establish native capture. When capture is configured, select and read back the
actual task before implementation. Reading this Skill or starting a watch does
not record the task. If binding is unavailable, report the specific attribution
gap and continue the user's ordinary authorized work without borrowing another
session's state. This applies independently of the development workflow.

For engineering work with an explicitly selected native FormSy capture state, read
[the progress contract](references/progress-recording.md) before starting work,
redirecting to a distinct deliverable, returning to a paused target, or recording
a material decision, verification, blocker or handoff. Check the current task
against the actual work target, not the overarching delivery goal. Same-target
tests and commits remain within that task. For task entry, the lifecycle contract
owns selecting actual user Activities and recording explicit trigger references.
Local progress does not require a selected or ready SOP. Follow the context's
legacy or explicit lifecycle interface; `formsy record` stores milestones.
Use legacy Evidence only when explicitly selected. MCP remains read-only.
Report the observed task receipt or the attribution gap in a short sentence,
not stored JSON. Skill selection is not an every-turn capture guarantee,
task approval or proof of completion.

## Render a supplied report

When the user requests a report and supplies actual project/SOP context or
explicitly asks to render supplied structured data, read
[the report contract](references/report-rendering.md). Use the supplied
[schema](references/report-v1.schema.json) and fixed
[renderer](scripts/render-report.mjs), with the existing
[HTML template](assets/development-report-v1.html). Fill data; keep template,
CSS and renderer unchanged. Never invent SOP or identity fields to bypass an
unready project. Label fixtures as fixtures and never use them as production
fallbacks.

After generating HTML, use the current client's available preview capability
to open it in this session. A queued/open request is not proof of rendered
display; otherwise return an absolute file link and explain the limitation.
