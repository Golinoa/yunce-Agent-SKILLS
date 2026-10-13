# Data spec (single source of truth)

> This file is the **single source of truth** for validation and cleaning.
> If `SKILL.md` or `assets/meta-prompt.md` conflicts with this file, **this file wins**.
> System implementation: `yunce-backend/src/legacy-hours-import/`.

## 1. The 9 columns (order is fixed)

| # | Column | Required | Notes |
|---|---|---|---|
| 1 | 学员姓名 | ✅ | the only required field. ≤ 50 chars |
| 2 | 性别 | | only 男 or 女; leave blank if unknown |
| 3 | 出生日期 | | `YYYY-MM-DD`; year-only ⇒ pad with `01-01` |
| 4 | 手机号 | | 11-digit mainland number; leave blank if none |
| 5 | 科目 | | e.g. 钢琴, 书法 |
| 6 | 剩余课时 | | integer; **negative allowed**; see below |
| 7 | 有效期 | | `YYYY-MM-DD`; blank = permanent |
| 8 | 缴费金额 | | in 元 (yuan), non-negative, at most 2 decimals |
| 9 | 备注 | | free text, ≤ 191 chars |

**Same name = same student.** One student with several subjects ⇒ several rows with the name repeated (normal).

## 2. Required fields and the "pair" rule (the easiest thing to get wrong)

- **Only 学员姓名 is required.** The other 8 columns are all optional.
- **科目 + 剩余课时 form a pair**:
  - both filled → a lesson card is created normally;
  - **only one filled → that row creates the profile but records no lessons, and it is NOT an error**.
- Therefore: **never write "subject / lessons are required" into any prompt or note**
  (the old live template said exactly that — it is stale).

## 3. Remaining lessons

- Digits only, no units ("还剩 12 节课" → `12`).
- **Negative allowed**: `-2` = the student owes 2 lessons (recorded as a negative on the card).
- **0 is not allowed**: a 0-lesson card is invisible in the UI and meaningless → leave it blank.
- Lessons without a subject (or vice versa) ⇒ that row only creates the profile.

## 4. Multi-row consistency for one student (fails the whole group)

| Item | Rule | Consequence if inconsistent |
|---|---|---|
| 性别 / 出生日期 / 手机号 | either all blank, or **identical on every row** | the whole group is rejected |
| 备注 | **fill it on only one row**, or use **the identical sentence on every row** | the whole group is rejected |

> AIs most often fail here: two rows for the same student with two different phone numbers,
> or different remarks per row ⇒ the teacher's import fails for the entire group with no obvious cause.

## 5. Format and length limits

| Item | Rule | System behavior |
|---|---|---|
| 姓名 | ≤ 50 chars | error if exceeded |
| 备注 | ≤ 191 chars | error if exceeded (and combined with any existing remark also ≤ 191) |
| 有效期 | `YYYY-MM-DD` | if filled it must be valid, else error |
| 缴费金额 | non-negative, ≤ 2 decimals | error if invalid |
| 出生日期 / 性别 / 手机号 | **no format validation** | unrecognized = treated as blank (permissive) |
| rows per batch | **≤ 500** | error: 「单批最多 500 行」 |

> Note the bolded row: the system does not validate those three fields,
> so **normalizing them on the AI side** is the cheaper win (and the prompt asks for it anyway).

## 6. Cleaning and problem-row handling

1. **Do not guess, do not rewrite, do not drop**: for rows that are invalid or unclear,
   **write the original value into the table as-is**.
2. In the **chat reply**, list each problem row explicitly: `原始数据第 X 行 + 问题 + 原值`.
3. Let the teacher fix them before importing.

> This matches the product rule "never let an ambiguous row through on a guess":
> better that the teacher sees the problem than silently rewriting or silently dropping data.

## 7. 🔴 Hard rule: no non-data rows below the header row

The parser **skips exactly three kinds of rows**:

1. blank rows (first cell empty)
2. rows whose first cell starts with **示例**
3. rows whose first cell is exactly **必填**

⇒ Any other non-empty text is treated as **a student name**. So never put this in the table:

- `备注：第3行手机号疑似有误` ❌ → creates a student literally named "备注：第3行手机号疑似有误"
- `说明：以上共 12 条` ❌
- `合计` ❌

**All notes, lists and reminders belong in the chat reply only.**

## 8. Should values be cleaned?

| Case | Handling |
|---|---|
| Extra spaces around / inside a name | strip (including spaces inside the name) |
| "还剩 12 节课", "12 课时" | take the number `12` |
| Dates written `2015/1/1`, `2015年1月1日` | normalize to `2015-01-01` |
| Gender written 男孩子, 女孩 | normalize to 男 / 女; if genuinely unclear → leave blank |
| Phone with spaces or dashes | strip non-digits; wrong length → leave blank and flag it in the list |
| Optional fields absent from the source | **leave blank, never invent** (especially 缴费金额) |
