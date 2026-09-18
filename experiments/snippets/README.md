# 离线文档内片段选择

运行：

```bash
python experiments/snippets/compare.py --batch 20260917T090903.022551Z --qids 546 1094 517 --budget 400
```

固定原轨迹的 query 和文档排序，使用本地 tokenizer 和只读 SQLite；不调用 LLM，也不加载 embedding 模型权重。输出位于 `experiments/offline/snippets_v001/<UTC时间>/`。每次独立目录，保存原文对照、配置及源码。

selector.py 为段落/换行优先分块及文档内 BM25。没有词面匹配则回退开头，原始 HTML 暂缓清洗。单一片段可能丢失身份/表头或跨比赛上下文，不应直接当作已经验证的证据；本阶段不接入在线 Agent。

测试：`python -m pytest tests/test_snippets.py -q`

[首次结果与人工复盘](../offline/snippets_v001/20260917T095014.433850Z/README.md)

## v002：定位后扩展

运行：`python experiments/snippets/compare_windows.py`

复用 v001 的冻结 query、文档与固定块结果，比较句子/行 BM25 定位后在 400-token 预算内扩展相邻上下文。代码为 `window.py`，输出为 `experiments/offline/snippets_v002/<UTC时间>/`，不接入在线 Agent。

[首次结果与退化案例](../offline/snippets_v002/20260917T172302.738631Z/README.md)。候选单位变化也改变 BM25 排序，不能归因为单独的扩展操作。测试：`python -m pytest tests/test_snippets.py tests/test_snippet_windows.py -q`。

## v003：单块与多块

运行：`python experiments/snippets/compare_multiblock.py`。固定 v001 分块与 BM25 排序，对比 top-1 和最多两个不重叠块，每块上限 400 tokens。本轮增加总预算，不是等总预算实验；仅评价当前 query 的信息需求。

[实验结果与 Open 读取检查](../offline/snippets_v003/20260917T173025.031319Z/README.md)。新增测试：`python -m pytest tests/test_snippet_multiblock.py -q`。

## v004：空白重叠与相同总预算上限

运行：`python experiments/snippets/compare_budget.py`。同时保留旧严格重叠、允许纯空白重叠、单块 400 tokens、双块合计 400 tokens 四组对照。双块按前缀裁短，短块剩余额度转给另一块；该策略的截断损失明确记录。

[实验报告](../offline/snippets_v004/20260917T173648.577447Z/README.md)。测试：`python -m pytest tests/test_snippet_budget.py tests/test_snippet_multiblock.py -q`。

## v005：父块内短窗口

运行：`python experiments/snippets/compare_short_window.py`。固定 v004 父块和分配额度，比较前缀截取与父块内句子/行定位后扩展。保持原文位置，不新增模型调用。[结果与身份丢失案例](../offline/snippets_v005/20260917T174229.428315Z/README.md)。测试：`python -m pytest tests/test_short_window.py tests/test_snippet_windows.py -q`。本版本未替换在线 Search。
