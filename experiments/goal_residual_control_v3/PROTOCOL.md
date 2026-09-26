# V3 protocol

## Authority and immutable boundaries

以用户本轮任务书及 `V3_DESIGN_AUDIT.md` 为准。旧实验、生产工具、Retriever、localizer、状态字段、两 Claim 上限、三决策/两动作预算以及 v2 L2 batch scheduling 全部不变。原始 baseline tracked 文件见 `analysis/HISTORICAL_HASHES.json`。

## Capability first

`capability.py` 不执行研究工具。离线测试完整 schema 的正反例、schema/registry 区分、请求内容等价、无输出修复和 24 个历史包覆盖。服务端探针在提交 freeze 后运行，每个 ID 最多一次；四并发、240 秒、无 transport retry、无 redirect。

先运行四个 Responses probes，检验必填/额外键/枚举/整数边界、数组长度、完整 Actor oneOf 和完整 Updater。探针故意让普通文本要求与 schema 冲突，以检测字段被忽略的情况；它们是合成 capability diagnostics，不属于历史研究结果。

若 Responses 不可用，再执行三个预冻结 strict-function probes：数组上限、精确 Actor schema、仅逻辑等价变换后的 Actor schema。等价变换只将 disjoint const-discriminated oneOf 换为 anyOf、字符串 const 换 singleton enum、删除已被 non-whitespace pattern 蕴含的 minLength=1。**保留所有数组 min/max 和字段约束。** 不把外层工具执行语义改成 function execution。

完整 schema 能力无法确认时 fail closed，停止研究阶段；不把 JSON mode、prompt 遵循或局部 schema 当作 exact constrained output。任何错误原文、失败、usage 均保存，密钥不写入请求留档。

## Historical preflight

固定 24 requests，12 Actor/8 Updater/4 Reviewer。按历史输出类型分层并按固定 hash 排序机械选出，保持原 system/user 文本与顺序。API envelope 显式改变；目标 schema validity 为零 invalid。所需 D/W 必须仍是输入 Workspace 中存在的 handle。语义偏差需做小型 Uc canary，不直接扩大。

## Admission and conditional downstream stages

仅当 capability 和 preflight 通过后，按设计审计构建并逐包标定 Admission Bank，然后独立提交 stage freeze。U0 不重采样；U1 的语义变化限于 Current Gap 和 admission 条件；Uc 小样本区分 API-surface 影响。Admission 评价包含来源/相关/新颖 precision、预先标定 atom recall、限定保留、候选更新、no-change 和所有 failure/unknown。

Gate 以 paired improvement 为核心，必须同时审查 precision 和 recall。未通过不执行 G4/G5。通过后所有 arm 共用同一 Writer，从原 cohort 出发；G4/R2 oracle 保持冻结；G5 Current Gap 均绑定本轮实际 Actor output。所有 rubric 沿用 v2 主判据及 strict/source-visible sensitivities。每阶段看到 live result 后不得改 prompt 继续原 freeze。

## Costs and inference

保留 planned、attempted、completed、schema-valid、registry-valid、incomplete、API-error 分母。cache 按 token 加权 hit/(hit+miss)；Responses cached input 单列，缺失 usage 不能算零成本。模型 alias 相同不保证服务端永久版本固定；记录原始 model 字段、日期和 API surface。多窗口按 qid 聚类，不宣称独立样本显著性。
