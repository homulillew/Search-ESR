# P0/P1保真提示词：实现验证记录

日期：2026-09-21。基线：`3d5fc3da2265e3ae17deecb7fe3841624617d61c`。

## 本次实际完成

- 新增 `tests/test_first_observation_fidelity.py`：**39个测试方法，38通过，1跳过**。
- 测试命令：`python -m unittest discover -s tests -p 'test_first_observation_fidelity.py' -v`。
- 六个合成前缀、两条件共12个模拟请求跑通；全部请求逐对象与冻结计划一致，12张逐条评阅卡导出通过。
- 用合成档案走通 `plan_from_archive` 的输入、capture日志、profile继承路径；故意将旧 `note_outputs.json` 写成非法内容，确认新计划不读取旧模型输出。
- P0与原note请求精确相同；P1仅system文本增加段落。预评阅内容未进入模型；记录时间早于第一条请求。
- 覆盖：三对P0先行/三对P1先行、状态/输入/提示词/runtime漂移拒绝、无效引用/截断保留、不从reasoning补正文、空笔记仍需coverage、API错误与未知成本、未知计数不补0、用量加和错误、编程错误中断、未运行分母、损坏日志、快照篡改、重复执行拒绝、双组输出不能作为单份notes导出。
- 兼容回归：原单臂notes阶段及原Actor A/B阶段均用模拟客户端跑通；未执行任何实际工具。
- `run.py`只改变 `validate_plan`、`_classify`、`execute`、`audit` 四个函数；其余10个顶层函数AST未变。网络调用循环仍是原 `run.execute`。
- 本地已对原 `run.py`、`contracts.py`、`artifacts.py`、`note.txt`、`actor.txt` 与远端Git blob逐字核对；P0不修改，原始合同和模型参数不修改。

## 本次没有完成、不得宣称完成

完整真实 `notes_qwen_20260921` 档案未挂载到本环境，因此 `ActualArchiveTests.test_pinned_archive_prepares_offline` 跳过。已读取远端归档计划与代码，固定原计划/collection散列，但未在本机从完整真实档案生成12请求计划。Codex必须在完整checkout执行此测试并确认无skip；生成计划时还会核对固定散列和完整首搜日志。不能把合成档案测试称为真实BC+准备通过。

没有重跑原44项first_observation、旧state/need_review全套测试。没有运行新P0/P1真实模型、Search/Open、Actor、H2或rollout；没有得到语义效果或成本改善数据。

此次实际新增付费模型请求=0，实际检索=0。合成用量只用于统计逻辑测试，不得计入模型性能报告。程序校验引用/子串不是语义蕴含；测试特意保留“无据扩大书籍归属却schema合法”的示例，防止混淆这两个层次。
