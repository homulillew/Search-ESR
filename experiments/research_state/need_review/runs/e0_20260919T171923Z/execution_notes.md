# 执行补充记录

- 启动前代码与工作树检查均为只读；初始 status 为空，归档 status 含本批刚创建的 initial_git_head.txt。
- 实验入口未改动；首次模型调用前 freeze.json 与 pre_output_assessment.md 已写入。没有额外试跑或因结果改变配置。
- 30 次逻辑请求对应30次响应；SDK max_retries=0。未进行额外 HTTP 抓包计数，不保存认证头。
- C/776/r1 输出 length、JSON截断，原样保留并按入口规则回退。所有18分支在分母中。
- 后处理 write_mapped_labels 脚本初次运行出现一个缺右方括号的 SyntaxError，在执行任何写入前失败；修复后只重跑本地后处理。没有因此重跑实验或改任何响应。
- 预检目录 e0_20260919T171923Z_preflight 保留原件，副本在本次 run/preflight；冻结 SHA 的文件路径指向创建时原路径，两处对应文件字节相同。
- 语义评价由本 Codex完成，不标作独立人类评阅。揭示映射后只填写 regression 与元数据；初评所有其他标签保持。
- 配置能力核对使用官方模型说明页面，不把网络搜索内容或本报告发送至模型。

- 首次本地 git commit 因 Author identity unknown 退出128，未创建提交；随后仅对本次命令设置 Codex <codex@localhost>，未修改仓库/全局 Git 配置。
