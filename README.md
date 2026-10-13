# 松果排课 · 学员导入智能体（远程技能仓）

把杂乱的学员信息（名单 / 聊天记录 / 旧表）整理成**可直接导入「云策教务」系统**的表格，
或（AI 支持发请求时）**直接送进系统的临时区**等老师确认。

> 当前版本：以 [`VERSION`](VERSION) 为准 ｜ 变更见 [`CHANGELOG.md`](CHANGELOG.md)
> 支持的导入格式：**`.xlsx` / `.csv` / `.txt`**（教务系统三种都认）
> 远端仓库：https://github.com/Golinoa/yunce-meta-prompt

---

## ⚠️ 语言分层（先看清这条，别改错）

| 层 | 语言 | 文件 | 为什么 |
|---|---|---|---|
| **指令层**（AI 读） | **English** | `SKILL.md`、`references/*.md` | 对齐大厂技能惯例；指令用英文，模型命中率与 token 效率更好 |
| **产物层**（人读） | **中文** | `assets/starter-prompt.md`、`assets/meta-prompt.md`、`assets/interactive-meta-prompt.md`、官方模板 | 老师要看懂、要复制、要上传 |
| **维护层** | 中文 | `README.md`、`docs/*.md` | 团队与运营日常使用 |

🔴 **改的时候别串层**：`SKILL.md` 的英文指令**永远不能**让智能体用英文回老师。
`SKILL.md` 红线 0 已硬性规定：**面向用户的输出一律简体中文**。

---

## 按角色进入

| 你是 | 读什么 |
|---|---|
| 🟦 **AI**（被启动语指过来） | **[`SKILL.md`](SKILL.md)** —— 唯一入口，严格按它的 6 步执行 |
| 🟩 **老师**（人） | 复制 [`assets/starter-prompt.md`](assets/starter-prompt.md) 的「模板 1」发给任意 AI |
| 🟨 **运营/后端**（做小程序复制入口） | [`assets/interactive-meta-prompt.md`](assets/interactive-meta-prompt.md) —— 带 `{变量}` 的模板 |
| 🔧 **维护者** | [`docs/design.md`](docs/design.md)（设计）· [`docs/ops-checklist.md`](docs/ops-checklist.md)（线上要同步改什么） |

---

## 老师怎么用（3 步）

1. 复制 [`assets/starter-prompt.md`](assets/starter-prompt.md) 里的「模板 1」，发给任意 AI（豆包 / Kimi / 通义 / ChatGPT …）。
2. AI 会变成「松果排课」智能体，先回一句开场话术；然后把学员信息发过去（或按它提示逐项回答）。
3. 拿到表格后：小程序 →「老生录入」→ 选择文件 → 核对 → 提交。

**常见情况**

| 情况 | 怎么办 |
|---|---|
| AI 说"打不开链接" | 改用模板 2（把 `assets/meta-prompt.md` 当附件上传） |
| 不想让人看出提示词内容 / 看到网址 | 用 [`assets/starter-prompt-hidden.md`](assets/starter-prompt-hidden.md)（英文配置块 + 网址藏进 base64） |
| 想少一步上传（AI 直接送进系统） | 用**小程序里生成**的启动语（它带接口地址与凭证）。实测可用：**豆包（开「工作模式」）**、**Kimi** |
| AI 说"我没法直接写进系统" | **正常**。换上面那两个，或就用表格路线 —— 多一步自己上传而已 |

---

## 目录结构

```
SKILL.md                      唯一入口（英文）：6 步流程 + Output Format + 红线 + 目录
README.md                     本文件（人看）
VERSION / CHANGELOG.md        版本与变更

references/                   AI 按需加载（英文）
  10-capability.md            能力自检 / 四档模式 / NET / 备用地址
  20-data-spec.md             校验与清洗口径（唯一真源）
  30-output-spec.md           xlsx 逐格规格 + CSV/TXT 规格
  40-write-and-auth.md        写入全流程 6 步
  50-error-handling.md        错误码 + 降级话术
  60-guardrails.md            防注入 / 凭证不泄露
  70-opening.md               开场白 + 握手 + 选路

assets/                       给老师的产物（中文）
  starter-prompt.md           发给 AI 的第一条消息（模板 1 / 2 / 3）
  starter-prompt-hidden.md    不暴露网址的英文配置块版
  meta-prompt.md              纯文本版提示词（LEVEL=D / 当附件上传）
  interactive-meta-prompt.md  小程序生成的交互提示词模板（带 {变量}）
  老生课时导入模板-v1.3.xlsx   官方模板（老师下载，故保留中文文件名）

scripts/                      可选加速器（能跑就跑，跑不了不影响交付）
docs/                         设计与运维同步清单
```

---

## 维护者须知

- ⚠️ **本仓库是产物与文案的真源，不会自动同步线上**。线上生效的模板与提示词在运营后台
  `运营 / legacy-import-settings` 维护，需**重新上传/编辑**；对照清单见 [`docs/ops-checklist.md`](docs/ops-checklist.md)。
- ⚠️ **接口域名（`{apiBase}`）与任何凭证都不在本仓库里** —— 它们由小程序在复制时代入。
  **本仓库是公开的。** `assets/interactive-meta-prompt.md` 里只有 `{占位符}`，没有真实值。
- ⚠️ **发版三步**：改 `VERSION` + 在 `CHANGELOG.md` 记一条 + 把 `SKILL.md` /
  `assets/starter-prompt.md` / `assets/starter-prompt-hidden.md` 里钉的 tag 一起改掉，然后打 tag 推送。
- ℹ️ 文件名已全部英文化（除老师会下载的 xlsx）：避免中文路径在 raw 链接里需要 URL 编码。
