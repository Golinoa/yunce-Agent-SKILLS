#!/usr/bin/env python3
"""
把学员数据写成可直接导入的 CSV（UTF-8 带 BOM）。

什么时候用这个
- 执行环境**不能生成或下载 .xlsx**，但能产出文本文件时用。
- 教务系统的导入**同时支持 .csv**，规范一致（9 列、顺序固定），所以这是可靠的退路。
- 带 BOM 是为了让 Excel/WPS 双击打开不乱码；系统端会自动识别并剥掉 BOM。

用法
    python3 build_csv.py --data data.json --out 导入表.csv
data.json 同 build_xlsx.py：{"rows": [[9 列...], ...]}（短行自动补空，后 3 列可省略）
"""
import argparse
import json
import os
import sys

HEADER = ["学员姓名", "性别", "出生日期", "手机号", "科目", "剩余课时", "有效期", "缴费金额", "备注"]
KEYS = ["name", "gender", "birthday", "phone", "subject", "hours", "expiry", "amount", "remark"]


def norm_rows(raw):
    rows = raw.get("rows") if isinstance(raw, dict) else raw
    if not isinstance(rows, list):
        raise ValueError('data.json 顶层必须是 {"rows":[...]} 或直接是数组')
    out = []
    for i, r in enumerate(rows, 1):
        vals = [r.get(k, "") for k in KEYS] if isinstance(r, dict) else list(r)
        vals = ["" if v is None else str(v).strip() for v in vals]
        if len(vals) > 9:
            raise ValueError(f"第 {i} 行有 {len(vals)} 列，最多 9 列")
        vals += [""] * (9 - len(vals))
        if not vals[0]:
            raise ValueError(f"第 {i} 行「学员姓名」为空（姓名是唯一必填项）")
        out.append(vals)
    if not out:
        raise ValueError("没有可写入的数据行")
    return out


def field(v):
    """RFC4180：含逗号/引号/换行时用双引号包住，内部引号翻倍。"""
    if any(ch in v for ch in [",", '"', "\n", "\r"]):
        return '"' + v.replace('"', '""') + '"'
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    with open(a.data, "r", encoding="utf-8") as f:
        raw = json.load(f)
    rows = norm_rows(raw)

    lines = [",".join(HEADER)] + [",".join(field(v) for v in r) for r in rows]
    # 换行统一用 CRLF（Excel 友好），并加 UTF-8 BOM
    text = "\r\n".join(lines) + "\r\n"
    with open(a.out, "w", encoding="utf-8-sig", newline="") as f:
        f.write(text)
    print(f"[OK] 已写入 {len(rows)} 行 + 表头 → {a.out}（UTF-8 带 BOM）")


if __name__ == "__main__":
    main()
