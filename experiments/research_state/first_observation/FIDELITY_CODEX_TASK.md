# Codex任务：首次来源笔记P0/P1保真改写

只做六份冻结O1上的提示词对照。任务目的、评价边界见 `全链路排查报告/首次来源笔记保真改写P0P1对照方案.md`。不要重新Search、Open、改Query、生成初始goal，或启动Actor/H2/rollout。

## 1. 先离线核对

从完整checkout运行，保留命令输出和实际退出码：

```bash
python -m unittest discover -s tests -p 'test_first_observation*.py' -v
```

必须确认 `ActualArchiveTests.test_pinned_archive_prepares_offline` 未跳过。原44项与新增测试分别报告，不把缺失资产测试算通过。完整档案在 `runs/notes_qwen_20260921`；不得从报告重写collection、替换原文或改旧SHA。无需本机语料库/权重/GPU来做此次配对；模型阶段只读取已归档窗口。

先读旧REPORT、METHOD、共同note.txt、新addendum、fidelity.py和本轮设计。P0的Git blob固定为 `060e81d25a99e32ca66751702ca8ea24999c4ec7`，不要编辑它。P1是P0原样追加独立段落，不能中途改提示词。

## 2. 建立新目录和冻结计划

以下命令无模型调用：

```bash
EXP=experiments/research_state/first_observation
OUT="$EXP/runs/note_fidelity_$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$OUT"
python -m experiments.research_state.first_observation.fidelity plan \
  --archive "$EXP/runs/notes_qwen_20260921" --output "$OUT/plan.json"
python -m experiments.research_state.first_observation.fidelity review-template \
  --plan "$OUT/plan.json" --output "$OUT/review_basis.json"
```

检查计划恰有12个jobs、各组6个，同题相邻、P0/P1各先行三题；只有system文本不同。沿用归档profile的模型、端点、8192、180秒、零重试，不传新的thinking或sampling选项。端点失效/配置不适用则停止报告，不静默更换。

## 3. 调用前填写review_basis.json

仅查看每题Q/O1，为明确存在的关键局部关系填写id/description/source_ref/quote，并说明限制和替代选择。无明确核心可以声明 `no_clear_core=true`，例如517不能凭弱匹配强制产生目标候选。所有quote必须在可见窗口正文中；主体、归属、时间含义需另外人工/辅助代理复核。

填写reviewer，保留prior_cases_known的真实值，确认尚未看本批输出后 `current_outputs_seen=false`。标注不是模型输入，也不是金标答案。保存实际复核时间与所用材料，可额外记录文件SHA；不要倒填时间。对于明确core要保持宽于单句措辞：允许模型合并表达或选择同等有效的关系，不以逐字一致评分。

## 4. 执行一次已冻结批次

这是本任务唯一产生费用的命令，最多12次模型请求，不调用检索工具：

```bash
python -m experiments.research_state.first_observation.fidelity execute \
  --plan "$OUT/plan.json" --review-basis "$OUT/review_basis.json" \
  --env-file .env --output "$OUT/model"
```

凭证只来自环境/本机.env，不能提交。返回2表示存在未交付或成本不全；仍保留全部分支。API失败继续其余计划项；中断/本地程序错误停止并保留未运行分母。不得补采、自动repair、从reasoning抽JSON、静默续跑或重试直到全成功。

## 5. 审计、逐条分析

即使execute返回2，也对已落盘产物运行：

```bash
python -m experiments.research_state.first_observation.fidelity audit \
  --run "$OUT/model" --output "$OUT/review"
```

源快照/计划/预评阅散列不符先排查，不能重新签名掩盖变更。先填 `review/cards.json` 的逐条标签、核心覆盖及理由，另存首评文件，然后打开mapping配对；保留首评和最终解释，不覆盖自动导出的空模板。诊断文件只统计条数、交付和用量，不是语义judge。

所有12个计划分支写入报告，不将失败删除。逐条区分来源支持、归属/主体/时间范围和选材价值；unsupported不等于false。允许同窗上下文，但不把邻近叙述归给被引用书籍。空notes不能自动判成功；保真提升必须与核心保留一起看。按题配对，不把各条笔记当独立样本。涉及776标题、71地点/来源等歧义，保留严格/宽松口径，不夸大确定错误。

输出 `REPORT.zh-CN.md`、逐题bad_case和费用/失败表，交代模型标注者、非盲及开发题限制。明确本轮只测提示词干预，不测State长期收益、检索或最终准确率。提出下一轮只改一处的建议，不自动启动H2。

## 6. 提交边界

可以提交计划、输入快照、模型请求/响应、错误日志、源码快照、预评阅和结果报告。检查并排除.env、API key、私有header、完整数据库/索引/模型权重。不要修改旧笔记输出、旧报告、旧采集、默认Agent、Search/Open或note.txt。本次P0重新生成，不能复用旧控制组结果；也不能逐题挑P0/P1较好的笔记交给Actor。
