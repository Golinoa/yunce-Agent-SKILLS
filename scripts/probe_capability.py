#!/usr/bin/env python3
"""
能力自检：让 AI 先摸清自己这条通道能干什么，再决定用哪条输出路径。

跑法
    python3 probe_capability.py

输出是一段**给 AI 看的判读结论**（`LEVEL=` 一行最关键），
它会告诉你应该走 references/10-capability.md 里的哪一档。
"""
import json
import os
import sys
import tempfile
import urllib.request

REPO_RAW = "https://raw.githubusercontent.com/Golinoa/yunce-meta-prompt/main"
TEMPLATE_URL = f"{REPO_RAW}/assets/%E8%80%81%E7%94%9F%E8%AF%BE%E6%97%B6%E5%AF%BC%E5%85%A5%E6%A8%A1%E6%9D%BF-v1.3.xlsx"

result = {
    "python": sys.version.split()[0],
    "can_run_code": True,          # 脚本跑起来了，本身就是证据
    "can_write_file": False,
    "can_read_url": False,
    "has_openpyxl": False,
    "template_local": False,
    "template_reachable": False,
}

HERE = os.path.dirname(os.path.abspath(__file__))
LOCAL_TEMPLATE = os.path.join(HERE, "..", "templates", "老生课时导入模板-v1.3.xlsx")
result["template_local"] = os.path.exists(LOCAL_TEMPLATE)

# 1) 能否写文件
try:
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=True, encoding="utf-8") as f:
        f.write("ok")
        result["can_write_file"] = True
except Exception:
    pass

# 2) 有没有 openpyxl（有则能用更友好的方式生成 xlsx；没有也能用标准库的 build_xlsx.py）
try:
    import openpyxl  # noqa: F401
    result["has_openpyxl"] = True
except Exception:
    pass

# 3) 能否从网上取到仓库里的模板（决定"填模板"还是"从零生成"）
try:
    req = urllib.request.Request(REPO_RAW + "/VERSION", headers={"User-Agent": "probe"})
    with urllib.request.urlopen(req, timeout=6) as r:
        result["can_read_url"] = r.status == 200
        version = r.read().decode("utf-8").strip()
except Exception:
    version = None
    result["can_read_url"] = False

try:
    req = urllib.request.Request(TEMPLATE_URL, headers={"User-Agent": "probe"})
    with urllib.request.urlopen(req, timeout=8) as r:
        result["template_reachable"] = r.status == 200
except Exception:
    pass

# ---- 判读 ----
template_ready = result["template_local"] or result["template_reachable"]

if result["can_write_file"] and template_ready:
    level = "A"   # 最优：能写文件 + 拿得到模板 → 填模板出 xlsx（样式零漂移）
    note = "走 A：用 assets/ 里的模板 → scripts/build_xlsx.py 填数据 → 交付 .xlsx"
elif result["can_write_file"] and result["has_openpyxl"]:
    level = "B"   # 能写文件但拿不到模板 → 用 openpyxl 按规格从零生成
    note = "走 B：按 references/30-output-spec.md 用 openpyxl 从零生成 .xlsx"
elif result["can_write_file"]:
    level = "C"   # 能写文件，但既无模板也无 openpyxl → 出 CSV
    note = "走 C：scripts/build_csv.py 生成 CSV（系统支持 .csv 导入）"
else:
    level = "D"   # 不能写文件 → 只能输出 Markdown 表格，让用户自己粘贴另存
    note = "走 D：在对话里输出 Markdown 表格 + 另存指引（不要声称能生成文件）"

print(json.dumps(result, ensure_ascii=False, indent=2))
print()
print(f"VERSION={version}")
print(f"LEVEL={level}")
print(f"建议={note}")
