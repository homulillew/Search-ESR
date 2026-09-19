# E0 Need Review：固定前缀的一次决策实验

当前修订：`e0_audit_v1`。本次审计与修复见 [AUDIT_20260920.md](AUDIT_20260920.md)，后续执行直接使用 [CODEX_TASK.md](CODEX_TASK.md)。

E0 比较 A 原 Actor 直接继续、B 一般审查后继续、C Need Review 后继续。三道历史开发病例各组重复两次，共 18 次 Actor、12 次 Reviewer。**真实执行只调用模型并记录下一动作，不执行工具。** 它不能直接报告新检索收益、持久状态效果或 BC+ 答案准确率。

## 本次修复的范围

Reviewer 与 Actor 交接同一份可定位的引用索引；执行必须匹配事前保存的计划；审阅时核对实际请求/响应与固定前缀；日志损坏和中断保留可恢复记录与完整分母。原 `generic_review.txt`、`need_review.txt`、`memo.txt` 未改；新增来源合同 `need_review_source_grounded.txt` 和独立交接候选 `memo_indexed.txt`。

可选 `--memo-mode indexed_json_v1` 把审查文本和已见引用索引作为 JSON 数据交给 Actor。索引不提供未见全文，备忘不是新增事实；B/C 包装相同。此改动是显式的交接设计变化，有额外 token 成本。`--memo-mode legacy_text` 可保留旧文本包装，不能在同一批中混用后汇总。默认仍为legacy_text。

Search/Open、Query 初始化和默认 `chat.py` 未修改。E0 仍没有自动停滞触发、语义持久状态、强制换候选或停止接管。

## 文件与合同

| 文件 | 作用 |
|---|---|
| `checkpoint.py` / `checkpoints.json` | 固定源日志、完整工具批次与已见引用 |
| `node.py` / `prompts/` | 生成审查/Actor 请求，验证输出格式和协议 |
| `integrity.py` / `audit.py` | 冻结计划、引用解析、日志恢复和实际请求核对 |
| `run.py` / `report.py` | 准备、调度、执行、分组成本与审阅材料 |
| [EXPERIMENT_PLAN.md](EXPERIMENT_PLAN.md) | 当前对照与结论边界 |
| [VALIDATION_AUDIT.md](VALIDATION_AUDIT.md) | 本轮实际验证范围 |

## 最新结果与下一轮

809dfeb已推送 [e0_20260919T171923Z真实结果](runs/e0_20260919T171923Z/REPORT.zh-CN.md)：30次调用、零工具执行，一次C审查截断；尚无稳定整体改善。审计发现来源归属污染与Actor忽略提醒并存，不能统一归因API或模型上限。

下一轮只比较C0原提示词与C1来源归属提示词，保持原输入、legacy备忘、模型和输出额度。`--comparison source_contract_pair` 将两合同按固定调度交错，3题×2重复×2合同=12分支、24次逻辑调用。分支保留arm=C并记录review_contract，summary的by_contract给出分别分母和成本。不得同时切换indexed交接；该组合会在调用前拒绝。

原ABC仍可用 `--comparison abc`；`--review-contract baseline|source_grounded_v1` 供单独冻结的ABC版本使用。配对模式自动分配两个合同，`--review-contract` 保持baseline。

## 准备和执行

所有命令在仓库根目录运行。离线步骤只需标准库；真实 API 执行沿用 `requirements-chat.txt` 与现有凭证配置。不得输出密钥或认证头。

```bash
python -m unittest discover -s tests -p 'test_need_review*.py' -v
python -m experiments.research_state.need_review.run prepare --output /tmp/esr-e0-prepared
```

下面用 Bash 数组保证计划与执行的公共设置完全相同。目录和文件都应是新的；API_BASE 填现有配置的无凭证基础地址。

```bash
API_BASE='https://你的服务商地址/v1'
COMMON=(--prepared /tmp/esr-e0-prepared --repeats 2 --seed 20260919
        --review-max-tokens 512 --sdk-max-retries 0
        --memo-mode legacy_text --comparison source_contract_pair --expected-base-url "$API_BASE")
# 历史模型不可用时，在首次调用前决定并加入 COMMON：--model 可用模型名
python -m experiments.research_state.need_review.run plan "${COMMON[@]}"   --output /tmp/esr-e0-approved.json
# 检查并保存计划之后才执行：
python -m experiments.research_state.need_review.run execute "${COMMON[@]}"   --plan-file /tmp/esr-e0-approved.json --env-file .env   --output experiments/research_state/need_review/runs/e01_source_first
```

新付费 CLI 必须有 `--plan-file` 和 `--expected-base-url`。参数、提示词、准备数据或实现改变后重新冻结计划；不要改完代码继续沿用旧计划。API 基础地址也必须与配置一致。计划哈希防止意外漂移，不是签名或模型采样确定性保证。兼容的函数库调用仍允许注入客户端进行未批准的离线测试，这类运行标为 unapproved，不进入正式结果。

Reviewer 无效/API 失败时保留原始输出和成本，Actor 无备忘回退。没有自动 JSON 修复。适配器/本地校验异常为 harness_error，不算模型推理失败。完整工具调用但 `finish_reason=stop` 的服务响应仍保留动作意图，同时标记旧协议不兼容。退出码 0 只表示机械完成，非零失败分支也不能删除或反复生成直到满意。

## 审阅

```bash
python -m experiments.research_state.need_review.run review   --run-dir experiments/research_state/need_review/runs/e01_source_first   --output experiments/research_state/need_review/runs/e01_source_first/review
```

先只读 `prefix_cards.jsonl` 写下合理下一动作，再读 `cards.jsonl` 标注，最后看 `private_key.json` 分组。已经看过输出的审阅者不能宣称盲评；JSON 格式也可能暴露组别。引用存在与语义支持分别评价，所有标签初始为 null。分组成本和失败在 `summary.json` 的 `by_arm` 中；未知成本不当作零。完整性错误会保留卡片并返回非零退出码。

## 历史与限制

检查点仍是源提交 `6d1be8d9b04972d8a55752449294abf12383f554` 的 546 seq29、776 seq53、517 seq21，使用旧 v000 Search/get_document。它们用于研究重复路线、关系绑定和正常纠偏，不是当前 Search/Open 的端到端验证。这批全都自然结束，不是“充分仍不提交”的已验证样本。

旧 E0 合同和此前验证记录保留在版本历史；[旧实现说明](https://github.com/homulillew/Search-ESR/blob/0193fc072c31554284c9459bac62f436e9f7ba64/experiments/research_state/need_review/README.md)中的 execute 命令不再是当前入口规范。本次未额外执行真实API；既有E0结果完整保留，新增E0.1候选只做离线合同测试，E1工具分叉尚未实现。
