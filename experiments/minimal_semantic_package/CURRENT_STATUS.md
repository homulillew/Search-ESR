# E0完成；E1V等待本轮新的明确授权

| 阶段 | 状态 | 已调用 |
|---|---|---:|
| E0 Reference construction | 已冻结 source units、Gold Package和Support参考 | 0 |
| E1V Gold Package Verifier | 96条实际请求已准备；等待授权 | 0 |
| E1A Uncovered Material Auditor | 依赖E1V真实输出，尚未生成请求 | 0 |
| E2 Boundary Recovery | 尚未进入；须E1完整PASS | 0 |
| E3 Predicted Package Support | 尚未进入；须E2 PASS | 0 |
| E4 Residual View | 尚未进入；须E3 PASS | 0 |

本轮第33节明确要求“完整requests → commit → hash freeze → 准确call count → 新的明确授权”，不复用前一实验授权。

当前待授权范围：**DeepSeek `deepseek-flash` 的96次Verifier调用**，48证书×2重复，最多8并发、零重试，记录全部失败、usage和缓存命中。没有真实结果或缓存命中率可报告。

Auditor只看Verifier声称足够的Claim子集，其实际请求无法预先猜测。E1V完成后将生成0–96条实际Auditor请求，再冻结并申请对应数量的授权。整个E1需完成必要Audit才能判定Gate。

E0包含17 Parent、78原文unit、34唯一Package、48证书；Support参考21正例/27负例，4项预标歧义。旧letter证书A24_CAND2改为本轮OPEN：选定C2/C3没有明确的作者–国家绑定。历史Gold和结果未修改。

本轮新假设尚未验证；18项最终研究问题均须按实际完成阶段报告。不得把“准备完成”描述为实验通过。

详见[Protocol](PROTOCOL.md)、[参考审阅表](e0_reference/REFERENCE_REVIEW.md)、[调用预算](CALL_ESTIMATE.json)。
