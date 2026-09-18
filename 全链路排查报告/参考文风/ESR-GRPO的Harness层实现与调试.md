# ESR-GRPO的Harness层实现与调试

本周完成了ESR-GRPO在Harness层的前向推理流程，并分别使用**Qwen3.5-4B、Qwen3-32B和Lanz-Medium**进行了无训练评测。

这一阶段主要验证两个问题：

1. ESR的Research State和Verify机制**能否提高BC+上的答案正确率**；
2. ESR能否**减少无效搜索和错误提交，使长程检索更容易收敛**。

目前只验证**前向推理**，ESR-GRPO训练和Credit效果放在后续实验。

## 结论

当前实验有三个主要结论。

**第一，ESR能够明显减少错误提交，但4B下整体Accuracy没有提升。主要原因在于4B模型本身能力不足，多约束问题下verifier能力不够，不会提交答案**

100条Qwen3.5-4B评测中，baseline全部提交，Accuracy为17%；ESR只提交19条，其中15条正确，已提交答案准确率为78.9%，总体Accuracy为15%。

ESR的主要问题出在提交率。大量轨迹已经形成Candidate，但在Verify后产生Gap，后续无法继续补齐证据，最终不提交。

**第二，纯基座模型下，4B Verifier是当前主要瓶颈之一。**

对**12条答案已经匹配Gold、但始终无法通过Verify的轨迹**进一步分析：

| 原因                 | 数量 |
| -------------------- | ---- |
| Evidence缺少关键条件 | 5    |
| Verifier判断错误     | 4    |
| Verifier输出无法解析 | 3    |

1. 部分case中答案已经出现在Verifier实际看到的Evidence里，4B仍然返回`needs_revision`。**模型幻觉比较严重**
2. 将Verifier换成Qwen3-32B后，同一批12条轨迹有10条能够经过补证后正常Verify并提交。

**第三，强模型下ESR能够提高提交质量，但工具调用更多。主要原因可能是题目本身问题：样本少并且对强模型比较简单，baseline下一到两次搜索就能回答正确**

Lanz-Medium下独立重跑12条，ESR提交11条且全部正确，baseline提交12条、正确10条。**总体Accuracy分别为92%和83%。**

同时，**ESR平均工具调用为15.2次，baseline为6.2次**，约为2.45倍。

目前ESR更明显的收益是**提高答案可靠性、减少错误提交**，搜索效率还没有改善。

------

## 实验一：Qwen3.5-4B下的100条正式评测

首先使用Qwen3.5-4B比较baseline和ESR，两边使用相同检索环境，每条最多30轮。

| 指标                             | Baseline | ESR   |
| -------------------------------- | -------- | ----- |
| 提交率                           | 100%     | 19%   |
| 总体Accuracy                     | 17%      | 15%   |
| 已提交答案准确率                 | 17%      | 78.9% |
| 错误提交                         | 83       | 4     |
| 过程性答案（各种噪声和思考过程） | 30       | 0     |

ESR明显减少了错误提交。Baseline的83条错误提交中，有30条是搜索过程、计划或中间推理；ESR基本消除了这类情况。

问题主要集中在提交率。100条中有81条没有完成提交，大部分轨迹停在：

```text
Candidate
   ↓
Verify
   ↓
Gap
   ↓
补证失败
   ↓
不提交
```

因此**4B下ESR首先提高了提交质量，但Verify和Gap修复能力限制了最终Accuracy**。

------

## 实验二：强策略下区分模型能力和Harness问题

为了判断**未提交来自模型能力还是Harness**，保持BM25、ESREnvironment和4B Verifier不变，**只替换产生搜索动作的策略模型为Lanz强模型**。

选取典型失败case重新测试后发现，强策略可以解决其中一部分原来无法收敛的轨迹，说明搜索、Evidence组合和Candidate形成能力对最终提交有较大影响。

同时发现一个明确的Harness问题：部分长文档的正确Evidence位于原始16k观察窗口之外，即使已经检索到正确Doc，模型也无法读取关键内容。

因此这一阶段得到两个结论：

```text
部分失败 → 策略能力不足
部分失败 → Evidence观察窗口存在缺陷
```

后续分别从Evidence读取方式和Verifier能力继续排查。

------

## 实验三：修复Evidence观察窗口

针对长文档Evidence不可见的问题，**将原来的固定头部截断改成按Query召回相关Chunk**。

当前流程为：

```text
Search Query
    ↓
Document
    ↓
Chunk切分
    ↓
召回相关Chunk
    ↓
Open / Read
```

Raw Evidence仍完整保存在Harness中，Agent只读取和当前Query最相关的Chunk。

同时，Verify阶段使用相同的Chunk View，保证Agent和Verifier基于同一份可见Evidence判断。

修复后，**原来16k之外的关键Evidence已经可以正常进入观察窗口**。

继续复测后，部分轨迹仍然被4B Verifier拒绝，因此后续重点**转向Verifier本身**。

------

## 实验四：4B Verifier失败归因

从100条实验中选出**12条“答案已经匹配Gold，但始终没有一次Verify通过”的轨迹**，使用强策略重新走完整链路，同时保留真实BM25和4B Verifier。

结果在**“正确轨迹+4B作为verifier“**条件下，12条全部返回`needs_revision`，没有一条提交。

逐条检查后分成三类：

| 类型                                                       | 数量 |
| ---------------------------------------------------------- | ---- |
| 当前Evidence确实不足                                       | 5    |
| Evidence已有答案但Verifier仍拒绝（**模型幻觉，不会判断**） | 4    |
| Verifier输出无法解析                                       | 3    |

5条属于正常拒绝，当前Evidence没有覆盖完整条件。

另外7条主要来自Verifier。其中4条的答案已经出现在Verifier看到的Chunk中，4B仍然认为证据不足；另外3条因为输出无法解析，最终也被处理成`needs_revision`。

因此4B下的失败主要来自两部分：

```text
Evidence召回不足
+
Verifier判断不稳定
```

Verifier一旦持续返回`needs_revision`，当前State就无法进入Submit，这也是大量轨迹停在Verify阶段的重要原因。

------

## 实验五：Qwen3-32B Verifier验证

为了验证Verifier能力的影响，将Verifier**从Qwen3.5-4B替换为Qwen3-32B**，其余流程保持不变。

首先直接使用前面12条轨迹已有的Answer和Evidence重新判断：

```text
6 / 12 → supported
6 / 12 → needs_revision
```

随后允许强策略根据32B产生的Gap继续补证，最终：

```text
10 / 12 → Submit
2 / 12  → Needs Revision
```

剩余2条主要缺少完整的多跳Evidence，**这个主要是检索轮次不足（因为暂时设置的30轮），是正常现象**。

另外有4条轨迹能够做到完全控制变量：问题、Evidence、Harness全部一致，只替换Verifier。4B全部返回`needs_revision`，32B全部通过并提交。

这部分结果说明，**Verifier模型本身能力会直接影响ESR的提交率。更强的Verifier能够明显减少错误Gap，并让正确轨迹更快收敛。**

------

## 实验六：Lanz-Medium下ESR与Baseline对照

最后使用Lanz-Medium作为强策略，对12条样本重新进行ESR和baseline对照。评估ESR在强策略模型下的性能表现

每个`qid × mode`使用独立Session和独立进程，不共享其他轨迹的信息，也不提供Gold。

| 指标             | ESR      | Baseline |
| ---------------- | -------- | -------- |
| 提交率           | 11/12    | 12/12    |
| 已提交答案准确率 | 11/11    | 10/12    |
| 总体Accuracy     | **92%**  | **83%**  |
| 平均工具调用     | **15.2** | **6.2**  |

当前宽松判分下，ESR比baseline多答对1条，并保持11条提交全部正确。

但这个Accuracy差异只有1个case，还需要更大规模实验确认。

相比Accuracy，更稳定的现象是提交质量：

```text
ESR      11 / 11正确
Baseline 10 / 12正确
```

工具成本则明显更高：

```text
ESR      15.2次
Baseline  6.2次
```

ESR平均工具调用约为baseline的2.45倍。

因此目前强模型实验能够说明ESR减少了错误提交，但还没有体现出搜索轮数上的优势。

------

## 当前判断

Harness层目前已经能够稳定完成：

```text
Search
→ Evidence
→ State
→ Verify
→ Gap
→ Submit
```

当前剩下两个主要问题。

**1. 弱模型能力**

4B在Evidence组合、Verify、Gap修复和最终收敛上都不稳定。Verifier能力不足会进一步放大这个问题，使正确Candidate长期无法提交。

**2. 工具轮次更多问题**

另外，当前ESR的工具调用明显高于baseline。State和Gap虽然提高了答案可靠性，但还没有减少重复搜索和验证。**原因可能是选择的是在强策略模型下较为简单的题目并且样本量较少，下一步抽取较难题目**

------

## 下一步

### 1. 使用32B Verifier重跑100条正式评测

固定当前Harness和Chunk View，将Verifier替换为Qwen3-32B。

重点比较：

- Accuracy；
- Submit Rate；
- 已提交答案准确率；
- Gap解决率；
- 平均工具调用。

主要确认4B下81条未提交轨迹中，有多少能够在更可靠的Verifier下正常收敛。

### 2. 准备SFT和RL

当前4B还缺少稳定的ESR流程能力。

后续可以先蒸馏一批BC+高质量轨迹，让模型学习：

```text
Search
→ Open
→ Update
→ Verify
→ Gap Repair
→ Submit
```

再进入ESR-GRPO训练，重点验证Evidence、State和Gap能否改善长轨迹的Credit Assignment，以及训练后能否减少无效搜索和重复Verify。
