# -*- coding: utf-8 -*-
import docx
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

doc = Document()
style = doc.styles["Normal"]
font = style.font
font.name = "Times New Roman"
style.element.rPr.rFonts.set(qn("w:eastAsia"), "SimSun")

def h(text, level=1):
    doc.add_heading(text, level=level)

def p(text, bold=False):
    para = doc.add_paragraph()
    run = para.add_run(text)
    if bold:
        run.bold = True
    return para

def pb():
    doc.add_page_break()

# cover
doc.add_paragraph()
doc.add_paragraph()
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = title.add_run(u"Cascaded Hybrid Slicing for Fault Localization")
run.bold = True
run.font.size = Pt(24)

sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = sub.add_run(u"\u7ea7\u8054\u6df7\u5408\u5207\u7247\u6545\u969c\u5b9a\u4f4d")
run.font.size = Pt(16)
run.font.color.rgb = RGBColor(0x44, 0x44, 0x44)

sub2 = doc.add_paragraph()
sub2.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = sub2.add_run(u"\u79d1\u7814\u8fc7\u7a0b\u5168\u8bb0\u5f55")
run.font.size = Pt(14)
run.font.color.rgb = RGBColor(0x44, 0x44, 0x44)

info = doc.add_paragraph()
info.alignment = WD_ALIGN_PARAGRAPH.CENTER
info.add_run(u"\u7814\u7a76\u8d77\u59cb\uff1a2026\u5e74\u521d | \u6b63\u5f0f\u642d\u5efa\uff1a2026-05-20 | \u6587\u6863\u751f\u6210\uff1a2026-07-12")

pb()

# Ch1
h(u"\u7b2c\u4e00\u7ae0  \u7814\u7a76\u7684\u8d77\u70b9")

h(u"1.1  \u6700\u521d\u7684\u65b9\u5411", 2)
p(u"\u7814\u7a76\u8d77\u59cb\u4e8e\u5bf9\u7a0b\u5e8f\u5207\u7247\u8fd9\u4e00\u7ecf\u5178\u6280\u672f\u7684\u7cfb\u7edf\u5b66\u4e60\u3002\u7814\u7a76\u8005\u9605\u8bfb\u4e86 Weiser (1984) \u539f\u59cb\u5207\u7247\u5b9a\u4e49\u3001Ferrante \u7b49\u4eba (1987) PDG \u5f62\u5f0f\u5316\u3001Korel \u548c Laski (1988) \u52a8\u6001\u5207\u7247\u5f00\u521b\u6027\u5de5\u4f5c\u3002")
p(u"\u6838\u5fc3\u5c40\u9650\uff1a\u52a8\u6001\u540e\u5411\u5207\u7247\u662f\u4f9d\u8d56\u5173\u7cfb\u7684\u4f20\u9012\u95ed\u5305\uff0c\u65e0\u6cd5\u5728\u627e\u5230 bug \u5904\u81ea\u52a8\u505c\u6b62\uff0c\u4f1a\u4e00\u76f4\u8ffd\u6eaf\u5230\u7a0b\u5e8f\u5165\u53e3\u3002")

h(u"1.2  \u53d1\u73b0 Chop", 2)
p(u"\u5728\u63a2\u7d22\u524d\u5411\u52a0\u540e\u5411\u5207\u7247\u7ed3\u5408\u7684\u8fc7\u7a0b\u4e2d\uff0c\u53d1\u73b0\u4e86 Jackson \u548c Rollins (1994) \u7684 Chopping \u8bba\u6587\u3002Chop \u901a\u8fc7\u5f15\u5165\u4e24\u4e2a\u951a\u70b9\uff08source \u6e90\u70b9\u548c sink \u6c47\u70b9\uff09\u7ea6\u675f\u8ffd\u6eaf\u8303\u56f4\u3002\u4e0d\u662f\u7b80\u5355\u7684 forward \u4ea4 backward\uff0c\u800c\u662f PDG \u4e0a\u7684\u53d7\u9650\u53ef\u8fbe\u6027\u95ee\u9898\u3002")
p(u"\u7814\u7a76\u8005\u610f\u8bc6\u5230\uff1aChop \u7b2c\u4e8c\u4e2a\u951a\u70b9\uff08source\uff09\u672c\u8d28\u4e0a\u662f\u4e00\u4e2a\u4eba\u5de5\u8f93\u5165\u3002\u5982\u679c\u80fd\u7528 LLM \u81ea\u52a8\u63a8\u6d4b source \u5019\u9009\u70b9\uff0cChop \u5c31\u80fd\u6210\u4e3a\u4e00\u4e2a\u81ea\u52a8\u5316\u8c03\u8bd5\u5de5\u5177\u3002")

h(u"1.3  \u786e\u7acb\u65b9\u5411", 2)
p(u"\u7814\u7a76\u8005\u505a\u51fa\u5173\u952e\u51b3\u7b56\uff1a\u5c06\u53cc\u5411\u5207\u7247\uff08Chop\uff09\u4e0e LLM \u7ed3\u5408\uff0c\u63a2\u7d22\u81ea\u52a8\u5316\u8c03\u8bd5\u7684\u65b0\u8303\u5f0f\u3002\u540c\u65f6\u671f\u8c03\u7814\u4e86 WALA\u3001dg\u3001giri\u3001Slicer4J\u3001CodeQL \u7b49\u5de5\u5177\u3002")

outpath = "C:/Users/chenm/Desktop/program_slicing/paper/reports/research_process_summary.docx"
doc.save(outpath)
print("SAVED: " + outpath)