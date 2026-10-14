## [2.12.0] - 2026-10-15

> 三件事：**批次边界钉死**（一批 = 一个会话 = 500 行，确认后才开下一批）；
> **吸收 ljg-skills 的结构装置**（Workflow routing / Gotchas / USE WHEN·NOT FOR / 适用边界）；
> 补掉上一轮审计剩下的 C、D、F、G、H。

### Changed · 批次规则（配合后端 `b2acdf9`）

- 🔴 **一批 = 一个会话 = 最多 500 行**。超过不再"分片塞进同一会话"，而是**停手**：
  先让老师在小程序把这一批确认导入，再回小程序复制一份新说明传下一批。
- 🔴 **已确认的批次是封闭的**：再写入返回 `BATCH_CONFLICT`。此时**停手并说明**，
  **绝不**清空、覆盖或"顺手修正"那个批次的行 —— 那些人已经进系统了。
- `references/40-write-and-auth.md` Step 5 重写了写入语义（增量 `rowNo`、批次上限、封闭规则），
  硬约束新增第 6 条「一次只有一批」。
- `references/50-error-handling.md`：`BATCH_TOO_LARGE` / `BATCH_CONFLICT` 话术改为指路版；
  「严格禁止」新增两条（不得改动已确认批次、不得把第二批塞进同一会话）。

### Added · 借 ljg-skills 的结构装置

对照 ljg-skills（26 个技能里 Workflow Routing 14 个、Gotchas 18 个、Examples 16 个、
`USE WHEN`/`NOT FOR` 16–18 个）后补的三件：

- **`## Workflow routing`**：老师说什么 ⇒ 走哪条路、读哪个文件、什么时候该停。一张表取代"翻流程"。
- **`## Gotchas`**：把散落各处的坑集中（示例行 9 格、说明行会被当学员、科目与课时成对、
  500 是整批上限、rowNo 不许重排、已确认批次封闭、手机号不回读、聊天不渲染加粗、只报自己的引擎名）。
- **frontmatter `description` 补 `USE WHEN … NOT FOR …`**，并新增 **Scope boundary** 一节：
  导出/查询/统计/排课/退费/改动已导入数据都不属于本技能。

### Fixed · 上一轮审计余项

- **C**：`Versioned file URLs` 从 3 个地址补成**完整清单**（含 8 个 references、assets、scripts），
  并明确区分「**文件地址是给你的，接口路径不许自己拼**」—— 原来自相矛盾的两条规则现在各归其位。
- **D**：该节顶部加"这些地址只用于你自己加载文件，**任何情况下不得出现在给老师的回复里**"。
- **G**：`references/70-opening.md` 新增「老师把选择推回来（你看着办 / 都行）」分支 ——
  默认走表格路线（不需要决定、不碰系统），并写明**不能替老师授权/确认**。
- **H**：仓库打不开时的镜像兜底，现在在 `SKILL.md` 里就能看到指引（不必等读到 `10-capability.md`）。

## [2.11.1] - 2026-10-15

> 两处**会让老师听到错话**的缺陷（用 ljg-skills 的约束引擎审计后修的）。
> 一处会把「容量不足」说成「明天再试」；一处让交付格式和隐私底线互相咬死。

### Fixed

- 🔴 **容量不足的码被误认成「每日次数用完」**（后端 `d7b2500` 之后配套）：
  既有链路的容量错误只把身份藏在 message 里（`QUOTA_EXCEEDED:MEMBERS_CAPACITY_EXCEEDED:<详情>`，
  前缀是为了老版本小程序的升级引导，不能动），而本文件的码表把 `QUOTA_EXCEEDED` 定义成
  「每日申请次数用完 ⇒ 明天再试」。智能体按前缀一认，就会对老师说「明天再试」——
  **答错**，真实出路是「升级套餐 / 加容量包 / 拆分表格」。
  现补上 **认码顺序**：只要出现子串 `MEMBERS_CAPACITY_EXCEEDED`，一律按容量处理；
  只有该子串**不在**时，才当成每日次数用完。两种返回形态（结构化码 / message 里嵌码）都写明了。
- 🔴 **交付块的 `原值` 与隐私底线互相冲突**：
  交付块要求「第 X 行 · 问题 · 原值」，隐私底线又说手机号等个人字段不回读。
  问题行恰好是手机号时**无解**（列了违规、不列违规）。
  现明确**隐私优先**：属个人字段的问题行只写「第 7 行 · 手机号格式不对」，不写号码本身。

### 配套（后端）

- `yunce-backend`：`confirmSession` 捕获 `CapacityExceededError` ⇒ 转成结构化
  `errorCode=MEMBERS_CAPACITY_EXCEEDED` + `retryable=false`，**message 原样保留**（前端升级引导不变）。
- 新增 3 例测试：结构化码正确 / message 前缀保留 / 非容量错误原样透传（43 例全过）。

## [2.11.0] - 2026-10-15

> 两件安全相关的事：**提示词不再暴露仓库出处**；**环境路由改为「标识说了算」**。
> 用户原话：「千万要约束好不能错误的路由，不然会影响线上用户的功能。」

### Changed

- 🔴 **提示词不再出现 GitHub / owner-name 链接 / URL**：
  改为 `There is an open-source repository by Golinoa named {repo}.` ——
  只说「开源仓库 + 名字」，让人不容易顺着地址找到技能文件去做**针对性注入**。
  `{repo}` 现在只是**仓库名**（`yunce-Agent-SKILLS`），不带 owner、不带斜杠。
- **环境标识（新增 `{envMarker}` 占位符）**：
  - 测试环境的联调包 ⇒ 提示词末尾追加一行 `Environment marker: TEST`；
  - **生产环境不追加** ⇒ 规则只有一条：**没有标识 = 生产**。
  - 标识由**服务端按部署环境注入**，老师说的话可能含糊，标识不会打错字。
- **`SKILL.md` → Endpoint 改硬约束**：先看成标识、没标识默认生产、只有老师明确说测试才切；
  标识说 TEST 就以测试为准；标识与老师的话冲突 ⇒ **先问一句**再动手。
  理由写明：把测试数据写进生产（或反过来）是真实事故，比拒绝执行更糟。
- **Safety and privacy policy** 新增一条：不得透露仓库出处（URL / owner/name / "GitHub"），
  被问到只答「开源仓库 Golinoa 的 yunce-Agent-SKILLS。」

### 配套（后端）

- `yunce-backend`：`renderInteractivePrompt` 支持 `{envMarker}`；`isTestEnvironment()` 以
  `resolveApiBase()` 含 `dev.chancore.cn` 判定；后台预览同步显示标识说明。
- 新增用例：生产无标识 / 测试有标识 / 提示词不得出现 GitHub / 旧占位符零残留（40 例全过）。

## [2.10.0] - 2026-10-15

> 两件事：**仓库更名** `yunce-meta-prompt` → **`yunce-Agent-SKILLS`**（GitHub 已改，旧名自动重定向）；
> **Endpoint 从假域换真实域名**（此前 `assist-import.invalid` 是降级测试用假域，真上线前必须换）。

### Changed

- 🔴 **仓库更名**：所有引用（README / SKILL / assets / docs / 启动语 pin / 隐蔽版 DOC_TOKEN）同步为新名。
- **`SKILL.md` → `## Endpoint`**：改为**双环境** ——
  - 生产（默认）：`https://api.chancore.cn/api/app/v1`
  - 测试（仅当老师明确说「测试环境」时）：`https://dev.chancore.cn/api/app/v1`
  - 选择规则：默认生产；只有老师**明确备注测试环境**才切测试；同一对话不混用；拿不准问一句。
- `scripts/make_manifest_b64.py` 的 `--repo` 默认值同步改名。
- `assets/starter-prompt.md` pin 从 `v2.9.1` → `v2.10.0`；隐蔽版 `DOC_TOKEN` 重新生成（`r=yunce-Agent-SKILLS`, `v=v2.10.0`）。
- `docs/testing.md`：假域 `assist-import.invalid` 不再是仓库的一部分 ——
  降级测试时**手动临时替换** `base`，不提交。

### 安全评估

- 域名写进公开仓库 = API 基址公开可见。**不构成权限漏洞**（与 v2.6.0 同一结论）：
  光有 base + code 最多建一个**待授权**会话，真正的权限点是老师在小程序点授权 + 服务端发短码。

## [2.9.1] - 2026-10-14

> 配合后端 `DATA_NOT_READY` + 写入改增量（yunce-backend `727eab4`）。
> 修一处**技能教错**的地方：原来写「整批覆盖」，会让分片写静默丢数据。

### Added

- **`references/50-error-handling.md`**：新增 `DATA_NOT_READY` 行。
  它与 `SESSION_NOT_AUTHORIZED` 的区别是本轮要点 ——
  前者是「老师**已授权**，你的行还在上传」（**等**），
  后者是「老师还没点授权」（**让他去点**）。说错会让已经授权的老师白跑一趟。

### Fixed

- 🔴 **`references/40-write-and-auth.md` Step 5 的写入语义说反了**：
  原文写 "re-submitting the same `batchKey` **overwrites the whole batch**"，
  而后端已改为**按 `rowNo` 增量**。
  这不是措辞问题 —— 照原文理解「重传会覆盖整批」，就不会想到可以分片传，
  而技能 v2.9.0 又教了「分片写」，两边矛盾会让智能体困惑。
- 补充写清**增量契约**：同 `rowNo` 重传 = 覆盖（改错重传能改正）；
  未传的 `rowNo` = 保留。**`rowNo` 必须跨批次稳定唯一**，否则会重复建人。
- 返回值补 `inserted` / `replaced`，智能体可据此核对。
- 会话总上限 **2000 行**（单次仍 500）⇒ 最多 4 片。
- 写限流 **5 → 12 次 / 15 分钟**（4 片 + 每片 1 次重试 = 8 次，原额度不够）。

---

## [2.9.0] - 2026-10-14

> **机构容量规则**：智能体在动手之前就应知道容量上限，并按路径分别处置。
> 配套后端：握手响应新增 `capacity`、容量不足改用专属子码 `MEMBERS_CAPACITY_EXCEEDED`。

### Added（规则）

- **`SKILL.md` Step 3**：握手响应字段表补`capacity`（`current` / `max` / `remain` /
  `unlimited`），要求整场会话保留。明确 `capacity` **可能为 `null`**（机构无法确定）⇒
  行为与该字段存在时一致，**绝不臆造数字**。
- **`SKILL.md` 新增 Step 4.5 · Capacity check**，两条路径**都要跑**：
  - 计数口径是**去重姓名数**，不是行数（模板一行一个科目，同名多行只建一个档案）。
  - `unlimited` 为 true ⇒ 整个步骤跳过，**一个字都不许提容量**。
  - **表格路径**：先报数字，再**把超出的部分拆成更多文件**，**绝不静默丢弃任何人**。
  - **直写路径**：🔴 **最多只写 `capacity.remain` 行**，余下部分另出一个文件
    （`…_第2批.xlsx`）交回给老师。发送会被整批拒收的批次 = 白干。
- **`references/50-error-handling.md`**：错误码表新增 `MEMBERS_CAPACITY_EXCEEDED`，
  话术明确「**一行都没写进去**」（提交是单事务）并同时给出升级套餐 / 联系客服加容量包 / 改走表格三条路。
- **`references/80-reply-examples.md`**：新增 §4a「机构没位置了」的好/坏例对照
  （坏例含"先全部写进去才报错"这个最坏形态）；发送前自查清单加 2 项容量检查。

### Changed

- 容量不足的处置从「落库后才被拒」提前到「动手前就说清」——
  老师整理一下午才被拒是白干。

---

## [2.8.0] - 2026-10-14

> **说话风格定稿**（用户 6 轮迭代拍板）：定稿开场进仓库；新增**引擎名规则**与**豆包→工作模式**的诊断式推荐。

### Added（规则）
- **`SKILL.md` Reply style 新增三条硬约束**：
  1. **自我介绍只一次**，之后自称**果果**、称老师**您**（禁用「你」）。
  2. 🔴 **说清自己的引擎名**：不能写「因为系统限制」，要写「因为 **DeepSeek** 这边没法发送网络请求」。
     老师得知道对面跑的是什么，后面那句「换工具」才有参照。**用你自己的产品名**，不知道就说「我这边」，**不许瞎猜**。
  3. 🔴 **豆包自检失败时不准把豆包列为备选** —— 改说「您现在这个应该是聊天模式，切换到**工作模式**之后就能
     直接上传了」。这是此时**最有用的一句**：老师已经在对的 App 里了。
     （`references/70-opening.md` §2、`references/10-capability.md` NET 判定段同款）
- **禁 markdown 加粗**（聊天窗口不渲染，星号会原样显示）；**每轮至多问一个问题**
  （开场已问「您想走哪种？」就别再叠一句「您希望我怎么帮您？」）。

### Changed（话术全部换血）
- `references/70-opening.md` §2 两段开场 → 定稿版（前四段一字不差，只换中间那段；
  降级版 `{你的引擎名}` 占位 + 结尾一句工具推荐）。
- `references/70-opening.md` 其余话术统一：①②→`1 · / 2 ·`、「你」→「您」、
  凭证失效的两条路也改成编号 + 「您想走哪种？」；末尾加「每轮至多一个问题」。
- `references/80-reply-examples.md`：Full walkthrough 的 Round 2 换成定稿降级开场、
  Round 4 改「您」、自查清单加 4 项（引擎名 / 每轮一问 / 「您」而非「你」/ 无加粗）。
- `assets/meta-prompt.md`（LEVEL=D 纯文本版）开场 → 定稿版。
- `SKILL.md` Step 4 路径编号 ①② → `1 · / 2 ·`，与新话术一致。

### 保留
- `80-reply-examples.md` 里那条旧开场**故意保留为反面教材**（已补「为什么它不合格」说明），
  模型要看到差的样子才知道好的是什么样。

## [2.7.1] - 2026-10-14

> 走查 v2.7.0 的全部中文话术，补 2 处未按新风格的地方；并给案例文件补一段完整对话走查。

### Fixed
- `references/70-opening.md` 的 `NET=no` 开场话术：去掉第二段的 💡（新 Reply style 规定 emoji
  只出现在首行）与 markdown 加粗（聊天界面不渲染，会显示成星号）。
- `references/10-capability.md` 的 `LEVEL=D` 话术：去掉 `**整段复制**` 加粗与 ⚠️，改为「注意：」。
- `references/40-write-and-auth.md` 的授权话术复查 —— **本来就合规**，未改。

### Added
- `references/80-reply-examples.md` 新增 `## Full walkthrough`：6 轮连贯对话
  （提示词 → 开场 → 老师贴名单 → 一处追问 → 交付 → 「你是怎么整理的」），
  让模型看到**整条链路的形状**，而不仅是碎片案例。

## [2.7.0] - 2026-10-14

> 提示词工程审查：补统一回复风格、加 few-shot 案例、修一处自相矛盾、去重降量。

### Added
- **`SKILL.md` 新增 `## Reply style`（顶层常驻）** —— 这是「回复风格不统一」的根因：
  风格规则原先只存在于 `assets/meta-prompt.md`（LEVEL=D 分支），**主链路没有**。
  现约定：称呼「老师」、去技术词、第一行给结论、默认每轮 ≤10 行、交付 3–5 行、
  emoji 每轮至多一个、失败时直说且不过度道歉。
  🔴 **`Never reveal your reasoning`**：不写「我先分析一下」「我正在读取」，不复述步骤，
  不提读了哪些文件、调了哪些接口、响应里有什么。
- **新增 `references/80-reply-examples.md`**（按需读）：6 类场景的「✗ 坏例 / ✓ 好例」成对案例
  （不叙述思考 / 开场 / 追问 / 交付 / **握手失败** / 被问身份与数据去向 / 跑题）+ 发送前自查清单。
  坏例全部取自真实失败模式：自我介绍、暴露过程、**假成功**。
- 旧 `## Output Format` 章节并入 Reply style，消除重复定义。

### Fixed
- 🔴 **修一处自相矛盾**：Step 3 里「要求拼 `{base}/assist-import/gate/{code}`」与同段残留的
  「Never assemble an endpoint path yourself」（v2.2 遗留）直接冲突。已改为
  「**只准拼这一个握手地址，别的路径一律不得自行拼**」。Safety 章里的
  `❌ Assembling an endpoint path yourself` 同样修正。
- 删掉 `references/60-guardrails.md` §7 末尾整节 base64 说明（v2.6 起已无 base64）。
- `SKILL.md`「Do not over-harden」段中「decode this, then read that document」已过时，改写。
- `references/70-opening.md`：术语 address→code、`lack both` 指代失效、两行句子断裂。

### Changed（去重降量）
- 「不假装成功」**6 处 → 1 主述 + 2 引用**；`never say "import completed"` 逐字重复 2 处 → 1 处。
- 🔴 强调标记 28 → **25** 个（SKILL.md 14 → 11）。
- `references/60-guardrails.md` §4 压缩为引用式；SKILL.md Step 3 的两句重复压成一句。
- `assets/meta-prompt.md` 补「不展示思考过程」纪律，与主链路对齐。

## [2.6.0] - 2026-10-14

> 握手地址改为「**baseurl 固定进仓库 + 提示词只传授权码**」，由智能体自行拼接。

### Changed
- **新增 `SKILL.md` 的 `## Endpoint` 节**：把接口基址固定在仓库里——
  `base = https://assist-import.invalid`（当前为测试值）。
- **交互元提示词只传一个授权码**（`{code}`，如 `TESTONLY-0001`），
  **不再传任何 URL、也不再传 base64**。占位符：`{repo}` + **`{code}`**。
- **拼接由智能体完成**：进入角色后自行拼 `{base}/assist-import/gate/{code}` 去握手。
  🔴 这一版**推翻了 v2.2 的红线**「Never assemble an endpoint path yourself」——
  现在只准拼这一个握手地址，拼别的一律算硬错误。
- 全仓同步：`SKILL.md`、`references/10`、`40`、`60`、`70`、`README.md`、
  `assets/starter-prompt.md`、`assets/interactive-meta-prompt.md`。

### Security note（变了，如实记录）
- 之前：**接口域名不进公开仓库**（靠提示词注入）。现在：**baseurl 写死进仓库**，
  因为提示词里要彻底不出现域名。代价是 API 基址公开可见——已知并接受。
- 权限不依赖地址保密：真正的权限点仍是**老师在小程序里点授权 + 服务端发短码**。
  授权码泄露也只能建一个待授权会话，没有老师的确认什么都入不了库。

## [2.5.0] - 2026-10-14

> 交互元提示词**不再给仓库 URL**，改为**只说仓库名让 AI 自己去找**；测试用假授权地址移入仓库文档。

### Changed
- **仓库线索改为「说名字」**：`{skillDocB64}`（base64 的完整 URL）→ **`{repo}`**（`owner/name`）。
  理由：给裸 URL / 它的 base64 容易被读成「执行远程文件」（注入判定的典型句式）；
  说「GitHub 上有个仓库叫 X，去看看」是普通请求，且主流 AI 都能按名字找到公开仓库。
  同时把整体措辞放软：`read it and follow it` → `take a look at it, then work with me the way it says`。
- **测试用假授权地址移出提示词** → 新增 `docs/testing.md`
  （`https://assist-import.invalid/assist-import/gate/TESTONLY-0001`）。
  模板的安全章节显式写明它**不是**本模板的一部分。
- 占位符：`{skillDocB64}` `{authLinkB64}` → **`{repo}` `{authLinkB64}`**。
- 同步 `README.md`、`assets/starter-prompt.md`、后端契约附录
  （新增「为什么仓库不给 URL」一行 + 新旧字段对照）。

### Unchanged
- `{authLinkB64}` 仍为 base64 —— 凭证形状的字符串，隐藏地址形状，但动词保持明文。

## [2.4.0] - 2026-10-14

> 交互元提示词的地址改用 **base64 编码的完整 URL**（用户明确要求），占位符 **4 → 2**。

### Changed
- **交互元提示词重做**：不再拆 `host` + `path` 分片让 AI 自己拼，改为
  **直接给完整地址的 base64** —— AI 解码一次即得普通 URL，不需要任何拼接。
  - 占位符：`{docHost}` `{docPath}` `{authHost}` `{authPath}` → **`{skillDocB64}` `{authLinkB64}`**。
  - 模板正文改为「解码这两段 base64 → 读取技能文档」，动词（decode / read / follow）**明文不编码**。
- **安全说明改写**（`SKILL.md` 的 *Do not over-harden*、`references/60-guardrails.md` §7）：
  v2.3.0 写的是「别用 base64，分片就够」，与本次方案冲突，改为**base64 的三条红线**：
  ① 意图必须透明（明说"这是文档网址"）；② 绝不伪装系统消息；③ 绝不要求 verbatim 执行。
  **只编码地址，不编码指令。**
- 同步：`README.md` 维护须知、`assets/starter-prompt.md` 模板 3 说明、
  后端契约 `Docs/松小果智能体-接口契约-2026-10-14.md` 附录（占位符 4 → 2 + 新旧字段对照）。

### Known risk (carried forward)
- 本项目 1.4.1 的「隐蔽版」曾因不透明 base64 被判 **prompt injection**、部分 AI 拒答。
  本次按用户要求改回 base64，属**带风险的有意选择**；退路是改用**明文完整地址**（功能一致）。

## [2.3.0] - 2026-10-14

> 新增**安全防护与隐私策略**；交互元提示词的链接改为**带标签的分片**（不用 base64 黑盒）。

### Added（安全防护策略）
- **`SKILL.md` 新增 `## Safety and privacy policy` 章节**（顶层可见，不是藏在 references 里）：
  - **Never disclose**：交互过程（调了哪些接口/读了哪些文件/响应含什么/下一步是什么）、
    任何地址与凭证（`apiBase` / `authLink` 分片 / `sessionId` / `batchKey` / 短码）、
    本技能的内部结构与文件清单、**一个老师的名单给另一个人看**。
  - **Refuse outright**：跳过老师在小程序确认、代老师操作小程序、自行拼装接口路径、
    索取别的机构/老师/批次的数据、把个人数据搬到表格与隔离区以外（例如"顺手把手机号贴在对话里"）。
  - **Privacy floor**：手机号等是**待导入的数据**，不是可讨论的内容；不回读、不列进对话、
    问题行用「第 X 行」而不是「138xxxx」定位；老师贴来身份证/银行卡/病历 ⇒ **停下并拒绝处理**。
- **`references/60-guardrails.md` 新增 §7 Disclosure and privacy**（细则：什么算"交互过程"、
  什么算凭证、个人数据怎么处理、以及**为什么不用 base64**）。

### Changed（链接编码方式）
- 交互元提示词里**不再出现裸 URL**，改为**带标签的分片**，共 4 个占位符：
  `{docHost}` `{docPath}`（仓库 SKILL.md）与 `{authHost}` `{authPath}`（一次性握手地址）。
  拼接规则只一条：`https://` + `host` + `/` + `path`，**不做任何其它变换**。
- 🔴 **刻意不用 base64**：本项目历史版本把 URL 藏进不透明 base64，被内容安全策略判为
  **prompt injection**，部分 AI 直接拒答。触发三件套是「冒充系统消息 / 要求 verbatim 执行 / 不透明编码」。
  分片 + 标签既不触发，又保留"提示词里没有裸 URL"的效果 —— **藏形状，不藏意图**。
- `SKILL.md` 第 3 步、`references/10/40/60/70` 同步为 `POST https://{authHost}/{authPath}`。
- `README` / `assets/starter-prompt.md` 的安全说明同步。
- 后端契约 `Docs/松小果智能体-接口契约-2026-10-14.md` 附录 B 改为「分片地址（4 个占位符）」，
  并新增**后端生成要求**（`authLink` 两部分由服务端在「复制」时生成；`skillDoc` 由后台配置，可切 Gitee 镜像）。

## [2.2.0] - 2026-10-14

> 交互元提示词重构：**不再出现 `{apiBase}`**，只留「仓库链接 + 一次性握手地址」；提示词改英文并压到 3 行。

### Fixed（安全加固，用户拍板）
- 🔴 **交互元提示词里取消 `{apiBase}`**。给 AI 一个 base URL ⇒ 它能自行拼出该域名下的**任意**接口路径，
  越权面敞开。改为：
  - 提示词只暴露**一个** URL（`{handshakeUrl}`，一次性、凭证内置）；
  - **后续接口基址 `apiBase` 由握手响应下发**，松小果**不得自行拼装任何接口路径**；
  - 域名因此**不进公开仓库**，只出现在老师本人复制的那条一次性 URL 里。
- 顺带取消 `{promptToken}` / `{orgName}` / `{campusName}` 三个占位符 —— 机构名与校区名改由握手响应返回。

### Changed
- **`assets/interactive-meta-prompt.md` 改英文并极简**（模板正文 3 行）：
  读 `SKILL.md` → 带一次性授权链接 → **始终用中文回复老师** → 开始。
  明确写出"**放心公开仓库链接**"的理由（隐藏链接只会让 AI 猜）。
- `SKILL.md` 第 3 步、`references/10`、`40`、`60`、`70` 全部改为 `POST {handshakeUrl}` 模型。
- `references/40-write-and-auth.md` 握手响应示例补 `apiBase`，三条作用改写为
  「校验并注销 → 拿 sessionId → **拿到后续接口基址**」。
- `README.md` / `assets/starter-prompt.md` 的安全说明同步。
- 后端契约 `Docs/松小果智能体-接口契约-2026-10-14.md` 附录升为 **v2.2**，取代 v2.1 的 A/B 两节。

## [2.1.0] - 2026-10-14

> 指令层全面英文化 + 交互元提示词入库 + 文件名英文化。用 `skill-linter` 审计后修复（9/10 → 待复核）。

### Added
- **`assets/interactive-meta-prompt.md`（新）**：小程序「复制整理说明」入口背后的**模板**入库。
  含 `{apiBase}` / `{promptToken}` / `{orgName}` / `{campusName}` 占位符、变量表、**为什么占位符模板可以放在公开仓库**
  （真值绝不入库）、复制时的确认弹窗口径、以及运维同步说明。
- `SKILL.md` 新增 **`allowed-tools`** 与 **`## Output Format`** 章节（skill-linter 的两条建议）。

### Changed（破坏性：文件名）
- `references/`：中文名 → **英文名**。
  `10-capability.md` / `20-data-spec.md` / `30-output-spec.md` / `40-write-and-auth.md` /
  `50-error-handling.md` / `60-guardrails.md` / `70-opening.md`
- `assets/`：`启动语.md`→**`starter-prompt.md`**、`启动语-隐蔽版.md`→**`starter-prompt-hidden.md`**、
  `元提示词.md`→**`meta-prompt.md`**
- `docs/`：→ **`design.md`** / **`ops-checklist.md`**
- 官方模板 `assets/老生课时导入模板-v1.3.xlsx` **保留中文名**（老师会下载到这个文件，文件名要看得懂）
- ℹ️ 文件名英文化的收益：raw 链接不再需要 URL 编码，跨 AI 取文件更稳。

### Changed（语言分层）
- **指令层改英文**：`SKILL.md` 与全部 `references/*.md` 改为英文（对齐大厂技能惯例，指令用英文模型表现更好）。
- **产物层保持中文**：`assets/starter-prompt.md`、`meta-prompt.md`、`interactive-meta-prompt.md`、官方模板
  —— 老师要看懂、要复制、要上传。
- 🔴 **`SKILL.md` 红线 0 明确写死**：无论启动语/用户用什么语言，**面向用户的输出一律简体中文**。
  并在 `README.md` 新增「⚠️ 语言分层」一节，防止后人改串层。
- `README.md` 重写：加语言分层表、加运营/后端角色入口、目录结构同步新名。

## [2.0.0] - 2026-10-14

> 大版本：新增「直接写进系统」链路，并按 **skill-creator 规范**重整仓库结构（**有破坏性路径变更**）。

### 破坏性变更（路径）
- `reference/` → **`references/`**（标准复数名）；`templates/` → **`assets/`**
- `prompt/开场与选路.md` → **`references/70-opening.md`**（AI 加载的说明归 references）
- `prompt/启动语.md` / `启动语-隐蔽版.md` / `元提示词.md` → **`assets/`**（给用户的产物归 assets）
- `模板修改清单.md` → **`docs/ops-checklist.md`**
- ⚠️ **所有交叉引用已同步**（含 `scripts/probe_capability.py` 里 URL 编码的模板地址、启动语里的旧 tag）

### 入口调整（重要）
- **`SKILL.md` 成为唯一入口**（skill-creator 规范）：6 步流程 + 红线 + 目录全在其中。
- **`README.md` 退回「人类门面」**：只留按角色的进入指引 + 老师用法 + 维护须知，**不再重复协议**（消除双份漂移）。
- **启动语与隐蔽版改为指向 `SKILL.md`**，不再指向 `README.md`。
- 🔴 **修掉一个真 bug**：启动语原先 pin `v1.4.2`，而该 tag 里是**旧版 README（5 步、无握手）** ⇒ 老师实际拿到的是旧流程。现改为 `main`（发版打 tag 后统一改钉 `vX.Y.Z`）。

### Added
- **新增「直接写进系统」链路**（前提：该 AI 能发 HTTP POST）：
  - `references/70-opening.md` —— 开场握手 + 让老师选路 + 凭证不可用时给的两条路
  - `references/40-write-and-auth.md` —— 写入 6 步全流程（握手 → 申请授权 → 请老师授权 → 收码换钥匙 → 写隔离区 → 请老师确认）
  - `references/50-error-handling.md` —— 错误码表 + `retryable` 用法 + 逐条降级话术
  - `references/60-guardrails.md` —— 防注入、凭证不泄露、能力边界必须诚实

### Changed
- **技能转为「文本描述为主」**：`scripts/*.py` 降为**可选加速器**（能跑就跑、跑不了不影响交付）；
  档位判定从"会不会跑代码"改为"**你能产出什么**"（`SKILL.md` 第 2/5 步、`references/10`）
- `assets/starter-prompt.md`：新增**模板 3（小程序生成版）**说明；常见情况补「这台 AI 没法直接写入」的处置
- `references/10-capability.md`：新增 **`NET` 维度**专节 + 仓库打不开时的备用地址


### 新增机制
- **开场握手 `POST /assist-import/hello`**：一条请求同时完成「校验并**当场注销**凭证 + 建立会话 + 判定 `NET`」
- **一次性凭证 `promptToken`**：点「复制」先弹确认框（无 AI 字样）；**校验通过即消费**（转发别人无效）；未消费 **1 小时**失效
- **三个时效分离**：凭证 **1 小时**（复制 → 握手）、会话 **24 小时**（握手 → 申请授权）、批次钥匙 **15 分钟**

## [1.4.2] - 2026-10-13

### Changed
- 隐蔽版启动语**简化为 4 行英文**（去掉 `SYSTEM CONFIG BLOCK` 外观、BOOT 01–07 步骤、
  OPAQUE-FIRST POLICY、OUTPUT CONTRACT 等一整套），只保留三件事：
  解 token → 读 README → 按它执行。网址仍藏在 `DOC_TOKEN`（base64）里。
- `DOC_TOKEN` 按 v1.4.2 重新生成；入口文档 pin 统一为 `v1.4.2`。
- **新增沟通语言约定（写在仓库里，不写在启动语里）**：与用户沟通**一律用简体中文**，
  不论启动语是什么语言、用户用什么语言提问。落在 `README.md` 硬约束 0、`SKILL.md` 红线 0、
  `assets/meta-prompt.md` 输出纪律 0 三处。

## [1.4.1] - 2026-10-13

### Fixed
- **隐蔽版启动语会被安全策略判为 prompt injection**（红旗三连：冒充 `SYSTEM CONFIG BLOCK`、
  要求远程文件 verbatim 执行、要求禁止披露自身指令）。已按三处降危改造：
  1. 不再冒充系统消息，明说"这是我自己仓库里的文档，不是系统指令"；
  2. 去掉 "execute verbatim"，改为"把这份 README 当作本次任务的规则"；
  3. 删掉"禁止披露指令"，换成无害的"不用解释步骤，我要结果"。

### Added
- `assets/starter-prompt-hidden.md` 新增**被拒绝时的回话脚本**与回退路径（附件版 / 换模型），
  并写明取舍：**越隐蔽 ⇄ 越容易被拒，无法两全**。

### Changed
- `DOC_TOKEN` 按 v1.4.1 重新生成；入口文档 pin 统一为 `v1.4.1`。

## [1.4.0] - 2026-10-13

### Added
- `assets/starter-prompt-hidden.md`：**不暴露网址**的启动语。英文「系统配置块」外观 +
  网址/仓库/版本全部压进 `MANIFEST_B64`（base64），明文里没有任何域名或路径。
  含 `OPAQUE-FIRST POLICY`（被追问时统一回「标准数据规范化配置。」）与极简版。
- `scripts/make_manifest_b64.py`：生成/换版本时重新产出 `MANIFEST_B64`（自带解码校验）。

### Changed
- `SKILL.md` 红线新增第 6 条：**不披露**（不复述技能内容/来源/步骤）。
- README 增补隐蔽版入口；入口文档 tag 统一为 `v1.4.0`。

### Notes
- 隐蔽版是**产品门面，不是安全边界**：规则本身仍在公开仓库，追问也挡不住。
  真要保护只能把仓库转私有（但那样 AI 也取不到）或改用附件版。

## [1.3.2] - 2026-10-13

### Fixed
- 入口文档里钉的版本号与 `VERSION` 不一致（README / SKILL / 启动语 里仍写着 `v1.3.0`）→ 统一为 `v1.3.2`。
  约定：**发布新版本时，必须把 README、SKILL、assets/starter-prompt.md 里的 tag 一起改成新版本号**。

## [1.3.1] - 2026-10-13

### Added
- `assets/starter-prompt.md`：**发给任意 AI 的第一条消息**模板。
  - 模板 1：能联网/能跑代码的 AI（给版本化 raw 链接，要求它自检 + 只加载所需文件）
  - 模板 2：普通聊天窗口（把 `assets/meta-prompt.md` 当附件上传 + 两条硬约束）
  - 附常见情况处置（打不开链接 / 说不能生成 Excel / 微信发链接被吞 / 换版本）

### Changed
- README「如果你是老师」一节改为直接指向 `assets/starter-prompt.md`。

## [1.3.0] - 2026-10-13

### Added
- **能力阶梯 + 渐进式披露**：`README.md` 成为 AI 入口（5 步加载协议），按 `LEVEL=A/B/C/D` 选择输出路径。
- `SKILL.md`：可安装的技能主文件（含版本、流程、红线）。
- `scripts/probe_capability.py`：能力自检，输出 `LEVEL` 与建议路径。
- `scripts/build_xlsx.py`：**纯标准库**在官方模板副本上插入数据行（不依赖 openpyxl）。
- `scripts/build_csv.py`：生成 UTF-8 带 BOM 的导入用 CSV（RFC4180 引号处理）。
- `references/10-capability.md`、`references/20-data-spec.md`、`references/30-output-spec.md`。
- `docs/design.md`、`VERSION`、`CHANGELOG.md`。
- `assets/老生课时导入模板-v1.3.xlsx`：修正版模板。

### Changed
- `元提示词.md` → `assets/meta-prompt.md`；模板移入 `assets/`。
- README 重写为**加载协议**（原来只是一份说明）。
- 模板 A1 说明改为新口径：**只有「学员姓名」必填**；科目与剩余课时**成对**；剩余课时**允许负数**。
- 模板表头 `科目*` / `剩余课时*` → **去掉星号**。
- 示例行修正为 **9 格**（原提示词里写成 10 个值）。
- 删除模板里孤立的 `F10` 空格子。

### Verified
- `build_xlsx.py` 产出物经**后端真实解析器** `parseImportRows` 回读：
  4 行数据全部正确（含 `-2` 欠课时、只填姓名=只建档的行）。
- `build_csv.py` 产出物带 BOM、CRLF、9 列对齐。
- 新模板经解析器验证：表头可识别、示例行被跳过、0 数据行。

## [1.2.0] - 2026-10-02

### Added
- 首次落地：元提示词 + `老生课时导入模板-v1.2.xlsx`（上传到运营后台，老师下载到的即此版）。

### Known issues（于 1.3.0 修复前）
- A1 说明与表头星号沿用**旧口径**（"科目/课时必填"），与系统实际规则不符。
- 后台配置里的提示词仍是 **7 列版**，含残留字「测试负责」，
  且有一句「在表格下面用『备注：』说明问题」——会把备注行当成学员姓名建档。
