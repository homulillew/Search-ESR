# 必答 bad cases 与 ClaimSet 对照

所有分母均为Certificate × replicate；同一Case下多个locator相关，不视作独立新问题。这里讨论接受资格，未执行实际subtraction。

## 九类指定Case

| Case | Certificate | Q0 | Q1 | 判断 |
|---|---|---|---|---|
| Euler biography | A15_CAND1 | 错误接受2/2 | 错误接受0/2 | verdict改善；Q1一条明确指出book-reference缺口，另一条主要谈出生/人物限定，理由只部分对准核心关系。 |
| Book→article | A13_CAND1 | book-only错误接受2/2 | 错误接受1/2 | 未消除。另一次拒绝主要诉诸作者/PhD/目标绑定，而未直接指出缺少article。 |
| DLC qualifier | A20_CAND5、CAND6 | 错误接受0/4 | 错误接受0/4 | playable-European-nation限定稳定保留；不能称为Q1新增收益。 |
| Generic SPS | A16_CAND1 | 错误接受0/2 | 错误接受0/2 | 一般疾病症状不能替代具体个体的半年度病史。 |
| Patient nationality / report country | A17_CAND4 | 错误接受0/2 | 错误接受0/2 | nationality没有被当作report-country/history的充分证据。 |
| Memo date / letter date | A23_CAND1 | 错误接受0/2 | 错误接受0/2 | 未把转交memo日期当写信日期；accession时间也缺失。 |
| Teammate same-country | A22_CAND1 | 错误接受0/2 | 错误接受0/2 | Jerry国籍、队友姓名都不能证明另两位彼此同国。 |
| Kwon / Ding | A05、A06、A07、A08 | 只有alma-mater→building错误接受2/2 | 相应错误0/2；Ding婚姻正例2/2保留 | Q1修复角色错配；两组都拒绝用2025家庭情况推2019、或用Ding婚姻推整项gift。 |
| q637 actual clinical case | A17_CAND1–3 | 正确接受6/6 | 正确接受4/6 | C7真实局部支持被部分保留，但两次因country/history尚未完成而被错拒；任务指定正例并未全部保留。 |

## 各Case中的正负细分

### Book → article

- `A13_CAND1`：C1只有书的作者/日期/内容。Q1 r1拒绝、r2接受，核心关系保护不稳定。
- `A14_CAND1`：同一locator，增加C3同作者后续文章；Q0/Q1均接受2/2。
- `A14_CAND2`：C1+C3，locator为六年比较；Q0接受2/2、Q1接受1/2。拒绝理由是精确日期不足；冻结参考采用2016→2022出版年份。
- `A14_CAND3`：同一topic，两组均接受2/2。
- `A14_CAND4`：只给文章C3，无书日期，两组均拒绝2/2。

因此ClaimSet可以补齐比较双方，但全上下文verifier仍会在book-only条件上放行。增加上下文没有完全解决局部片段脱离governing relation。

### DLC mechanics 与 qualifier

- `A20_CAND1–3`：religion/technology及两者mechanics，Q0/Q1均正确接受6/6。
- `A20_CAND4`：只定位一般mechanics-change，Claims说明government/subjects变化。Q0接受2/2、Q1拒绝2/2，要求补宗教/技术等条件。Gold的局部范围解释在调用前声明为歧义。
- `A20_CAND5–6`：有mechanics线索但playable-European-nation不完整，两组均拒绝4/4。

Q1并未一律拒绝所有partial support；问题发生在应继承哪些限定条件的边界上。

### Kwon / Ding

- `A04_CAND1`：整个founder/game/university Parent限定不全，两组均拒绝2/2。
- `A05_CAND1`：Kwon身份/学历不能推出2019childlessness，两组均拒绝2/2。
- `A06_CAND1`：Kwon就读Sogang不能推出building属于Sogang，Q0接受2/2、Q1拒绝2/2。
- `A07_CAND1`：Ding绑定+C5的2019married/childless，两组均接受2/2。
- `A07_CAND2`：Kwon2025 children→2019 childlessness，两组均拒绝2/2。
- `A07_CAND3`、`A08_CAND1`：婚姻/学历不能支持整个gift/building或opening/university Parent，两组均拒绝各2/2。

没有把Kwon分支事实和Ding分支事实拼接成最终目标，也没有用Ding婚姻正例关闭gift Parent。

### q637

同一个C7：完整临床句`A17_CAND1`在Q1接受1/2；半年度多部位疼痛`A17_CAND2`接受2/2；行走/肩部困难`A17_CAND3`接受1/2。Q0三者全部接受。临床已观察不应替代country/history，但冻结任务也不要求先证明country/history才允许记录候选病例的局部临床支持。

额外同疾病控制`A17_CAND5`使用一般FOP genetics/trauma信息，两组拒绝2/2。由此不能把正确拒绝SPS简单归因为不同病名；同疾病背景也未被提升为具体病史。

## 六个描述性配对对照

这些配对在执行期间、读取模型内容前列出；不是额外primary门槛。表中是“第一Certificate接受数 → 第二Certificate接受数”，每项分母2。

| 对照 | 参考方向 | Q0 | Q1 |
|---|---|---:|---:|
| Book-only → 同书+article，保持publication locator | 拒绝→接受 | 2→2 | 1→2 |
| Nationality-only → 增加champion membership，保持coder locator | 拒绝→接受 | 2→2 | 0→2 |
| Table C5 alone → 加D10/table C4，保持emotion locator | 拒绝→接受 | 2→2 | 2→1 |
| DLC release-only → 加base-game date/genre，保持完整Parent | 拒绝→接受 | 0→2 | 0→2 |
| DLC局部mechanics → 整个含nation限定的Parent | 接受→拒绝 | 2→0 | 2→0 |
| Ding婚姻片段 → 同Claims整个gift Parent | 接受→拒绝 | 2→0 | 2→0 |

前三/第四组检视缺少关系操作数时联合Claims是否有帮助，后两组检视coverage范围。DLC范围对照的ClaimSet也有所变化，不能当成纯locator因果干预。

Table反向结果值得保留：孤立C5两次被接受，加C4之后一次被拒绝。C4同时带来D10绑定和“5张表”的信息，而问题要求6张。因而此对照并非纯净的“增加绑定”实验；新增事实也暴露全局冲突。这进一步说明当前资格问题混入了候选是否为最终目标的判断。

## 额外参考争议

`A24_CAND2`的C2+C3提到King Michael交信、信里Romania收回地区，但没有直接写其统治Romania。冻结Gold将其作为绑定过的letter上下文正例；Q1一次严格拒绝，有可辩护的字面依据。原Gold保持不变，报告另给排除此项的事后敏感性。`A24_CAND1`含明确“King Michael of Romania”的C1，两组接受2/2。

这些争议要求后续先明确候选分支下的局部支持契约，再研究新verifier；它们不能成为本轮事后放宽门槛的依据。
