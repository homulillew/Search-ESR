# Asymmetric Research Progress

用户任务原文见 TASK.md。执行基线为远程 `origin/experiment/dynamic-progress-blockers` 的 `094b87382668fa21e68290eed3050d5f8e5f979a`；新分支 `experiment/asymmetric-progress-closure-audit`。此前实验只读。

## 数据与输入边界

主集 24 个真实历史 checkpoint，9 qids，最多 4/qid：19 unresolved + 5 resolved。以 Q + 按原序 Claim statements 的 SHA256 排除历史 Frontier F1、Dynamic Progress primary 和 semantic exploration 的输入。全部现有 Claims 原样保留；不增删事实造样本。完整历史 state 仅用于保存 provenance，模型请求只有 Q 与编号 Claim statements。

5 个 fresh resolved 是所有剩余可用控制，仅 2 qids。严格 near-closure（强候选仅剩一个关键关系）主集 1 个/1 qid；不能满足 10–12/5-qid 目标。主集无 material inter-Claim conflict，单独压力集覆盖。此限制必须进入最终结论，不能用压力集补主分母或夸大验证范围。选择为标签驱动、调用前固定的目的抽样，不是随机总体样本；exact freshness 不等于语义独立。

压力集 9 个：历史 P17/P19、C06/C07/C08/C10/C12/C15，以及已知 over-demand 的 resolved C04。C04 保持旧 materiality 标签，不因新输出更改。主/压力均每 checkpoint L0×2、L1×2、Audit×2，无条件运行。

## 干预与冻结

L0 为旧 B prompt 逐字节复制；L1 只追加任务 §28 的单关系文字。Audit 使用 §30 核心 prompt 与明确 JSON serialization contract。相同 DeepSeek flash/provider defaults，retry=0，四并发；无工具、无第二模型、无修复或补采样。一次 dummy transport canary 在正式 freeze 前执行；输入不涉及研究语义。

每阶段 manifest 固定 git preparation HEAD、provider、prompts/schema、bank/labels、request hashes、pairing、样本量、horizon、失败政策；执行前提交，日志保留每次真实 run HEAD。所有失败保留，不因失败缩小 planned denominators。历史全体 tracked experiment 文件单独哈希审计。

## C1 预注册 gate

L1 false closure ≤3/38 unresolved slots（≤10%），valid blocker presence ≥35/38，blocker precision ≥90%，correct closure ≥9/10 resolved slots。不得出现相对同 replicate L0 新增 ≥3 个 critical semantic regressions 且涉及 ≥2 qids。Critical：新增 false/missed closure、无有效 blocker、unsupported premise 或 false evidence promotion；不把单纯 breadth/status 差异叫 critical。所有条件同时满足。

## C2 预注册 gate

Audit false closure ≤1/38（采用任务允许的整数规则）；correct closure ≥9/10；拒绝输出 blocker precision ≥90%；所有 confirmed 输出 certificate adequacy ≥90%（false closure certificate 必为不足）。额外要求 valid rejection presence ≥35/38，防止 transport failure 获益。schema failure 不计正确输出。主集 5 个控制/2 qids 是适用性限制。

## C3 预注册 gate 与配对

Pairing.json 由 SHA256(case_id) 的 parity 指定 L1 primary；SHA256(case_id+':audit') 指定 Audit primary；另一 replica 为 confirmation/stability，禁止结果后换配对。L=primary L1；LL=L1 primary AND confirmation；LA=L1 primary AND Audit primary。失败不能 STOP，并另外计 decision invalid，不能算正确 continue。

主集 24 decisions：LA false stop ≤0/19，correct stop ≥5/5（≥90%的整数上取整），整体有效 decision accuracy ≥23/24，且 LA 不低于 LL 的 decision accuracy、不高于 LL 的 false stop。此 C3 是安全/非劣条件，不强迫出现优势；若 L 无错误或 LA≈LL，语义收益不可辨别。只有 C1+C2+C3 全部通过才进入无 Search 的 Frontier F1；压力集不得翻转 gate。

所有策略报 FalseStop / CorrectStop / MissedStop / invalid，条件第二调用比例、每 decision 调用数及 input/output/reasoning tokens。LL/LA 条件触发均为 L1-primary 有效 resolved=true。逻辑成本只计实际会走的分支；离线真实费用另计全部调用。cache hit ratio = sum(hit)/sum(hit+miss)，tokens 不转换未经核验的金额。

## Semantic review

由单一 Codex reviewer 依 Q+Claims、冻结标签和 RUBRIC 执行。无新模型 reviewer，不查外部事实。输出用 opaque review IDs 混排；schema 和题意可泄露条件，不宣称完全盲审或独立审稿。每个 blocker 单独判 material/single relation/unsupported/over-demand；Light 的 status 与 ref fidelity 独立打分。Audit certificate 检查主要关系是否真实由所引 Claims 支持，且整体充分。

## 停止与探索

最多一次 ≤12 checkpoints/24 submissions 的探索，必须先从已观察错误定位机制，独立 EXPLORATION_PLAN/commit/freeze；不能覆盖 formal gate。FULL 仅在 Audit 仍 false close 且条件扫描不足时可用。任何 closure gate 失败不运行 Frontier/Retrieval/Writer/P3/P4。通过才另冻 Frontier D/O/G；不挑选好 G 输出。

## Cache 原型

仅离线 mechanics：Q/Claim statements hash 改变清空 Light/Audit；Hypothesis/Workspace/attempts 改变不清空。Audit rejection 可重用，不同状态不可复用，不在同状态反复采样直到确认。无生产 controller 集成、无 hard gate、无新 persistent State 字段。
