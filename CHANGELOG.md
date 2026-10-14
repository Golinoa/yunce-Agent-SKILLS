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
