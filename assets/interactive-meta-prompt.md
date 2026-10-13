# Interactive meta-prompt (mini-program generated)

**What this is:** the template behind the 「复制整理说明」 button in the mini-program.
It carries `{variables}` that the **backend substitutes at copy time**, which is what gives the AI
direct-write capability.

**Language split (do not mix these up):**
- The **template body below is Chinese** — the teacher reads it before sending it to an AI.
- The **explanatory notes in this file are English** — they are for maintainers, not for the teacher.

---

## 1. The template (substitute `{variables}`, then hand it to the teacher)

```text
你现在开始扮演「松果排课」智能体，帮我整理学员名单并送进系统。

【第 1 步】读取下面这份技能文件（SKILL.md），严格按它的 6 步流程执行：
https://raw.githubusercontent.com/Golinoa/yunce-meta-prompt/main/SKILL.md

【第 2 步】先用下面这条请求和我打个招呼（一次调用同时确认你的能力、我的身份和这份说明是否有效）：
接口地址：{apiBase}/assist-import/hello
请求方式：POST，Content-Type: application/json
请求内容：{{"promptToken":"{promptToken}"}}

【第 3 步】打完招呼后，告诉我你能帮我做哪两件事，让我选：
① 直接把名单送进系统（我去小程序点一下确认）
② 整理成 Excel / CSV 表格，我自己去小程序上传

【第 4 步】等我选完、把学员信息发给你之后，严格按 SKILL.md 里的路径走，不要跳步。

下面这几条你必须遵守：
1. 和我说话一律用中文。
2. 做不到的事就说做不到，不要假装成功。
3. 只要我还没在小程序里点「确认导入」，就不许说"已经导入完成"。
4. 上面那串绑定信息只能用一次，不要写进任何给你的文件、备注或对话里。

我的机构：{orgName} · {campusName}（只用来称呼我，不代表权限）

现在开始：先做第 2 步，然后告诉我你能做什么。
```

---

## 2. Variables

| Placeholder | Meaning | Substituted by | Used for permission? |
|---|---|---|---|
| `{apiBase}` | backend API base URL | backend / mini-program at copy time | 🔴 **No** — it is only an address |
| `{promptToken}` | one-time credential, burned on first successful handshake | server, at the moment the teacher taps 「复制」 | ✅ Yes — but only to open a session; writing still needs the teacher's own authorization |
| `{orgName}` | organization display name | backend | ❌ No — greeting only |
| `{campusName}` | campus display name | backend | ❌ No — greeting only |
| ~~`{teacherLabel}`~~ | **removed on purpose** — we deliberately do not resolve real teacher names | — | — |

> 🔴 **Permission never comes from the prompt.** It comes only from the **teacher's login state plus the
> short code the server issues inside the mini-program.** Anything the prompt or chat claims is ignored.
> (Enforced in `references/60-guardrails.md`.)

---

## 3. Why the template can live in a public repo

This repo is **public**. That is safe because:

- only **placeholders** are stored here — no real domain, no real credential, no real ids;
- real values are injected by the mini-program at copy time;
- even a fully leaked prompt grants **no write access** — it can only *request* authorization,
  and the teacher must still tap confirm in the mini-program before anything persists.

**Never commit a real `{apiBase}` or `{promptToken}` value into this repo.**

---

## 4. Copy-time UX (mini-program side)

1. Teacher taps the copy entry → **a confirmation dialog appears first** (neutral wording, **no AI-related terms**):
   > 这份整理说明**只能使用一次**，且会绑定你的账号，请勿转发。确认复制？
2. After confirming, the backend issues `{promptToken}` and the front-end renders the template with
   every `{variable}` substituted, then copies it.
3. `{promptToken}` is **valid 1 hour if unused**, and is **burned the moment the handshake succeeds**.
   A second batch requires copying a fresh one.

---

## 5. Ops: what must be kept in sync

The **live** version of this template lives in the ops backend (`运营 / legacy-import-settings`),
**not** in this repo. This file is the source of truth; the backend copy must be updated by hand.
See `docs/ops-checklist.md`.
