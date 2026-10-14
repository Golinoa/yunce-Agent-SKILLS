# Opening and routing

> Follow this file at the start of every session. **Present the paths first, let the teacher choose,
> never decide for them.**

---

## 1. Shake hands first (**one call**; it decides whether you can write directly)

Your starter prompt carries a one-time authorization `{code}`. Join it to the `base` fixed in this
repo (`SKILL.md` → **Endpoint**). That assembles to `{base}/assist-import/gate/{code}` — the handshake URL.
**The first thing you do** is shake hands with it:

```bash
curl -s -X POST "{base}/assist-import/gate/{code}" \
  -H "Content-Type: application/json" \
  -d '{}'
```

| Result | Meaning | What to do |
|---|---|---|
| **Success** (contains `sessionId`) | `NET=yes`: you can send requests and the credential is valid | **Keep the `sessionId`** (everything downstream uses it) and offer the "write directly" path |
| **Command will not run / no response** | `NET=no` | **Only** the "produce a table" path |
| **TOKEN_MISSING / TOKEN_EXPIRED / TOKEN_CONSUMED** | credential unusable | see §2 "credential unusable" below |

🔴 **Three hard rules**:
1. **Never guess.** If it cannot run, say so (Hard rule 11).
2. **Handshake exactly once.** The credential **is burned the moment it validates**; a second call returns
   `TOKEN_CONSUMED`.
3. **No `{code}` in your starter prompt** ⇒ you have **no** direct-write capability;
   take the table path.

> Prompts copied straight from the public repo carry no `{code}` ⇒ **take the table path**.
> The teacher may never have asked you to write at all (e.g. they only said "make me a table") ⇒
> **no handshake needed**, just clean the data.

---

## 2. Opening lines (copy them; do not improvise)

```
老师你好，我可以帮你整理学员名单，有两条路：

① 直接写进系统：你把名单发我，我整理好直接送进系统，你去小程序点一下确认就行。
② 整理成表格：我整理成 Excel/CSV 给你，你拿去小程序上传。

你想走哪条？
```

### If `NET=no`, use this instead (**do not offer ①**, but recommend switching tools)

```
老师你好，我可以帮你把学员名单整理成表格（Excel / CSV / 实在不行 TXT），
你拿到后去小程序上传就行。

💡 另外提一句：我这台 AI 目前没法直接把名单送进系统。
如果你想让它一步到位，可以换 **豆包（记得开「工作模式」）** 或 **Kimi** 再来找我。
当然，现在这样也能完成，只是多一步上传。
```

> **Never force a switch.** Recommending is informing, not requiring.

### The teacher picked ① but your starter prompt has no `{code}`

That means your starter prompt carries no authorization code (likely copied straight from the public repo) ⇒
**you have no direct-write capability**:

```
我这份配置里没有直连权限，走不了①。我可以帮你整理成表格，你拿去小程序上传就行。
```

### Credential unusable (`TOKEN_MISSING` / `TOKEN_EXPIRED` / `TOKEN_CONSUMED`)

**State it plainly and offer two options** (do not decide for them):

```
这份说明里的绑定信息用不了了（可能已经失效，或者已经用过一次）。
两个办法你选一个：
A. 你回小程序重新复制一份发我，我们接着走「直接写进系统」；
B. 我现在直接帮你把名单整理成表格，你拿去小程序上传。
```

> 🔴 **Never "just try it one more time"** — the credential is one-time; retrying only keeps failing.

---

## 3. After the choice

| Teacher's choice | Read next |
|---|---|
| ① Write directly into the system | `references/40-write-and-auth.md` (**must** also read `references/60-guardrails.md`) |
| ② Produce a table | `references/20-data-spec.md` → produce per your tier (scripts if they run, otherwise from the spec) |

**On either path, check `references/50-error-handling.md` first on any error.**

---

## 4. Applies to both paths

- When collecting item by item: **echo confirmation after each item**; the teacher can ask
  "现在整理到哪了" at any time (you have no server-side memory — you continue from the chat transcript).
- For **rows that do not line up** (duplicate names, missing name, wrong column count) ⇒
  **list them and ask the teacher; never guess** (see `references/20-data-spec.md`).
- Before handing back the finished table, **get the teacher's confirmation first**; do not just deliver.
