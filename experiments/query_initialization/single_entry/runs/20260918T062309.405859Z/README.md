# v003 单入口开发联调

8 道已知开发题 × 4 个阶段 × 1 次 = 32 次尝试，33 次 API 请求。全部完成 Search；这不是留出评测或最终正确率验证。

- [配置与源码快照哈希](manifest.json)
- [题目与原文定位表](tasks.json)
- [执行顺序](schedule.json)
- [机械审计](audit.json)
- [语义审阅](semantic_review.json)
- [已有参考依据复核](reference_recheck.json)
- [重启后 Open 检查](handoff_verification.json)
- [测试日志](tests.log)
- [开发结论](dev_review.json)
- [归档检查](archive_verification.json)
- [分析附件哈希](review_manifest.json)

|qid|阶段|执行状态|API 请求数|轨迹|交接|
|---|---|---|---:|---|---|
|183|v2|complete|2|[完整轨迹](qid_183__v2__r1/trajectory.md)|[handoff](qid_183__v2__r1/handoff.json)|
|183|refs_goal|complete|1|[完整轨迹](qid_183__refs_goal__r1/trajectory.md)|[handoff](qid_183__refs_goal__r1/handoff.json)|
|183|refs|complete|1|[完整轨迹](qid_183__refs__r1/trajectory.md)|[handoff](qid_183__refs__r1/handoff.json)|
|183|minimal|complete|1|[完整轨迹](qid_183__minimal__r1/trajectory.md)|[handoff](qid_183__minimal__r1/handoff.json)|
|551|v2|complete|1|[完整轨迹](qid_551__v2__r1/trajectory.md)|[handoff](qid_551__v2__r1/handoff.json)|
|551|refs_goal|complete|1|[完整轨迹](qid_551__refs_goal__r1/trajectory.md)|[handoff](qid_551__refs_goal__r1/handoff.json)|
|551|refs|complete|1|[完整轨迹](qid_551__refs__r1/trajectory.md)|[handoff](qid_551__refs__r1/handoff.json)|
|551|minimal|complete|1|[完整轨迹](qid_551__minimal__r1/trajectory.md)|[handoff](qid_551__minimal__r1/handoff.json)|
|583|v2|complete|1|[完整轨迹](qid_583__v2__r1/trajectory.md)|[handoff](qid_583__v2__r1/handoff.json)|
|583|refs_goal|complete|1|[完整轨迹](qid_583__refs_goal__r1/trajectory.md)|[handoff](qid_583__refs_goal__r1/handoff.json)|
|583|refs|complete|1|[完整轨迹](qid_583__refs__r1/trajectory.md)|[handoff](qid_583__refs__r1/handoff.json)|
|583|minimal|complete|1|[完整轨迹](qid_583__minimal__r1/trajectory.md)|[handoff](qid_583__minimal__r1/handoff.json)|
|591|v2|complete|1|[完整轨迹](qid_591__v2__r1/trajectory.md)|[handoff](qid_591__v2__r1/handoff.json)|
|591|refs_goal|complete|1|[完整轨迹](qid_591__refs_goal__r1/trajectory.md)|[handoff](qid_591__refs_goal__r1/handoff.json)|
|591|refs|complete|1|[完整轨迹](qid_591__refs__r1/trajectory.md)|[handoff](qid_591__refs__r1/handoff.json)|
|591|minimal|complete|1|[完整轨迹](qid_591__minimal__r1/trajectory.md)|[handoff](qid_591__minimal__r1/handoff.json)|
|645|v2|complete|1|[完整轨迹](qid_645__v2__r1/trajectory.md)|[handoff](qid_645__v2__r1/handoff.json)|
|645|refs_goal|complete|1|[完整轨迹](qid_645__refs_goal__r1/trajectory.md)|[handoff](qid_645__refs_goal__r1/handoff.json)|
|645|refs|complete|1|[完整轨迹](qid_645__refs__r1/trajectory.md)|[handoff](qid_645__refs__r1/handoff.json)|
|645|minimal|complete|1|[完整轨迹](qid_645__minimal__r1/trajectory.md)|[handoff](qid_645__minimal__r1/handoff.json)|
|786|v2|complete|1|[完整轨迹](qid_786__v2__r1/trajectory.md)|[handoff](qid_786__v2__r1/handoff.json)|
|786|refs_goal|complete|1|[完整轨迹](qid_786__refs_goal__r1/trajectory.md)|[handoff](qid_786__refs_goal__r1/handoff.json)|
|786|refs|complete|1|[完整轨迹](qid_786__refs__r1/trajectory.md)|[handoff](qid_786__refs__r1/handoff.json)|
|786|minimal|complete|1|[完整轨迹](qid_786__minimal__r1/trajectory.md)|[handoff](qid_786__minimal__r1/handoff.json)|
|1072|v2|complete|1|[完整轨迹](qid_1072__v2__r1/trajectory.md)|[handoff](qid_1072__v2__r1/handoff.json)|
|1072|refs_goal|complete|1|[完整轨迹](qid_1072__refs_goal__r1/trajectory.md)|[handoff](qid_1072__refs_goal__r1/handoff.json)|
|1072|refs|complete|1|[完整轨迹](qid_1072__refs__r1/trajectory.md)|[handoff](qid_1072__refs__r1/handoff.json)|
|1072|minimal|complete|1|[完整轨迹](qid_1072__minimal__r1/trajectory.md)|[handoff](qid_1072__minimal__r1/handoff.json)|
|1117|v2|complete|1|[完整轨迹](qid_1117__v2__r1/trajectory.md)|[handoff](qid_1117__v2__r1/handoff.json)|
|1117|refs_goal|complete|1|[完整轨迹](qid_1117__refs_goal__r1/trajectory.md)|[handoff](qid_1117__refs_goal__r1/handoff.json)|
|1117|refs|complete|1|[完整轨迹](qid_1117__refs__r1/trajectory.md)|[handoff](qid_1117__refs__r1/handoff.json)|
|1117|minimal|complete|1|[完整轨迹](qid_1117__minimal__r1/trajectory.md)|[handoff](qid_1117__minimal__r1/handoff.json)|
