# 交给 Codex：执行经过审计的 E0

请先阅读本目录 README、EXPERIMENT_PLAN、AUDIT_20260920、checkpoints.json 及 prompts。目标是运行一次固定前缀 C0/C1 来源归属配对实验并定位下一处 bad case。仅执行模型的下一决策，不执行其提出的任何工具；不自动升级到 E1、完整 rollout、持久 State 或停止器。

已有运行 `runs/e0_20260919T171923Z/` 属于历史E0，必须保留。新实验不覆盖它，也不据历史517恢复表现臆造本批成功基线。请以审计报告中的当前三题说明为准。

## 1. 预检与冻结

遵循现有 AGENTS.md（如有），保留用户工作树改动，记录当前提交和实际工作树状态。不打印密钥、环境文件内容或认证头。不要修改 Search/Open、Query 初始化、旧 Actor 提示词和历史轨迹。

```bash
python -m unittest discover -s tests -p 'test_need_review*.py' -v
python -m experiments.research_state.need_review.run prepare --output /tmp/esr-e0-prepared
```

目录必须是新的。准备入口校验源文件 blob 后提取546 seq29、776 seq53、517 seq21，不重新拼装历史。缺源文件、哈希不符或完整前缀超服务能力时记录阻塞，不跳过验证、不截断/摘要、不换检查点冒充同一实验。

使用 Bash 公共参数数组；API_BASE 填当前服务商的无凭证基础地址。历史模型不可用时先决定替换模型，并向 COMMON 添加 `--model 模型名`；不得根据某组结果择优选模型。检查提供商支持捕获的工具请求参数和完整上下文。

```bash
API_BASE='https://你的服务商地址/v1'
COMMON=(--prepared /tmp/esr-e0-prepared --repeats 2 --seed 20260919
        --review-max-tokens 512 --sdk-max-retries 0
        --memo-mode legacy_text --comparison source_contract_pair --expected-base-url "$API_BASE")
python -m experiments.research_state.need_review.run plan "${COMMON[@]}"   --output /tmp/esr-e0-approved.json
```

确认12个分支、24次逻辑调用、零工具执行；C0原来源合同与C1新来源合同同批交错，不额外调用A/B，检查输入与提示词哈希和provider地址。仅C Reviewer来源合同有语义变化；不同时改备忘包装、Actor、schema或512输出上限。保存并检查该计划；若实现、参数、提示词或准备数据改变，重测后另存计划，不能绕过不匹配错误。先不额外增加试跑模型调用。plan_approved表示匹配该文件，不自动证明人工审查或实验科学性。

## 2. 一次完整批次

```bash
python -m experiments.research_state.need_review.run execute "${COMMON[@]}"   --plan-file /tmp/esr-e0-approved.json --env-file .env   --output experiments/research_state/need_review/runs/e01_source_first
```

运行目录换成本次唯一的新目录，并在后续命令保持一致。代码默认不做 SDK 重试；改配置需事前冻结。Reviewer无效/API失败时原样保存并无备忘回退Actor，不人工改JSON、不重复采样直到成功。Actor失败也保留分母。本地适配器/校验异常为harness_error，应停止并报告，不伪装成模型能力不足。

命令非零不代表所有结果无用：检查 summary 的机械错误、未知成本及各 arm 状态。完整工具调用但返回stop的响应保留意图、标旧协议不兼容，不修改finish_reason后宣称成功执行。日志破损仅使用可解析连续前缀，不能跳过坏行续接。零退出码也不证明动作合理或答案正确。

## 3. 审阅与归因

```bash
python -m experiments.research_state.need_review.run review   --run-dir experiments/research_state/need_review/runs/e01_source_first   --output experiments/research_state/need_review/runs/e01_source_first/review
```

先读不含输出的prefix_cards.jsonl，写合理下一动作；再读cards.jsonl逐卡标注，最后查private_key.json匹配组别。格式可能暴露分组，曾看过输出更不能声称盲评。若是代理辅助审阅，明确写出，不称独立人工金标。

先排除输入、计划、请求/日志、引用定位错误，再检查审查假设/需求是否合理、是否被Actor使用、是否产生新错误。memo_injected=false不能记需求传递成功。给出全部分母/失败数及逐题逐重复记录，不用两次中任一次成功代替总体比较。

至少详述1—3条病例的链路：原题限定 → 已见观察 → 前提/信息需求 → 实际下一动作 → 仍未知内容。E0没有新工具结果，不能写新检索命中率或最终准确率。旧v000结果不外推当前Search/Open。

## 4. 交付

把计划、源哈希、实际请求/响应、失败、成本、标注及中文报告保存到本次运行目录，不覆盖历史。报告明确是否全部完成、配置是否改变、各组成本、逐题发现、下一轮仅修改哪一处。C0/C1比较首先看来源归属，再看动作方向与正文断言；不因旧报告全0就改主评价。C1无收益时不增加State字段掩盖问题；需求合理但不影响动作再提出交接/需求替换；动作合理才提出E1。不要自动执行后续实验。

提交前检查diff无密钥、环境文件、模型权重和无关资产。本次任务若授权推送，推送本批记录与报告并提供提交；否则提交可复核结果待确认。没有执行的真实调用、工具调用或验证不得写成已完成。
