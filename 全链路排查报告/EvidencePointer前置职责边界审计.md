# EvidencePointer 前置职责边界审计

基线：`750257d19c45c0547b579f20fc13ea42ff7095c4`（远端 `origin/main` 已核对停在该提交，工作区干净，无未提交修改）。

本审计**不读取上一轮报告的汇总数字**，而是直接读 `runs/note_fidelity_20260921T064837Z/model_retry2_072407Z/*/events.jsonl` 的原始 request/response，在本机重跑 `contracts.note_result`，并对每一个失败引文做字符级定位。所有下列数字都可由 `python3 /tmp/esr_audit.py` 复现。

---

## 0. 审计对象与可复现性

| 项 | 值 |
|---|---|
| 交付批次 | `model_retry2_072407Z`（第三批，前两批为凭证失败，见 §7） |
| job 数 | 12（6 题 × P0/P1） |
| 重跑 validator | `experiments.research_state/first_observation/contracts.note_result` |
| observation 来源 | 直接从 request 的 user payload 反序列化，不重跑检索 |
| 真实模型调用（本次审计） | 0 |
| 真实 Search/Open（本次审计） | 0 |

---

## 1. 机械 invalid 到底有多少

独立重跑结果与报告一致：

| 状态 | 数量 | 占比 |
|---|---|---|
| ok | 6 / 12 | 50.0% |
| invalid | 5 / 12 | 41.7% |
| empty | 1 / 12 | 8.3% |

**但"组级 invalid"掩盖了笔记级故障率。** 12 组共交付 32 条笔记（invalid 组的正文仍完整存在于 response 中，可逐条重建）：

- 32 条笔记中，**5 条引文机械失败** = 15.6% 笔记级失败率；
- 由于 all-or-nothing（§4），这 5 条坏引文连带丢弃了 **11 条本来逐字合法的笔记**；
- 即 32 条交付里 16 条（50%）因为 5 条的缘故不可注入下游。

**这是本审计最重要的量化结论**：机械失败的真实破坏力不是"5/12 组"，而是"16/32 条笔记被浪费"。语义内容本身大部分是好的。

---

## 2. 每种 invalid 的直接原因（字符级定位）

五个失败，五种机制，全部定位到具体码点。下列 `matched from anchor` 指从引文在窗口中的真实起点开始逐字符比对的最长公共前缀长度。

### 2.1 191 P0 note 2 — `source_ref` 截短

```
模型输出: w_eb79e233ddb35ebb          (18 字符)
窗口实际: w_eb79e233ddb35ebb6cd02553  (26 字符)
```

模型输出的 ref 是真实 ref 的**前缀**（截掉末尾 8 字符）。5 个可见窗口全是 26 字符，18 字符的不匹配任何窗口。

分类：**ref 复制错误**。

### 2.2 517 P0 note 0 — 段落分隔符被压成空格

从锚点匹配 170/357 字符后：

```
模型写出: ' Firstly, the Chinese zodiac i'   →  U+0020
来源实际: '\n\nFirstly, the Chinese zodiac '  →  U+000A
```

来源用 `\n\n` 分段，模型用单个空格替代，把两段并为一段。

分类：**whitespace / 结构字符复制错误**（不是 Unicode 归一化，是换行被丢弃）。

### 2.3 546 P1 note 1 — NBSP 被写成普通空格

从锚点匹配 114/350 字符后：

```
模型写出: ' million in prize money over t'  →  U+0020
来源实际: '£8\xa0million ...'               →  U+00A0
```

来源的 `£8\xa0million` 含不可分空格，模型写成 `£8 million`。

分类：**Unicode whitespace 归一化**。语义完全等价。

### 2.4 519 P1 note 1 — 引号字符替换

锚点查找返回 -1（`hay.find(q[:40])` 失败），比对从第 0 字符就分歧：

```
模型写出: 'I invited them both out to tea. ...'  →  U+0027 (')
来源实际: '"Clerides was quoted as saying ...'  →  U+0022 (")
```

来源用双引号包裹这段茶会引述，模型改用单引号。

分类：**标点字符替换**。语义完全等价。

### 2.5 776 P1 note 2 — 省略号跳句 + 段落合并

从锚点匹配 133/214 字符后：

```
模型写出: '...\n\nRuth Benedict also wrote '  →  U+002E U+002E U+002E
来源实际: ', deemed one of the major work'    →  U+002C
```

模型把来源的 `, deemed one of the major works...` 整句替换为 `...`，并跨段拼接下一段。

分类：**ellipsis / 非连续文本**。这条是五条里唯一同时含"内容省略"和"结构字符改写"的。

### 2.6 归类汇总

| 分类 | 数量 | 具体 |
|---|---|---|
| ref 复制错误 | 1 | 191 P0 note 2（前缀截短） |
| exact quote 字符复制错误（whitespace/换行） | 2 | 517 P0 note 0（`\n\n`→空格）、546 P1 note 1（NBSP→空格） |
| 标点 / 引号字符替换 | 1 | 519 P1 note 1（`"`→`'`） |
| ellipsis / 非连续文本 | 1 | 776 P1 note 2（`, `→`...` 且跨段） |
| **真正的 semantic attribution / scope 错误（被判 invalid 的）** | **0** | — |

**五条机械失败中，没有一条是语义错误。** 反过来，语义错误全部藏在被判 `ok` 的笔记里（§5）。

---

## 3. 失败的分布不对称

| arm | ok | invalid | empty |
|---|---|---|---|
| P0 | 4（776, 519, 546, 71） | 2（191, 517） | 0 |
| P1 | 2（191, 71） | 3（776, 519, 546） | 1（517） |

**关键不对称**：P1 消除了语义扩展（§5），但 P1 的 invalid 更多（3 vs 2），且 776 P1 那条"改对了的"笔记恰在其组内，组因省略号机械失败而整体无效。**保真收益与机械可靠性反向拉扯**，这不是巧合，而是同一干预的两面：addendum 要求更精细的措辞，模型在改写措辞时顺带改动了引文字符。

---

## 4. 当前 validator 是否 all-or-nothing

**是。** `contracts.note_result`（约 170 行）：

```python
result = {'status': 'invalid', 'notes': None, 'errors': [], 'quote_locations': []}
try:
    ...
    for note in notes:
        ...
        if ref not in refs or quote not in refs[ref]['text']:
            raise ValueError('Quote is not in this visible window body')
        ...
    result.update(status='ok' if notes else 'empty', ...)
except (ValueError, TypeError, KeyError, RecursionError) as exc:
    result['errors'] = [str(exc)]
```

任意一条 note 的任意一个字段失败，整个 `notes` 列表被置为 `None`。这是有意的设计（"strict all-or-nothing validation"），但它把**局部机械瑕疵放大成整组语义损失**。

注意 `empty` 是合法输出（`status='ok' if notes else 'empty'`），所以 all-or-nothing 只惩罚"有内容但不完美"，不惩罚"没内容"。这产生了一个已知偏置：**输出空集是零风险路径**，而 517 P1 正好走了这条路径。

---

## 5. 两类关键病例

### 5.1 「语义可能合理，但字符级失败导致整组 invalid」

**有，且是主要受损模式。** 4 条（517 P0 n0 除外，其余 4 条各自拖垮整组）：

- **546 P1 note 1**：引文 350 字符，仅 NBSP 一处不同，LCS 占比 67.1%。statement（Williams 600+ 破百、Class of '92）语义完全正确。整组 3 条笔记全部作废。
- **519 P1 note 1**：仅引号字符不同，LCS 占比 56.8%。茶会归属正确。整组作废。
- **776 P1 note 2**：这条本身是偏题选材（Ruth Benedict），但失败机制仍是机械的。
- **191 P0 note 2**：ref 前缀截短，且内容（Pinder Prize）本来就偏题——**机械失败与选材失败叠加**。

最有说服力的是 **546 P1** 与 **519 P1**：坏引文对应的 statement 没有任何语义问题，同组的另外两条笔记也全部逐字合法，却一起被丢弃。

### 5.2 「字符级引用合法，但 statement 语义上扩大了来源含义」

**有，而且正是被判 `ok` 的笔记。** 两例：

**776 P0 note 0**（status=ok，引文 22 字符，精确成员）：

```
STATEMENT: Diamond Jenness was born in 1886 and his early life period is
           noted as spanning until 1910.
QUOTE    : 'Early life (1886–1910)'
```

来源的小节标题给出区间，statement 据此断言出生年份。**validator 完全无法发现**：`quote in refs[ref]['text']` 为真，`source_ref` 合法。这是"合规但错误"。

**71 P0 note 2**（status=ok，引文 176 字符，精确成员）：

```
STATEMENT: Historical records indicate that by the late 19th century, the
           structure was no longer required ...
QUOTE    : 'By the late 19th century, sailing ships were replaced by steam
            packets. The Ballast Bank, no longer required for its original
            purpose, became a storage site for coal.'
```

来源是单一 Wikipedia 条目，statement 用 "Historical records indicate" 把来源层级抬高为复数历史记载。同样 validator 无法发现。

**这两例说明：字符级校验与语义保真是正交的。** 当前的 `quote` 字段既不能保证语义正确（§5.2），其失败也不代表语义错误（§5.1）。它在校验一个与目标无关的性质。

---

## 6. 职责重复：Harness 已知 source identity，却要求 LLM 再生成

**确实存在，且可在代码中直接指认。**

观察窗口在传给模型时已经携带全部 provenance 字段：

```python
# run._request
payload = {'question': row['question'], 'first_query': row['query'],
           'observation': deepcopy(row['observation'])}
```

而 `contracts.windows()` 校验每个窗口必含：

```python
for key in ('window_ref', 'docid', 'document_sha256'):
    nonempty(item.get(key), 4000)
...
if ... end - start != len(body):
    raise ValueError('Window body and character range differ')
```

即 Harness 在请求发出前就已确知：`window_ref`、`docid`、`document_sha256`、`url`、`offset`、`end_char`。

模型被要求**重新输出**其中两项：`source_ref`（= window_ref 的复制）与 `quote`（= window 正文子串的复打）。

更直接的证据在校验器自身：

```python
starts = [i for i in range(len(text)) if text.startswith(quote, i)]
locations.append({'source_ref': ref, 'relative_starts': starts,
                  'absolute_starts': [refs[ref]['offset'] + i for i in starts]})
```

**校验器自己就能把引文定位到绝对字符坐标。** 也就是说，只要模型给出 `[start, end)`，Harness 就能确定性地恢复 exact text、docid、hash、绝对偏移——一个字符都不用模型复制。

所以 `statement + source_ref + quote` 接口要求模型复打的，正是 Harness 已持有且能自行切片的信息。§2 的五种失败（前缀截短、`\n\n`→空格、NBSP→空格、`"`→`'`、`,`→`...`）**全部**落在这段重复职责上，没有一条落在真正的语义判断上。

一个佐证：**776 P1 note 0** 的引文是 131 字符的多段引用，精确包含 `\n\nFamily and childhood\n\n`——模型**有能力**逐字复制换行。失败不是因为能力不足，而是因为"复制 350 字符且一个码点都不能变"是一个没有任何机械反馈的开放式任务，偶尔失手是必然的。

---

## 7. 认证失败批处理行为

`model/` 与 `model_retry_071500Z` 两批：

| 批次 | 发送请求数 | 响应数 | api_error | 错误类型 | 耗时范围 |
|---|---|---|---|---|---|
| `model` | 12 | 0 | 12 | AuthenticationError | 0.06–0.31 s |
| `model_retry_071500Z` | 12 | 0 | 12 | AuthenticationError | 0.06–0.24 s |
| `model_retry2_072407Z` | 12 | 12 | 0 | — | — |

`run.execute` 的发送循环（约 298 行）：

```python
for job in plan['jobs']:
    ...
    journal.emit('request', request=deepcopy(job['request']))
    try:
        response = client.chat.completions.create(**deepcopy(job['request']))
    except ... :
        journal.emit('api_error', error_type=type(exc).__name__, ...)
```

**没有任何短路。** 凭证无效时，仍把剩余 11 个请求逐个发给同一端点，每次 0.06–0.31 秒返回 401。两批共 24 次明确无效的 API 请求。

这不是语义问题，是 execution harness reliability 问题，与 Evidence Pointer 实验分开处理（见 §9 与独立工程修复）。

---

## 8. P0/P1 是否已演变成 case-specific prompt patching

**部分成立，需要区分两个文件。**

`prompts/note.txt` 的历史很干净：只在 `edcfb92` 引入一次，此后**从未修改**（2025 bytes，单一 blob 版本）。它不含任何针对具体题目的细则。

`prompts/note_fidelity_addendum.txt`（`bf25c7e` 引入）是另一回事。它的三条核心规则与上一轮观测到的具体失败一一对应：

| addendum 原文 | 对应的上一轮具体病例 |
|---|---|
| "A section's date range does not by itself establish a birth date" | 776：标题区间被写成出生日期 |
| "If an article narrates one event and explicitly attributes a different passage to a book, do not attribute both events to the book" | 519：BBC 相遇被归给书本 |
| "Keep ambiguous attribution, place, and time at the level actually supported" | 71：来源层级被抬高 |

三条规则分别是 776、519、71 三道**固定开发题**的失败复述。这不是泛化的保真原则，而是对已知 bad case 的逐条修补。本轮结果也吻合这个判断：

- 776 的扩展被消除（addendum 命中）；
- 519 的扩展未复现（小样本不确定，不能算改善）；
- 71 的扩展被消除，但代价是措辞从 "constructed in 1905" 弱化为 "erected around 1905"（过度修正）。

**同时本轮新增的 5 条机械失败，没有一条能被任何 prompt 规则稳定预防**——因为它们是字符复制失手，与语义指令正交。继续在 note prompt 上加规则，会继续增加"措辞精细度"却不能增加"字符复制可靠性"。

**结论：note fidelity 分支的方向已经从"研究 State 的语义表达"漂移到"修 citation 序列化"。** 证据是 §1 的 50% 笔记浪费率与 §2 的零语义失败同时存在。

---

## 9. 当前 note branch 实际研究的是什么

必须明确区分三件不同的事：

| 研究对象 | 当前状态 | 证据 |
|---|---|---|
| **State utility**（显式中间状态对下一动作是否有价值） | **未被测试** | 本轮没有任何 Actor 调用、没有下一动作、没有 A/B。`fidelity.py` 的 plan 只有 note job，`prior=None`，没有 actors stage |
| **State writer fidelity**（模型能否保真地表达来源关系） | **被测试了，但与下面一项混淆** | 三轴分析中的"无据扩展"轴（P0 2 例 → P1 0 例） |
| **Citation serialization**（模型能否逐字复制 ref 与 quote） | **被测试了，且主导了结果** | 5/12 组无效，原因全部是字符复制；16/32 条笔记被浪费 |

**当前 note branch 实际测的是后两者的混合体，而 citation serialization 的噪声大到足以掩盖 writer fidelity 的信号**：776 P1 的保真改善被同组的省略号失败完全抹掉，在注入合同层不可见。

这是暂停该分支的充分理由——**不是因为 semantic note 被证明无用，而是测量信噪比被机械层摧毁了。**

---

## 10. 对任务说明中假设的核对

> "继续给 note prompt 增加 attribution、time、quote、ID-copy 等规则，很可能是在做 case-specific prompt patching"

**成立**（§8：addendum 三条规则 = 776/519/71 三题的失败复述；note.txt 本身未被 patch）。

> "window_ref、exact quote、offset、document hash 等信息本来已经存在于 Observation / Harness 中，却要求模型再次复制"

**成立**（§6：payload 携带 window_ref/docid/document_sha256/offset/end_char；validator 自行算出 absolute_starts）。

> "导致大量机械失败"

**成立且可量化**：5/12 组（41.7%）、5/32 条笔记（15.6%）纯机械失败，连带丢弃 11 条合法笔记，总浪费 16/32（50%）。零条语义失败由机械层捕获。

**与假设不一致之处**（据实补充）：
1. 机械失败并非"大量"在比例上压倒一切——笔记级 15.6%——但 **all-or-nothing 把它放大到 50% 的笔记浪费率**。真正的放大器是 validator 的整组作废策略，不只是复制任务本身。
2. 假设未指出的一点：**空集是零风险路径**。`empty` 合法而 `有瑕疵` 致命，构成系统性保守偏置（517 P1 已出现）。任何 fidelity 分支都必须显式处理这个偏置。
3. 假设聚焦"LLM 重生成 source identity"，但实际失败里有 4/5 是 **quote 正文复制**而非 identity 复制。两者都属重复职责，但修法不同：identity 可由指针消除，正文复制必须由 span 切片消除。

---

## 11. 由此得出的设计结论

1. **deterministic-first 是必需的，不是可选优化。** §6 的证据是代码级的：Harness 已持有全部 provenance，且校验器已能自行定位引文。模型不应再输出这些字段。
2. **第一版 Research State 只表达"哪些已看见的原文值得保留"，不表达 statement。** §5.2 证明 statement 是语义扩张的实际载体，而它恰恰没有任何机械约束。
3. **pointer 用 `[start, end)` 而非 quote 文本。** 这直接消除 §2 的全部五种失败模式（它们在 Evidence Pointer 路径中结构性不存在）。
4. **State utility 必须与 State writer fidelity 分开测。** §9 说明当前分支把两者混在一起且噪声主导。新实验第一轮用 reference/human-reviewed pointer，正是为了把 selector 的错误从 State 价值中剥离。
5. **all-or-nothing 的设计教训要继承**：新 contract 仍应严格，但严格在校验"指针是否指向当前可见窗口的合法区间"，而不是在校验"模型是否逐字复打了一段文本"——后者是不可靠的，前者是确定性的。
6. **认证失败短路是独立工程修复**，不混入语义结论（§7）。

---

## 12. 本次审计的限度

- 只重跑了一轮 12 job 的交付批次；前两批为凭证失败，未纳入引文分析（但完整保留在分母里）。
- LCS / 锚点定位是诊断辅助，**不是**新的校验规则；本审计未放宽任何 validator。
- 未修改任何旧实验、旧 response、旧标签；`model_retry2_072407Z` 目录字节未动。
- 语义判断（§5.2 的"扩展"判定）由本审计者做出，非程序判定；`quote in text` 只证明可见性，不证明蕴含。
- 6 题均为开发题，不构成泛化结论。
- 未执行任何真实模型调用、Search 或 Open（§0 表）。
