# 首次真实调用前的兼容性依据

捕获模型与已授权模型均为 qwen3.7-flash，不使用 --model 覆盖。此前会话已在同一地址成功列出该模型并完成普通、流式和 tools 调用，本批不增加试跑。公开官方模型页 https://help.aliyun.com/zh/model-studio/qwen3-7-flash （2026-09-20 北京时间查阅）给出 1,000,000 上下文、非思考最大输入 991,808，并支持 Function Calling。完整请求大小见 input_audit.json，最大为约 140 KB；UTF-8 字节量仅用作保守量级核对，不冒充服务端 token 实测。真实 usage 后报告实测长度，不删改前缀。Actor 保留 tools、tool_choice=auto、stream=false、enable_thinking=false，无新增输出预算；Reviewer 使用相同模型且固定 512 tokens。工具仍是 v000 search/get_document，不映射到当前 open。若出现全局上下文/认证/服务错误，应保留记录、停止批次并报告；单个输出无效按入口规则回退。

凭证只由 execute 中现有 Config.load 读取；本批未查看 .env、认证头或密钥。初始工作树无用户改动；本次预检产物是新增文件。用户明确授权 30 次模型调用，因此不再请求技能模板中的重复执行确认。
