# 执行前审计

## 基线

已执行用户指定的`git fetch origin --prune`、远程`rev-parse`和20条log检查。远程`experiment/minimal-semantic-package`仍为任务书已知HEAD `1e5b426b037eda91395664b820ce64cd4f12c708`，没有前移。新分支`experiment/minimal-recoverable-loop`直接从该远程HEAD创建。

旧实验已完成E1 FAIL；新研究问题是保护事实入口及闭环恢复，不能将旧FAIL重标PASS。本轮不改旧结果。历史保护清单为22,238个tracked实验文件；其它未跟踪的auto_research、research_loop及中文研究笔记保持原状。

## 已完成的离线材料

- 53个真实历史observation/20qid及完整出处；没有新检索。
- 56个语义召回项及禁止强化规则，Q/R源锚点、单一熟悉材料的reviewer披露。
- 10个Fresh qid按预注册式确定规则冻结，正文不用于Prompt修补。
- 6qid/12个Recovery prefix、40个自然Closure snapshot的来源ID冻结；对应stage语义Gold未开始，待前置PASS后审查。
- 106个Writer实际requests、Admission确定性依赖编译器及E1计分器；尚无实际Writer候选，Admission数目未知。
- 最小视图/Mutation/NoGain/Closure权限契约；此为离线准备，不宣称完整live scheduler已通过。

## 明确处理的任务书边界

1. 第47节fresh授权：本轮付费调用仍为0。完成精确请求commit/hash后，只申请106次Writer；未来Admission单独授权。
2. 召回数值门槛与“safe but conservative”表述：已向用户询问可选偏好；当前默认严格全部门槛。未收到回答不会自动授予例外。
3. Actor示例中的expected_gain不在允许列表内：以允许列表为契约；E2实际request前披露schema，不引入新语义字段。
4. OPEN不是任意全文读取：机械映射现有open(window_ref,direction)，pattern为before/after/around。没有新增工具。
5. 最新真实acquisition是现有SearchFindTools，非Orthogonal替换；模型仍DeepSeek/deepseek-flash。当前无需GPU，也没有启动检索服务或发送连通性探针。
6. 任务书要求所有未来live requests先存在才付费；自适应未来请求无法预知。冻结预算不等于精确请求授权。按依赖波次准备/提交/授权，绝不以本轮106次许可自动执行loop。
7. 旧C未自动认定为Verified：E2/E3前需要source-grounding资格审查，不能复制旧Writer错误进入trusted C后声称无污染。
8. Closure bank的complete数量尚未审查；若为0则指标null，不能冒充safe高Recall或制造额外证据。

所有本轮选择、参考与代码目前均在新目录，历史实验/production schema均不变。最终准备检查与哈希见PREPARATION_VALIDATION及WRITER_FREEZE。
