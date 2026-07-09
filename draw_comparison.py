"""
Generate a comparison diagram: WALA vs Chop4LLM slicing flows.
Output: desktop/comparison_flow.png
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.lines as mlines
import os

# ─── Setup ────────────────────────────────────────────────────────────
desktop = os.path.expanduser("~/Desktop")
output_path = os.path.join(desktop, "comparison_flow.png")

# Use a clean style
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Microsoft YaHei', 'SimHei', 'DejaVu Sans'],
    'font.size': 12,
})

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(22, 10))
fig.patch.set_facecolor('#FAFAFA')

# ─── Common color scheme ─────────────────────────────────────────────
C_SOURCE  = '#1B4332'  # dark green — source code
C_IR      = '#D62828'  # red — intermediate representation
C_SLICE   = '#F77F00'  # orange — slice computation
C_OUTPUT  = '#0077B6'  # blue — final output
C_MAP     = '#9B5DE5'  # purple — mapping step
C_BOX     = '#F8F9FA'  # light gray — box background
C_BORDER  = '#495057'  # dark gray — box border
C_ARROW   = '#343A40'  # black — arrows
C_BAD     = '#E63946'  # red for problem markers
C_GOOD    = '#2D6A4F'  # green for advantage markers


def draw_box(ax, x, y, w, h, color=C_BOX, border=C_BORDER, lw=1.5, z=1):
    """Draw a rounded box."""
    box = FancyBboxPatch((x, y), w, h,
                         boxstyle="round,pad=0.15",
                         facecolor=color, edgecolor=border,
                         linewidth=lw, zorder=z)
    ax.add_patch(box)
    return box


def draw_arrow(ax, x1, y1, x2, y2, color=C_ARROW, lw=2, style='->', z=2):
    """Draw an arrow."""
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color,
                                lw=lw, connectionstyle='arc3,rad=0'),
                zorder=z)


def label(ax, x, y, text, size=11, bold=False, color='#212529', ha='center', va='center', z=10):
    """Place a text label."""
    weight = 'bold' if bold else 'normal'
    ax.text(x, y, text, fontsize=size, fontweight=weight,
            color=color, ha=ha, va=va, zorder=z, wrap=False)


def multilabel(ax, x, y, lines, size=10, color='#495057', ha='left', va='top', z=10):
    """Place multi-line text."""
    text = '\n'.join(lines)
    ax.text(x, y, text, fontsize=size, color=color, ha=ha, va=va,
            zorder=z, linespacing=1.4)


# ══════════════════════════════════════════════════════════════════════════
# LEFT SIDE: WALA Pipeline
# ══════════════════════════════════════════════════════════════════════════
ax1.set_xlim(0, 10)
ax1.set_ylim(0, 14)
ax1.set_title("WALA 流程：源码 → IR → 切片 → 映射回源码", fontsize=15,
              fontweight='bold', color='#212529', pad=20)
ax1.axis('off')

# Box 1: Java Source
draw_box(ax1, 1.5, 11.5, 7, 2, color='#E8F5E9', border=C_GOOD)
label(ax1, 5, 13.1, "Java 源码 (.java)", size=13, bold=True)

# Show source code inside
code_lines_wala = [
    "int x = foo(1);",
    "int y = bar(2);",
    "System.out.println(x+y);",
]
multilabel(ax1, 1.8, 12.4, code_lines_wala, size=9.5, color='#1B4332')

# Arrow 1: Soot compilation
draw_arrow(ax1, 5, 11.5, 5, 10.4, color=C_ARROW, lw=2.2)
label(ax1, 6.3, 11.0, "Soot 编译\n(生成三地址码)", size=9, color='#6C757D')

# Box 2: Jimple IR
draw_box(ax1, 1.5, 8.4, 7, 2, color='#FFEBEE', border=C_IR)
label(ax1, 5, 10.0, "Jimple IR（中间表示）", size=13, bold=True, color=C_IR)

ir_lines = [
    "$r0 = staticinvoke <foo(int)>(1)",
    "x = $r0",
    "$r1 = staticinvoke <bar(int)>(2)",
    "y = $r1",
    "$r2 = x + y",
    "virtualinvoke <println(int)>($r2)",
]
multilabel(ax1, 1.8, 9.2, ir_lines, size=9, color=C_IR)

# Arrow 2: WALA slicer
draw_arrow(ax1, 5, 8.4, 5, 7.3, color=C_ARROW, lw=2.2)
label(ax1, 6.3, 7.8, "WALA Slicer\n(在 IR 上构建 PDG\n+ 指针分析)", size=9, color='#6C757D')

# Box 3: Slice Result (Jimple)
draw_box(ax1, 1.5, 5.3, 7, 2, color='#FFF3E0', border=C_SLICE)
label(ax1, 5, 6.9, "切片结果（Jimple 级别）", size=13, bold=True, color=C_SLICE)

slice_ir = [
    "$r0 = staticinvoke <foo(int)>(1)",
    "x = $r0",
    "$r2 = x + y",
    "virtualinvoke <println(int)>($r2)",
]
multilabel(ax1, 1.8, 6.1, slice_ir, size=9, color=C_SLICE)

# Arrow 3: Map back
draw_arrow(ax1, 5, 5.3, 5, 4.2, color=C_MAP, lw=2.5)
label(ax1, 6.3, 4.7, "LineNumberTable\n反向映射", size=9, color=C_MAP)

# Box 4: Final source-level output
draw_box(ax1, 1.5, 2.2, 7, 2, color='#E3F2FD', border=C_BOX)
label(ax1, 5, 3.8, "最终输出（源码行号）", size=13, bold=True, color=C_OUTPUT)

final_wala = [
    "Slice1.java:15  (int x = foo(1))",
    "Slice1.java:17  (println(x+y))",
    "Slice1.java:21  (return x + 2)",
]
multilabel(ax1, 1.8, 3.0, final_wala, size=9.5, color=C_OUTPUT)

# Problem annotations on WALA side
label(ax1, 5, 1.6, "[x] 1 行源码 -> 多条 IR -> 切完再映射 -> 可能丢失行号", size=8.5, color=C_BAD)
label(ax1, 5, 1.1, "[x] 临时变量、synthetic 方法映射回去是 -1", size=8.5, color=C_BAD)
label(ax1, 5, 0.6, "[x] 结果不可直接读：每条 IR 都要查 LineNumberTable", size=8.5, color=C_BAD)


# ══════════════════════════════════════════════════════════════════════════
# RIGHT SIDE: Chop4LLM Pipeline
# ══════════════════════════════════════════════════════════════════════════
ax2.set_xlim(0, 10)
ax2.set_ylim(0, 14)
ax2.set_title("Chop4LLM 流程：源码 AST → 逐语句 PDG → 直接输出源码行", fontsize=15,
              fontweight='bold', color='#212529', pad=20)
ax2.axis('off')

# Box 1: Java Source
draw_box(ax2, 1.5, 11.5, 7, 2, color='#E8F5E9', border=C_GOOD)
label(ax2, 5, 13.1, "Java 源码 (.java)", size=13, bold=True)

code_lines_chop = [
    "int x = foo(1);",
    "int y = bar(2);",
    "System.out.println(x+y);",
]
multilabel(ax2, 1.8, 12.4, code_lines_chop, size=9.5, color='#1B4332')

# Arrow 1: javalang parse
draw_arrow(ax2, 5, 11.5, 5, 10.4, color=C_ARROW, lw=2.2)
label(ax2, 6.3, 11.0, "javalang 解析\n(直接拿到 AST 语句)", size=9, color='#6C757D')

# Box 2: PDG Construction
draw_box(ax2, 1.5, 8.4, 7, 2, color='#E8F5E9', border=C_GOOD)
label(ax2, 5, 10.0, "逐语句 PDG 构建", size=13, bold=True, color=C_GOOD)

pdg_info = [
    "N1 L15: int x = foo(1)    def={x} use={}",
    "N2 L16: int y = bar(2)    def={y} use={}",
    "N3 L17: println(x+y)       def={} use={x, y}",
    "边: N1 →(DATA_DEP, x)→ N3",
    "边: N2 →(DATA_DEP, y)→ N3",
]
multilabel(ax2, 1.8, 9.2, pdg_info, size=9, color=C_GOOD)

# Arrow 2: Chop slicing
draw_arrow(ax2, 5, 8.4, 5, 7.3, color=C_ARROW, lw=2.2)
label(ax2, 6.3, 7.8, "Chop 切片\n(在 PDG 上双向\n受限可达性)", size=9, color='#6C757D')

# Box 3: Slice Result (direct source)
draw_box(ax2, 1.5, 5.3, 7, 2, color='#E3F2FD', border=C_OUTPUT)
label(ax2, 5, 6.9, "切片结果（直接就是源码行）", size=13, bold=True, color=C_OUTPUT)

slice_chop = [
    'L0015: int x = foo(1);    // [source]',
    'L0017: println(x+y);       // [sink, D:x]',
]
multilabel(ax2, 1.8, 6.1, slice_chop, size=9.5, color=C_OUTPUT)

# Arrow 3: LLM formatting
draw_arrow(ax2, 5, 5.3, 5, 4.2, color='#9B5DE5', lw=2.2)
label(ax2, 6.3, 4.7, "模板格式化\n(标注依赖类型)", size=9, color='#9B5DE5')

# Box 4: LLM Prompt
draw_box(ax2, 1.5, 2.2, 7, 2, color='#F3E5F5', border='#7B1FA2')
label(ax2, 5, 3.8, "LLM-Ready Prompt", size=13, bold=True, color='#7B1FA2')

llm_out = [
    "## Sliced Code",
    "L0015: int x = foo(1);    // [source]",
    "L0017: println(x+y);      // [sink, D:x]",
    "## Task: Analyze this slice...",
]
multilabel(ax2, 1.8, 3.0, llm_out, size=9.5, color='#7B1FA2')

# Advantage annotations
label(ax2, 5, 1.6, "[v] 无 IR 转换：切出来就是源码行，可直接阅读", size=8.5, color=C_GOOD)
label(ax2, 5, 1.1, "[v] 无反向映射：不需要 LineNumberTable", size=8.5, color=C_GOOD)
label(ax2, 5, 0.6, "[v] 每条语句标注依赖类型 [D:x] [C]，LLM 可理解代码关联", size=8.5, color=C_GOOD)

# ══════════════════════════════════════════════════════════════════════════
# Bottom title
# ══════════════════════════════════════════════════════════════════════════
fig.suptitle("WALA vs Chop4LLM — 切片流程对比\n(以 Slice1.java: println(x+y) 为 sink 的后向切片)",
             fontsize=17, fontweight='bold', color='#212529', y=0.99)

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig(output_path, dpi=180, bbox_inches='tight',
            facecolor=fig.get_facecolor(), edgecolor='none')
plt.close()
print(f"Saved to: {output_path}")
