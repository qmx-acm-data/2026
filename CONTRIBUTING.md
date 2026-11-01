# 收录规范

## 1. 公式

- 行内公式用 `$...$`，独立公式用 `$$...$$`。
- 禁用 `\(...\)` 与 `\[...\]`（GitHub 不渲染）。

## 2. 题解命名

- 文件名：`[题解]平台题号 题名称.md`，例如 `[题解]CF2277C 树形DP.md`。
- 平台取值：`CF`（Codeforces）、`AT`（AtCoder）、`LG`（洛谷）、`NC`（牛客）、`Oth`（其他平台）。平台号不带方括号。
- 目录：`problems/<平台>/`，例如 `problems/CF/`。

## 3. 算法笔记命名

- 文件名：算法名称.md，不要有空格，可以有括号与中文。
- 例如：`线段树.md`、`最短路(Dijkstra).md`。
- 目录：`algorithms/`。

## 4. 提交方法

1. 打开仓库，点进要修改或新建的文件；
2. 新建文件点 `Add file → Create new file`，文件名写全相对路径（如 `problems/CF/[题解]CF2277C 树形DP.md`）；
3. 修改或写完向下滚，在 `Commit changes` 处选 **Create a new branch for this commit and start a pull request**，分支名自取（如 `add-cf2277c`）；
4. 点 `Propose changes` 生成 PR，等待 `core` 成员 review 后合并。
