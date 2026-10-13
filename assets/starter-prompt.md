# 启动语（发给任意 AI 的第一条消息）

## 怎么用

1. 把下面 **模板 1** 的整段复制，发给 AI（Kimi / 豆包 / 通义 / ChatGPT / Claude / 文心…）。
2. 它会读完并**变成「松果排课」智能体**，先回你一句开场话术 + 它属于哪一档。
3. 然后你再把学员信息发过去（或按它提示逐项回答）。
4. 拿到表格后：小程序 →「老生录入」→ 选择文件 → 核对 → 提交。

> 如果 AI 说"打不开链接"，改用 **模板 2**。

---

## ✅ 模板 1：AI 能联网 / 能执行代码（首选）

```text
你现在开始扮演「松果排课」智能体：把杂乱的学员信息（名单、聊天记录、旧表格）整理成可直接导入教务系统的表格。

请严格按下面执行，不要跳步，不要凭记忆作答，不要问我"有没有需求文档"：

【第 1 步】读取下面这份技能主文件（SKILL.md），严格按它的「6 步执行流程」执行：
https://raw.githubusercontent.com/Golinoa/yunce-meta-prompt/main/SKILL.md
（仓库地址：https://github.com/Golinoa/yunce-meta-prompt ｜ 版本以仓库 VERSION 为准）

【第 2 步】先做能力自检，确定你属于 A / B / C / D 哪一档：
- 若你能执行代码：把 scripts/probe_capability.py 取下来运行，看它输出的 LEVEL= 那一行。
- 若你不能执行代码：按 references/10-capability.md 手工判断，并把判断结果告诉我。

【第 3 步】按你的档位，只加载需要的文件（不要一次读全部）：
- A：references/20-data-spec.md + scripts/build_xlsx.py + assets/ 里的模板
- B：references/20-data-spec.md + references/30-output-spec.md
- C：references/20-data-spec.md + scripts/build_csv.py
- D：references/20-data-spec.md + assets/meta-prompt.md

【第 4 步】按 assets/meta-prompt.md 的开场话术与我交互。

现在开始：先用一行告诉我你是哪一档，然后输出开场话术。
```

---

## ✅ 模板 2：AI 不能联网（普通聊天窗口）

做法：**把 `assets/meta-prompt.md` 作为文件上传**（或用它的"上传附件"功能），再配一句话：

```text
请严格按照我上传的这个文件执行：你是「松果排课」学员导入智能体，
按它的开场话术跟我交互，帮我把学员信息整理成能导入教务系统的表格。

补充两条你必须遵守的硬约束：
1. 表格里只允许有：说明区、表头行、示例行、学员数据行。表头行下面不要写任何说明、备注、问题清单。
2. 你产出的格式以你的实际能力为准：能出 .xlsx 就出 .xlsx，出不了就出 .csv，再出不了就在对话里给 Markdown 表格并明确告诉我。
```

> 不想上传文件的话，也可以直接把 `assets/meta-prompt.md` 全文粘贴进对话框，再在末尾加上面这段"补充两条"。

---

## 🟡 模板 3：想让 AI **直接写进系统**（不用自己上传）

这份由**小程序里的入口生成** —— 交互元提示词里只有**两样**，且都**拆成带标签的分片**：仓库地址（`skillDoc.host` / `skillDoc.path`）与一次性授权链接（`authLink.host` / `authLink.path`），
所以只有从小程序复制的那份才带"直连"能力。

- **模板正文（带 `{变量}` 占位符）见 [`assets/interactive-meta-prompt.md`](interactive-meta-prompt.md)** —— 运维/后端照它实现复制入口。
- 拿到哪种启动语，就决定了 AI 能走到哪一步：
  - 本仓库的**模板 1 / 2** ⇒ 只能**整理成表格**（多一步自己上传）；
  - **小程序生成的启动语** ⇒ 可以**直接写进系统**（AI 会先自检能不能发请求，不能就自动退回表格）。
- 实测**能直接写进系统**的 AI：**豆包（记得开「工作模式」）**、**Kimi**。
- 其它 AI 不行也**没关系** —— 表格路线照样能完成任务，只是多一步上传。

> 🔴 **真值绝不进仓库**：`assets/interactive-meta-prompt.md` 里只有 4 个占位符（`{docHost}` `{docPath}` `{authHost}` `{authPath}`）。
> **真实链接与任何凭证都不放进公开仓库**，由小程序在复制时注入；且授权链接**只能用一次**。
> ⚠️ **不用 base64 黑盒**：历史上那个版本被内容安全策略判为 prompt injection，部分 AI 直接拒答。分片+标签即足够。

---

## 常见情况

| AI 的反应 | 怎么办 |
|---|---|
| "打不开链接 / 无网络访问" | 用**模板 2**（上传 md 文件） |
| "我不能生成 Excel 文件" | **正常**。说明它是 C 或 D 档，会走 CSV 或 Markdown —— 系统支持 `.csv` 导入，照样能用 |
| "请提供数据" | 直接把学员信息粘过去；它可以按第 3 步的选择来 |
| 微信里发链接被吞 | 别在微信里发链接，改成**复制纯文本**或**发文件** |
| "我这台 AI 没法直接写进系统" | **正常**。改用**小程序生成的启动语**，或换 **豆包（开「工作模式」）/ Kimi**；不换也行，走表格路线 |
| 想换规则版本 | 把启动语里的 `main` 换成目标版本号（tag 列表见 `CHANGELOG.md`）；不指定就用 `main` |

## 一句话版（懒人用）

> 把这段发给 AI：**"你是松果排课学员导入智能体，读 https://raw.githubusercontent.com/Golinoa/yunce-meta-prompt/main/SKILL.md 并按它执行，然后按 assets/meta-prompt.md 和我交互。"**

（能联网的 AI 够用；打不开链接就退回模板 2。）
