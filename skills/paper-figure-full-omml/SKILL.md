---
name: paper-figure-full-omml
description: >-
  Use when any paper-figure math must be real editable OMML AND look like ORIG
  LaTeX in LO preview — never Unicode ₍paren₎ or underscore fakes. Hard gate
  Fig01–10/SI.
---
# Full real OMML + ORIG-visible LaTeX (Kevin t37u/t40u/t41u/**t42u**)

**Hard rule:** ORIG 数学 → 真可编辑 `m:oMath`（Choice）**且** LO/SBS 预览必须看起来像原图 LaTeX（真下标、∩/∏ 下限、横分式），禁止粗糙 Unicode `₍risk₎` / `V(sys)` / `PattacK` / `V_sys`。

Load with [paper-figure-quality-merge](sand-workflow:paper-figure-quality-merge).

## Why Fallback matters (t42u)
- PowerPoint 画 **Choice OMML**（Cambria Math）。
- LibreOffice 画 **Fallback**；`unwrap_omml_choice_only` 会让 LO **公式空白**（已实测）。
- 因此：**保留 AlternateContent**；Fallback 必须是 **DrawingML 富文本**（`a:rPr baseline` 真下标/上标、分号分式或堆叠分子分母+横线、大算子+下方极限），视觉对齐 ORIG，而不是单行 `pretty_fallback` 括号下标。

## Must match ORIG visually
- Fig03 DHR: $V_{sys}(t)=\bigcap_{i\in A(t)}V_i$，∏ 同；$T=\frac{N!}{r!(N-r)!}$ 横分式；$P_{attack}\to 0$
- Fig08 Dominant: $\alpha_{risk}$, $L_{req}$, $f_{byz}$, $\kappa$, $\Theta$ — 下标贴底、无 `₍ ₎`
- Gate FAIL if SBS/prev shows paren-subscript glyphs `₍`/`₎` or slash-only T when ORIG has stacked frac.

## Implementation
1. EQF Choice = full `E.sub`/`E.nary`/`E.frac`.
2. EQF Fallback = `rich_math_fallback`（baseline runs + 分式堆叠），写入 `items/_ommlfix.py`。
3. Ban unwrap for delivery builds of math-heavy figs.
4. Audit: `fallback_paren_sub_leaks`, `preview_looks_latex_pass`, plus t40u fields.

## Quality sync — tree, not a coverage count
Load [paper-figure-source-symbol-audit](sand-workflow:paper-figure-source-symbol-audit) whenever math is present.
Caption lines, axis labels, isolated inequalities, and conditions outside the main box are math when they are math. Prose and filenames stay prose.
Compare namespace, order, attributes, and text. An operator in `m:chr/@m:val` is part of the signature. Limits above and below the operator are part of it. A duplicated Choice term is not certified by a clean Fallback, and a complete Choice is not certified by a Fallback that drops the limits.
`reviewed/N`, including a historical full count, is only coverage. Later errata do not increase that denominator. Unknown stays unknown.

```bash
python3 tools/quality_sync.py math-signature --xml qa/<fig>_choice_math.xml --compare qa/<fig>_other_math.xml
```

Equal signatures only say the selected roots match. They do not prove the source was read.

## Chart companion (Fig08 t42u)
Predicted Mechanism **彩色阶梯粗线**（每 20s 一段，色=机制，高度对齐 ORIG）必须画；仅有图标+标签无粗线 = FAIL（见 layout-gates）。
