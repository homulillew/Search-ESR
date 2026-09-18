# 单入口 Query 初始化 v003

新增实验候选 `entry_v1`：使用 [五条通用原则](ENTRY_PROMPT.txt)，保持 `minimal` 的输入、输出与执行流程。具体错误类型放在 [离线审阅规则](ENTRY_EVALUATION.md)。默认运行组与默认生成策略未改变。

已完成 [开发 32 次](runs/20260918T072122.779614Z/README.md)和[新题 80 次](runs/20260918T072839.341275Z/README.md)真实 API 对照。精简版约节省四分之一 API tokens，但未证明检索或语义优势，保留为候选。见 [完整分析](../../../全链路排查报告/Query通用原则提示词落地与对照实验.md)。

开发对照命令（8 道已知开发题、每组两次，共 32 次初始 API 请求，修复另计）：

```bash
python -m experiments.query_initialization.single_entry.run --arms minimal entry_v1 --repeats 2 --workers 4
```

已完成 [首批 32 次真实 API 联调](runs/20260918T062309.405859Z/README.md)，详见 [落地与问题分析](../../../全链路排查报告/Query单入口初始化落地与联调.md)。

独立实验实现。默认只执行一次 Search，不修改 chat.py、Search–Open 工具描述、原文窗口或后续 Agent 循环。没有增加 candidate、gap、语义进展判定或 REPLAN。

## 初始化与交接

```text
完整原题 → 原文定位表 → 一次模型生成 → 确定性校验 → Search(top6) → handoff.json + 观察账本
```

最终候选 `minimal` 输出：

```json
{"intents": [{"basis_refs": ["q5"], "query": "university overseas campus 10th anniversary between 2020 and 2023"}]}
```

允许零或一个 intent；零条记录为 `no_direction`，不强制编造。引用编号仅表示原题位置，不是语义约束或方向 ID。完整问题和带编号原文同时提供给模型。模型无须抄写句子或计算字符偏移。

`source_units.py` 按换行、明确的行内项目符号及保守句末规则编号；常见缩写、学位缩写与不确定边界保留在较大单元中。这不是通用语义断句器。不改字符、空白或 Unicode，所有单元拼回原题；版本和 SHA-256 一起保存。偏移采用 Python Unicode 字符索引，区间为 `[start, end)`，不是 UTF-8 字节偏移。允许一条入口引用多个单元。

生成只检查格式、长度、引用存在性和重复编号。不能据此判断 query 是否忠实、线索是否有辨识度或候选是否正确。query 上限仍为 512 字符，输出仍为 1536 tokens，最多一次格式修复；API 截断不抢救、不追加修复。非法计划与失败不会静默退回整题搜索。

每次 Search 返回 top6；每个窗口标题与正文合计最多 400 tokens，总上限 2400。执行完成状态不等于语义成功。`handoff.json` 保存完整原题、引用表、尝试 ID、计划、实际参数、失败状态、原始结果及窗口引用。`observations.sqlite` 保存可恢复的来源版本和观察记录；`events.jsonl` / `trajectory.md` 保存完整 SDK 请求响应与工具轨迹。

## 逐步对照

|arm|模型输出|与前一阶段的主要差别|
|---|---|---|
|v2|goal + source_clues + query|现有 B 组，固定单方向|
|refs_goal|goal + basis_refs + query|原题摘录改为引用选择，并提供编号表|
|refs|basis_refs + query|去掉 goal 字段及对应指令，其余沿用旧选择与改写指令|
|minimal|basis_refs + query|使用 MINIMAL_PROMPT.txt 中的单入口、最小改写指令|

前三组沿用 `directions` 根字段；最后一组使用 `intents`。harness 统一交接结构。v2 的 basis_refs 由已验证的原题摘录位置映射得到，显式记录 `basis_origin=runtime_mapped_exact_quotes`，不伪装成模型选择的编号。

这是分阶段开发对照：引用接口变化同时增加了编号输入，不能将效果全部归因于字段名称；各组自由选择入口，也不能把端到端差异单独归因于 query 表达。保留全部实际提示词供复核。需另用固定原题线索的表达实验识别更细的因果。

## 运行

从仓库根目录执行，API 凭据沿用现有配置。默认四线程 API，单线程共享本地检索，使用 8 道已知开发题，每组一次，共 32 次尝试：

```bash
python -m experiments.query_initialization.single_entry.run
```

仅运行最终候选示例：

```bash
python -m experiments.query_initialization.single_entry.run --arms minimal --qids 591 786 --repeats 1 --workers 2
```

输出位于 `runs/<UTC>/`。该命令会产生真实 API 调用；默认运行不会自动抽样留出集或升级默认方案。联调题和次数可显式配置，原始问题之外不向模型输入标准答案。

开发结果审阅后，可在批次 `dev_review.json` 中记录 `proceed_holdout`，用 `python -m experiments.query_initialization.single_entry.holdout <development_run>` 建立一次性清单。随后用 `run --evaluation-lock <holdout_lock.json>`，显式传入清单中的 qids、arms、repeats。runner 会核对开发决定、题目、提示词、源码、数据集和 API 配置。修改已锁定策略后应重新做开发审阅，不覆盖既有清单。

离线测试与审计：

```bash
python -m pytest -q experiments/query_initialization/single_entry/test_single_entry.py
python -m experiments.query_initialization.single_entry.audit <run_directory>
```

## 后续阅读接口

初始化只交付观察，不自动生成 Agent 对话 checkpoint。下游可以读取 handoff，再使用已有观察工具继续 Open：

```python
from pathlib import Path
from llm_chat.observations import ObservationStore
from llm_chat.observed_agent import ObservedTools

session_dir = Path("<run_directory>/qid_591__minimal__r1")
store = ObservationStore(session_dir / "observations.sqlite")
tools = ObservedTools(store)
try:
    result = tools.execute("open", {"window_ref": "<handoff 中的引用>", "direction": "after"})
finally:
    tools.close()
    store.close()
```

现有可执行 Open 协议仍为 `before/after/around`，没有因本节点实现而增加 `focus`。下游若用这个例子继续读取，会追加观察账本；复核封存实验时应先复制账本，不能修改原始运行记录。

离线重启阅读检查（在临时账本副本上执行，不调用 API）：

```bash
python -m experiments.query_initialization.single_entry.check_handoff <run_directory>
```
