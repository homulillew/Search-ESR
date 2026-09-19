# 交给 Codex：执行 E0 真实模型实验

下面的任务可直接复制给具有本仓库、API 凭证和网络访问的 Codex。实验入口已经实现；任务是按冻结计划运行并分析结果。真实执行只产生下一条模型响应，不执行响应提出的工具。需要真实 Search/Open 的短分叉属于之后另提的 E1。

---

请在当前 Search-ESR 仓库执行 `experiments/research_state/need_review/` 的 E0 实验，先完整阅读该目录的 `README.md`、`EXPERIMENT_PLAN.md`、`checkpoints.json` 和三个提示词文件。目标是定位 Need Review → 原 Actor 下一动作的链路问题。

遵循仓库现有 AGENTS.md（如有）。不要修改默认 Search/Open、Query 初始化或 Actor 提示词。不要运行 BC+ 完整 rollout，不要执行模型提出的工具，不要自动扩展成 E1、持久 Research State 或停止器。不要读取或打印 API key、`.env` 内容或请求认证头。

## 1. 冻结与离线检查

记录当前代码提交、工作树状态、固定源提交、提示词与检查点哈希，以及本次执行命令。检查当前工作区是否有用户改动，保留已有文件。使用新的运行目录，例如 `experiments/research_state/need_review/runs/e0_<UTC时间戳>`，不覆盖原轨迹和既有运行。

在仓库根目录执行：

```bash
python -m unittest discover -s tests -p 'test_need_review*.py' -v
python -m experiments.research_state.need_review.run prepare --output /tmp/search-esr-e0-prepared
python -m experiments.research_state.need_review.run plan --prepared /tmp/search-esr-e0-prepared --repeats 2 --seed 20260919
```

准备目录也必须为新目录；上次已存在时换一个路径，所有后续命令保持一致。准备使用提交 `6d1be8d9b04972d8a55752449294abf12383f554` 对应的三个固定 `api_request.request`：546 seq 29、776 seq 53、517 seq 21。入口核对配置中的原始 Git blob SHA 后才解析前缀，不依赖完整 Git 历史。文件缺失或哈希不一致时，应取得对应原始文件再继续；不要跳过哈希检查。

确认计划为 18 个分支、18 次 Actor 和 12 次 Reviewer，共 30 次逻辑模型调用。默认 SDK 重试为 0。检查准备产物只含原题、已见消息和合法引用；选点说明、分析结论、gold、未来事件和未见全文不得进入模型请求。

确认服务支持捕获的模型、工具请求参数和完整前缀长度。A Actor 必须等于检查点请求，除显式记录的模型覆盖。B/C Reviewer 与 Actor 使用相同模型。若历史模型不可用，选择本任务环境可用且满足要求的模型，并在首次真实调用前写明 `--model` 覆盖及其原因；不要根据某组输出结果再挑模型。`plan` 和 `execute` 的 `--model`、`--review-max-tokens`、`--sdk-max-retries` 必须一致，覆盖参数变化后先重新生成计划。若当前服务不能容纳完整前缀，记录阻塞原因，不擅自摘要、截断或替换检查点。

运行前固定本次配置与提示词。离线实现缺陷可以先修复并重新测试，但必须记录修改并在首个真实调用前重新冻结。开始真实调用后不针对某题或某组结果改提示词；需要改动时先完成/结束本批并报告，再另立实验版本。

## 2. 按计划执行一次完整批次

以下示例使用检查点模型；把 `e0_20260919_01` 替换为本次新目录名，并在后续审阅命令中保持一致。已有凭证按仓库约定读取，不在日志或报告中展示。

```bash
python -m experiments.research_state.need_review.run execute \
  --prepared /tmp/search-esr-e0-prepared \
  --output experiments/research_state/need_review/runs/e0_20260919_01 \
  --repeats 2 \
  --seed 20260919 \
  --review-max-tokens 512 \
  --sdk-max-retries 0 \
  --env-file .env
```

如已在执行前决定覆盖模型，在命令中显式添加 `--model 模型名` 并记录完整配置。不增加模型试跑或额外样本来挑选较好结果。

Reviewer 无效或 API 失败由入口记录并回退到无备忘 Actor。不要人工在线修正 Reviewer 输出，不做 JSON 修复，不删除错误分支，不手动重复生成直到得到满意结果。Actor 报错也保留在该分支的分母中。API 全局不可用或上下文不兼容时，保留实际已发生的调用与失败状态，报告未完成分支，不假称整批完成。

来源/哈希不符、请求配置歧义或凭证配置错误会在首个模型调用前终止；修复并重新冻结配置后再开始。不能跳过验证，也不能把配置错误当作 Reviewer 无效而强行运行回退组。

保存实际请求、完整响应、校验结果、参数差异、用量和耗时。检查请求与输入哈希，确保三个 arm 使用相同前缀。一次响应有多个工具调用时保留全部；不要为了比较挑选其中一条，也不要执行调用。原工具名、参数和 tool_choice 保持捕获语义，不能将 v000 改成当前 Search/Open。

若响应有完整工具调用却返回 `finish_reason=stop`，保留其动作意图，结合 `syntactic_complete`、`protocol_compatible` 和 `tool_calls_with_stop` 单独报告。旧 Agent 对这种返回不兼容，不能说原运行时已可执行，也不能把 API 格式差异误判成动作语义失败。自然语言弃答与 SDK refusal 字段也要分开。

## 3. 离线审阅与逐题链路分析

```bash
python -m experiments.research_state.need_review.run review \
  --run-dir experiments/research_state/need_review/runs/e0_20260919_01 \
  --output experiments/research_state/need_review/runs/e0_20260919_01/review
```

先读原题和可见前缀，在未查看分支输出时写下允许的合理下一动作，再按生成的 `cards.jsonl` 和 `rubric.json` 逐项标注。完成逐卡标注后再打开 `private_key.json` 查分组。若你此前已看过输出，明确说明，不宣称盲评。内容格式可能暴露 arm，也应说明此限制。只有引用存在性属于机械判断；语义支持必须看实际可见内容。

每个分支至少回答：

1. 审查是否识别了有影响且尚未证实的前提？如果为 null，是否合理？
2. `next_need` 是否未解决、是否影响当前判断，能否容纳反证或替代关系？
3. Actor 是否在语义上响应了一个合理需求？Query 改词但保留错误过滤不算改善。
4. Actor 自身的下一动作是否合理？服从一个错误需求不能算成功。
5. 是否出现无依据换候选、错缩年份、错绑定关系、忽略已有原文或过早结束？
6. 517 的正常纠偏是否被保留？它不是整题正确的 gold 对照。
7. 实际成本、失败和回退是什么？自然语言弃答与协议拒绝分别判断。

先给每组完整分母及失败数，再给逐题、逐重复的记录。三题都是开发病例；不报告 BC+ 准确率提升，不对两次重复做强统计推断。B/C 改善相近时，结论应优先支持更简单的一般审查，不能把差异强归因于 gap。C 有效也只能支持整个审查包，暂不证明某一个字段的独立作用。

## 4. 交付与下一轮

将本次运行配置、原始记录、人工评价文件和中文分析报告整理到本次目录。报告包含：执行是否完整、配置与版本、各组成本/失败、逐题链路发现、最有说明力的 1–3 个 bad case，以及下一轮仅改一处的建议。必要时引用精确消息/观察位置，不把全文缓存当作模型已见证据。

根据失败位置选下一步：审查读错证据→改读取合同；需求是单向确认→改需求定义；需求合理但 Actor 忽略→改传递合同；B/C 相近→保留简单 B；动作合理→提出 E1 的工具恢复实验。停止问题另选当前协议检查点做诊断。不要在同一批里同时改这些节点，不自动执行下一轮。

提交前检查无凭证、环境文件、缓存模型或无关数据进入 diff；保留足够复核实验的请求响应和源哈希。完成后给出代码/配置提交、本次运行目录、实际调用数和下一处建议。如果当前任务同时明确授权推送，则推送实验记录并提供提交链接；否则先形成可复核提交和报告。
