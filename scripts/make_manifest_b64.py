#!/usr/bin/env python3
"""
生成「隐蔽启动语」里那段 MANIFEST_B64。

用途
- 隐蔽启动语不写明文网址：把 主机 / 组织 / 仓库 / 版本 四项打包成 base64，
  粘给 AI，由 AI 解码后拼出 ROOT，再去取 SKILL.md。
- **每次发新版本（VERSION 变化）都要重新跑一次本脚本**，把新码替换进
  assets/starter-prompt-hidden.md，否则 AI 会去取旧版本。

用法
    python3 scripts/make_manifest_b64.py
    python3 scripts/make_manifest_b64.py --host raw.githubusercontent.com --owner Golinoa --repo yunce-meta-prompt
"""
import argparse
import base64
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="raw.githubusercontent.com")
    ap.add_argument("--owner", default="Golinoa")
    ap.add_argument("--repo", default="yunce-meta-prompt")
    ap.add_argument("--version", default=None, help="默认读仓库 VERSION，并加 v 前缀")
    a = ap.parse_args()

    version = a.version
    if version is None:
        with open(os.path.join(HERE, "..", "VERSION"), encoding="utf-8") as f:
            version = "v" + f.read().strip()

    manifest = {"h": a.host, "p": a.owner, "r": a.repo, "v": version}
    raw = json.dumps(manifest, ensure_ascii=False, separators=(",", ":"))
    blob = base64.b64encode(raw.encode("utf-8")).decode("ascii")

    print("明文 JSON :", raw)
    print("MANIFEST_B64 :")
    print(blob)
    print()
    print("解码校验  :", base64.b64decode(blob).decode("utf-8"))
    print("拼出的 ROOT:", f"https://{a.host}/{a.owner}/{a.repo}/{version}/")


if __name__ == "__main__":
    main()
