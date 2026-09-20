# S0：研究笔记与调查状态视图

一个无训练、Actor-only 的独立实验包。先固定研究笔记、当前调查问题和完整已见材料，比较**相同内容的不同视图**。不修改默认 Search/Open、Query、旧 Need Review 或已保存的运行结果。

详细设计：[ResearchNotebook与调查状态节点设计与实验](../../../全链路排查报告/ResearchNotebook与调查状态节点设计与实验.md)。
执行交接：[CODEX_TASK.md](CODEX_TASK.md)。离线验证：[VALIDATION.md](VALIDATION.md)。

## 实验

| comparison | 组别 | 唯一处理 | 默认正式规模 |
|---|---|---|---|
| layout（默认S0） | flat / typed | 同条目按原序平铺或按来源/职责分组 | 12次Actor |
| attempt_linkage（后续S1） | typed / linked | 分层视图额外提供机械尝试关联索引 | 12次Actor |

每组每题重复2次，3个冻结前缀。0 Reviewer、0真实工具执行。保留原题、全部原始messages及引用；不生成摘要、不删除错误历史、不把缓存全文加入原文。`flat` 仍保留所有类型标签，不是故意缺失来源的弱基线。

笔记夹具是助手依据已见前缀编写的、有待逐项复核的诊断输入，不是自动抽取结果或人工金标。两个臂共享它们，因此这轮不能报告自动状态生成的收益。它也不是与原始Actor的同期基线比较。

## 运行（仓库根目录）

先安装已有 API 依赖，再冻结计划，避免 SDK 版本发生隐式变化：

```bash
python -m pip install -r requirements-chat.txt
python -m unittest discover -s tests -p 'test_investigation_state.py' -v
python -m experiments.research_state.investigation_state.run prepare --output /tmp/esr-state-prepared
cp experiments/research_state/investigation_state/profile.example.json /tmp/esr-state-profile.json
```

profile 是待验收候选配置，明确模型、地址、token cap、SDK timeout 和输入字节保护；**不是已证明生效的推理关闭配置**。不继承旧 enable_thinking。请在付费调用前检查当前模型参数支持，必要变更只用于新的 pilot 计划。不要将 API key 写入 profile。

先做单独的交付 pilot，3题×2视图×1重复＝6次Actor：

```bash
python -m experiments.research_state.investigation_state.run plan \
  --prepared /tmp/esr-state-prepared --profile /tmp/esr-state-profile.json \
  --purpose pilot --comparison layout --repeats 1 --output /tmp/esr-state-pilot-plan.json
python -m experiments.research_state.investigation_state.run execute \
  --prepared /tmp/esr-state-prepared --plan /tmp/esr-state-pilot-plan.json --env-file .env \
  --output experiments/research_state/investigation_state/runs/pilot_UNIQUE_ID
python -m experiments.research_state.investigation_state.run audit \
  --run-dir experiments/research_state/investigation_state/runs/pilot_UNIQUE_ID \
  --output /tmp/esr-state-pilot-review
```

`execute` 才加载密钥并调用模型；prepare/plan/audit 不访问 API。只使用 OPENAI_API_KEY 或 DASHSCOPE_API_KEY；模型/地址/预算不被 .env 中的其他配置暗改。运行目录必须全新。调用中断、超时或reasoning-only输出都保留，不自动重试或修复。

逐项复核 `/tmp/esr-state-prepared/fixture_review.template.json` 对应笔记/原文，另存 `fixture_review.json` 并填写实际reviewer和审核声明。哈希绑定内容；它只是审阅声明，不是密码学签名或自动事实验证。

在 pilot 机械交付干净、成本已知且夹具复核完成后，生成正式计划：

```bash
python -m experiments.research_state.investigation_state.run plan \
  --prepared /tmp/esr-state-prepared --profile /tmp/esr-state-profile.json \
  --purpose formal --comparison layout --repeats 2 \
  --fixture-review /tmp/esr-state-prepared/fixture_review.json \
  --accepted-pilot experiments/research_state/investigation_state/runs/pilot_UNIQUE_ID \
  --output /tmp/esr-state-formal-plan.json
python -m experiments.research_state.investigation_state.run execute \
  --prepared /tmp/esr-state-prepared --plan /tmp/esr-state-formal-plan.json --env-file .env \
  --output experiments/research_state/investigation_state/runs/s0_UNIQUE_ID
python -m experiments.research_state.investigation_state.run audit \
  --run-dir experiments/research_state/investigation_state/runs/s0_UNIQUE_ID \
  --output /tmp/esr-state-formal-review
```

pilot gate 不看语义好坏，也不选择成功例。失败pilot须保留并解释；禁止以不变配置反复采样直到一批全过。某节点/profile修正须重新记录、重新计划。正式批次的失败也不能删除。

退出0只代表机械调用/记录完整，不代表状态有效。成本缺失另见cost_accounting_complete。audit输出前缀卡、完整交付卡、空标签rubric和私有配对表；不自动填语义标签。审阅推理原文不替代正式content，也不进入评阅卡或后续状态。

## 当前边界

默认夹具固定 `396592c` 档案中的517/s21、546/s29、776/s53独立checkpoint；来自旧v000，不能说已经验证当前Search/Open。prepare验证Git blob、自校验hash、完整工具批次和引用/quote；多用户追问暂拒绝。没有生成新的ResearchState，没有自动更新或停止器。

新配置的token上限和timeout与旧实验不同，因此只作本批同profile视图比较。服务端模型别名、默认推理及采样不保证位级重现。profile的seed（如设置）与调度seed分开；未设置的默认值记录为未指定。

需要采集当前Search/Open前缀或改变任务/笔记时，应另立夹具与计划，不改旧档案、不混入本轮分母。S1不会自动执行。
