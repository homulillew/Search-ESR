# E0：五个旧 W 的离线复审

## Material Passport

- Type: offline semantic re-audit; single Codex reviewer, nonblind.
- Input: frozen B5 primary confirmation QCH and its five W outputs.
- New model / retrieval / Writer calls: **0 / 0 / 0**.
- Historical labels and files: retained unchanged; new rubric version only.

## 结果

| State | qid | 旧标签 | resolution objectives | 新标签 | 原因 |
|---|---:|---|---:|---|---|
| F08_S00 | 228 | W | 2 | W_independent | 捐赠交易与婚姻无子女状况是两项独立调查。 |
| F10_S00 | 971 | W | 2 | W_independent | 职称晋升与教育经历是独立目标；本科/研究生同校本身可以组成一个连贯判断。 |
| F11_S00 | 538 | W | 1 | W_multiquery | 插图数量及电话/电报内容共同用于识别一本书的出版内容特征，没有打包其他清理锈迹或人物谜题。 |
| F14_S00 | 843 | W | 1 | W_multiquery | 宗教、技术和国家机制是同一个 DLC 的发布特征组合。 |
| F14_S01 | 843 | W | 1 | W_multiquery | 同一 DLC 特征判断，查询对象缩到已观察的 EU4；不把具体 DLC 或其完整资格当作事实。 |

**2/5 仍是独立目标捆绑；3/5 按新定义可判为合法 coherent multi-query Need。**
五条来自四个 qid，三条重分类只涉及两个 qid；两条 DLC 状态不能算独立重复证据。

## 评价边界

一个书目/发布特征组合可以服务一个有界识别判断，不能因此把任意多个最终答案条件都算一个目标。共同指向某个人，不足以将其婚姻、捐赠、晋升、教育全部合并。此边界存在语义判断空间，全部标 medium ambiguity，并保存不同读法。这里的 objective_count 是 reviewer 判断，不是自动解析的事实。

`has_dependency=false` 表示从现有 Q 即能提出描述式检索入口，无须预先知道另一条 query 的答案；它不允许把随后发现的人名、书名或 DLC 名提前塞进依赖它的属性查询。`multiquery_sufficient=true` 仅指结构上能由一个 Need 下的互补查询处理，**没有测到检索充分性**。W_independent 的 false 也不表示多次检索永远不能解决，而是需要先选一个当前目标。

所有输入保持原样；其余六维按当前 QCH 审阅，未借助 gold、后续轨迹或全文核查。F14_S01 的 EU4 是可检验候选对象，查询未声称它已满足整题，也未确定具体 DLC。若改成询问一个尚未确定 DLC 的第三设计师，则会遇到需先绑定目标的问题。

这是 **rubric correction**。旧实验 16/27 和 FAIL 保持原结论。本轮不将五条局部重分类外推为对全部 27 条的重新评测，也不宣称新 prompt 已改善或 E2 已有收益。

逐项输入、旧理由、六维判断和新理由见 [REVIEW.json](REVIEW.json)，计数见 [METRICS.json](METRICS.json)。
