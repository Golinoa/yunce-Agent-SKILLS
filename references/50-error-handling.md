# Error handling

> When anything goes wrong, check this file first.
> **Core rule: never retry anything with `retryable=false`, and never tell the teacher "it succeeded".**

---

## 1. The worst outcome

> **Errors are not the danger. The danger is the teacher believing "the import succeeded".**
> So: **until Step 6 is reached and the teacher confirms in the mini-program, never say "import completed".**

---

## 2. How to use the `retryable` flag

Every server error returns:

```json
{ "code": "XXX", "message": "给用户看的人话", "retryable": false }
```

| `retryable` | What to do |
|---|---|
| **false** | **Stop immediately, do not retry**, and tell the teacher using the wording in the table below |
| **true** | **Back off and retry, at most 3 times** (2s → 5s → 10s); if all 3 fail, treat it as false |

---

## 3. Error code → what to say

| code | Meaning | Action | Wording to the teacher |
|---|---|---|---|
| `FEATURE_DISABLED` | direct write is temporarily disabled | **stop**, switch to "produce a table" | 「这边暂时没法直接送进系统了，不过我可以帮你整理成表格，你拿去小程序上传就行」 |
| `TOKEN_MISSING` | the starter prompt **carries no credential** (likely copied straight from the public repo) | **stop**, do not force it | 「这份说明里没有绑定你的账号。麻烦你回小程序**重新复制一份**发我；不方便的话，我现在直接帮你**整理成表格**也行」 |
| `TOKEN_EXPIRED` | credential **unused for over 1 hour** (only surfaces at the opening handshake) | **stop** | 「这份说明拖太久了。麻烦你回小程序**重新复制一份**发我；或者我直接帮你**整理成表格**」 |
| `TOKEN_CONSUMED` | credential **already used** (one use only; forwarding it to someone else is useless) | **stop** | 「这份说明已经用过了。麻烦你回小程序**重新复制一份**；不想折腾的话，我现在帮你**整理成表格**」 |
| `BATCH_CONFLICT` | the teacher still has an unconfirmed batch | **stop**, open no new batch | 「你还有一批名单没确认，先去小程序把那一批处理完，我再帮你弄新的」 |
| `COOLDOWN` | requests too frequent, cooling down | **stop** | 「刚才连续操作了几次，需要等大概 {N} 分钟再试；或者我现在先帮你整理成表格」 |
| `QUOTA_EXCEEDED` | **daily request quota exhausted** | **stop** | 「今天申请的次数到上限了，明天再试；现在我可以帮你整理成表格」 |
| `MEMBERS_CAPACITY_EXCEEDED` | the institution has no room for more students — **the whole batch was refused** | **stop**, do not retry | 「这批人数超过机构的容量上限了，一行都没写进去。您可以升级套餐，或者联系客服加容量包；我也可以现在就把名单整理成表格给您。」 |

> 🔴 **Capacity vs daily quota — do not confuse the two.** They read alike and lead to opposite advice.
>
> | | what it means | what the teacher should do |
> |---|---|---|
> | `QUOTA_EXCEEDED` | today's **request** quota is used up | **come back tomorrow** |
> | `MEMBERS_CAPACITY_EXCEEDED` | the institution has **no room for more students** | **upgrade / buy a capacity pack, or split the list** |
>
> Two shapes you may meet, both mean capacity:
> 1. a structured field, `code = MEMBERS_CAPACITY_EXCEEDED`;
> 2. the code buried in the message: `QUOTA_EXCEEDED:MEMBERS_CAPACITY_EXCEEDED:<detail>`
>    (the legacy `QUOTA_EXCEEDED:` prefix exists so the mini-program keeps showing its upgrade
>    prompt — it is **not** a statement that today's quota is gone).
>
> ⇒ **Match on the substring `MEMBERS_CAPACITY_EXCEEDED` first.** Only if that substring is
> **absent** may you treat it as the daily-request quota. Telling the teacher 「明天再试」 when the
> real problem is capacity wastes their day and hides the one action that would fix it.
| `AUTH_CODE_EXPIRED` | short code expired (over 5 minutes) | no retry, **authorize again** | 「短码过期了，麻烦你再打开小程序刷新一下首页、重新点一次授权，把新的短码发我」 |
| `AUTH_CONSUMED` | short code already used | no retry, **authorize again** | 「刚才那串码用过了，需要再授权一次：打开小程序刷新首页，把新的短码发我」 |
| `CODE_MISMATCH` | short code does not match | no retry | 「短码好像没对，麻烦你回小程序页面再看一眼，整串发我（8 位）」 |
| `SESSION_REVOKED` | this authorization was revoked | no retry, **authorize again** | 「这次授权被撤回了，需要重新走一遍：打开小程序刷新首页 → 授权 → 把短码发我」 |
| `SESSION_NOT_AUTHORIZED` | the teacher has not finished authorizing | **wait for them**, do not retry on your own | 「还没看到你的授权，麻烦打开小程序刷新一下首页、弹出来的框点一下授权」 |
| `DATA_NOT_READY` | the teacher **has** authorized, your rows are still uploading | **wait**, then retry the read | 「名单还在传过来，到了我马上显示。等一下再看就行」 |
| `IDENTITY_MISMATCH` | authorizing account ≠ roster owner | **stop** | 「授权用的账号和这批名单对不上，我没法继续。麻烦你在小程序里用本人的账号再授权一次」 |
| `NOT_OWNER` | not the batch initiator | **stop** | 「这批名单不是当前账号建的，我看不到。请用当初发起的那台设备/账号操作」 |
| `BATCH_TOO_LARGE` | over 500 rows | no retry | 「一次最多 500 人，我们分两批发吧。先发前 500 个？」 |
| `RATE_LIMITED` | requests too frequent | **back off, retry ≤3** | do not bother the teacher during retries; after 3 failures say 「网有点忙，稍等我再试一下」 |
| `SERVER_BUSY` | server busy | **back off, retry ≤3** | same as above |

**Withdrawal** (only encountered when the teacher acts in the mini-program; just explain it):
| code | Wording |
|---|---|
| `WITHDRAW_WINDOW_CLOSED` | 「超过 24 小时了，撤回不了。如果确实导错了，需要在小程序里把对应的期初卡删掉再重新上传」 |
| `WITHDRAW_NOT_ALLOWED` | 「这批学员已经有后续记录（比如已经点过名/消过课），不能整批撤回了。需要手动处理有问题的几条」 |

---

## 4. Network-level failures (not yet "server rejected")

| Symptom | Meaning | Handling |
|---|---|---|
| Command will not run / no `curl` / sandbox blocks networking | **`NET=no`** | abandon "direct write" at once, switch to **produce a table**, and recommend switching AI using the wording in `references/70-opening.md` |
| Request sent but **no response / timeout** | success unknown | the staging-write step **can be retried safely** (idempotent); **never retry the key exchange** — have the teacher authorize again |
| A response came back but it is not JSON | likely a gateway error | treat as `SERVER_BUSY` (back off, retry ≤3) |

---

## 5. Strictly forbidden

1. ❌ Treating a `retryable=false` error as "network jitter" and retrying it.
2. ❌ After a failure, telling the teacher "it's imported / it's in".
3. ❌ Continuing downstream after an error (e.g. forcing a staging write after a failed key exchange).
4. ❌ Inventing an "error cause" to cover for yourself — **report it verbatim and keep the raw error**.
