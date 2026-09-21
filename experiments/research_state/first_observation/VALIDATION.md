# 本次实现验证

基线：32789024890650d246917060b809fcef0153594e。新增独立 first_observation 实验，不修改现有模块。

本地执行：Python 3.13.5，`python -m compileall -q experiments/research_state/first_observation`；`python -m unittest discover -s tests -p 'test_first_observation.py' -v`：**42项测试通过，0跳过**。

覆盖：原题Unicode/空白不改写、答案字段不进入选择包、查询超限不裁剪、空检索、检索异常和坏窗口、连续日志篡改、来源引文/重复位置/未知ref、全批拒绝无效笔记、空笔记、reasoning-only截断、无隐式JSON修复、完整双工具提议、Open可见性、stop兼容显式开关、profile拒绝凭据/无效参数、请求深拷贝、人工笔记替换拒绝、冻结参数/源码漂移拒绝、A/B除笔记外一致、失效笔记精确回退、额外重复Actor不执行工具、中断/未运行分母、未知成本和不一致用量、审阅卡不把推理替换成交付正文。

集成测试用合成问答、合成原文窗口、模拟检索器和模拟模型；模型异常通过显式异常类型注入。测试不是实际OpenAI SDK/BCPlus兼容性验收，更不是BC+效果。两个模型阶段都调用同一执行器，真实CLI只将SDK的APIError类归为API失败，普通本地异常停止且保留记录。

限制：此容器无法连接GitHub网络地址或访问用户/data环境，远端通过已连接GitHub工具审读和推送。本地没有BCPlus资产、transformers或可用模型SDK安装；没有运行真实检索/生成，也没有重跑整个旧仓库测试集。真实适配器已按当前ObservedTools/RawWindowBuilder/qa.jsonl接口核对，但实际query_prefix、内部截断、模型预算、超时和特殊来源仍须由Codex在完整环境验收。

程序校验通过仅证明结构/引用范围成立；有一项测试明确证明错误statement仍可通过真实quote成员校验。语义验收必须另做，不标“状态正确率100%”。

真实首搜=0，真实生成调用=0；本次无实验准确率或性能提升结论。
