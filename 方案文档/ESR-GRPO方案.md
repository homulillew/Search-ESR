ESR-GRPO方案与实验计划
1. AREX bad_case分析与启发

在上周AREX评测中，190条正常提交但回答错误的轨迹里，有104条 Evidence Recall ≥ 0.5，其中47条 Recall = 1.0。说明不少错误发生在证据被召回之后。
1.1 搜到相关内容但未形成可用证据

错误轨迹平均进行了64.05次 search，约为正确轨迹的3.15倍，但实际访问的页面更少。错误轨迹的平均 Evidence Recall 只有54.1%，明显低于正确轨迹的93.0%。

问题主要发生在：

搜索结果 → 访问 / 阅读 → Evidence

AREX能够持续搜索并得到大量候选页面，但关键内容没有被充分读取和使用。

AREX问题： 状态设计没有明确区分搜索结果和已经实际读取的Evidence。

启发： 状态中要明确记录真正读取过的Evidence，并对形成和使用这些Evidence的动作进行奖励。
1.2 Evidence正确但State写错

部分轨迹已经访问到正确页面，但在 update_context 时对Evidence进行了错误解释，后续搜索继续基于错误State展开。

正确 Evidence → 错误 State → 污染后续搜索

AREX问题： Evidence、模型推断和候选判断都写在同一段自然语言Context中。一次错误解释进入State后，会继续影响后续推理。

启发： 原始Evidence需要独立保存，TaskState只记录当前理解，并支持后续重新读取Evidence和修正State。
1.3 Evidence已经找到但关系判断错误

47条错误轨迹的 Evidence Recall 已经达到1.0，其中22条错误答案的置信度仍超过90%。说明部分错误主要发生在Evidence后续的分析和关系判断中。

常见情况是人物、条件和相关Evidence都已经找到，但Evidence最后绑定到了错误的人物或条件上。

Evidence A → 条件1
Evidence B → 条件2
        ↓
      错误绑定

AREX问题： 当前Context缺少对不同条件及其Supporting Evidence的明确关系表示。

启发： TaskState需要记录Claim和Evidence之间的关系，明确每个结论分别由哪些Evidence支持，并在后续验证中重新检查这些关系。
1.4 错误State会继续影响后续搜索

部分高Recall错误轨迹会较早锁定错误候选，之后的搜索持续围绕该候选展开。虽然Context中也会记录未解决条件，但这些信息和候选判断、搜索计划混在一起，搜索方向仍然容易被当前候选带偏。

错误候选
   ↓
围绕候选搜索
   ↓
继续强化当前判断

同时，AREX会通过 update_context 压缩历史。如果错误判断已经写入新的Context，旧Evidence又退出当前上下文，后续修复会更困难。

AREX问题： Gap对后续搜索的约束较弱，错误State又可能在压缩后持续保留。

启发： TaskState需要显式维护当前Gap，并保留可重新读取的原始Evidence，使后续搜索和状态修正都有明确依据。
1.5 当前主要问题

这些bad_case主要集中在下面这条链路：

搜索 → Evidence → State → 后续搜索

    搜到相关页面后，不一定真正形成可用Evidence；

    Evidence进入State时可能被错误解释或错误绑定；

    错误State会继续影响后续搜索，并在上下文压缩后更难修正。

后续方案主要围绕这三点重新设计Research State，并利用State中的Evidence关系和Gap信息进行后续信用分配。
2. 从bad_case到设计思路

第一章的问题基本都集中在Research State上：Evidence是否真正进入状态、Evidence和结论之间的关系是否正确、错误State能否被发现，以及后续搜索是否围绕真正缺失的信息展开。

因此，我们希望重新设计一套更稳定的Research State，并让这套State同时服务后续搜索和训练信用分配。
2.1 Evidence和State分开保存

AREX会把Evidence、模型推断和候选判断一起写入Context。一旦对Evidence理解错误，后续只能继续基于压缩后的State推理。

我们的设计中，真正读取过的页面单独保存为Raw Evidence：

Search Result → Open / Read → Raw Evidence → TaskState

Raw Evidence保存原始内容，TaskState保存模型当前对这些Evidence的理解。即使State写错，后续仍然可以重新读取原始Evidence进行修正。
2.2 显式记录Claim和Evidence的关系

对于多条件任务，只保存最终答案和Evidence列表很难判断每条Evidence具体支持哪个条件。

因此将任务中的关键结论拆成Claim，并记录对应Evidence：

Answer
  ↓
Claims
  ↓
Evidence

这样可以明确当前每个结论由哪些Evidence支持，也方便后续单独检查某个Claim是否成立。
2.3 通过Verify和Gap修正State

update_state负责根据新Evidence更新当前理解，但模型对Evidence的解释仍然可能出错。

因此在关键阶段增加Verify，重新读取Raw Evidence并检查当前Claim。如果发现某个条件还没有被充分支持，则记录为Gap：

Update State
    ↓
Verify
    ↓
Gap
    ↓
继续搜索

Gap会保留在TaskState中，后续搜索可以优先围绕这些未解决问题展开，减少持续围绕错误候选进行搜索的情况。
2.4 用同一份State进行信用分配

结构化State除了用于前向搜索，也可以提供更明确的动作回溯关系。

最终答案中的Claim可以回溯到对应Evidence，再进一步找到产生这些Evidence和更新State的相关动作：

最终答案 → Claim → Evidence → 相关动作

类似地，一个Gap从产生到最终解决，也可以形成一条明确的修复链。

因此训练时仍然使用最终任务Reward，但只把正信用分配给最终答案、Evidence和Gap修复真正相关的动作，减少长轨迹中无关搜索和无效操作获得相同奖励的问题。

整体设计思路可以概括为：

Raw Evidence
     ↓
Claim-Evidence State
     ↓
Verify + Gap
     ↓
指导后续搜索
     ↓
反向信用分配

3. 相关工作与当前缺口

近期一些最新工作已经从上下文管理、Evidence追踪、Claim验证和细粒度信用分配等方向改进长程搜索Agent。
方法	主要设计	和我们相近的部分	主要区别
ECHO	选择性Turn Memory + 来源追踪	Context压缩、正信用分配	主要追踪历史Turn，没有显式Claim-Evidence关系
STAMP	Evidence来源追踪 + Step Credit	Evidence到搜索动作的信用分配	主要用于训练Credit，没有完整的前向Research State
TRACE	基于状态价值进行Turn-level Credit	解决长轨迹Credit过粗	依赖Gold Answer估计每一步状态价值
HALT	Claim-Evidence Coverage	Claim验证、判断搜索是否完成	主要解决Stopping问题
LedgerMind	Structured Evidence Ledger	Evidence、Claim、Verification和Repair	更关注结构化可信推理，没有结合Search RL信用分配

这些工作已经分别覆盖了Context压缩、Evidence追踪、Claim-Evidence关系和细粒度Credit等设计。但暂时没有一套设计将这些统一起来，使前向搜索过程中维护的State同时用于验证、Gap修复和反向信用分配。

Raw Evidence
     ↓
Claim-Evidence State
     ↓
Verification + Gap
     ↓
指导后续搜索
     ↓
反向信用分配

4. ESR-GRPO方案设计

ESR-GRPO的核心是维护一套可验证的Research State，并让这套State同时服务前向搜索和反向信用分配。

整体流程如下：

Search → Open / Read → Raw Evidence → Update State
                                ↓
                         Claim / Gap
                                ↓
                              Verify
                                ↓
                    Continue Search / Submit

训练阶段再根据最终State反向找到真正有贡献的动作：

Final Reward
     ↓
Final Verified State
     ↓
Claim / Evidence / Gap（根据harness保存的版本化state轨迹回溯）
     ↓
相关动作
     ↓
GRPO Credit

4.1 Research State设计

Research State主要包含Raw Evidence、Finding、Claim和Gap。
Raw Evidence

模型真正打开并读取页面后，由Harness保存原始页面内容：

Evidence(
    evidence_id,
    source,
    raw_content
)

Raw Evidence独立于TaskState保存，不参与后续压缩，模型可以通过 evidence_id 重新读取原始内容。

能解决什么问题： State写错或Context压缩后，仍然可以重新检查原始Evidence，避免错误解释持续污染后续推理。
Finding

Finding是对单条Evidence的简短记录，用于快速查看已经读过哪些信息。

Evidence Directory
├── E1: ...
├── E2: ...
└── E3: ...

Finding只描述Evidence中的主要内容，不负责判断这条Evidence最终支持哪个结论。主要负责维护证据目录Evidence Directory方便后续重新回溯

Raw Evidence = 页面原始内容
Finding      = 对Evidence的简短记录
Claim        = 当前需要验证的任务结论

能解决什么问题： 明确区分原始内容、Evidence摘要和模型结论，减少不同类型信息混在同一段State中的问题。
Claim

对于需要同时满足多个条件的任务，将关键结论拆成不同Claim，并记录对应Evidence。

Claim(
    claim_id,
    statement,
    status,
    supporting_evidence_ids,
    contradicting_evidence_ids
)

例如：

C1: X毕业于Amherst        ← E1
C2: X的父亲是Bob         ← E2
C3: X在2015年后加入Z     ← E1

能解决什么问题： 明确每条Evidence具体支持哪个条件，减少Evidence已经找到但人物、条件或关系绑定错误的问题。
Gap

当前无法充分支持的Claim记录为Gap：

Gap(
    claim_id,
    description
)

Gap用于记录当前还缺什么证据，并指导后续搜索。

能解决什么问题： 减少模型持续围绕当前候选重复搜索，使后续搜索优先解决真正缺失的信息。

最终TaskState可以简化为：

TaskState
├── Answer / Candidate
├── Claims
├── Evidence Directory
├── Gaps
└── Verification Status

4.2 State更新与验证

State更新、验证和上下文压缩分别处理不同问题：
操作	触发时机	作用
update_state	新Evidence改变当前判断时	更新Claim、Candidate和Evidence关系
verify	当前答案基本形成、Gap修复后、提交前	重新检查Claim和Raw Evidence
Context Compression	上下文过长时	删除已经被State吸收的旧历史
State Update

模型读取新的Evidence后，如果该信息会改变当前判断，则调用 update_state。

New Evidence
     ↓
update_state
     ↓
Candidate / Claim / Evidence关系更新

update_state可以更新当前判断，也可以修正之前错误的Finding或Claim-Evidence关系。Gap不能直接通过Update清除，需要后续Verify确认。

能解决什么问题： 新Evidence可以稳定进入Research State，同时保留后续修正错误State的能力。
Verification

Verify阶段重新读取Claim对应的Raw Evidence，检查：

    Claim是否真正得到Evidence支持；

    Evidence是否绑定到正确的人物、实体和条件；

    当前答案是否覆盖任务中的关键条件。

如果发现问题，则生成对应Gap：

Claim
  ↓
Raw Evidence
  ↓
Verify
  ↓
Pass / Gap

当模型认为Gap已经解决后，需要再次Verify才能清除。

能解决什么问题： 发现Evidence解释错误、关系绑定错误和过早确认候选等问题，避免错误State直接进入最终答案。
Submit

最终提交前要求：

所有关键Claim已验证
+
Gap为空
+
当前State已经通过Verify

能解决什么问题： 减少Evidence链仍然存在缺口时过早提交，以及高置信度错误答案直接输出的问题。
4.3 Context管理

完整Research State由Harness管理，推理阶段实际看到的是根据当前阶段生成的View。

正常搜索阶段：

Research View
=
Answer / Candidate
+ Claims
+ Gaps
+ Evidence Directory
+ Recent Trajectory

Raw Evidence不需要长期放在Active Context中，需要重新检查时再通过 evidence_id 读取。

Verify阶段：

Verify View
=
Question
+ Current Claims
+ Referenced Raw Evidence

Verify阶段不保留形成Candidate的大量历史推理，只重新检查当前结论和原始Evidence。

上下文过长时：

Research State + Long History
            ↓
Research State + Recent History

Context压缩不会修改Research State。

能解决什么问题： 在控制长轨迹上下文长度的同时，避免一次Context压缩直接覆盖Evidence和State；验证时也能减少历史错误推理对当前判断的影响。
4.4 State指导后续搜索

显式Gap可以让后续搜索围绕当前真正缺失的信息展开。

例如：

C1 已解决
C2 Gap: 尚未确认父亲是否为Bob
C3 已解决

后续搜索可以直接围绕C2展开：

Gap
 ↓
Search
 ↓
New Evidence
 ↓
Update
 ↓
Verify

能解决什么问题： 减少围绕错误Candidate的重复搜索，让长轨迹中的搜索动作更直接地推动当前State向完成状态变化。
4.5 ESR-GRPO信用分配

普通Outcome-based GRPO通常给整条轨迹共享同一个Group-relative Advantage。

因此一条成功轨迹中的无关搜索也可能获得正信用；失败轨迹中的有效动作也可能获得负信用。

ESR-GRPO利用最终Verified State进一步筛选真正相关的动作。
Final Support Chain

最终答案中的Claim可以回溯到Supporting Evidence，再找到形成这些Evidence和更新State的相关动作：

Final Answer
    ↓
Claim
    ↓
Evidence
    ↓
Search / Open / Update

只有最终仍然支持正确答案的Claim-Evidence关系参与信用分配。
Gap Repair Chain

Gap从产生到解决也可以形成一条完整链：

Verify
  ↓
Gap
  ↓
Search / Open
  ↓
Evidence
  ↓
Update
  ↓
Verify
  ↓
Gap Resolved

如果Gap最终被成功解决，对应的搜索和状态更新动作也可以获得正信用。

最终对GRPO Advantage进行动作级Mask：

$$
\widetilde A_{i,t}=M_{i,t}Z_iA_i^+
$$

其中：

    $A_i$：原始GRPO轨迹级Advantage；

    $A_i^+=\max(A_i,0)$；

    $Z_i$：最终答案正确且Research State验证通过；

    $M_{i,t}$：当前动作是否位于最终有效的Evidence或Gap修复链中。

因此：

成功轨迹 + 有效动作   → 正信用
成功轨迹 + 无关动作   → 0
失败轨迹             → 0

ESR-GRPO仍然使用最终任务Reward，不额外训练Reward Model或Critic。Research State主要负责确定最终Reward应该分配给哪些中间动作。

能解决什么问题： 减少成功轨迹中的无关动作被一起奖励，同时避免失败轨迹中的有效搜索因为最终答案错误而被直接分配负信用。

整体可以概括为：

前向：
Evidence → Claim → Gap → Search / Verify

反向：
Reward → Verified State → Claim / Evidence / Gap → Action Credit

5. 实验计划

整体实验环境参考ECHO在BrowseComp-Plus上的配置，首先使用较小模型和本地benchmark验证ESR-GRPO的State维护和信用分配设计。
配置	设置
数据集	BrowseComp-Plus（BC-Plus）
策略模型	Qwen/Qwen3.5-4B
检索模型	Qwen3-Embedding-8B
RL算法	GRPO / ESR-GRPO
Judge	Qwen3-32B
主要评测指标	Accuracy、Evidence Recall、平均交互轮数、Search / Visit次数

BrowseComp-Plus同时提供最终答案和Evidence relevance judgement，可以同时评估答案正确率和Evidence Recall。

实验首先在 Qwen/Qwen3.5-4B 上验证以下问题：
1. 验证ESR Research State的有效性

先不进行RL训练，在 Qwen/Qwen3.5-4B 上实现 ESR 的完整推理流程，包括 Raw Evidence、Claim-Evidence State、Gap 和 Verification，并与相同模型下的普通Agent/AREX式Context进行对比。

重点观察：

    Accuracy 和 Evidence Recall 是否提升；

    高 Evidence Recall 但回答错误的case是否减少；

    Search次数、Visit次数和平均轨迹长度是否下降；

    Evidence已经找到但State写错、关系绑定错误等bad_case是否减少；

    Gap是否能够实际引导后续搜索并被正确解决。

这里最关键的是验证：

Raw Evidence
    ↓
Claim-Evidence State
    ↓
Verification + Gap
    ↓
更有效的后续搜索

2. 验证ESR-GRPO信用分配

在第一阶段确定Research State设计有效后，固定相同的模型、搜索环境和State机制，对比普通GRPO和ESR-GRPO。

相同ESR前向框架
      ↓
GRPO        vs        ESR-GRPO
整轨迹Credit          State-based Credit

ESR-GRPO根据最终验证通过的State进行回溯，只给Final Support Chain和Gap Repair Chain中的相关动作分配正信用。

重点观察：

    ESR-GRPO相比GRPO是否提升最终Accuracy；

    成功轨迹中的无关Search是否减少；

    平均交互轮数和Search次数是否下降；

    高Recall但回答错误的轨迹是否减少；

    抽样检查Credit Mask，确认被奖励的动作是否真正参与最终Evidence链或Gap修复。

主要验证： Research State提供的结构化关系能否改善长轨迹中的信用分配，使模型更倾向于保留真正推动任务完成的搜索和状态更新动作。