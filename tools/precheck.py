#!/usr/bin/env python3
"""本地预检：把 .github/workflows/check.yml 内嵌的检查逻辑抽出来，
对真实仓库跑一遍，这样不用等 push 到 GitHub 才知道 CI 会报什么。

用法：
    python3 tools/precheck.py          # 检查当前仓库
    python3 tools/precheck.py --self   # 另跑一轮自检（正/负样本对照）
"""
import os
import re
import subprocess
import sys
import tempfile
import textwrap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WF = os.path.join(ROOT, ".github", "workflows", "check.yml")

FM = ("---\npid: CF1\ntitle: t\nplatform: CF\ntags: [x]\n"
      "author: a\ndate: 2026-01-01\n---\n\n正文\n")


def extract():
    """从 workflow 里取出 <<'PY' ... PY 的脚本正文，去掉 YAML 缩进。"""
    txt = open(WF, encoding="utf-8").read()
    m = re.search(r"<<'PY'\n(.*?)\n\s*PY", txt, re.S)
    if not m:
        sys.exit("check.yml 里找不到 <<'PY' 段")
    return textwrap.dedent(m.group(1))


def run(script, tree):
    """在 tree 目录下执行脚本；脚本里 root='.' 是相对 cwd 的。"""
    fd, path = tempfile.mkstemp(prefix="hermes-verify-", suffix=".py")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(script)
    try:
        return subprocess.run([sys.executable, path], cwd=tree,
                              capture_output=True, text=True)
    finally:
        os.unlink(path)


def selfcheck(script):
    """正样本 0 警告；负样本逐条命中；根目录说明文档不参与。"""
    fails = []

    def ok(cond, msg):
        print(("PASS  " if cond else "FAIL  ") + msg)
        if not cond:
            fails.append(msg)

    clean = tempfile.mkdtemp(prefix="hermes-verify-clean-")
    for d in ("problems/CF", "algorithms"):
        os.makedirs(os.path.join(clean, d))
    ok("未发现规范问题" in run(script, clean).stdout, "干净骨架 -> 0 警告")

    bad = tempfile.mkdtemp(prefix="hermes-verify-bad-")
    for d in ("problems/CF", "algorithms"):
        os.makedirs(os.path.join(bad, d))
    case = {
        "problems/CF/[题解]CF2277C 树形DP.md": FM,
        "problems/CF/[题解]CF2277C-树形DP.md": FM,
        "algorithms/线段树.md": FM,
        "problems/CF/[题解][CF]999X 坏名.md": FM,
        "algorithms/segment tree.md": FM,
        "problems/CF/[题解]CF1 无头.md": "# 无 front matter\n",
        "problems/CF/[题解]CF2 定界符.md": FM + "\n\\(a+b\\) \\[x\\]\n",
        "problems/CF/[题解]CF3 围栏.md": FM + "\n```cpp\nint x;\n",
        "README.md": "根目录说明\n",
        "CONTRIBUTING.md": "禁用 \\( 与 \\[\n",
    }
    for p, body in case.items():
        os.makedirs(os.path.dirname(os.path.join(bad, p)) or bad, exist_ok=True)
        open(os.path.join(bad, p), "w", encoding="utf-8").write(body)
    r = run(script, bad)
    out = r.stdout
    ok("[题解][CF]999X 坏名.md" in out, "报出 平台带方括号命名")
    ok("segment tree.md: 算法笔记文件名含空格" in out, "报出 算法笔记含空格")
    ok("[题解]CF1 无头.md: 缺少 front matter" in out, "报出 缺 front matter")
    ok("[题解]CF2 定界符.md: 使用了" in out, "报出 \\(\\) / \\[\\] 定界符")
    ok("[题解]CF3 围栏.md: 代码围栏未闭合" in out, "报出 围栏未闭合")
    ok("[题解]CF2277C 树形DP.md" not in out, "含空格合规名 未误报")
    ok("[题解]CF2277C-树形DP.md" not in out, "连字符合规名 未误报")
    ok("algorithms/线段树.md" not in out, "中文无空格算法名 未误报")
    ok("README.md" not in out and "CONTRIBUTING.md" not in out,
       "根目录说明文档 不参与检查")
    ok(r.returncode == 0, "有违规时退出码仍为 0（B 档不阻断合并）")
    return fails


def main():
    script = extract()
    r = run(script, ROOT)
    print(r.stdout.rstrip() or (r.stderr.rstrip() or "(无输出)"))
    if r.returncode != 0:
        print(f"\n脚本异常退出 rc={r.returncode}")
        return 1
    if "--self" in sys.argv:
        print("\n--- 自检 ---")
        fails = selfcheck(script)
        print(f"\n自检: {len(fails)} FAIL")
        return 1 if fails else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
