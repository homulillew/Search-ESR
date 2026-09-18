# 统一 Search/Open 真实原文检查

本轮固定四篇文档及 query，不重新召回、不调用大模型。代码已经接入默认 Agent，但此处仅是工具行为验证，不是在线效果实验。

| 文档 | 原文标题 | Search 标题＋正文 tokens | Search 起点 |
| --- | --- | ---: | ---: |
| 67431 | Peter Nzioki - Wikipedia | 399 | 1299 |
| 23800 | 2005 UEFA Champions League final - Wikipedia | 385 | 15709 |
| 84585 | 2023 British Open | 396 | 51843 |
| 55516 | Mark Selby - Wikipedia | 394 | 34146 |

Search、before、after、around 均与对应原文范围逐字符一致。around 包含原窗口；旧引用记录不变。四篇文档均经 after 多次读取到文档末尾，过程中位置持续向后推进。

67431 的返回包含人物标题和 Policeman 1 角色记录，避免此前窗口重新定位时完全丢失身份。其他窗口未据此判定满足 query，尤其赛事年份、时间和名称仍需语义核查。

结果见 [results.json](results.json)，配置和源码哈希见 [manifest.json](manifest.json)。前后展开采取不重叠连续分页；around 保留原范围。结构规则仅提供句子/行启发式，不保证复杂表格、比赛记录、指代或普通小节边界完整。
