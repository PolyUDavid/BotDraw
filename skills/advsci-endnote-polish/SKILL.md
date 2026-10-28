---
name: AdvSci文献核实排版润色EndNote
description: >-
  用户要把稿件按 Wiley Advanced Science 排版、逐条核实参考文献并生成 EndNote RIS/临时引文、或做学术 humanizer
  润色（第一人称 we、去 AI 套话、词级黄标）时使用；含 Crossref/OpenAlex/Semantic Scholar 核验、合并库、Adv
  Sci 版式、中文 README 与 Drive 交付。
---
# AdvSci：文献核实 · 排版 · 润色 · EndNote

适用：Wiley **Advanced Science** 正文 + Supporting Information。完整说明文档见工作区或 Drive 上的《AdvSci_文献核实排版润色EndNote_完整技能与流程说明.docx》。参考实现：`/workspace/advsci`（DeepBFT）。

## 何时用
- 要按 Advanced Science 格式化主稿 + SI（两端对齐、图近首次提及、AS 图注、OMML、三线表）
- 要核实全部参考文献并产出可导入 EndNote 的合并 RIS
- 要学术润色（we、去套话、词级黄标 marked/clean/EndNote-cite）
- 要中文 EndNote README（空库导入、Adv Sci 样式、Update Citations）

## 硬约束（用户偏好）
1. **永不臆造**文献元数据；存疑标 `Probable match – needs author confirmation`。
2. **禁止自动化查询 Google Scholar**（会封锁）；须在核验报告写明。来源：Crossref / OpenAlex / Semantic Scholar / 出版社页面。
3. 正文**两端对齐**；图靠近**首次提及**；**不压缩**插图 media（MD5 不变）。
4. 润色：除摘要外 **we/our**；摘要第三人称现在时（Adv Sci）；去 AI 套话与草稿/prompt 语；**每个改动的词黄色高亮**。
5. EndNote 临时引文 `{Author, Year #RecNum}` 的 RecNum = `all_refs.ris` 导入顺序；**.enl 无 EndNote 软件不可生成**。
6. Drive 上传后**不要改 sharing**；zip **扁平**（无目录项）。

## 流程摘要
0. 工作区 `/workspace/<proj>/{src,work,out,polish,preview}`
1. 解析正文+SI 参考文献 → 去重 uid
2. Crossref DOI/书目 → OpenAlex → Semantic Scholar → 出版社页；写 `reference_verification.xlsx|.md`
3. `all_refs.ris`（只推荐导入这一个）+ main/si 对照 RIS
4. Adv Sci 排版：`*_AdvSci_formatted.docx` + `*_EndNote_cite.docx`；中文 `README_EndNote_*.md`（未引用文献、Probable、空库 RecNum、.enl 限制）
5. 润色 → `*_polished_marked.docx` / `_clean` / `_EndNote_cite` + `change_log`（含作者待决 A1…）
6. 扁平 zip → Drive；对照 QA 清单

## 可复制长提示词
```
请按技能「AdvSci文献核实排版润色EndNote」（id: advsci-endnote-polish）完整处理：
正文 <Main.docx>，SI <SI.docx>，工作区 /workspace/<proj>。

(1) 核实全部文献：Crossref/OpenAlex/Semantic Scholar/出版社；禁止 Google Scholar 自动化；不臆造；
Probable 黄标；合并 all_refs.ris（RecNum 序）+ 核验 xlsx/md；列出未引用条目。
(2) Adv Sci 排版：两端对齐；图近首次提及且不压 media；AS 图注；三线表；OMML；
静态 [n] 与 EndNote {Author, Year #Rec} 双版本。
(3) 润色：除摘要外 we；去 AI 套话与 TODO/prompt；不擅自改数值；词级黄标 marked + clean + EndNote-cite；change_log。
(4) 中文 README：空库导入 RIS、Adv Sci.ens、Update Citations、未引用文献、.enl 限制。
(5) 扁平 zip 上传 Drive，不改 sharing。先自检 QA 再交付。
```

## 短提示词
```
按 advsci-endnote-polish 处理 <Main> + <SI>：核实（禁 Scholar 自动化）→ all_refs.ris；
Adv Sci 排版双版本；we 润色黄标三件套；中文 EndNote README；扁平 zip 上 Drive、不改 sharing。
```

## QA（放行门）
- 核验来源完整；报告含「未用 Google Scholar」；Probable 可见
- 两端对齐；图近提及；media MD5 不变；OMML 无 `$...$`
- 黄标仅改动词；EndNote 临时引文未被破坏；待决项入 change_log
- README 含空库/Adv Sci/未引用/.enl；Drive sharing 未改；unzip -t 通过

## 参考文件（DeepBFT）
`/workspace/advsci/out/README_EndNote_中文说明.md`、`reference_verification.md`、`all_refs.ris`；
`/workspace/advsci/polish/out/change_log*.md`；脚本 `work/{verify,build_final,fmt,outputs}.py`、`polish/apply.py`。
