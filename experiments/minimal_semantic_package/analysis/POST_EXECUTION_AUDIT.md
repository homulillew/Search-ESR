# 执行后审计

## 执行与封存顺序

1. E0源边界在`61a2eda23bdf31cc7f133690ac7228275129053c`提交；Support参考、96个实际Verifier请求及实现随后独立冻结。
2. 96次Verifier在新的明确授权后执行；原始结果及accounting先提交，再生成35个实际Auditor请求。
3. Verifier中期结果已证明最终Recall上界仅76.19%。35次Auditor定位为诊断rescue与误拒，未声称可恢复E2资格。
4. Auditor请求提交`647d5a428d5f02efce26a53a869565024f2d8d4e`；Auditor freeze在`ab805cf0db0f570f7f6ea9838db5bea653ed6066`提交，SHA为`17f0b814bfa313559383e4c47ad815fa45da1503ebd1de766bfb3904d4dbe1c7`。
5. 用户本次“授权”记录于`7da3ba3d9747330f64af04d7a18bf03b6247109b`，仅限这35次。该HEAD下完成35次调用。
6. 全部Auditor原始请求、响应、解析结果及accounting先提交至`d490e7cab66e4400005705d52606e9cad38ef500`，再执行冻结score，得到E1 FAIL。
7. 在该机械计分之后进行单一、任务熟悉、未掩码的内容复核，覆盖96条链。复核没有重标Gold或改变Primary规则，不宣称先盲审后解盲。

## 核验内容

- 两批实际请求与冻结schedule一致，发送HEAD与RUN一致。
- 所有131个原始响应仅从content重解析，结果与归档一致；reasoning未用于语义复核。
- 两批usage和合并usage可重放；缓存率用输入token加权，reasoning不重复相加。
- 冻结score可重复得到相同METRICS；分母保留全部96个slot。
- 11个边界freeze文件、6个support freeze文件、39个Verifier freeze文件、439个Auditor freeze文件均匹配哈希。这些集合相互重叠，不能相加称独立文件数。
- 21,632个历史实验文件保持原哈希。
- E2–E4调用0，指标null；没有Search、Find/Open、Residual、动态闭环或持久状态改写。

机器证据：[FINAL_INTEGRITY](FINAL_INTEGRITY.json)、[AUDITOR_INTEGRITY](AUDITOR_INTEGRITY.json)、[TOTAL_ACCOUNTING](TOTAL_ACCOUNTING.json)。完整性PASS与研究Gate FAIL是不同判断。

## 假设状态及实用解释

| 假设 | 本轮状态 |
|---|---|
| H1：Boundary recovery是主要失败源 | 未单独测试；固定Gold输入下验证链已失败，不能把当前失败只归因于extractor。 |
| H2：Gold边界使验证足够稳定 | 未达到门槛；最终Precision89.66%、Recall61.90%。与旧Q0/Q1输入和标签不同，不构成单因素因果比较。 |
| H3：Predicted package接近Gold | E3未运行，未测量。 |
| H4：支持能安全partial-evaluate Parent | E4未运行，未测量。 |

反向审计在本bank上0/3 rescue、6次新增误拒，是清楚的负面机制结果。3次误支持都涉及预标参考歧义；即使按预注册集合描述性排除，Recall68.42%、临床0/6、Ding1/2仍失败。

没有修改冻结Prompt、Gold、case选择、模型参数或失败政策。没有追加尝试、修复、投票、择优或用API重评。新增`final_analysis.py`与`review_and_report.py`只是调用结束后的本地诊断/报告写入器，不参与任何模型输入或Primary评分。

## 复现方式

原始结果已存在，禁止再次运行`run execute`。冻结执行器也会拒绝覆写。
读取/重算Primary无需网络：

```bash
python - <<'PY'
from experiments.minimal_semantic_package.common import P, read, verify_history
from experiments.minimal_semantic_package.score import results
assert results() == read(P / 'e1_gold_support/METRICS.json')
assert verify_history() == 21632
print('score and historical hashes match')
PY
```

报告生成器和`verify_batch`使用exclusive写入；已有产物时不应重跑写入命令。最终`RESULTS_SEAL.json`提供交付文件的哈希，不把后期诊断冒充调用前预注册材料。
