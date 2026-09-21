# 本批分析脚本

这些脚本只读取归档，不发起模型或工具调用。

1. `record_prefix.py RUN` 在读取本批语义输出前记录各题允许的动作。
2. `manual_judgments.json` 保存逐个完整响应的人工/单Codex辅助判断；`record_labels.py` 将其与卡片合并，记录实际首次标注时间。
3. 首次标签落盘后读取private_key，填写`pair_judgments.json`；`finish_annotations.py`只更新regression及其证据，增加条件元数据并生成逐分支报告。
4. `summarize_delivery.py`、`verify_artifacts.py`复核交付、成本、同内容对照、标签完整性和凭据扫描。

不要重跑首次声明脚本来伪造初评时间。需要修改判断时应保留初评并另存更正，不能覆盖已发生的审阅历史。本批已知上一轮Atria输出和开发案例，不宣称盲评或留出集。对空正文搜索提议，来源身份/正文断言/最终答案无评价对象时记not_applicable；不由此推断来源理解正确。
