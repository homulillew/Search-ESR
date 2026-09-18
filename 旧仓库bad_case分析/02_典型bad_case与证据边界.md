# 典型 bad case 与证据边界

本文件配合 [审计报告](01_ESR远程仓库审计报告.md) 阅读。来源固定为提交 `253beb48865ffa14cd9b0861e83fef0f45b7cd67`。下文动作编号均为 SQLite 的 **0-based sequence_index**，不混用日志中的自然语言轮次。

## 1. qid 120：先分开可见性、流程与验证器

### 可直接复核的事实

原 100 条批次共 24 个动作：11 search、4 open、5 read、2 update、2 verify；未提交。两个 verify 均 needs_revision，没有 supported。

该 episode 保存的 docid `37015` 正文长 **223,876 个字符**，目标问句首次出现在字符偏移 **18,680**。它不在前 16,000 字符中。这是“已找到正确文档但固定前缀无法展示关键段”的直接证据。旧日志部分写成 byte，本次使用 Python 字符串索引，单位为字符。

原轨迹的 verify seq6、seq13 转而质疑导师/机构等定位条件，末段继续搜索并重复打开文档。材料可见性与验证器审计范围相互作用，不能只说“模型不会停止”。

来源：[120 原始 store](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/results/exp1/exp100_merged_esr/stores/120.sqlite)。

### 后续版本的现象不要混用

- Fix7 日志声称 coverage 修复后 verify 曾通过，但又继续 search/open，最终未提交。对应 Fix7 原始 store 未在本快照中定位到；这是日志级证据，不能当成原 100 条批次的情况。
- `analysis-L/drive_120/120.sqlite` 只有 3 个动作，无完整 verify/submit 闭环，不能独立证明强策略完整实验的结局。
- `analysis-L/q120_e2.db` 有 6 个动作，seq3 的 verify 以片段没有字面“West African entrepreneurship”为由 needs_revision，支持“chunk 可见性修复后仍有 verifier 问题”的诊断。

来源：[迭代日志](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/analysis-L/ITERATION_LOG.md)、[后期 120 store](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/analysis-L/q120_e2.db)。

### 对新研究的启示

首先测“关键证据是否能被工具合法获取”。当前 Search-ESR 的 get_document 已支持分页，因此已不存在相同的绝对前缀屏障；现有 search 仍只回前 1600 字符，关键证据可能需要多次翻页。新 chunk 工具主要检验的是**发现效率和证据选择质量**，不能直接宣称复制旧修复的提升。

自动停止只解决已经 PASS 后的执行问题，不能解决 verifier 根本不 PASS。120 不适合作为四个机制同时有效的展示题。

## 2. qid 186：证据组合、指代消歧与解析错误并存

原 100 条批次 20 个动作，5 open、2 verify，未提交。

- seq6：候选为空，支持材料不相关，verifier 打回有具体依据。
- seq15：把文档 ID 当成 Evidence ID，update 被拒。
- seq16：read 被拒。
- seq17、18：打开新文档并更新成功。
- seq19：verifier 输出无法解析，却作为 needs_revision 写入状态。

这些现象不能合并成“有证据仍不会推理”。最后一次中断尤其受到格式错误污染。

强策略归档 `drive_186/186.sqlite` 中，共 **17 个动作**，最终提交：先获得游戏材料；第一次 verify 要求补曾用名证据；补第二篇公司材料后，验证又卡在“曾用名指游戏还是公司”；最终明确消解指代后 supported 并提交。中间依然出现未登记证据、重复验证被拒。

来源：[原始 186](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/results/exp1/exp100_merged_esr/stores/186.sqlite)、[强策略 186](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/analysis-L/drive_186/186.sqlite)。

**支持的结论：** 当前门禁存在一条可达成功路径；证据组合和明确指代对这一题有帮助。

**不支持的结论：** 门禁没有任何成本，或失败一定只能通过训练修复。人工/外部强策略逐动作驱动证明的是可达性，不是自动策略稳定成功率。

对当前研究，应记录中间实体与目标实体是否被区分、第二篇证据何时取得、replan 是否改变有效搜索方向。第一版 criteria + known_facts 可以先尝试表达这些关系，不急于引入 DAG。

## 3. qid 324：目标实体与定位线索实体混淆

原 100 条批次共 11 个动作。seq4 verify 打回初始候选；seq7 打开新的比赛资料；seq8 修改候选；seq9 的 verifier 仍把问题中定位 X 的属性要求套到最终目标实体上，再次打回；seq10 继续搜索。

问题包含“定位某位选手 X，再找她之前两年的获胜者”的关系，因此确认 X 与回答最终目标是两步。候选名字出现只证明实体被提及，不自动证明年份映射和目标关系成立；反过来，也不能要求最终答案继承 X 的所有属性。

来源：[324 原始 store](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/results/exp1/exp100_merged_esr/stores/324.sqlite)。

Fix7 日志报告“只写某年冠军描述、没有具体名字也被 PASS”，Fix8 随后加强实体要求。这里存在 verifier 放行过宽与打回过严的双向风险。

强策略 `drive_324/324.sqlite` 则有完整 **5 动作**闭环，seq3 supported，seq4 submit。它说明显式关系和证据能让该 verifier 接受，但不足以支持“Fix8 稳定修复所有同类题”。

来源：[强策略 324](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/analysis-L/drive_324/324.sqlite)。

对新研究，应让 criteria 表述目标关系，候选可撤销，verifier 审核的是该关系链。不要以“gold 字符串出现”当充分证据，更不要在线使用 gold 指导检索或放行。

## 4. 停止问题：文档点名的 416 与归档不符，533 是更清晰的例子

`RETRY20_V2_CLASSIFY.md` 声称 416 三次 verify 全 supported 而未提交。但实际 `esr_retry20_v2_g1/stores/416.sqlite` 的 seq6、15、25 均为 **needs_revision**。其理由是材料不足、目标论文未定位或候选为空。

同批 **533** 的 seq29 确实 supported，最终未提交；这是直接可用的“验证成功但出口没有完成”的回归例子。它也提示另一种原因：PASS 出现在预算尾部，没有给显式 submit 留出足够空间。需区分预算出口与模型拒绝 commitment。

原 100 条 ESR 中 supported 后未提交为零。因此不能从这批数据得出“自动停止会普遍提升提交率”。

来源：[分类报告](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/analysis-L/RETRY20_V2_CLASSIFY.md)、[416 store](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/results/exp1/esr_retry20_v2_g1/stores/416.sqlite)、[533 store](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/results/exp1/esr_retry20_v2_g1/stores/533.sqlite)。

## 5. qid 170 / 1044：运行时问题不要计为研究问题

170 原批次 30 个动作，最后 5 个都是 read_evidence 非法：模型重复尝试读取 directory 外的 ID。可见性与登记协议确实造成反复失败；是否需要强制登记所有证据值得重新设计。

1044 原批次中多次 verify 以 HTTPError 拒绝；retry 日志另报告尾部 7 次服务失败。部分“再验证/继续搜索”的行为受错误提示驱动。基础设施错误应内部重试并以独立终态退出，不应成为新 open_question。

来源：[170](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/results/exp1/exp100_merged_esr/stores/170.sqlite)、[1044](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/results/exp1/exp100_merged_esr/stores/1044.sqlite)。

## 6. 12 题“强策略 / verifier”结果的适用范围

### 6.1 两个 JSON 是不同实验，不要混为一组输入

`strongA_12_result.json` 保存重新搜索、打开的 docid 与 verify 结果；`replay_shortboardA_result.json` 记录旧状态、supporting evidence 的重放。两者即使 qid 相同，也不一定用了同一批文档。

前者 12 条均 needs_revision，后续日志将其归为 5 条材料不足、4 条假打回、3 条解析失败。这是作者的诊断分类；“名字在文本中出现”不充分证明所有约束成立，本次不把 4 条标签直接升级为独立人工金标。

后者还受到本次发现的 replay 输入 bug 影响：日志的 view_evidence 并非脚本实际传给 verifier 的内容。

### 6.2 有 gold 参与的诊断不能算 blind benchmark

迭代日志明确记录强策略某次使用正确答案和正确 docid，replay 选择样本也基于 gold-match；它们适合检查“给定正确候选及材料，验证器能否工作”，不适合估计端到端 discovery 能力。

`drive_harness.py` 是 stdin 接收外部动作并执行环境，不是完整强模型 API 自动循环。它与自动 rollout 的上下文、预算和信息可得性未严格等同。

### 6.3 后期 32B 与 Lanz-Medium 结果暂为报告级证据

顶层总结报告：换 32B verifier 后初次 6/12 PASS，补证后 10/12 提交；Lanz-Medium 对照 ESR 11/12 正确、baseline 10/12，平均工具调用 15.2 vs 6.2。

在本快照中没有定位到与这些结果绑定的完整逐题请求/响应、独立 session 记录和对应 32B/Lanz batch。可以保留为研究线索，不能重新计算其指标或宣称已复验。6/12 直接重验与 10/12 补证后结果，也不能都归为单纯“只换 verifier”的效果。

来源：[顶层总结](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/ESR-GRPO的Harness层实现与调试.md)、[强策略驱动](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/analysis-L/drive_harness.py)、[重放脚本](https://github.com/homulillew/ESR-GRPO-Code-L/blob/253beb48865ffa14cd9b0861e83fef0f45b7cd67/analysis-L/replay_shortboardA.py)。

## 7. 对旧结论的修正清单

| 旧表述 | 本次审计后更合适的表述 |
|---|---|
| 78 条卡在 Gap，说明材料已齐 | 78 条尝试过验证；材料是否充分要逐次看实际输入 |
| 提交精度显著提高，所以整体更强 | 选择性精度与总体准确率、覆盖率必须同时报告 |
| 验证通过仍不提交是能力问题，Harness 无能为力 | 可以改由 runtime 自动结束；收益与误停风险仍需测量 |
| 强策略能走通，所以门禁全合理 | 证明存在可达路径，不证明门禁无额外成本或无隐藏 bug |
| 两轮 winner 不重合，证明是随机能力上限 | 表明结果不稳定；同时改了 harness，未隔离采样、服务与策略因素 |
| 更少轮数但没提交，说明更快收敛 | 可能是提前退出、无工具输出或错误，不能计为效率提升 |
| 含 gold 就是假打回 | 字符命中不等于关系和全部关键约束被支持 |
| 移除 offset 才能保证无证据泄露 | 可以保留分页，只要将实际展示的文本固定存档并交给 verifier |
| 相同 Gap 重复拒绝 N 次，可推断 verifier 错误 | 重复不足以判断语义真假；应独立诊断或输出未验证终态 |
| 已修 chunks，就保证 model/verifier 同视图 | 动态重建、去重、服务 fallback 都会破坏保证，需输入快照 |

这些修正不否定旧 ESR 的探索价值，而是明确它们在新实验中应当作为假设、协议不变量还是历史观察使用。
