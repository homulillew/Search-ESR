# Minimal Recoverable Loop

## Material Passport

用户指定的代码机制实验，base `1e5b426b037eda91395664b820ce64cd4f12c708`，分支`experiment/minimal-recoverable-loop`。使用academic-research-suite实验执行流程，角色在当前会话内执行。用户任务书授权准备代码与参考；第47节明确要求每个付费批次在精确请求冻结后另行授权。技能中的一般执行确认不覆盖该已授权的离线准备。

参考作者/语义复核者为单一、熟悉历史材料的Codex，不是独立评审。材料为历史研究题目与真实工具observation，无新人工参与者。所有历史结果不变。R、Source库和回执均不引入新的持久语义图。

## 核心假设与阶段

检验局部控制错误能否在保护事实状态、保持H低权限、用NoGain反馈和保守Closure的条件下恢复。E1检验事实入口，E2检验Actor/恢复策略，E3检验Closure，E4才检验真实闭环。

严格顺序E0→E1→E2→E3→E4。任何前置FAIL停止后续；无自动修补重跑。默认采用全部数值门槛，低召回即使安全也只描述为conservative，不静默算PASS。用户若在调用前明确采用任务书的保守例外，需独立记录前瞻修订，重新冻结；不改历史结果。

当前准备范围：E0 Admission来源/参考、全部cohort来源ID与Fresh问题冻结，E1A Writer完整请求和E1B确定性编译器，以及MinimalStateView的离线权限/反馈契约。E2/E3的grounding/语义Gold及具体请求在前置PASS后、对应调用前完成。E4调度器尚未启用；离线契约不是已经验证过的live loop。

## E0：来源与抽样

Admission Bank取历史evidence_packet全部44行，按(qid,url,text)精确去重，保留首个历史行，得到28个observation；加入25个预先明确的自然风险窗口。共 **53个observation、20个qid**。每条保留完整历史可见文本，不追加全文、不改OCR、不把未来内容补进窗口。最近25条逐字段匹配真实tool observation；老28条保留上游历史window/tool出处与哈希。异质旧窗口截取边界本身是历史事实，不是本轮重写。

53个来源逐条人工复核，冻结 **56个有用语义召回项**、具体禁止强化的推断。正例不是对最终答案身份的确认。例如Euler出生可进入窄Claim，书籍引用关系不能因此成立；Ding2019婚姻可成立，gift仍缺。9个零预定召回项来源允许空输出；若输出其它确由来源蕴含的事实，不因为没写入参考就算假Claim，另记usefulness。

R使用Q中的完整句子/项目源片段；去掉纯提示性开头，将孤立编号与随后句子合并，保持精确源offset。R不是topic tags、可减去的程序或细粒度依赖图。本轮所有原始Q保持原字节文本。

Recovery Development为6qid：546、1094、228、637、843、971，共12个历史prefix来源ID。旧prefix可能含未经本轮认证的Claim；E2前必须依据真实prefix支持逐条审查。不得静默清洗/假称旧Writer的Claim已通过新Gate，问题prefix标为ineligible并报告覆盖损失，不注入false C。

Closure来源bank在57个自然S00/Sxx历史快照内，按qid内固定哈希、qid间轮转机械冻结40个；尚未赋予complete/near-complete/trap Gold。E3前按Q/R/C与源证据标注，不看最终答案。若没有合格complete快照，分母为null，不能伪造complete来通过门槛，也不能看结果后补样。

Fresh使用BC+原始query分布，排除所有仓库实验/本地研究工作中的明确qid/题目暴露；对剩余非空题目按固定seed哈希取前10。共589个eligible、选10；没有难度、答案或成功率筛选。只声明仓库实验未暴露，不声明预训练未见过。题目正文不用于Prompt修补。

## 权限与最小视图

长期语义只允许Q/R/C/H；机械T记录intent、实际操作及delta。Source原文、工具handle和provider回执是可追溯机械材料，不是额外语义判断状态。

Actor收到Q/R/C/H/compact TraceView的深拷贝。Actor输出仅能选focus/probe/acquisition或REQUEST_CLOSURE_AUDIT；未知字段、写C/R/Q/closure/STOP均不接受。Writer只产生候选；Admission结果与精确来源检查共同决定是否commit。H操作只改H，最多6个active；规范化的重复假设不算Gain。

C保留statement、source_refs、supporting_excerpts及status。当前E1只测试追加active Claim；superseded/disputed及证据冲突解决的live转换需在E4前单独冻结并验证，不让Actor或H Manager代行。当前代码不声称已实现或测得conflict-resolution Gain。

NoGain family固定为(requirement_id,strategy,sorted H IDs)。同family连续两次NoGain后，再选同family记录POLICY_VIOLATION，不自动重试。只换query措辞不清零；仅改变route但family不变也不能绕过任务书第36节的机械检验。语义上是否真换路线另行人工评价，换strategy标签本身不是语义成功证明。

Gain来自新入库Claim、非重复新H、active H被rejected/deprioritized、新未检查的followup source；仅更多搜索结果或重复pending anchor不算Gain。C/H去重是保守的词面处理，不能声称解决所有同义改写。E4仍需报告语义冗余导致的虚假进展风险。

TraceView仅最近3条记录、NoGain streak、近期family、visited/pending与可见source handles/title；不回填全轨迹。available_sources是机械目录，为已有D#/W#路由提供合法ID，不含相关性score/Gold/LLM summary。

Closure不看H/T，仅Q/R/C和C中的真实摘录。接受任务书的逐R输出，也接受overall-only READY；后者是一个“全部覆盖”的实质判断，必须按Gold计分，不能隐藏为格式失败以减少false READY。只有Closure组件READY才能调用答案生成器；之后C变化使旧READY失效。CONTINUE缺口反馈只进Trace，不进C/R。

## E1A：Writer请求

**53 sources × 2 replicates = 106次**，固定哈希顺序，无工具。原任务书第11节Prompt保留，追加仅限定格式的JSON Schema。实际输入只有Original Q、一个相关coarse R、source_id及这一个observation的原始title/url/text；无H、旧Claim、Gap、Gold、历史Writer输出、答案或模型reasoning。

Writer候选数量不人为限为固定K、不截断列表、不择优。有效JSON但错误结构为失败；所有106个slot保留。空候选列表是有效输出，相关参考atom仍计Recall分母。followup提示无事实权限；未知/未观察handle不可登记为新Gain，需另记无效hint。

## E1B：Admission依赖批次

1. 完成并提交全部Writer原始响应/解析/usage。
2. 给每个有效Writer候选分配机械candidate_id，不按Gold筛选。
3. 先验证source_id与真实来源一致，摘录是该来源`text`或原始`title`字段的非空精确子串。不得跨字段拼接、规范化空白、补省略号或借外部来源修复。失败候选机械REJECT，保留ledger，不将伪摘录发给Verifier当证据。
4. 对其余每条候选生成一次独立Admission请求，输入只有statement、实际摘录、原始source metadata。metadata用于识别来源；来源title/url本身不能补足未被所选excerpt证明的事件关系。没有Q/R/H/Trace/完整其它正文。
5. 单一复核者依据实际excerpt及预冻结来源政策，建立candidate-level参考；看不到尚未生成的Admission verdict，不读provider reasoning。所有实际候选都评，包括意外输出。判断该Claim是否被全observation和所选excerpt分别蕴含、错误类型、风险、是否candidate hardening及匹配哪些冻结atoms。
6. 把完整候选ledger、review、确切Admission请求提交，hash freeze，再请求新的精确调用数授权。初始106次授权不覆盖这批。
7. 全部依赖结果归档后才能给E1最终PASS/FAIL。无有效Admission请求时不得凭空增加call；写零调用账本并照样评分（如必要分母null则不能PASS）。

任务书第13节base Prompt保留，格式Schema补全ADMIT/REJECT及11种允许tag；tag仅诊断，不用于改变控制策略。返回失败不修复，不把失败当ADMIT。

## E1计分

Primary单位是实际candidate Claim；两replicate都保留，无vote。Precision=被引用摘录完整蕴含的最终admitted Claims / 全部admitted Claims，包括参考未列出的其它输出。对整句评，部分正确仍是false admission。

Recall=最终正确admitted Claims覆盖的(source semantic atom, replicate) / **112**。覆盖使用语义等价或蕴含，不用字符串匹配；同一atom在一个replicate至多记一次。Writer将事实拆成多条不应受罚：Admission调用前为每个atom冻结实际候选的充分集合，最终保留完整充分集合即可计覆盖。每个失败/空Writer仍保留它的参考分母。另报Writer原始Recall、候选精确摘录率、被机械拒绝数和新增Verifier误拒。

危险错误包括candidate hardening、未建立身份/关系/角色、跨源组合、时间/模态/量词/条件强化、把推断写成确定事实；只要最终admit此类一个就触发high-risk gate。关系/角色与scope率分母都是全部admitted Claims，可能重叠，不能相加。最终摘录有效率100%由硬检查保证，是harness指标；必须同时展示Writer原始摘录有效率，不能据此称模型引用完美。

Schema分别要求Writer≥95%、Admission≥95%，不让数量较多的组件掩盖另一组件失败。失败保留计划请求分母；所有失败都留raw。没有实际调用时不声称PASS。门槛精确数值见GATES，不用四舍五入替代比较。

E1没有把H输入模型，因此只能报告“H结构上不可见”和Q/R强线索引起的candidate-hardening proxy。真实H→C因果泄漏需E2/E4，不能把未测试的干预报为经验0。

## 后续阶段与授权可实现性

E2只测冻结prefix的Actor一次响应，不执行Search。P1使用真实历史坏candidate，只改H；P2 trace注入明确标为实验扰动；P3只用当前已观察source。语义appropriateness/真策略变化的Gold在调用前冻结。Actor示例的`CANDIDATE_CONFIRM_OR_REJECT`不在任务书允许枚举中；实际schema以列出的五种expected_gain为准，另行披露，不依赖无效例子。

E3只用审查过的自然快照，false READY=0优先；按全部门槛进入E4。只要一个前置FAIL就停止。

E4计划12条历史配对trajectory + 10条fresh=22条；每条最多8次acquisition、2次Closure。全体最多176个检索动作，故Search上限也为176，Closure上限44。Search k=5，无多query变体。Writer/Admission/H Manager的实际次数依赖返回observation和候选，当前不能给虚构精确数目。

第47节要求完整实际requests。自适应loop的未来payload在真实Observation前不存在，冻结compiler和预算上限不能冒充冻结所有payload。若进入E4，按依赖波次分别生成/commit/hash实际请求并新授权；不能复用本轮106次许可或自动展开未知调用。未获得另行明确的执行规则修订前保持该边界。

## Backend、失败与账本

DeepSeek `deepseek-flash`、temperature0、JSON mode、max_retries0、并发≤8，max_tokens沿用省略，240秒HTTP inactivity（非总wall deadline）。400/401/402/403/404/422停止新发送，已在途请求完成。保留失败、发送意图与未发送slot。exclusive文件拒绝覆写/自动resume。

不改检索器。最新真实acquisition使用`deferred_recovery.tools.restore`中的现有`SearchFindTools`；不能误称或静默替换成Orthogonal。SEARCH/FIND/OPEN仅作现有参数的机械映射，OPEN的pattern编码before/after/around。E1–E3实际检索0；E4前再冻结全部执行依赖和资源预算。

usage记录input/output/total、其中reasoning、hit/miss、usage缺失、延迟及失败。缓存率=sum(hit)/sum(input)，仅用一致计数，不平均批次百分比。reasoning是output子集且不参与语义审阅；金额未知保留null。22,238个历史实验文件SHA保护，原Prompt/结果/标签不改写。

## 解释限制

Admission precision通过不能单独证明整个loop可恢复；这是先决条件。53个来源来自20个已熟悉的问题，多个窗口共享文档，两replicate不独立；Fresh10qid仅用于之后真实loop，不作夸张accuracy门槛。不得与不同分母的旧accuracy排名。最终逐项回答任务书20问，未执行阶段明确标未测量。
