# E0：固定前缀上的一次 Need Review

这个独立实验入口检验一个局部问题：**在完全相同的真实轨迹前缀上，一次简短的前提与信息需求审查，能否改善原 Agent 的下一决策？** 代码只请求下一条模型响应，保存完整工具调用批次，不执行这些工具。真实模型实验由后续 Codex 执行；本次交付不包含模型实验结果。

原始 Search/Open 和 Query 初始化保持其既有实现。E0 尚未接入持久 Research State、自动停滞触发或停止接管。三道已讨论的开发病例用于找到下一处具体的 bad case，不能用来报告 BC+ 总体准确率提升。

## 三组比较

| Arm | 在固定前缀上做什么 | 模型调用 |
|---|---|---:|
| A | 原请求直接继续一次 | 1 次 Actor |
| B | 一次自由文本进度审查，再让原 Actor 继续一次 | 1 次 Reviewer + 1 次 Actor |
| C | 一次结构化 Need Review，再让原 Actor 继续一次 | 1 次 Reviewer + 1 次 Actor |

B/C 使用同一模型、同一已见材料和引用索引、同一审查输出上限、同一备忘包装和注入位置。默认审查上限为 512 tokens；Actor 保留检查点原参数。三题、三组、两次重复对应 **18 次 Actor + 12 次 Reviewer = 30 次逻辑模型调用**。默认 SDK 重试次数为 0；改变重试配置时，实际 HTTP 请求可能更多。

C 相对 B 检验整个定向审查包。即使 C 更好，也不能直接归因于 `next_need` 单字段、JSON 格式或持久状态。实际输出 token 不一定相等，需报告成本。

## 文件

- [checkpoints.json](checkpoints.json)：三个固定检查点及源提交。
- [prompts/generic_review.txt](prompts/generic_review.txt)：B 组提示词。
- [prompts/need_review.txt](prompts/need_review.txt)：C 组提示词。
- [prompts/memo.txt](prompts/memo.txt)：B/C 共用的 Actor 备忘包装。
- [EXPERIMENT_PLAN.md](EXPERIMENT_PLAN.md)：输入合同、评价表、失败归因和下一轮规则。
- [CODEX_TASK.md](CODEX_TASK.md)：交给 Codex 的可直接执行任务。
- [VALIDATION.md](VALIDATION.md)：62 项离线测试及三个真实前缀的模拟链路验证记录。

## 离线准备与检查

在仓库根目录执行；准备、计划和人工评价材料生成均不调用模型。需要仓库中三个原始事件文件；普通 checkout 或保留原始字节的仓库下载均可，不依赖完整 Git 历史。

```bash
python -m unittest discover -s tests -p 'test_need_review*.py' -v
python -m experiments.research_state.need_review.run prepare --output /tmp/search-esr-e0-prepared
python -m experiments.research_state.need_review.run plan --prepared /tmp/search-esr-e0-prepared --repeats 2 --seed 20260919
```

`prepare` 先核对本地 `events.jsonl` 的原始 Git blob SHA 是否等于配置所固定的源文件，再解析到指定 `api_request.request` 为止，检查完整工具批次和引用，保存独立快照及哈希。对整个文件计算字节哈希不会把未来事件解析进模型输入。模型输入不包含轨迹未来事件、标准答案、分析稿或未见全文。选点理由只用于离线记录，不进入模型请求。`plan` 将交错执行安排及逻辑调用数输出到终端，便于在 API 调用前检查规模。`plan` 与 `execute` 都接受 `--model`、`--review-max-tokens`、`--sdk-max-retries`；执行前的计划必须使用相同参数。

准备自定义检查点时可使用 `prepare --checkpoints PATH --repo-root PATH --output DIR`。这会成为新的实验选点配置，应单独保存配置与哈希，不把结果混入本轮三题。

## 后续真实模型执行

安装仓库现有 API 依赖（`requirements-chat.txt`），按仓库约定配置 `.env` 或环境变量中的 API key、基础 URL。输出目录必须是本次新目录；不要覆盖原轨迹或已有实验。下面保留检查点模型，运行前需确认服务支持该模型及捕获的请求参数。

```bash
python -m experiments.research_state.need_review.run execute \
  --prepared /tmp/search-esr-e0-prepared \
  --output experiments/research_state/need_review/runs/e0_first \
  --repeats 2 \
  --seed 20260919 \
  --review-max-tokens 512 \
  --sdk-max-retries 0 \
  --env-file .env
```

历史检查点使用的模型如已不可用，可在上面命令中显式增加 `--model 可用模型名`，并先使用同一覆盖参数重新运行 `plan`。该覆盖同时用于 Actor 和 Reviewer，并作为实验变化记录。不要依靠 `.env` 中的模型名暗中替换捕获模型。模型能力、上下文长度和参数兼容性应在计划冻结前检查；本入口不会偷偷摘要、裁剪前缀或修改 Actor 的生成预算来迁就服务。

Reviewer 将捕获的全部 messages（包括原 system）和引用索引序列化为输入数据，由本组审查提示词作为有效 system 指令。B/C 这层包装完全相同。Reviewer 沿用原生成/thinking 配置，但移除工具权限、原 response_format 和流式选项，固定单个非流式响应，并设置审查输出上限。这些是审查请求与 Actor 请求的预期差异；实际请求完整记录。有歧义的 `extra_body` 保留键覆盖会被拒绝，不隐式改写。

`execute` 只会调用模型，**不会执行模型提出的 Search、get_document、Open 或其他工具**，因此不需要启动 BC+ 检索器、加载 embedding 模型或恢复语料库。一次 Actor 响应中多个工具调用会完整保留，属于同一个动作批次。自然回答、工具调用及生成/协议失败分别记录；自然语言中的弃答含义由离线语义审阅判断。

API 若返回完整工具调用但 `finish_reason=stop`，记录仍保留整个批次，标记 `response_kind=tool_calls`、`syntactic_complete=true`、`protocol_compatible=false` 和 `tool_calls_with_stop`。旧 Agent 要求 `finish_reason=tool_calls` 才执行，因此这种返回可以评价动作意图，但不能宣称原运行时会实际执行；协议兼容性与语义动作质量分开标注。

Reviewer 输出无效或请求失败时，保留错误、原始输出和已发生的成本，Actor 使用无备忘的原请求继续一次。C 的 JSON/schema/引用无效记为节点失败；B 的空响应、拒绝响应、工具调用或未正常结束同样不能注入。没有自动修复或额外重试审查。语义上不合理但结构合法的审查仍属于该组的真实表现，不能人工修正后再记作自动结果。

回退只适用于实际审查输出无效或审查 API 调用失败。来源/哈希不符、请求配置歧义及凭证配置错误会在首个模型调用前终止，不能靠回退绕过输入合同。

## 生成审阅材料

```bash
python -m experiments.research_state.need_review.run review \
  --run-dir experiments/research_state/need_review/runs/e0_first \
  --output experiments/research_state/need_review/runs/e0_first/review
```

准备目录保存 `manifest.json` 与 `checkpoints/<id>.json`。执行目录保存计划/版本/哈希的 `manifest.json`，提示词及检查点副本，各分支的 `branches/<sample_id>/events.jsonl` 和 `result.json`，以及 `summary.json`。中断不会抹去此前分支，尚未执行的分支也保留在计划分母中。

审阅目录包含 `cards.jsonl`、`rubric.json` 和分组映射 `private_key.json`。人工标签初始为 null，需逐项填写标签、依据与说明。缺失、失败、部分完成的分支都保留；中断时尚未校验的审查输出标记为 `unvalidated_partial`。先独立读原题和检查点已见观察，写下几种合理的下一动作，再评价隐藏组名的输出卡；完成逐卡标注后再读映射。内容和格式可能暴露组别，因此这里是尽量降低组名影响，不声称完全盲评。保留机器记录与人工标注的分界：引用存在由代码检查，引用是否支持断言、需求是否未解决、动作是否响应合理需求由人工判断。

一行一个分支保留成功、节点失败、API 失败和 Actor 错误；不得删除失败分支后比较有效样本。按 [实验计划](EXPERIMENT_PLAN.md) 找到下一处链路问题，再做一次局部修改。

## 当前检查点的边界

三个检查点固定在提交 `6d1be8d9b04972d8a55752449294abf12383f554`，均来自历史 `v000_baseline`：Search 返回前 1600 字符，可继续 `get_document`。它们不是当前定向窗口 Search/Open 协议。

| 检查点 | request seq | 选点用途 |
|---|---:|---|
| qid 546 | 29 | 第七次 Search 后，观察路线前提和关系取证 |
| qid 776 | 53 | 第十三次 Search 后，观察重复检索及条件缩窄 |
| qid 517 | 21 | 第五次 Search 后，检查是否破坏原本存在的纠偏行为 |

517 的正向性只指纠偏行为，并不表示整题答案和解释正确。该旧批次实际自然结束，不能用来诊断用户其他 rollout 中“证据充分仍不提交”的情况。停止问题需要另选真实检查点；`next_need = null` 也不会直接触发提交。

只有 E0 出现有依据的需求和合理的动作变化后，才考虑 E1：实际执行下一批工具，再观察一次决策。E1 需要恢复工具版本、有效引用和原剩余预算；本入口没有实现这一步。若要检验当前 Search/Open 的收益，先在当前冻结版本采集新前缀，所有组共享该版本。
