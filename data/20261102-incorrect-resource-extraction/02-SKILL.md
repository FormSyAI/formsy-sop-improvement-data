---
name: formsy-sop-workflow
description: "在已绑定 FormSy 的项目收到新增功能、修改或修复需求时，自动采用当前 Codex 对话的开发流程；也用于启动或继续已有流程。普通问答和只读解释不创建 run，单独文档整理使用对应模块。"
metadata:
  version: "0.3.6"
  contract: "formsy-workflow-v1"
---

# 当前对话中的开发流程

开发入口、缺失 Server、项目补充读取及 Verifier 验收统一按[内置流程与三类项目补充](references/optional-project-context.md)执行。该合同优先于历史在线强依赖描述；SOP 方法和真实检查始终保留。


当前 Codex 是文档和代码的主要作者；`formsy-sop flow` 保存阶段状态和执行依据，FormSy CLI 负责真实采集与同步。当前发布配置的阶段为：项目原则 → 需求规格 → 技术规划 → 任务拆分 → 执行预览 → 实施任务 → 完成验收。完成验收在同一阶段内完成检查、修复与复验；检查结果必须对应当前代码，失败历史和修复预算继续保留。需求阶段沿用 specify 标识，边问边更新同一份规格，统一审阅一次；见[需求阶段](references/requirements-phase.md)。旧流程按保存的阶段继续，读取不自动迁移。没有独立确认、上传或 Verifier 阶段。

## 资料读取与压缩后续接

以 `flow context.method_reading` 提供的真实路径和内容 SHA-256 定位本阶段资料。已经读过且路径、内容版本未变的段落直接沿用；刷新 context、阶段切换或上下文压缩本身不要求重读入口、完整指南或全部规则。未读、被截断、版本变化或恢复后确实缺失的内容，只补读当前操作所需段落；目录列出不代表已读。

压缩或交接摘要保留实际读过的路径/内容摘要/段落、当前正式文档、准备/草稿/回执路径、未完成 condition_id/item_id 和下一操作。恢复先读已有草稿与回执，不重新创建同一份检查。阅读记录不等于语义自检通过，不新增批准或完成台账。

先保存本阶段所需草稿，再对当前目录的适用义务检查。按需读取原生规则全文，延期条件不要求提前加载所有后续阶段规则；当前材料引入的真实跨模块依赖及运行/交付/关闭声明仍必须核对。规则、材料、范围、依赖变化按既有复用合同失效并复检；不以少读资料为理由漏检。

## 开始与继续

开发或继续流程时，先读[阶段执行合同](references/workflow.md)，按实际 `flow context` 的阶段执行。技术规划、任务与一致性分析、本地影响预览和自检都是内置流程内容，不能等用户提醒后才补充，也不能用未来阶段草稿替代已执行回执。Birdview、项目 SOP、知识与 Verifier 是按配置和当前阶段读取的可选补充；未配置、未授权或读取失败时保留具体缺口，继续完整本地流程。

用户测试、演练或验收 FormSy 流程时，以流程产品为交付对象、示例需求为测试输入；“继续”沿这个测试目标解释。保留示例 run，不自行转成实现示例业务功能；发现的问题记录到流程产品，不扩大示例需求范围。先验证分发 Skill、CLI 和 MCP 的实际行为，缺少的能力修到对应产品入口，不靠当前会话临时补做来宣称修复。

收到已授权开发需求后，先确定真实仓库与范围，CLI 自动准备本地项目并尝试在线匹配；多仓库候选按[候选仓库与 Server 匹配](references/repository-candidates.md)逐一独立核对，在线不可用保留补充缺口；保留原始用户请求到真实本地文件，使用 `formsy-sop flow enter PROJECT --feature specs/FEATURE --request-file FILE` 进入流程；可用 `--title TITLE` 指定任务标题。同一 feature 和请求继续时复用已有 run，不因对话轮次重复新建。独立新需求遇已有 current-run 时，核对真实旧 run 后用 enter --switch-from OLD_RUN_ID 明确保留并切换；返回暂停需求用 flow select PROJECT --run-id 原ID，不能新建同名替身或替其确认。入口保存请求、核对真实项目绑定并读取首次架构上下文；流程 run 与采集 Session 内的原生 Task 分别记录，入口不新建独立业务任务。缺口按真实回执说明。普通问答、只读解释和没有开发请求的上下文浏览不调用 enter/start。手动初始化已有任务仍可使用 `flow start`，继续时读取 `flow context PROJECT --json`。以返回的显式 feature、路径、current_stage、revision、输入摘要和阶段指令为准；不要按最近分支或同名文件猜任务。不另起具有写权限的 Codex 代替当前会话。

默认逐步审阅：每次只执行当前一步，展示本步产物和操作卡；guided 进入 awaiting_review 后先展示产物和检查结果，再用 Codex 的 request_user_input_async 原生弹窗收集阶段确认与修改意见，工作台仅供阅读和状态展示。问题绑定真实项目、run、阶段、revision、input_digests 和产物版本；记录真实问题 ID 与答案来源。发出、默认选项、超时、关闭和暂不决定均不构成批准；用户限制只读或不要推进的任务不提阶段决定。revise 必须有用户实际意见；过期答案不得套到新版本。没有原生问题工具时说明缺口并在当前对话提问，不造网页表单。详见 references/presentation.md。用户真实确认被 flow interact 接受后，在同一会话自动执行新当前阶段，直到其 awaiting_review 再等待原生弹窗的真实决定；每阶段继续保留真实审阅。已有任务授权继续有效，阶段审阅不重复询问执行权限。用户明确要求自动连续执行时可选择 automatic 模式。文件、自检结论和模型声明都不能生成用户批准。先读[共同约定](references/共同约定.md)；阶段结果接口和操作方式见[流程交互约定](references/workflow.md)。

## 当前会话的实际调用闭环

这是执行入口，不只是文档目录。先读取目标项目 `.formsy-sop/runtime.json` 的 `cli_argv`，若已配置，以该实际 argv 后接完整 CLI 参数执行，保持参数数组而不是拼接 shell；不要把当前主机路径写入 Skill。可用随包 `scripts/run_flow.py` 薄入口读取配置并委托调用。没有 runtime 配置时，再使用项目 `tools/formsy-flow.py` 或 PATH 中已安装的 `formsy-sop`。例如后缀 `flow context PROJECT --json` 在三种入口保持一致。入口报缺依赖或配置时报告实际错误，不能假定命令已经运行，也不自动改全局 PATH。

1. 新开发请求实际调用 `flow enter PROJECT --feature specs/FEATURE --request-file FILE`；请求和 feature 稳定，同一请求重放复用已有 run。继续已有流程先调用 `flow context PROJECT --json`。
2. 读取返回的 `prompt`，执行当前阶段的固定指令，并只按当前任务需要读取产品、技术、自检规则。在 constitution 可用时使用 `flow shared-refresh PROJECT` 读取实际绑定的共享架构补充；`flow context` 在配置存在时尝试读取项目 SOP 和当前阶段知识。缺项目配置、项目绑定或读取授权时记录“未核对”，不是零条规范；可用 `flow knowledge-refresh PROJECT` 显式重试。
3. 当前 Codex 直接写真实文档或代码。保留开始工作时取得的 `revision` 和 `input_digests`，把真正完成的输出路径放入结果；不要只回复计划就当阶段完成。
4. 将结果 JSON 保存到 `.formsy-sop/runs/<真实run_id>/requests/<稳定调用键>.json`，再实际调用 `flow advance PROJECT --result PATH`。字段和 Preview execution 参数见[流程交互约定](references/workflow.md)。读取程序回执，只有程序接受才展示已推进；过期时刷新并核对实际变化。
5. finish/reverify 核对已有真实检查回执及当前目标；缺失、失败、过期或受变更影响时实际调用 `flow check PROJECT --operation-id KEY --expected-revision N`。仍对当前目标有效的结果保留，不因进入 reverify 清空。读取退出码和日志；失败按真实追加任务修复后换新调用键重测，原失败不能删除或改写。完成审查后再提交 `findings:[]` 的阶段结果；这是当前模型审查声明，不冒充独立审计。
6. 每次成功操作后读取最新 context，按[展示与交互](references/presentation.md)用统一工作台发布当前步骤与完整流程；统一模式使用已连接的工作台 MCP；未连接时说明缺口，不生成独立HTML替代。guided 模式下，结果进入 awaiting_review 后展示最新产物与检查结论，用 request_user_input_async 发起绑定当前版本的原生阶段决定问题，再等待真实回答；未回答不调用 interact；真实 confirm 接受后按回执 continuation 在同一会话读取最新 context，并使用最新 revision/input_digests 执行指定的新当前阶段，提交结果到 awaiting_review 后停下。知识刷新可递增 revision，不因正常刷新拒绝继续；必须保持同一 run、源确认 operation 和下一阶段。重复确认、阶段已待审或末阶段没有可执行 continuation 时不重做、不重复批准；保持 guided，不自动采用、发布或上传。正文、说明和按钮沿用用户沟通语言，保留必要术语。

兼容旧工作台保存的操作时，先核对实际 project_directory/worktree/run_id/expected_revision/input_digests。按钮只发送简短中文动作和后台请求链接，完整参数留在请求文件。把链接目标作为 --request-ref，按可见动作明确 --request-action（不能从文件自行改动作）。confirm/revise/rerun/guided 直接调用 flow interact PROJECT --request-ref REF --request-action ACTION；其余动作先调用 flow context PROJECT --request-ref REF --request-action ACTION --json 校验并内部读取 workbench_request，再按该完整请求使用既有接口。context 可因正常知识读取递增 revision；保持原 run/action，执行阶段使用最新 context 的 revision/input_digests，不重写原后台请求、不把 continue 改为 confirm。引用必须有原字节 SHA-256，属于准确项目/current run/requests/operation；动作、摘要、路径、版本不符时拒绝。不得复制 JSON、摘要或内部指令到可见回复。旧卡的无摘要请求先刷新，不把旧请求补造成新批准。continue 只执行当前一步；refresh 只刷新 context 并展示，二者不能作为阶段确认。文档原子项的用户满足声明不确认流程阶段。

兼容旧页面保存的操作时，先核对实际 worktree/run_id/revision/input_digests；confirm、revise、rerun 或 guided 请求实际调用 `flow interact PROJECT --request FILE`。按原始用户操作保存请求，不自行补造确认。过期操作刷新卡片，重复操作复用原 operation_id。修改与重做保留历史、材料和失败预算，不能重开 run 清除失败。普通问答不触发阶段执行。

`flow check` 执行检查期间持有项目锁。只读 flow context、工作台 show/status/detail 可读取带版本的运行中快照，不刷新补充或推进阶段。检查 argv **不得重入同项目的 render/advance/check 等写操作**，否则会遇到递归锁；需要检查入口时用 `--version`、`flow --help` 或独立只读校验脚本，真实业务检查按项目需要配置。界面导航不执行阶段；页面“继续”发来的请求仍要先核对真实 context。

项目知识召回与 Verifier 接入按[Server 项目数据](references/server-project-data.md)执行：需求/规划召回经验，实际采用经验时承接对应 Verifier，预览展示关联，完成与重验时再细读原定义并实际执行。不提前精读全部候选或单独挑选验证集合。原始页面、适用性、执行结果和历史分别保留；没有独立上传阶段。

## 阶段工作

阶段交付只使用协调器的固定产物：原则为 constitution.md，需求与澄清为同一 spec.md，技术为 plan.md，任务与一致性分析为 tasks.md 和 analysis.md。技术研究、数据与接口决定并入 plan.md，不另铺 research/data-model/contracts/quickstart。执行预览使用现有范围、影响与检查视图，不把原始 preview.json 当普通文档交付；实施交付代码，完成阶段交付实际检查与修复结果，不新增过程报告。

`flow advance.outputs` 只登记本阶段正式交付。临时提纲、命令回包、查询快照、审稿草稿和覆盖计算用临时目录，使用后清理；运行必需的请求、检查回执和恢复状态使用 `.formsy-sop/runs/<run>/` 内部目录，不进入正式产物列表。结论写回对应正文。收尾时清除未再引用的中间稿，不把它们提交到功能目录；仍支撑当前审阅或实际运行的内部记录不能当成可删除的草稿。

原则、需求、技术文档每次形成或实质修订后，按[展示与交互](references/presentation.md)完成本阶段适用原子条件与当前证据的比较、保存和复检；读取 context.document_selfcheck 核对缺口。不能等到任务分析才首次检查，不能用 Markdown 自查表或摘要替代正式回执。缺 Server 规则时仍做通用文档自检，分别保留项目层及完整方法走读中未核查的内容。

- constitution：按原 Spec Kit 宪章模板，结合用户要求、已有 README/docs 和有效原则撰写；没有 Birdview 仍可生成并标共享资料缺口。经真实项目绑定取得的 active required 只是补充约束。读取固定发布版 Birdview 架构和规则目录；发布不表示规范已启用。此阶段的 `stage_recall` 只读原生项目原则和已发布 Birdview 规则目录，不调用按任务相关性检索的业务经验，不展开经验文档正文或读取其业务 Verifier；单独配置的 active required 项目上下文仍遵循其现有读取规则。结果分别记录已发布规则数量和经验召回状态（不适用）；不得把规则目录数量写成经验命中数。
- specify（旧流程兼容 clarify）：按[需求阶段](references/requirements-phase.md)持续澄清并更新唯一 spec.md，同时实际读取产品模块字段、模板、PC 规则及来源，映射方式见[产品内容对应](references/spec-product-mapping.md)。此阶段按实际需求正常检索相关项目经验；选中材料才采用，保留未采用和冲突原因。不另立平行 PRD 或需求状态。处理需求、边界和验收；重要未知逐项澄清，无关键歧义可说明后继续。初稿即保存，澄清产生新版本，不等待全部确定。
- plan：调用技术规则形成模块、接口、数据、范围和实际检查计划，并按实际技术问题正常检索相关项目经验。已启用规范定位已读 knowledge entry/source_refs；Birdview 规则提议保留提议标签，不能混入强制项。 可列工作大项，正式可执行任务清单留到 tasks_analyze。
- tasks_analyze：将方案拆成含依赖与验收条件的可执行 checkbox 任务，写入 tasks.md；在 analysis.md 核对一致性；可用时读取项目补充知识的完整快照并记录采用项；始终保存内置文档原子自检回执，检查需求、方案、任务及原则的覆盖与冲突。文档语义审查是模型声明，不是业务运行证明。
- preview：汇总已有需求验收项和前面阶段已采用经验对应的原 Verifier，展示来源、阶段、版本与关联状态，不精读全部候选或独立挑选、确认验证集合；验收时再细读并执行。没有 Verifier 的内容只作指导，不新增验收项。按 references/acceptance-scope.md 承接已有清单，不把本阶段设为首次召回点。生成 preview.json，以 flow preview-local 保存来源可核对的本地预测影响，包含材料版本、采用规范、检查计划和未决；Birdview 可用时再补充固定共享基线与图示对照。标清预测与缺口，不自动发布共享候选。
- implement：程序自动保存 execution context 后，在已有授权和明确范围内连续完成本步任务；保留需求、计划、原始任务与已有验收断言。任务完成只改 checkbox，每批用 `flow progress` 保存进展并更新工作台，接口见[流程交互约定](references/workflow.md)。批次结束后继续未完成任务；仅阻塞依赖该问题的工作。全部任务完成后才提交本步结果。
- finish（旧流程兼容 reverify）：沿已有 findings、修复任务、需求验收及已采用知识的原 Verifier，只补查待办、失败/unknown/缺证据与实际受变更影响的项；首次验收无当前证据的需求仍待核查，不因阶段切换重做完整文档目录。保留有效未受影响结果及失败历史，目标或断言变化仍须复验，显式实际审计继续按原义务核对。使用 `flow check` 运行真实检查。失败保留，程序追加有依据的修复任务，在预算内由当前会话修复并重测。最终 review 与真实结果分别记录。

知识治理或汇总文档按需读取 knowledge / assemble Skill；这些方法归 SOP 自身，Server 项目知识仅在可用时按阶段补充。TraceAudit 是独立候选审查，不能替代代码执行或完成证明。

知识读取在 constitution/specify/clarify 使用 understand，plan/tasks_analyze/preview 使用 plan，implement 使用 execute，finish/reverify 使用 verify。阶段首次缓存读取结果（含失败）；显式重试才重新请求。保留实际响应快照、摘要、读取范围和 updated_at；updated_at 不是不可变版本。实际已采用 required 内容发生影响本次结论的变化时需复核相关产物，读取时间变化不能制造规则变更。已完成 run 的普通查看不自动读取新知识；补充读取不能冒充原完成依据。

## 身份与采集边界

Session 是真实采集会话；Task 是该 Session 内的原生交付目标，活动按原生生命周期回执归属。工作流 run 只组织阶段、文档与审阅，不能代替 Session/Task 身份。沿统一入口的采集进度合同核对 context 和真实触发引用；已有目标继续沿用，新目标显式执行原生 task-start/task-switch/task-resume，阶段切换不隐式创建或切换 Task；tasks.md 的 checkbox 条目只是实施清单，不逐项生成原生 Task。项目知识和规范使用项目级只读授权，不依赖独立业务 Task 写授权。旧业务绑定和失败回执仅作历史，不重放、不据此新增权限。

## 记录与交接

关键成果用 handoff，取舍用 decision，真实审查/检查用 verification，阻塞用 blocked；不因页面切换、每轮对话生成记录。指定产物保存后沿既有采集同步链处理；缺原生 state 或桥未接通时明确“工作文件已保存、未归档”，不能借其他日志制造 FormSy 身份。中断恢复先核对实际副作用，不盲目重放在途操作。

## 统一工作台入口

新任务沿 [展示与交互](references/presentation.md) 恢复原来的问答、决定、文档版本和自检粒度。每次回复记录当前变化，先保存收到的答案再继续长处理。流程状态用于组织执行，不用阶段总结替代问题台账。包内模板和模块提供操作方法；原 SOP 的通用审查方法和真实机器子集使用 general profile；项目实际采用的规则从 Server 独立读取并使用 server profile。两层分别保留来源、版本、回执和未核查，不能互相冒充。通用机器子集不代表完整 PC/TC/KB/TASK、安全、质量及领域范围已走读。


## 独立缺陷

明确修复独立 Bug 时使用 `flow enter --profile bugfix`，按[Bug 三阶段契约](references/bugfix-workflow.md)及固定 Spec Kit 原生指令执行 assess → fix → test；保留三报告、真实原复现、当前回归和已采用的原 Verifier。功能开发内部的修复沿原 run 循环，不自动迁移旧任务。

已有流程仅在用户要求且完成检查与重验均未开始时，可使用 `flow merge-acceptance PROJECT --input REQUEST.json` 显式合并。请求包含实际 run_id、expected_revision、原样 input_digests、稳定 operation_id 与用户原始 reason；保留旧阶段历史、检查及失败预算，不确认或推进当前阶段。已经开始验收的流程保留原序列。
