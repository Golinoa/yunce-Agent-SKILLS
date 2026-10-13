# Output spec (read at LEVEL=B, or when building from scratch)

> ✅ **LEVEL=A does not need this file**: use the template in `assets/` plus `scripts/build_xlsx.py`
> and the styling matches by construction. Follow the spec below strictly **only** when the template
> is unavailable and you must build from scratch.

---

## 1. Cell-level xlsx spec

Filename: `松果排课学员导入模板.xlsx`
Sheet: **exactly one**, named **老生课时导入**
Global: whole sheet **宋体 (SimSun)**, font color `#000000`; **uniform row height 22pt**;
**no borders, no freeze panes, no filters, no extra sheets**

Column widths: `A 18 / B 10 / C 16 / D 16 / E 16 / F 14 / G 26 / H 22 / I 24`

### 1) `A1:I5` merged — the notes block

Text (**5 lines, keep the line breaks**):

```
当前模板版本：1.3
请勿增加、删除、修改列；说明行之后从「学员姓名」表头下一行开始填写
必填：只有「学员姓名」。其余列都可以留空，留空就只建档案、不录课时
要录课时：请把「科目」和「剩余课时」一起填上（缺一列就只建档、不录课时）；剩余课时为整数，欠课时写负数（如 -2），不要填 0
选填：性别（男/女）、出生日期（YYYY-MM-DD）、手机号、有效期（YYYY-MM-DD，留空=永久）、缴费金额（元，最多两位小数）、备注；一行一个科目
```

Styling: 宋体 **11**, **wrap text**, horizontal left / vertical top, light green fill.

> Fill: the official template uses **theme color accent3 (`#9BBB59`) with transparency**,
> which renders around `#D7E4BD`. Writing `#BBD18E` directly is also fine —
> **purely a visual difference, it does not affect importing**.

### 2) Row 6 `A6:I6` — the header row

In order (**only the first column carries an asterisk**):

```
学员姓名*  ｜ 性别 ｜ 出生日期 ｜ 手机号  科目 ｜ 剩余课时 ｜ 有效期（空=永久） ｜ 缴费金额（元） ｜ 备注
```

Styling: 宋体 **14 bold**, horizontal center / vertical center, green fill (around `#A7C36C`;
the official one is accent3 + transparency).

> ⚠️ **Do not put an asterisk on columns 5 and 6.** It misleads the teacher into thinking
> subject / lessons are required (they are not — see `references/20-data-spec.md`).

### 3) Row 7 `A7:I7` — the example row (**exactly 9 cells**)

```
示例：张三（删） ｜ 男 ｜ 2015-01-01 ｜ （空） ｜ 语文 ｜ 12 ｜ （空） ｜ （空） ｜ （空）
```

Styling: 宋体 11, center/center, **no fill**.

> - The name must start with **示例** (the system skips the row by it).
> - Count carefully: **9 values**, not more.
> - If unsure, **omit the example row entirely** (importing still works).

### 4) Row 8 onward — student data rows

Styling: 宋体 11, center/center. One row per student-subject pair.

---

## 2. CSV spec (preferred at LEVEL=C)

- Encoding: **UTF-8 with BOM** (so double-clicking in Excel/WPS shows no mojibake; the system strips the BOM)
- Line endings: CRLF
- Structure: **row 1 = header, then data rows**. **Do not write a 5-line notes block**
  (CSV has no merged cells; note lines can interfere instead)

Header (9 columns, fixed order):

```
学员姓名,性别,出生日期,手机号,科目,剩余课时,有效期,缴费金额,备注
```

- When a field contains a **comma, quote or newline**, wrap it in double quotes and double the inner quotes (RFC4180).
  I.e. `"喜欢钢琴，有点""调皮"""` — Excel/WPS handle this automatically when saving as CSV.
- One student-subject per row; omit missing fields (consecutive commas are fine).

> CSV and xlsx have an **identical column structure and meaning**; CSV just lacks styling.
> The system uses the same parser for both, so the two paths cannot drift.

## 3. TXT spec (optional)

- Tab (`\t`) or comma separated, both accepted; **prefer plain CSV** for better compatibility.
- Same rule: the first row is the 9-column header and **it must have ≥ 7 columns**
  (the system recognizes "this is the header row" by column count).
- Encoding UTF-8; GBK is also recognized.

## 4. Choosing among the three

| Priority | Format | When |
|---|---|---|
| 1 | `.xlsx` | can run code + template available (LEVEL=A/B) — fullest styling, most familiar to teachers |
| 2 | `.csv` | xlsx impossible (LEVEL=C) — no styling but **structurally identical import logic** |
| 3 | `.txt` | the user explicitly wants plain text, or the environment can only emit text |
| — | Markdown table | cannot produce a file (LEVEL=D) — requires manual pasting, highest risk |

## 5. Self-check before delivery (mandatory)

1. Reopen the artifact with Python and read it back: **header has 9 columns, first column starts with 学员姓名**;
2. Confirm **no extra text rows below the header row**;
3. Confirm row count ≤ 500;
4. Put "共 N 行 / 问题行 / 导入方法" into the delivery note.
