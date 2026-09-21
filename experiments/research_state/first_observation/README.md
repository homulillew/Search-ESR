# 原题直接首搜 → 首次来源笔记

独立实验；默认Agent不变。初始 `query == question`，没有初始化模型调用或goal。首个语义对象只有零到三条 `statement/source_ref/quote`。设计见[节点设计](../../../../全链路排查报告/原题直搜与首次Observation来源笔记节点设计.md)。

## 文件与职责

- `retrieval.py`：调用原有BCPlusSearcher、ObservedTools baseline和ObservationStore；只做首次真实Search。
- `contracts.py`：原文窗口、笔记、Search/Open提议、调用配置和用量的纯校验。不宣称校验蕴含关系。
- `run.py`：选择、采集、冻结计划、执行一个模型阶段、审计和导出。模型阶段不能执行工具。
- `artifacts.py`：严格JSON、散列、原子保存、连续日志。
- `prompts/note.txt` / `prompts/actor.txt`：来源解读与两组共同下一动作合同。

## 0. 安装与确认

```bash
python -m pip install -r requirements-chat.txt
python -m unittest discover -s tests -p 'test_first_observation.py' -v
```

以上不验证GPU检索。采集还依赖现有 `/data/model/Qwen3-Embedding-8B`、`BCPlus/scripts/search_bcplus.py`、`BCPlus/indexes/bcplus-qwen3-8b/` 和原检索依赖。缺资产应报告，不用旧v000轨迹/合成文本替代真实O1。

复制 `profile.example.json` 到本轮目录，填入本次实际批准的模型、无凭证endpoint及预算。示例8192/180秒不是已验证配置，尤其不能假设该额度能关闭或约束服务商的推理方式。`reasoning_effort`仅在该接口已验证支持时显式填写；不继承旧enable_thinking。安装完SDK再生成计划。

## 1. 冻结题目并真实采集（0次生成模型）

以下示例使用已知开发题，不称留出集。输出均必须是新路径。

```bash
RUN=/tmp/esr-first-observation-v1
mkdir "$RUN"
cp experiments/research_state/first_observation/profile.example.json "$RUN/profile.json"
# 先核对/编辑 profile.json，再继续。凭据仅存在 .env / 进程环境。
python -m experiments.research_state.first_observation.run select \
  --qids 517 546 776 519 191 71 --output "$RUN/selection.json"
python -m experiments.research_state.first_observation.run collect \
  --selection "$RUN/selection.json" --k 5 --output "$RUN/capture"
```

首搜保留原题字符串，包括空白/换行；query超1024 embedding tokens（含prefix/special）或16000字符时不执行、不裁剪。结果/错误按题保存。空返回也保留。每题`observations.sqlite`是现有原文观察账本，模型输入只取`collection.json`里的实际窗口；不得把账本全文供给模型。

采集会散列语料、索引和模型权重，可能有显著I/O成本。请使用不再写入的资产。未获得完整capture时，先排查环境/格式问题，不绕过capture_complete。

## 2. 来源笔记，先停在这里看bad case

```bash
python -m experiments.research_state.first_observation.run plan \
  --collection "$RUN/capture" --profile "$RUN/profile.json" --stage notes \
  --output "$RUN/notes-plan.json"
# 查看冻结请求：六份原题/原文，无gold、候选或初始goal；最多六次模型调用。
python -m experiments.research_state.first_observation.run execute \
  --plan "$RUN/notes-plan.json" --env-file .env --output "$RUN/notes"
python -m experiments.research_state.first_observation.run audit \
  --run "$RUN/notes" --output "$RUN/notes-review"
```

模型输出截断、无正文、未知引用、引文越界等保留，**不修复、不从reasoning拼笔记、不重复采样**。0—3条notes中任何一条非法，整份不注入。空notes是合法语义结果，另计遗漏风险。

原始响应在events.jsonl，审阅卡只展示正式content/工具/refusal。先标注笔记的来源保真与信息覆盖；不要修改模型原笔记。每个计划请求、模型响应/错误、配置和源码均可回查。哈希不是人类确认或语义正确证书。

## 3. 显式选择继续后，再运行A/B（不执行下一工具）

```bash
python -m experiments.research_state.first_observation.run plan \
  --collection "$RUN/capture" --profile "$RUN/profile.json" --stage actors \
  --notes-run "$RUN/notes" --repeats 1 --output "$RUN/actors-plan.json"
python -m experiments.research_state.first_observation.run execute \
  --plan "$RUN/actors-plan.json" --env-file .env --output "$RUN/actors"
python -m experiments.research_state.first_observation.run audit \
  --run "$RUN/actors" --output "$RUN/actors-review"
```

A=Q+同一首搜记录+O1；B只多实际模型生成的非空有效笔记。笔记空/无效/API失败时B精确回退为A输入，保持分母且memo_injected=false；回退的好动作不是笔记收益。note_outputs从原始响应重新校验，不接受人工编辑后的笔记替换。完全中断或未运行的笔记批次不能无声补成回退。

六题完整规模是6次首搜+6次笔记+12次Actor；初始化0次，后续工具0次。重复Actor共享同一份笔记；笔记成本只计一次，并单列。两个模型阶段可用不同profile但必须记录；A/B始终同profile，建议第一轮保持同一已验收模型。

退出2表示存在未交付/未知成本/完整性问题，应检查summary；不代表没有可分析记录。不因已有失败就自动加预算或调用。源代码/提示词/SDK改变后计划拒绝执行；审计历史运行须使用其匹配源码及环境，不把升级后重算结果冒作旧记录。

## 4. 报告

`cards.json`供逐项审阅，`mapping.json`保留分组、全部原始响应和运行信息；不是盲评。汇总保留全选择分母、实际调用分母、结构有效分母、空笔记、首搜失败、回退、无支持表述、未知成本和各组成本。不按每题best-of取成功。

未执行下一Search/Open，不报告新召回、最终准确率或长程记忆收益。不将旧原题/Selector实验百分比拼成本次对照。
