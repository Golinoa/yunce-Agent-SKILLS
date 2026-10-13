#!/usr/bin/env python3
"""
把学员数据写入「老生课时导入模板」副本，产出可直接导入的 .xlsx。

设计要点
- **只用 Python 标准库**（zipfile + re），不依赖 openpyxl：
  不同 AI 的执行环境里 openpyxl 常常装不上，而本仓库自带模板文件，
  所以在模板副本的 XML 上插入数据行是**最稳**的路径。
- 样式一律沿用模板里「示例行」的样式（s=1：宋体 11 / 居中），不新增样式。
- 单元格用 inlineStr（内联字符串），不碰 sharedStrings.xml，改动面最小。

用法
    python3 build_xlsx.py --data data.json --out 导入表.xlsx
    python3 build_xlsx.py --data data.json --out 导入表.xlsx --template ./assets/老生课时导入模板-v1.3.xlsx

data.json 格式（9 列，顺序固定；后 3 列可省略，短行自动补空）
    {"rows": [
      ["张三", "男", "2015-01-01", "13800000001", "书法", "20", "2026-12-31", "1200", "喜欢钢琴"],
      ["张三", "",   "",           "",            "舞蹈", "10", "",           "",     ""]
    ]}
    也接受 9 个英文键的对象：{"name","gender","birthday","phone","subject","hours","expiry","amount","remark"}
"""
import argparse
import json
import os
import re
import sys
import zipfile

# 模板里「示例行」(第 7 行) 使用的样式索引：宋体 11 / 居中
DATA_STYLE = "1"
COLS = "ABCDEFGHI"
KEYS = ["name", "gender", "birthday", "phone", "subject", "hours", "expiry", "amount", "remark"]


def norm_rows(raw):
    """把各种输入形态收敛成「9 元素字符串数组」的列表。"""
    rows = raw.get("rows") if isinstance(raw, dict) else raw
    if not isinstance(rows, list):
        raise ValueError('data.json 顶层必须是 {"rows":[...]} 或直接是数组')
    out = []
    for i, r in enumerate(rows, 1):
        if isinstance(r, dict):
            vals = [r.get(k, "") for k in KEYS]
        elif isinstance(r, list):
            vals = list(r)
        else:
            raise ValueError(f"第 {i} 行既不是数组也不是对象")
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


def esc(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))


def cell_xml(col, row, value):
    if value == "":
        return ""
    return f'<c r="{col}{row}" s="{DATA_STYLE}" t="inlineStr"><is><t xml:space="preserve">{esc(value)}</t></is></c>'


def build(template_path, rows, out_path):
    with zipfile.ZipFile(template_path) as zin:
        items = zin.infolist()
        blobs = {it.filename: zin.read(it.filename) for it in items}

    sheet_name = next(n for n in blobs if n.endswith("worksheets/sheet1.xml"))
    sheet = blobs[sheet_name].decode("utf-8")

    # 起始行 = 已有最大行号 + 1（v1.3 模板为 8，即表头第 6、示例第 7 之后的下一行）
    existing = [int(m) for m in re.findall(r'<row r="(\d+)"', sheet)]
    start = (max(existing) if existing else 0) + 1

    new_rows = []
    for offset, vals in enumerate(rows):
        rno = start + offset
        cells = "".join(cell_xml(COLS[i], rno, v) for i, v in enumerate(vals))
        new_rows.append(f'<row r="{rno}" spans="1:9">{cells}</row>')
    last = start + len(rows) - 1

    if "</sheetData>" not in sheet:
        raise RuntimeError("模板结构异常：找不到 </sheetData>")
    sheet = sheet.replace("</sheetData>", "".join(new_rows) + "</sheetData>", 1)

    # 更新已使用区域，避免某些阅读器把新行当"越界"
    sheet = re.sub(r'<dimension ref="[^"]*"/>', f'<dimension ref="A1:I{last}"/>', sheet, count=1)

    blobs[sheet_name] = sheet.encode("utf-8")

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zout:
        for it in items:
            zout.writestr(it, blobs[it.filename])
    return start, last


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    default_tpl = os.path.join(here, "..", "templates", "老生课时导入模板-v1.3.xlsx")
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="数据文件（json）")
    ap.add_argument("--out", required=True, help="输出的 xlsx 路径")
    ap.add_argument("--template", default=default_tpl, help="模板路径（默认用仓库自带模板）")
    a = ap.parse_args()

    if not os.path.exists(a.template):
        sys.exit(f"[FAIL] 找不到模板：{a.template}（请从仓库下载 assets/ 下的模板）")
    with open(a.data, "r", encoding="utf-8") as f:
        raw = json.load(f)

    rows = norm_rows(raw)
    start, last = build(a.template, rows, a.out)
    print(f"[OK] 已写入 {len(rows)} 行（第 {start}–{last} 行）→ {a.out}")


if __name__ == "__main__":
    main()
