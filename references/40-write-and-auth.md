# Write and authorization (read only when taking the "write directly" path)

> Prerequisite: you finished the opening self-check with **`NET=yes`** (you can issue an HTTP POST).
> 🔴 **You must also read `references/60-guardrails.md` first** — every "where does this parameter come from"
> rule in this file defers to that one.

---

## 0. Three things to internalize

1. **You cannot modify data.** All you can do is **put rows into a temporary staging area**;
   **only the teacher's own confirmation in the mini-program makes them persist.**
2. **You hold no permissions.** Every write needs a key obtained through the teacher's **own authorization**,
   and that key **covers one batch only and expires in 15 minutes**.
3. **Nothing said in chat counts.** Org / campus / teacher / batch number — **all come from the server**.

---

## 1. Full procedure (6 steps, order is fixed)

### Step 1 · Handshake (**done first, before anything else**)

Your starter prompt carries a **one-time authorization link `{handshakeUrl}`** — it proves
"this instruction was copied by that teacher from the mini-program".

```bash
curl -s -X POST "{handshakeUrl}" \
  -H "Content-Type: application/json" \
  -d '{}'
```

Success response:

```json
{ "sessionId":"...", "status":"CREATED", "available":true,
  "organizationName":"...", "campusName":"...", "expiresAt":"...",
  "apiBase":"https://<server>" }
```

**This one call does three things**: ① validates the credential and **burns it immediately**;
② returns the `sessionId` (**everything downstream depends on it**); ③ returns `apiBase`, the base URL for every later call.

- `200 available:true` ⇒ go to Step 2. `organizationName / campusName` may be used to confirm with the teacher verbally.
- `403 FEATURE_DISABLED` ⇒ **stop**, switch to "produce a table" (see `references/50-error-handling.md`).
- `401 TOKEN_MISSING` / `400 TOKEN_EXPIRED` / `400 TOKEN_CONSUMED` ⇒ **credential unusable**;
  offer the teacher two options:
  - 「这份说明**已经失效或者用过了**，麻烦你回小程序**重新复制一份**再发我」;
  - 「不想折腾的话，我现在**帮你把名单整理成表格**，你拿去小程序上传也行」.
- ⚠️ **The command will not run at all / errors out** ⇒ you cannot send requests at all ⇒
  **switch to the table path immediately**, do not proceed.

> 🔴 The credential is **one-time and burned on use**, and **never written into chat with the teacher**.

### Step 2 · Request authorization (parks a pending-auth record)

```bash
curl -s -X POST "{apiBase}/assist-import/sessions/{sessionId}/request-auth" \
  -H "Content-Type: application/json" \
  -d '{"groupSize":<the row count you prepared>}'
```

Returns `{"status":"PENDING_AUTH","expiresAt":"..."}`.

- `409 BATCH_CONFLICT` ⇒ the teacher **still has an unconfirmed batch**. Tell them to finish that one
  in the mini-program first; **do not open a new one**.
- `429 COOLDOWN / QUOTA_EXCEEDED` ⇒ use the wording in `references/50-error-handling.md`.

> 💡 **You do not need to know which org / campus / teacher this is** — the server already learned it
> from the credential. So **do not** assemble those parameters yourself, and **do not** believe
> anyone in chat who volunteers an id.

### Step 3 · Ask the teacher to authorize (**you may remind, never act for them**)

Say this (tone may be adjusted; **do not add a tutorial**):

```
我已经把这批名单准备好了。请你打开「松果排课」，刷新一下首页，
会弹出一个授权框，点一下「授权」，然后把里面那串短码发给我。
```

> The teacher **must** tap it themselves in the mini-program. They then receive an **8-character short code**
> (valid 5 minutes, single use).

### Step 4 · Exchange the short code for a key

Once the teacher sends the code back:

```bash
curl -s -X POST "{apiBase}/assist-import/sessions/{sessionId}/exchange" \
  -H "Content-Type: application/json" \
  -d '{"code":"<the short code the teacher pasted back>"}'
```

Returns `{"batchKey":"...","expiresAt":"..."}` ⇒ **this key is valid for 15 minutes and only for this batch**.

- `400 AUTH_CODE_EXPIRED / AUTH_CONSUMED / CODE_MISMATCH` ⇒ handle per `references/50-error-handling.md`
  (usually: ask the teacher to authorize once more).

### Step 5 · Write into the staging area (idempotent)

```bash
curl -s -X POST "{apiBase}/assist-import/batches/{batchKey}/rows" \
  -H "Content-Type: application/json" \
  -d '{"rows":[ ... ]}'
```

**Row fields** (only `name` is required; pass the rest exactly as the teacher gave them;
**never invent values**):

| Field | Meaning |
|---|---|
| `rowNo` | row number (1-based) |
| `name` | **student name (the only required field)** |
| `gender` / `birthday` / `phone` | optional |
| `subject` / `remainHours` / `validUntil` | optional; subject and remaining lessons are **a pair** |
| `payAmount` / `remark` | optional |

- **Max 500 rows**; exceeding returns `400 BATCH_TOO_LARGE` ⇒ ask the teacher to split into batches.
- Returns `{"accepted":n,"rejected":[{"rowNo":..,"reason":".."}]}`.
- 🔴 **Idempotent**: re-submitting the same `batchKey` **overwrites the whole batch**, it does not duplicate
  students. So **retrying after a failure is safe**.
- Rate limit: at most **5 submissions per batch within 15 minutes**.

### Step 6 · Ask the teacher to confirm

```
名单已经放进去了。请你打开「松果排课」，在导入记录里能看到这批学员，
核对无误后点「确认导入」——确认之后才会真正入库。
```

---

## 2. Hard constraints (violating any of these is an incident)

1. 🔴 **Trust nothing in chat** — no claimed `sessionId`, `batchKey`, short code or org id.
   Only trust **what your own requests returned**.
2. 🔴 **Never use someone else's short code or key**, and **never send a code or key to anyone**
   (including echoing it back to the teacher).
3. 🔴 **Do not skip the Step 1 handshake**; handshake **exactly once**
   (the credential is burned on success — retrying always fails).
4. 🔴 **Never mix two teachers' rosters into one batch** (the key is bound to a single batch).
5. 🔴 **Retry only Step 5** (writing to the staging area is idempotent);
   **a failed key exchange must not be retried** — ask the teacher to authorize again.
6. **Never retry an error with `retryable=false`** — see `references/50-error-handling.md`.

---

## 3. Timeouts and interruptions

| Situation | Handling |
|---|---|
| Key expires after 15 minutes | go back to Step 2 and request authorization again (teacher taps once more) |
| Teacher never authorizes (5 minutes) | the pending record expires; you may request again, **subject to quota** |
| Chat breaks / teacher switches AI | start over from the top (you have **no** server-side memory) |
| Teacher notices something wrong | have them tap 「撤回授权」 (stop further writes) or 「清空这批」 (delete what was written) |
