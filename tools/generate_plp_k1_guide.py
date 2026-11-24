#!/usr/bin/env python3
"""Build a Polish beginner tutorial and solution guide for the PLP K1 PDFs.

Requires: reportlab (tested with ReportLab 5.x).
Run from the repository root:
    python tools/generate_plp_k1_guide.py
"""
from __future__ import annotations

from pathlib import Path
import re
import unicodedata

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "PLP_K1_samouczek_i_rozwiazania.pdf"
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")

NAVY = colors.HexColor("#17324D")
TEAL = colors.HexColor("#087E8B")
TEAL_DARK = colors.HexColor("#075C66")
SKY = colors.HexColor("#E8F4F6")
PALE = colors.HexColor("#F3F6F9")
GOLD = colors.HexColor("#E5A323")
INK = colors.HexColor("#233247")
MUTED = colors.HexColor("#58687A")
RED = colors.HexColor("#A44343")
WHITE = colors.white
LINE = colors.HexColor("#D7E0E8")

PAGE_W, PAGE_H = A4
LEFT = 18 * mm
RIGHT = 18 * mm
TOP = 17 * mm
BOTTOM = 16 * mm
CONTENT_W = PAGE_W - LEFT - RIGHT

# Reused node colors: matching colors denote the same electrical node within a diagram.
NODE_A = colors.HexColor("#087E8B")   # teal
NODE_B = colors.HexColor("#E5A323")   # amber
NODE_C = colors.HexColor("#7353BA")   # violet
NODE_D = colors.HexColor("#48566A")   # slate / reference node


def paint_node(canvas, x, y, label, color, dx=5, dy=4, radius=3.2):
    canvas.saveState()
    canvas.setFillColor(color)
    canvas.setStrokeColor(WHITE)
    canvas.setLineWidth(1.0)
    canvas.circle(x, y, radius, fill=1, stroke=1)
    canvas.setFillColor(color)
    canvas.setFont("DejaVu-Bold", 7.6)
    canvas.drawString(x + dx, y + dy, label)
    canvas.restoreState()


# Register an embedded font with complete Polish diacritics and math symbols.
pdfmetrics.registerFont(TTFont("DejaVu", str(FONT_DIR / "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(FONT_DIR / "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DejaVuMono", str(FONT_DIR / "DejaVuSansMono.ttf")))
pdfmetrics.registerFontFamily(
    "DejaVu", normal="DejaVu", bold="DejaVu-Bold", italic="DejaVu", boldItalic="DejaVu-Bold"
)


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="BodyPL", fontName="DejaVu", fontSize=9.35, leading=13.5,
    textColor=INK, spaceAfter=5.2, allowWidows=0, allowOrphans=0,
))
styles.add(ParagraphStyle(
    name="BodyCompact", parent=styles["BodyPL"], fontSize=8.85, leading=12.1,
    spaceAfter=3.6,
))
styles.add(ParagraphStyle(
    name="SmallPL", fontName="DejaVu", fontSize=7.6, leading=10.3,
    textColor=MUTED, spaceAfter=3,
))
styles.add(ParagraphStyle(
    name="H1PL", fontName="DejaVu-Bold", fontSize=17.0, leading=21.0,
    textColor=NAVY, spaceBefore=3, spaceAfter=9, keepWithNext=True,
))
styles.add(ParagraphStyle(
    name="H2PL", fontName="DejaVu-Bold", fontSize=11.6, leading=15.0,
    textColor=TEAL_DARK, spaceBefore=8, spaceAfter=4.5, keepWithNext=True,
))
styles.add(ParagraphStyle(
    name="H3PL", fontName="DejaVu-Bold", fontSize=10.0, leading=13,
    textColor=NAVY, spaceBefore=5, spaceAfter=3, keepWithNext=True,
))
styles.add(ParagraphStyle(
    name="EqPL", fontName="DejaVu", fontSize=9.15, leading=13.0,
    textColor=NAVY, spaceAfter=0,
))
styles.add(ParagraphStyle(
    name="BoxPL", fontName="DejaVu", fontSize=8.8, leading=12.4,
    textColor=INK, spaceAfter=0,
))
styles.add(ParagraphStyle(
    name="BoxTitlePL", fontName="DejaVu-Bold", fontSize=8.6, leading=11.0,
    textColor=TEAL_DARK, spaceAfter=2,
))
styles.add(ParagraphStyle(
    name="CoverKicker", fontName="DejaVu-Bold", fontSize=9.6, leading=13,
    textColor=colors.HexColor("#8FE2E7"), spaceAfter=5,
))
styles.add(ParagraphStyle(
    name="CoverTitle", fontName="DejaVu-Bold", fontSize=27, leading=32,
    textColor=WHITE, spaceAfter=6,
))
styles.add(ParagraphStyle(
    name="CoverSub", fontName="DejaVu", fontSize=13.2, leading=19,
    textColor=colors.HexColor("#EAF3FA"), spaceAfter=8,
))
styles.add(ParagraphStyle(
    name="CoverMeta", fontName="DejaVu", fontSize=9.2, leading=13.4,
    textColor=INK, spaceAfter=5,
))
styles.add(ParagraphStyle(
    name="TOCHeading", fontName="DejaVu-Bold", fontSize=19, leading=24,
    textColor=NAVY, spaceAfter=15,
))
styles.add(ParagraphStyle(
    name="BulletPL", parent=styles["BodyPL"], leftIndent=12, firstLineIndent=-8,
    bulletIndent=0, spaceAfter=3.3,
))
styles.add(ParagraphStyle(
    name="TableHeadPL", fontName="DejaVu-Bold", fontSize=8.1, leading=10.4,
    textColor=WHITE,
))
styles.add(ParagraphStyle(
    name="TableCellPL", fontName="DejaVu", fontSize=7.85, leading=10.5,
    textColor=INK,
))
styles.add(ParagraphStyle(
    name="TableCellBoldPL", fontName="DejaVu-Bold", fontSize=7.85, leading=10.5,
    textColor=INK,
))


def P(text: str, style: str = "BodyPL") -> Paragraph:
    return Paragraph(text, styles[style])


def H1(text: str) -> Paragraph:
    return P(text, "H1PL")


def H2(text: str) -> Paragraph:
    return P(text, "H2PL")


def H3(text: str) -> Paragraph:
    return P(text, "H3PL")


def bullet(text: str) -> Paragraph:
    return Paragraph("• " + text, styles["BulletPL"])


def eqbox(text: str, bg=PALE, accent=TEAL) -> Table:
    cell = Paragraph(text.replace("\n", "<br/>"), styles["EqPL"])
    t = Table([[cell]], colWidths=[CONTENT_W], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.45, LINE),
        ("LINEBEFORE", (0, 0), (0, -1), 3, accent),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def callout(title: str, text: str, kind: str = "tip") -> Table:
    if kind == "warn":
        bg, accent = colors.HexColor("#FFF4EC"), GOLD
    elif kind == "answer":
        bg, accent = colors.HexColor("#EAF5EF"), colors.HexColor("#39845B")
    else:
        bg, accent = SKY, TEAL
    inner = [Paragraph(title, styles["BoxTitlePL"]), Paragraph(text, styles["BoxPL"])]
    t = Table([[inner]], colWidths=[CONTENT_W], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.45, LINE),
        ("LINEBEFORE", (0, 0), (0, -1), 3, accent),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return t


def info_table(rows, widths=None, header=True):
    data = []
    for ri, row in enumerate(rows):
        out = []
        for value in row:
            if isinstance(value, Flowable):
                out.append(value)
            else:
                sty = "TableHeadPL" if header and ri == 0 else "TableCellPL"
                out.append(P(str(value), sty))
        data.append(out)
    if widths is None:
        widths = [CONTENT_W / len(rows[0])] * len(rows[0])
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    cmds = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.35, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if header:
        cmds.extend([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PALE]),
        ])
    else:
        cmds.append(("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, PALE]))
    t.setStyle(TableStyle(cmds))
    return t


class SymbolDiagram(Flowable):
    def __init__(self, width=CONTENT_W, height=91):
        super().__init__()
        self.width, self.height = width, height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return self.width, self.height

    def _arrow(self, c, x1, y1, x2, y2, color=NAVY, head=5):
        c.setStrokeColor(color)
        c.setFillColor(color)
        c.setLineWidth(1.4)
        c.line(x1, y1, x2, y2)
        import math
        a = math.atan2(y2 - y1, x2 - x1)
        p1 = (x2, y2)
        p2 = (x2 - head * math.cos(a - 0.48), y2 - head * math.sin(a - 0.48))
        p3 = (x2 - head * math.cos(a + 0.48), y2 - head * math.sin(a + 0.48))
        path = c.beginPath()
        path.moveTo(*p1); path.lineTo(*p2); path.lineTo(*p3); path.close()
        c.drawPath(path, fill=1, stroke=0)

    def draw(self):
        c = self.canv
        c.saveState()
        c.setFillColor(PALE); c.setStrokeColor(LINE)
        c.roundRect(0, 0, self.width, self.height, 6, fill=1, stroke=1)
        col = self.width / 4
        labels = ["E — źródło napięcia", "J — źródło prądu", "źródło sterowane", "R — rezystor"]
        for i, lab in enumerate(labels):
            x0 = col * i
            cx = x0 + col / 2
            c.setStrokeColor(NAVY); c.setFillColor(WHITE); c.setLineWidth(1.3)
            if i < 2:
                c.circle(cx, 54, 13, fill=1, stroke=1)
                if i == 0:
                    c.setFont("DejaVu-Bold", 11); c.setFillColor(TEAL_DARK)
                    c.drawCentredString(cx, 51, "+")
                    c.drawCentredString(cx, 39, "−")
                else:
                    self._arrow(c, cx, 46, cx, 62, TEAL_DARK, 5)
            elif i == 2:
                path = c.beginPath(); path.moveTo(cx, 69); path.lineTo(cx + 15, 54); path.lineTo(cx, 39); path.lineTo(cx - 15, 54); path.close()
                c.setFillColor(WHITE); c.drawPath(path, fill=1, stroke=1)
                self._arrow(c, cx - 6, 48, cx + 6, 60, TEAL_DARK, 4)
            else:
                c.roundRect(cx - 20, 47, 40, 14, 2, fill=1, stroke=1)
            c.setFont("DejaVu", 7.3); c.setFillColor(INK)
            c.drawCentredString(cx, 17, lab)
        c.restoreState()


class SourceConversionDiagram(Flowable):
    def __init__(self, width=CONTENT_W, height=126):
        super().__init__(); self.width, self.height = width, height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return self.width, self.height

    def _res(self, c, x, y, w, h, label):
        c.setStrokeColor(NAVY); c.setFillColor(WHITE); c.setLineWidth(1.3)
        c.roundRect(x, y, w, h, 2, fill=1, stroke=1)
        c.setFont("DejaVu", 8); c.setFillColor(INK)
        c.drawCentredString(x + w / 2, y + h / 2 - 3, label)

    def _arrow(self, c, x1, y1, x2, y2):
        import math
        c.setStrokeColor(TEAL); c.setFillColor(TEAL); c.setLineWidth(1.5)
        c.line(x1, y1, x2, y2)
        a = math.atan2(y2-y1, x2-x1); h=5
        p=c.beginPath(); p.moveTo(x2,y2); p.lineTo(x2-h*math.cos(a-.5),y2-h*math.sin(a-.5)); p.lineTo(x2-h*math.cos(a+.5),y2-h*math.sin(a+.5)); p.close(); c.drawPath(p,fill=1,stroke=0)

    def draw(self):
        c=self.canv; c.saveState()
        c.setFillColor(PALE); c.setStrokeColor(LINE); c.roundRect(0,0,self.width,self.height,6,fill=1,stroke=1)
        half=self.width/2; y0=40; y1=91; ym=(y0+y1)/2
        c.setStrokeColor(NAVY); c.setLineWidth(1.2)
        # Thévenin: the open A-B port is on the right; E and R are in series.
        sx=23; rleft=58; rwidth=48; port=140
        c.line(sx,y0,sx,ym-11); c.line(sx,ym+11,sx,y1)
        c.circle(sx,ym,11,fill=0,stroke=1)
        c.setFont("DejaVu-Bold",7.2); c.setFillColor(TEAL_DARK)
        c.drawCentredString(sx,ym+2.5,"+"); c.drawCentredString(sx,ym-7.5,"−")
        c.setFont("DejaVu-Bold",7.0); c.drawString(sx-17,ym-2,"E")
        c.line(sx,y1,rleft,y1); self._res(c,rleft,y1-7,rwidth,14,"R")
        c.line(rleft+rwidth,y1,port,y1); c.line(sx,y0,port,y0)
        paint_node(c,port,y1,"A",NODE_A,dx=4,dy=3)
        paint_node(c,port,y0,"B",NODE_B,dx=4,dy=-10)
        c.setFont("DejaVu",8); c.setFillColor(INK); c.drawCentredString(half/2,18,"Thévenin: E szeregowo z R")
        # Norton: same two port nodes A/B, J and R are parallel.
        xr=half+28; branch_j=xr+25; branch_r=xr+116; port2=xr+151
        c.line(branch_j,y1,branch_r,y1); c.line(branch_j,y0,branch_r,y0)
        c.line(branch_j,y0,branch_j,ym-11); c.line(branch_j,ym+11,branch_j,y1)
        c.circle(branch_j,ym,11,fill=0,stroke=1); self._arrow(c,branch_j,ym-6,branch_j,ym+6)
        self._res(c,branch_r-7,ym-13,14,26,"R")
        c.line(branch_r,y1,port2,y1); c.line(branch_r,y0,port2,y0)
        paint_node(c,port2,y1,"A",NODE_A,dx=4,dy=3)
        paint_node(c,port2,y0,"B",NODE_B,dx=4,dy=-10)
        c.setFont("DejaVu",8); c.setFillColor(INK); c.drawCentredString(half+half/2,18,"Norton: J=E/R równolegle z R")
        c.setFont("DejaVu-Bold",9); c.setFillColor(TEAL_DARK); c.drawCentredString(half,ym,"⇔")
        c.restoreState()


class DeltaStarDiagram(Flowable):
    def __init__(self, width=CONTENT_W, height=142):
        super().__init__(); self.width, self.height = width, height

    def wrap(self, aw, ah):
        self.width=min(self.width,aw); return self.width,self.height

    def draw(self):
        c=self.canv; c.saveState(); c.setStrokeColor(NAVY); c.setFillColor(INK); c.setLineWidth(1.5)
        # Delta, left half.
        cx=self.width*0.25
        A=(cx,111); B=(cx-62,35); C=(cx+62,35)
        for u,v in [(A,B),(B,C),(C,A)]: c.line(u[0],u[1],v[0],v[1])
        node_colors={"A":NODE_A,"B":NODE_B,"C":NODE_C}
        for name,(x,y) in zip(["A","B","C"],[A,B,C]):
            paint_node(c,x,y,name,node_colors[name],dx=5,dy=3)
        c.setFont("DejaVu",8); c.drawCentredString(cx-34,77,"R_AB"); c.drawCentredString(cx,26,"R_BC"); c.drawCentredString(cx+35,77,"R_CA")
        c.setFont("DejaVu-Bold",8.5); c.drawCentredString(cx,9,"Δ: trzy boki")
        # Star, right half. A/B/C keep their colors after the transformation.
        sx=self.width*0.75; O=(sx,67); S_A=(sx,111); S_B=(sx-62,35); S_C=(sx+62,35)
        for q in [S_A,S_B,S_C]: c.line(O[0],O[1],q[0],q[1])
        for name,(x,y) in zip(["A","B","C"],[S_A,S_B,S_C]):
            paint_node(c,x,y,name,node_colors[name],dx=5,dy=3)
        paint_node(c,O[0],O[1],"O",NODE_D,dx=5,dy=3)
        c.setFont("DejaVu",8); c.drawCentredString(sx-18,90,"R_A"); c.drawCentredString(sx-34,47,"R_B"); c.drawCentredString(sx+34,47,"R_C")
        c.setFont("DejaVu-Bold",8.5); c.drawCentredString(sx,9,"Y: trzy ramiona")
        c.restoreState()


class OpAmpDiagram(Flowable):
    def __init__(self, width=CONTENT_W, height=130):
        super().__init__(); self.width,self.height=width,height
    def wrap(self,aw,ah): self.width=min(self.width,aw); return self.width,self.height
    def draw(self):
        c=self.canv; c.saveState(); c.setStrokeColor(NAVY); c.setFillColor(WHITE); c.setLineWidth(1.4)
        x=160; y=65
        p=c.beginPath(); p.moveTo(x-18,y-40); p.lineTo(x-18,y+40); p.lineTo(x+62,y); p.close(); c.drawPath(p,fill=1,stroke=1)
        c.setFont("DejaVu-Bold",10); c.setFillColor(TEAL_DARK); c.drawString(x-8,y+17,"−"); c.drawString(x-8,y-26,"+")
        c.setStrokeColor(NAVY); c.setFillColor(INK); c.setFont("DejaVu",8.3)
        c.line(x-70,y+20,x-18,y+20); c.drawString(x-96,y+17,"u₋")
        c.line(x-70,y-20,x-18,y-20); c.drawString(x-96,y-23,"u₊")
        c.line(x+62,y,x+122,y); c.drawString(x+126,y-3,"u_out")
        for nx,ny,nc in [(x-70,y+20,NODE_A),(x-70,y-20,NODE_B),(x+122,y,NODE_C)]:
            c.setFillColor(nc); c.setStrokeColor(WHITE); c.setLineWidth(1); c.circle(nx,ny,3.3,fill=1,stroke=1)
        c.setFont("DejaVu",8); c.setFillColor(MUTED); c.drawCentredString(x+22,y-3,"A")
        c.drawCentredString(self.width*0.72,18,"Idealny model: I₊ = I₋ = 0; przy ujemnym sprzężeniu u₊ ≈ u₋")
        c.restoreState()


class ManualDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        cover_frame = Frame(LEFT, BOTTOM, CONTENT_W, PAGE_H - TOP - BOTTOM,
                            leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id="cover")
        body_frame = Frame(LEFT, BOTTOM, CONTENT_W, PAGE_H - TOP - BOTTOM,
                           leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id="body")
        self.addPageTemplates([
            PageTemplate(id="Cover", frames=[cover_frame], onPage=self.draw_cover),
            PageTemplate(id="Body", frames=[body_frame], onPage=self.draw_body),
        ])
        self._heading_counter = 0

    def draw_cover(self, canvas, doc):
        canvas.saveState()
        canvas.setFillColor(colors.HexColor("#F7FAFC")); canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        canvas.setFillColor(NAVY); canvas.rect(0, PAGE_H - 105 * mm, PAGE_W, 105 * mm, fill=1, stroke=0)
        canvas.setFillColor(TEAL); canvas.rect(0, PAGE_H - 108 * mm, PAGE_W, 3 * mm, fill=1, stroke=0)
        # A quiet circuit motif at the upper-right of the dark band.
        canvas.setStrokeColor(colors.HexColor("#3A657E")); canvas.setLineWidth(1.1)
        pts=[(PAGE_W-78*mm,PAGE_H-23*mm),(PAGE_W-43*mm,PAGE_H-23*mm),(PAGE_W-43*mm,PAGE_H-58*mm),(PAGE_W-18*mm,PAGE_H-58*mm)]
        for a,b in zip(pts,pts[1:]): canvas.line(a[0],a[1],b[0],b[1])
        for x,y in [pts[0],pts[1],pts[2],pts[3]]:
            canvas.setFillColor(GOLD if (x,y)==pts[2] else TEAL)
            canvas.circle(x,y,2.5*mm,fill=1,stroke=0)
        canvas.setFillColor(TEAL_DARK); canvas.roundRect(LEFT, 25*mm, PAGE_W-LEFT-RIGHT, 28*mm, 4*mm, fill=1, stroke=0)
        canvas.setFont("DejaVu", 8.2); canvas.setFillColor(WHITE)
        canvas.drawString(LEFT+7*mm, 43*mm, "OPRACOWANIE WŁASNE • PLP K1")
        canvas.drawString(LEFT+7*mm, 34*mm, "Podstawy, algorytmy i rozwiązania zadań z obu plików PDF")
        canvas.setFont("DejaVu", 7.5); canvas.setFillColor(MUTED)
        canvas.drawRightString(PAGE_W-RIGHT, 14*mm, "Lublin · 2026")
        canvas.restoreState()

    def draw_body(self, canvas, doc):
        canvas.saveState()
        canvas.setFillColor(WHITE); canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        canvas.setStrokeColor(LINE); canvas.setLineWidth(0.6)
        canvas.line(LEFT, PAGE_H-10*mm, PAGE_W-RIGHT, PAGE_H-10*mm)
        canvas.setFont("DejaVu-Bold", 7.4); canvas.setFillColor(NAVY)
        canvas.drawString(LEFT, PAGE_H-7.5*mm, "PLP K1  ·  OBWODY PRĄDU STAŁEGO")
        canvas.setFont("DejaVu", 7.2); canvas.setFillColor(MUTED)
        canvas.drawRightString(PAGE_W-RIGHT, PAGE_H-7.5*mm, "Samouczek i rozwiązania")
        canvas.line(LEFT, 10*mm, PAGE_W-RIGHT, 10*mm)
        canvas.setFont("DejaVu", 7.2); canvas.setFillColor(MUTED)
        canvas.drawString(LEFT, 6.5*mm, "Wynik ujemny oznacza kierunek przeciwny do przyjętej strzałki.")
        canvas.drawRightString(PAGE_W-RIGHT, 6.5*mm, f"str. {doc.page}")
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if not isinstance(flowable, Paragraph):
            return
        style_name = flowable.style.name
        if style_name not in ("H1PL", "H2PL"):
            return
        text = flowable.getPlainText()
        level = 0 if style_name == "H1PL" else 1
        normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
        slug = re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")
        key = f"bookmark-{slug}"
        self.canv.bookmarkPage(key)
        try:
            self.canv.addOutlineEntry(text, key, level=level, closed=False)
        except ValueError:
            pass


def make_task(title: str, ref: str, data: str, steps: list[str], answer: str, note: str | None = None):
    story = [H2(title), P(f"<font color='#58687A'><b>Źródło:</b> {ref}</font>", "SmallPL"),
             callout("Dane i szukana", data)]
    story.extend(P(s) for s in steps)
    story.append(callout("Wynik", answer, "answer"))
    if note:
        story.append(Spacer(1, 4))
        story.append(callout("Uwaga metodyczna", note, "tip"))
    story.append(Spacer(1, 7))
    return [KeepTogether(story)]


def build_story():
    story = []
    # Cover.
    story += [Spacer(1, 25*mm),
              P("SAMOUCZEK + AUTORSKIE ROZWIĄZANIA", "CoverKicker"),
              P("Obwody prądu stałego", "CoverTitle"),
              P("PLP K1 · od pierwszego węzła do źródła Thevenina", "CoverSub"),
              Spacer(1, 11*mm),
              callout("Co znajdziesz w środku", "Przystępny kurs podstaw, uniwersalny algorytm rozwiązywania oraz krok po kroku opracowane zadania z zestawów K, L, O, P i skanów z notatek.", "tip"),
              Spacer(1, 8*mm),
              P("Opracowanie przygotowane od nowa na podstawie plików <b>plp_k1_packed.pdf</b> i <b>plp_k1_packed0.pdf</b>. Zawiera 14 rozpoznanych zadań oraz 2 dodatkowe przykłady z notatek. Zduplikowane skany rozwiązano tylko raz.", "CoverMeta"),
              P("Najważniejsza konwencja: strzałka prądu wyznacza dodatni kierunek odniesienia. Wynik ujemny nie jest błędem — mówi, że rzeczywisty prąd płynie przeciwnie.", "CoverMeta"),
              NextPageTemplate("Body"), PageBreak()]

    # Contents (static page references keep layout stable; PDF outline entries are also added).
    toc_rows = [
        ["Rozdział", "Zakres", "str."],
        [P("Jak korzystać z opracowania", "TableCellBoldPL"),
         "Pliki źródłowe, zakres i konwencja znaków", "3"],
        [P("Samouczek dla początkujących", "TableCellBoldPL"),
         "Podstawy obwodów, prawa Kirchhoffa, metody oraz elementy nieliniowe i WO", "4"],
        [P("A. Superpozycja i redukcje", "TableCellBoldPL"),
         "Przykład z notatek, zestawy K/L/O/P i mostek", "8"],
        [P("B. Thévenin i Norton", "TableCellBoldPL"),
         "Rozwiązania symboliczne, źródła sterowane i obciążenie", "11"],
        [P("C. Metoda węzłowa", "TableCellBoldPL"),
         "Zadanie z trójkąta źródeł i konduktancjami", "17"],
        [P("Tabela wyników", "TableCellBoldPL"),
         "Zbiorcze odpowiedzi i końcowa lista kontrolna", "18"],
    ]
    story += [P("Spis treści", "TOCHeading"),
              info_table(toc_rows, [58*mm, CONTENT_W-75*mm, 17*mm]),
              Spacer(1, 8),
              callout("Nawigacja", "Główne rozdziały i podrozdziały są także dostępne w panelu zakładek PDF. Tabela poniżej podaje strony startowe najważniejszych części."),
              PageBreak()]

    # Scope, notation, source inventory.
    story += [H1("Jak korzystać z opracowania"),
              P("Najpierw przejdź przez krótki samouczek, a potem wybieraj rozwiązanie według typu zadania: superpozycja dla kilku niezależnych źródeł, metoda węzłowa dla układów z czytelnymi węzłami, a Thevenin/Norton wtedy, gdy trzeba opisać dwójnik widziany z zacisków."),
              P("Wszystkie prądy i napięcia są wielkościami ze zwrotem odniesienia. W obliczeniach nie poprawiamy strzałek po fakcie — zapisujemy znak wyniku i dopiero go interpretujemy."),
              info_table([
                  ["Materiał", "Zakres wykorzystany w poradniku"],
                  ["plp_k1_packed.pdf", "25 stron: zestawy K/L/O/P, notatki odręczne i cztery końcowe skany zadań."],
                  ["plp_k1_packed0.pdf", "21 stron; merytorycznie powtarza wcześniejszy materiał z pierwszego pliku."],
                  ["Powtórzenia", "Końcowe strony 22 i 24 oraz 23 i 25 pierwszego PDF-u są powtórzonymi skanami. Każde z dwóch zadań policzono raz."],
              ], [38*mm, CONTENT_W-38*mm]),
              Spacer(1, 6),
              H2("Konwencja znaków używana w rozwiązaniach"),
              P("Dla napięcia między węzłami A i B zapis <b>u_AB = V_A − V_B</b> oznacza, że A jest biegunem dodatnim. Strzałka źródła napięcia oznacza wzrost potencjału w kierunku grotu. Dla rezystora zawsze dopisujemy, jaki kierunek prądu i napięcia przyjęliśmy."),
              eqbox("Jeśli obliczone I = −0,25 mA przy strzałce w prawo, to rzeczywisty prąd ma wartość 0,25 mA i płynie w lewo."),
              Spacer(1, 5),
              P("Notacja: E — idealne źródło napięcia (SEM), J — idealne źródło prądu, R — rezystancja, G=1/R — konduktancja, g — transkonduktancja (A/V = S), r — współczynnik o wymiarze oma przy źródle sterowanym prądem. Zapis k=1 V/V albo β=3 mA/mA oznacza wzmocnienie bezwymiarowe."),
              PageBreak()]

    # Tutorial.
    story += [H1("Samouczek dla początkujących"),
              P("Nie zakładam wcześniejszej znajomości elektrotechniki. W każdym zadaniu zacznij od schematu i jednostek; dopiero potem wybieraj wzór."),
              H2("1. Węzeł, gałąź, oczko i zwroty"),
              P("<b>Węzeł</b> to zbiór punktów połączonych idealnym przewodem — mają ten sam potencjał. <b>Gałąź</b> łączy dwa węzły i może zawierać jeden lub kilka szeregowych elementów; w jej nie rozgałęzionej części płynie ten sam prąd. <b>Oczko</b> jest zamkniętą drogą w obwodzie, a <b>oczko elementarne (siatka)</b> nie zawiera w środku innego oczka."),
              P("Prąd w gałęzi przyjmujemy jako dodatni w narysowanym kierunku. Napięcie węzła zawsze mierzymy względem wybranego węzła odniesienia (zwykle masy, 0 V). Napięcie elementu to różnica potencjałów jego końców."),
              SymbolDiagram(),
              H2("2. Prawo Ohma, konduktancja, moc i liniowość"),
              eqbox("u = R i     ·     i = u/R = G u     ·     G = 1/R     ·     P = u i = i²R = u²/R"),
              P("Prawo Ohma dotyczy rezystora o stałej rezystancji R. Jednostki: Ω (om), S (siemens), V (wolt), A (amper). Przy kierunkach zgodnych z konwencją pasywną prąd wpływa do dodatniego zacisku napięcia, a moc P>0 oznacza pobór energii."),
              P("Obwód jest <b>liniowy</b>, jeśli zależności elementów są liniowe: np. stały rezystor oraz źródła sterowane proporcjonalne do napięcia lub prądu. Liniowość pozwala dodawać odpowiedzi (superpozycja). Dioda nie jest liniowa w całym zakresie."),
              eqbox("Szybkie przeliczniki: 1 kΩ · 1 mA = 1 V; 1 V / 1 kΩ = 1 mA; 1 mS · 1 V = 1 mA."),
              H2("3. Połączenia szeregowe i równoległe"),
              P("<b>Szeregowo:</b> elementy mają wspólny węzeł, do którego nie dochodzi żadna inna gałąź; płynie przez nie ten sam prąd. <b>Równolegle:</b> oba końce każdego elementu są przyłączone do tych samych dwóch węzłów; napięcie jest takie samo."),
              eqbox("R_sz = R₁ + R₂ + …     ;     1/R_równ = 1/R₁ + 1/R₂ + …     ;     dla dwóch: R₁ ∥ R₂ = R₁R₂/(R₁+R₂)"),
              P("Nie oceniaj po wyglądzie rysunku: o szeregu i równoległości decydują węzły, nie to, czy symbole są narysowane obok siebie."),
              H2("4. Dzielnik napięcia i dzielnik prądu"),
              P("Dwa rezystory szeregowe zasilone napięciem E dzielą napięcie proporcjonalnie do rezystancji. W dzielniku prądu prąd rozdziela się odwrotnie proporcjonalnie do oporów."),
              eqbox("Dzielnik napięcia:  u_R₂ = E · R₂/(R₁+R₂).   Dzielnik prądu (dwie gałęzie):  i_R₁ = I · R₂/(R₁+R₂)."),
              callout("Uwaga na obciążenie", "Jeśli do R₂ dołączono obciążenie R_L, najpierw zastąp dolny fragment przez R₂ ∥ R_L. Wzór bez obciążenia zwykle wtedy przestaje dawać poprawny wynik."),
              PageBreak()]

    story += [H2("5. Źródła niezależne i sterowane"),
              P("Źródło <b>niezależne</b> ma zadaną wartość E albo J. Źródło <b>sterowane</b> zależy od innej wielkości obwodu; na schemacie ma zwykle romb. Przykłady: g·u (źródło prądowe sterowane napięciem), k·u (źródło napięciowe sterowane napięciem), β·i (źródło prądowe sterowane prądem), r·i (źródło napięciowe sterowane prądem)."),
              P("Parametry muszą mieć poprawne jednostki: g w siemensach, r w omach, a wzmocnienia k i β w V/V albo A/A. Źródło sterowane nie jest „kolejnym niezależnym źródłem” — jego wartość trzeba za każdym razem wyznaczyć z wielkości sterującej."),
              SourceConversionDiagram(),
              H2("6. Zastępowanie źródeł napięciowych i prądowych"),
              P("Źródło E w szeregu z R można zastąpić źródłem prądu J=E/R równoległym z tym samym R. Odwrotnie, źródło J równoległe z R można zastąpić źródłem napięcia E=JR w szeregu z R. Oba modele mają identyczną charakterystykę widzianą z tych samych dwóch zacisków."),
              P("Przy przekształceniu pilnuj biegunowości: grot źródła prądowego wskazuje kierunek dodatniego prądu; jego odpowiednik napięciowy ma „+” po stronie, do której wpływa ten prąd przez rezystor."),
              H2("7. Prawa Kirchhoffa"),
              eqbox("I prawo (KCL, prądowe): suma prądów wpływających do węzła = suma prądów wypływających.\nII prawo (KVL, napięciowe): algebraiczna suma napięć w każdym zamkniętym oczku = 0."),
              P("To są prawa zachowania ładunku i energii. Znak zapisujemy według przyjętych strzałek. Jeśli w węźle wszystkie prądy przyjmiemy jako wypływające, zapisujemy ich sumę równą zero."),
              H2("8. Metoda węzłowa — najpewniejsza przy źródłach prądu"),
              P("<b>Algorytm:</b> (1) wybierz węzeł odniesienia; (2) oznacz napięcia pozostałych węzłów; (3) każdą gałąź rezystancyjną zapisz jako (V_a−V_b)/R albo G(V_a−V_b); (4) napisz KCL w każdym nieodniesionym węźle; (5) rozwiąż układ równań i wyznacz szukaną gałąź."),
              eqbox("Przykład: źródło J wstrzykuje prąd do węzła V, a R₁ i R₂ łączą ten węzeł z masą.\nJ = V/R₁ + V/R₂  ⇒  V = J/(1/R₁+1/R₂) = J(R₁ ∥ R₂)."),
              P("Idealne źródło napięcia między dwoma nieodniesionymi węzłami tworzy <b>węzeł super</b>: piszemy KCL dla całej otoczki, a dodatkowo równanie różnicy potencjałów narzucone przez źródło."),
              PageBreak()]

    story += [H2("9. Metoda oczkowa"),
              P("Metoda oczkowa jest wygodna w obwodach planarnych z niewielką liczbą oczek. Przyjmij prądy oczkowe (np. wszystkie zgodnie z ruchem wskazówek zegara), a następnie zapisz KVL dla każdego oczka. Na rezystorze wspólnym dwóch oczek spadek w równaniu oczka 1 wynosi R(I₁−I₂)."),
              P("Gdy źródło prądu leży na brzegu oczka, prąd oczkowy jest znany (z właściwym znakiem). Gdy leży między dwoma oczkami, twórz superoczko i dodaj równanie wiążące prądy oczkowe. Przy źródle sterowanym dopisz jego zależność od wielkości sterującej."),
              H2("10. Metoda superpozycji"),
              P("Działa dla <b>liniowego</b> obwodu z kilkoma źródłami niezależnymi. Rozpatrujemy jedno niezależne źródło naraz, wyznaczamy jego wkład do tej samej szukanej wielkości i dodajemy wkłady algebraicznie."),
              eqbox("Przy pozostawieniu jednego źródła: idealne E → zwarcie; idealne J → rozwarcie.\nŹródła sterowane pozostają aktywne. Rezystory pozostają na miejscu."),
              P("Nie sumuje się mocy wprost: najpierw sumujemy napięcia lub prądy, a moc liczymy z końcowej wartości. Jeśli wkład źródła jest przeciwny do strzałki, zapisujemy go ze znakiem minus."),
              H2("11. Źródła zastępcze Thévenina i Nortona"),
              P("Każdy liniowy dwójnik widziany z zacisków A–B można zastąpić równoważnie źródłem napięciowym E_T w szeregu z R_w albo źródłem prądowym J_N równolegle z tym samym R_w."),
              eqbox("E_T = U_AB przy rozwarciu;     J_N = I_AB przy zwarciu;     R_w = E_T/J_N.\nJeśli znasz E_T i R_w: J_N = E_T/R_w. Jeśli znasz J_N i R_w: E_T = J_N R_w."),
              P("<b>R_w bez źródeł sterowanych:</b> wyzeruj źródła niezależne (E zwarciem, J rozwarciem) i policz rezystancję widzianą z zacisków. <b>Jeśli w obwodzie jest źródło sterowane:</b> go nie wyłączaj. Wyzeruj tylko źródła niezależne, przyłóż źródło testowe U_x lub I_x i policz R_w=U_x/I_x."),
              callout("Najczęstszy błąd", "Źródło zależne zostaje aktywne także przy wyznaczaniu R_w. Wyłączenie go może dać błędną rezystancję, a nawet zniszczyć zależność portu." , "warn"),
              H2("12. Transformacja trójkąt–gwiazda"),
              P("Używaj jej, gdy rezystory nie redukują się bezpośrednio szeregowo ani równolegle (np. mostek). Dla trójkąta o bokach R_AB, R_BC, R_CA suma boków S=R_AB+R_BC+R_CA."),
              eqbox("Δ → Y:  R_A = R_AB·R_CA/S;   R_B = R_AB·R_BC/S;   R_C = R_BC·R_CA/S.\nY → Δ:  R_AB = R_A+R_B+(R_A R_B)/R_C  (pozostałe wzory przez permutację)."),
              DeltaStarDiagram(),
              P("Przykład: symetryczny Δ z trzema bokami 3 kΩ daje gwiazdę z trzema ramionami 1 kΩ. Po transformacji ponownie sprawdź, czy powstał szereg lub równoległość."),
              PageBreak()]

    story += [H2("13. Punkt pracy i rezystancja skuteczna / dynamiczna"),
              P("Dla elementu nieliniowego (np. diody) zależność U–I nie jest prostą. <b>Punkt pracy Q</b> to para (U_Q, I_Q) ustalona przez przecięcie charakterystyki elementu z prostą obciążenia reszty obwodu."),
              eqbox("Rezystancja statyczna (ilorazowa) w punkcie Q:  R_Q = U_Q/I_Q.\nRezystancja dynamiczna (małosygnałowa):  r_d = dU/dI|_Q ≈ ΔU/ΔI w pobliżu Q."),
              P("R_Q to nachylenie siecznej od początku układu do Q; r_d to nachylenie stycznej w punkcie Q. Dla idealnego rezystora liniowego obie wartości są równe R. W niektórych materiałach „rezystancja skuteczna” oznacza iloraz U/I w danym punkcie pracy — nie myl jej z wartością skuteczną napięcia przemiennego."),
              P("Przy małych zmianach wokół Q element nieliniowy można lokalnie przybliżyć rezystorem r_d. To przybliżenie jest poprawne tylko blisko wybranego punktu pracy."),
              H2("14. Wzmacniacz operacyjny — minimum potrzebne na K1"),
              OpAmpDiagram(),
              P("W idealnym wzmacniaczu operacyjnym prądy wejściowe są zerowe. Jeśli działa ujemne sprzężenie zwrotne i wyjście nie jest nasycone, napięcia wejść są prawie równe: u₊≈u₋ (tzw. zwarcie wirtualne). To nie jest fizyczne zwarcie wejść — oznacza tylko równe potencjały."),
              eqbox("Odwracający:  u_out = −(R_f/R_in)u_in.\nNieodwracający:  u_out = (1+R_f/R_g)u_in.   Wtórnik:  u_out≈u_in."),
              P("Jeśli brak ujemnego sprzężenia lub wyjście osiągnie ograniczenie zasilania, nie wolno automatycznie zakładać u₊=u₋. W przeglądanych zadaniach nie ma osobnego zadania z WO; temat jest tu ujęty jako część listy do nauki."),
              H2("15. Uniwersalny algorytm rozwiązywania"),
              info_table([
                  ["Krok", "Co zrobić"],
                  ["1. Odczyt", "Zapisz dane, szukaną wielkość, zaciski i wszystkie strzałki."],
                  ["2. Jednostki", "Ujednolić przed liczeniem (np. kΩ, mA, V); pamiętać kΩ·mA=V."],
                  ["3. Uproszczenie", "Najpierw rozpoznaj szereg/równoległość i idealne zwarcia/rozwarcia."],
                  ["4. Wybór metody", "Wiele źródeł → superpozycja; wiele węzłów → metoda węzłowa; mało oczek → oczkowa; dwójnik → Thévenin/Norton."],
                  ["5. Znaki", "Ustal kierunki, pisz równania Kirchhoffa, nie zmieniaj strzałek w trakcie."],
                  ["6. Kontrola", "Sprawdź jednostki, znak, graniczny sens wyniku i równoważność E_T=J_N R_w."],
              ], [25*mm, CONTENT_W-25*mm]),
              Spacer(1,5),
              callout("Wybór metody", "Jeśli nie wiesz od czego zacząć: metoda węzłowa jest uniwersalna. Superpozycja i redukcje są szybsze, gdy układ ma czytelną symetrię lub źródła dają się wyłączać bez komplikowania schematu."),
              PageBreak()]

    # Solutions part A.
    story += [H1("Rozwiązania krok po kroku"),
              P("Wyniki podano względem strzałek na oryginalnych rysunkach. Dodatkowo pokazuję kontrolę jednostek i to, dlaczego znak ma sens."),
              H2("A. Prądy i napięcia — superpozycja / redukcje")]

    story += make_task(
        "Przykład z notatek: pięć rezystorów i dwa źródła",
        "plp_k1_packed.pdf, s. 5–6 (odręczne rozwiązanie)",
        "R₁=1 kΩ, R₂=2 kΩ, R₃=3 kΩ, R₄=4 kΩ, R₅=5 kΩ; J=3 mA; E=9 V. Szukany I płynie przez R₅ zgodnie ze strzałką.",
        [
            "<b>Wkład źródła E.</b> Rozewrzyj źródło J. R₄+R₅=9 kΩ, a R₃∥(R₄+R₅)=3∥9=9/4 kΩ. Prąd do rozgałęzienia: I_x=−9 V/(2+9/4) kΩ=−36/17 mA.",
            "Z dzielnika prądu prąd w gałęzi R₄+R₅ wynosi I_E=I_x·R₃/(R₃+R₄+R₅)=−9/17 mA.",
            "<b>Wkład źródła J.</b> Zewrzyj E. R₂∥R₃=6/5 kΩ; po dodaniu R₄ mamy R₂₃₄=26/5 kΩ. Podział prądu między tę gałąź a R₅ daje I_J=J·R₂₃₄/(R₂₃₄+R₅)=26/17 mA.",
            "R₁ jest równoległy do idealnego źródła E, więc nie zmienia napięcia wymuszającego w tej gałęzi. Przy wyłączonym E zostaje zwarty przez idealne zwarcie źródła.",
        ],
        "I=I_E+I_J=(−9+26)/17 mA=<b>1 mA</b>.",
        "Zapisz osobno każdą konfigurację źródeł. Nie „kasuj” elementów poza idealnymi źródłami wyłączanymi w superpozycji."
    )

    story += make_task(
        "Zestaw K — zadanie 1",
        "plp_k1_packed.pdf / plp_k1_packed0.pdf, s. 1",
        "J₁=5 mA, J₂=1 mA, E=3 V; R₁=1 kΩ, R₂=2 kΩ, R₃=3 kΩ. Wyznaczyć I.",
        [
            "Rezystory tworzą wspólną sumę R_Σ=R₁+R₂+R₃=6 kΩ. Włączamy po kolei każde źródło, pozostałe źródła idealne wyłączamy.",
            "Wkład J₁: I₁=J₁·R₂/R_Σ=5·2/6=5/3 mA.",
            "Wkład E jest przeciwny do strzałki I: I_E=−E/R_Σ=−3/6=−1/2 mA.",
            "Wkład J₂: I₂=J₂·(R₂+R₃)/R_Σ=1·5/6=5/6 mA.",
        ],
        "I=5/3−1/2+5/6=<b>2 mA</b>."
    )

    story += make_task(
        "Zestaw L — zadanie 1",
        "plp_k1_packed.pdf / plp_k1_packed0.pdf, s. 2",
        "E₁=5 V, J₁=2 mA, J₂=5 mA; R₁=1 kΩ, R₂=2 kΩ, R₃=3 kΩ. Wyznaczyć I.",
        [
            "R_Σ=1+2+3=6 kΩ.",
            "Wkład J₁ ma zwrot przeciwny: I₁=−J₁·R₁/R_Σ=−2·1/6=−1/3 mA.",
            "Wkład źródła napięcia: I_E=E₁/R_Σ=5/6 mA.",
            "Wkład J₂: I₂=J₂·R₃/R_Σ=5·3/6=5/2 mA.",
        ],
        "I=−1/3+5/6+5/2=<b>3 mA</b>."
    )

    story += make_task(
        "Zestaw O — zadanie 1",
        "plp_k1_packed.pdf / plp_k1_packed0.pdf, s. 3",
        "E=2 V, J=2 mA, R=2 kΩ. Wyznaczyć U zgodnie ze strzałką na rysunku.",
        [
            "Źródło E daje U_E=(E/2)·R/(R/2+R+R)=E/5=2/5 V=0,4 V.",
            "Źródło J daje U_J=JR·R/(R+R/2+R)=2JR/5. Ponieważ JR=2 mA·2 kΩ=4 V, U_J=8/5 V=1,6 V.",
            "Dodajemy napięcia algebraicznie: oba wkłady mają w tym zadaniu zwrot zgodny z U.",
        ],
        "U=2/5+8/5=<b>2 V</b>."
    )

    story += make_task(
        "Zestaw P — zadanie 1",
        "plp_k1_packed.pdf / plp_k1_packed0.pdf, s. 4",
        "E=4 V, J=4 mA, R=1 kΩ. Wyznaczyć I.",
        [
            "Wkład źródła prądowego: I_J=(JR/(R/2+R+R))·1/2=J/5=4/5 mA=0,8 mA.",
            "Wkład źródła napięciowego: I_E=E/[R+(R∥2R)]. Ponieważ R∥2R=2R/3, dostajemy I_E=3E/(5R)=12/5 mA=2,4 mA.",
            "Oba wkłady mają zgodny zwrot ze strzałką I.",
        ],
        "I=4/5+12/5=<b>16/5 mA = 3,2 mA</b>."
    )

    story += make_task(
        "Mostek z rezystorem R₀ — wyznaczenie U",
        "plp_k1_packed.pdf, s. 18 (odręczny skan)",
        "R=2 kΩ (cztery boki mostka), R₀=1 kΩ, J=2 mA, E=8 V. U jest napięciem na R₀, w kierunku wskazanym na rysunku.",
        [
            "<b>Wkład E.</b> Otwieramy J. Między górnym węzłem a prawym środkiem mamy R∥(R+R₀)=2∥3=6/5 kΩ; dolny prawy opornik ma 2 kΩ. Napięcie na tej równoległej części: U₁=8·(6/5)/(6/5+2)=3 V.",
            "W gałęzi R+R₀ dzielnik daje na R₀: U_E=U₁·R₀/(R+R₀)=3·1/3=1 V.",
            "<b>Wkład J.</b> Zewrzyj E. Dwa prawe boki R są równolegle: R∥R=1 kΩ. Gałąź przez R₀ ma łącznie 2 kΩ; druga gałąź (lewy R) też ma 2 kΩ. Prąd J dzieli się po równo, więc przez R₀ płynie 1 mA i U_J=1 V.",
        ],
        "U=U_E+U_J=<b>2 V</b>."
    )

    # Equivalents.
    story += [PageBreak(), H1("B. Źródła zastępcze Thévenina i Nortona"),
              P("W odpowiedziach poniżej R_w oznacza rezystancję widzianą z zacisków A–B. Znak E_T i J_N odnosi się do zaznaczonego kierunku napięcia/prądu; gdy jest ujemny, źródło równoważne ma zwrot przeciwny."),
              H2("Zestaw K — zadanie 2: rozwiązanie symboliczne")]
    story += [P("W zadaniu źródło sterowane jest napięciowym źródłem zależnym od prądu (wartość r·i). Dla źródła testowego na zaciskach zapis z oryginalnego schematu upraszcza się do:"),
              eqbox("i = u/R₁ + (u − r i)/R₂  ⇒  i(1+r/R₂)=u(1/R₁+1/R₂).\nR_w = u/i = R₁(r+R₂)/(R₁+R₂)."),
              P("Przy rozwarciu zacisków prąd w gałęzi sterującej wynosi i=J. Z podziału napięcia/prądu otrzymujemy i₁=rJ/(R₁+R₂), a więc E_T=R₁i₁."),
              eqbox("E_T = R₁ r J/(R₁+R₂).\nJ_N = E_T/R_w = J r/(r+R₂).   (Kontrola: E_T=J_N R_w.)"),
              callout("Co tu robi r?", "r ma jednostkę Ω, bo mnoży prąd i i tworzy napięcie r·i. Wartości są dodatnie, więc przy odniesieniu zgodnym z rysunkiem parametry wychodzą dodatnie."),
              Spacer(1,7)]

    story += [H2("Zestaw L — zadanie 2: rozwiązanie symboliczne"),
              P("Źródło sterowane ma wartość g·u, gdzie g jest transkonduktancją. Przy wyznaczaniu R_w źródło zależne pozostaje aktywne; z równania testowego:"),
              eqbox("u = R₂ i + R₁(i−g u)  ⇒  u(1+R₁g)=i(R₁+R₂).\nR_w = (R₁+R₂)/(1+R₁g)."),
              P("Przy obwodzie otwartym R₂ nie przewodzi, a źródło sterowane odpowiada konduktancji g. Dzielnik napięcia daje E_T=E·R₁/(R₁+1/g)."),
              eqbox("E_T = E·R₁g/(1+R₁g).\nJ_N = E_T/R_w = gR₁E/(R₁+R₂)."),
              P("Warto sprawdzić jednostki: R₁g jest bezwymiarowe, ET ma wolty, a gR₁E/(R₁+R₂) ma ampery."),
              Spacer(1,7)]

    story += [H2("Dodatkowy przykład z notatek: źródło sterowane αI₁"),
              P("W skanie s. 7–9: J=2 mA, R₁=1 kΩ, R₂=2 kΩ, α=1/2. Najpierw prąd R₁ przy zwarciu zacisków: I₁=J·R₂/(R₁+R₂)=4/3 mA."),
              eqbox("J_N = J−I₁+αI₁ = 4/3 mA.\nR_w = (R₁+R₂)/(1−α) = 3 kΩ/(1/2) = 6 kΩ.\nE_T = J_N R_w = 8 V."),
              P("Ten przykład pokazuje, dlaczego samo „wyłączenie źródła” nie wystarcza przy źródłach zależnych: trzeba uwzględnić, że ich wartość zmienia się razem z prądem sterującym."),
              PageBreak()]

    story += [H2("Zestaw O — zadanie 2: źródło zastępcze"),
              P("Dane: J=2 mA; R₁=R₂=R₃=R=3 kΩ; k=1 V/V. Współczynnik k jest wzmocnieniem bezwymiarowym źródła sterowanego napięciem."),
              P("Z równania testowego dla portu otrzymujemy R_w=R(3+k)/(2+k). Dla k=1: R_w=3·4/3=4 kΩ."),
              P("Przy rozwarciu portu napięcie sterujące u=0, więc napięcie Thévenina jest spadkiem na R₃ wywołanym przez J: E_T=R₃J=3 kΩ·2 mA=6 V."),
              eqbox("E_T=6 V;   R_w=4 kΩ;   J_N=E_T/R_w=1,5 mA."),
              Spacer(1,7),
              H2("Zestaw P — zadanie 2: źródło zastępcze"),
              P("Dane: E=4 V; R₁=R₂=R₃=R=4 kΩ; k=1 A/A. W gałęzi z R₁ płynie (1+k)i, a w R₂ i R₃ — i."),
              P("Z KVL: i=E/[R₃+R₂+R₁(1+k)]=E/(4R)=0,25 mA. Stąd E_T=E−R₃i=3E/4=3 V."),
              P("Rezystancja wyjściowa z testu wynosi R_w=R(2+k)/(3+k)=3 kΩ."),
              eqbox("E_T=3 V;   R_w=3 kΩ;   J_N=E_T/R_w=1 mA."),
              callout("Kontrola liczbowa", "W obu zestawach można policzyć drugi model z zależności E_T=J_N R_w. Jeśli wynik nie zgadza się z prądem zwarcia, wróć do znaków albo do procedury testowej.")]

    story += [PageBreak(), H2("U z obciążeniem R₅ — źródło Thévenina z notatek"),
              P("Skan s. 14–15. Dane: J=32 mA, E=2 V; R₁=1 kΩ, R₂=3 kΩ, R₃=4 kΩ, R₄=1 kΩ, R₅=4 kΩ. Szukane U jest napięciem na R₅."),
              P("Najpierw wyznaczamy napięcie jałowe na zaciskach R₅. Wkład źródła J: prąd gałęzi R₂+R₃ wynosi J·R₁/(R₁+R₂+R₃)=32·1/8=4 mA, więc na R₃ powstaje 16 V. Wkład E ma zwrot przeciwny do U i wynosi −2 V."),
              eqbox("E_T=16−2=14 V."),
              P("Dla R_w wyłączamy źródła niezależne: J rozwieramy, E zwieramy. Z zacisków widzimy R₄ szeregowo z R₃∥(R₁+R₂):"),
              eqbox("R_w=R₄+[R₃∥(R₁+R₂)] = 1+[4∥4] = 3 kΩ."),
              P("Dołączamy R₅ i stosujemy dzielnik napięcia: U=E_T·R₅/(R_w+R₅)."),
              callout("Wynik", "U=14·4/(3+4)=<b>8 V</b>.", "answer"),
              P("To podejście działa także wtedy, gdy pierwotny układ wygląda na skomplikowany: najpierw odłącz obciążenie, znajdź E_T, potem R_w, a na końcu dołącz obciążenie z powrotem."),
              PageBreak()]

    story += [H2("Źródło z g·u₂ — Thevenin i Norton ze skanu"),
              P("Skan s. 16–17. Dane: E=10 V, R₁=R₄=1 kΩ, R₂=R₃=0,5 kΩ, g=3 mS. Źródło sterowane ma zwrot zgodny z rysunkiem; R₁ jest równoległy do idealnego E i nie zmienia zadanego napięcia węzła."),
              P("Przy rozwarciu portu R₄ nie przewodzi. Oznaczmy i₂ prąd przez R₂, i₃ prąd przez R₃. Z KCL: i₃=i₂−g u₂, a u₂=R₂i₂. Stąd i₃=i₂(1−gR₂)=−0,5i₂, bo gR₂=1,5."),
              P("Z KVL: E=R₂i₂+R₃i₃=(0,5−0,25)kΩ·i₂, więc i₂=40 mA i i₃=−20 mA. Napięcie jałowe E_T=R₃i₃=−10 V."),
              P("Dla R_w wyłączamy E (zwarcie), ale pozostawiamy źródło sterowane. Widziana konduktancja wewnętrznego węzła: 1/R₂+1/R₃−g=2+2−3=1 mS, zatem R_w,wew=1 kΩ. R₄ jest z nią szeregowo."),
              eqbox("E_T=−10 V;   R_w=R₄+1/(1/R₂+1/R₃−g)=2 kΩ;\nJ_N=E_T/R_w=−5 mA."),
              callout("Interpretacja znaku", "Jeśli J_N odniesiono od A do B, wynik −5 mA oznacza, że rzeczywisty prąd źródła Nortona płynie od B do A. Ujemny E_T ma tę samą informację o polaryzacji." , "warn"),
              PageBreak()]

    story += [H2("Zadanie o prądzie I — źródło g·u₁ (Norton)"),
              P("Skan s. 19–21. Dane: R₁=1 kΩ, R₂=2 kΩ, R₃=3 kΩ, g=0,5 mS, E=1 V, J=1 mA. W oryginalnym schemacie R₁ jest obciążeniem między węzłami A–B; u₁=V_A−V_B, a I jest skierowany od A do B."),
              P("Odłącz R₁ i patrzymy w zaciski A–B. Przy rozwarciu, prąd J oraz sterowany prąd g·u₁ płyną przez R₃ do węzła B. Z KCL: V_B=R₂(J+g u₁), a V_A=E, więc u₁=E−R₂(J+g u₁)."),
              eqbox("E_T=u₁=(E−J R₂)/(1+gR₂)=(1−2)/2=−0,5 V."),
              P("Dla R_w wyłączamy źródła niezależne, ale nie zależne. Portowa konduktancja wynosi 1/R₂+g, więc R_w=R₂/(1+gR₂)=1 kΩ. R₃ leży w gałęzi ze źródłem idealnym J i nie zmienia prądu tej gałęzi."),
              eqbox("J_N=E_T/R_w=−0,5 mA.\nPo dołączeniu R₁:  I=E_T/(R_w+R₁)=−0,5/(1+1) mA=<b>−0,25 mA</b>."),
              callout("Kontrola", "Znak minus oznacza, że prąd przez R₁ rzeczywiście płynie przeciwnie do narysowanej strzałki. Taką samą wartość otrzymuje się z dzielnika prądowego w modelu Nortona."),
              PageBreak()]

    story += [H2("Dodatkowy skan: parametry Nortona dla zacisków A–B"),
              P("Skan s. 23/25 (powtórzony na s. 25). Dane: E₁=4 V, J₂=2 mA, R₁=4 kΩ, G₂=4 mS, β=3 mA/mA=3. Źródło J₂ jest skierowane w stronę A, a źródło βI′ od A do B; I′ jest prądem gałęzi R₁ zgodnym ze strzałką."),
              P("Przy rozwarciu zacisków KCL w A daje J₂=I′+βI′, czyli I′=J₂/(1+β)=0,5 mA. Napięcie A–B: E_T=E₁+I′R₁=4+0,5·4=6 V."),
              P("Aby znaleźć R_w, zerujemy źródła niezależne: E₁ zwieramy, J₂ rozwieramy. Prąd testowy płynie przez R₁ i źródło sterowane; i_test=(1+β)V_test/R₁."),
              eqbox("R_w=R₁/(1+β)=4/4=1 kΩ.\nJ_N=E_T/R_w=6 V/1 kΩ=<b>6 mA</b> (strzałka źródła Nortona: B→A)."),
              P("G₂ jest w szeregu z idealnym źródłem prądowym i nie ma dodatkowego odgałęzienia w ich wspólnym węźle. Zmienia napięcie wewnętrzne, ale nie prąd narzucony przez źródło, dlatego nie zmienia parametrów widzianych na A–B."),
              PageBreak()]

    # Nodal problem.
    story += [H1("C. Złożony układ — metoda węzłowa"),
              H2("Zadanie z trójkąta źródeł: wyznaczyć I"),
              P("Skan s. 22/24 (te same dane i rysunek są zdublowane). Dane: E₁=7 V, E₂=14 V, J=8 A, R₁=4 Ω, G₂=8 S, G₃=4 S. I jest skierowany od prawego górnego węzła do węzła środkowego przez R₁."),
              P("Przyjmij dolny węzeł za masę. Z kierunków strzałek źródeł napięcia: lewy węzeł V_L=+E₂=14 V, prawy górny V_R=−E₁=−7 V. Źródło J łączy te dwa węzły o zadanych potencjałach; jego wartość zmienia prądy źródeł napięcia, ale nie potencjały węzłów."),
              P("Nieznane jest napięcie węzła środkowego V_C. Zapisujemy KCL jako sumę prądów wypływających z C:"),
              eqbox("G₂(V_C−V_L)+G₃(V_C−0)+(V_C−V_R)/R₁=0.\n8(V_C−14)+4V_C+(V_C+7)/4=0."),
              P("Po zebraniu wyrazów: 12,25 V_C=110,25, stąd V_C=9 V. Prąd I odniesiony zgodnie ze strzałką (od R do C):"),
              eqbox("I=(V_R−V_C)/R₁=(−7−9)/4=<b>−4 A</b>."),
              callout("Co mówi znak?", "Rzeczywisty prąd ma wartość 4 A i płynie od węzła środkowego ku prawemu górnemu. Duże G₂ i G₃ są konduktancjami, więc prąd przez nie to G·różnica potencjałów." , "answer"),
              Spacer(1,5),
              H2("Dlaczego metoda węzłowa jest tu najkrótsza?"),
              P("Trzy napięcia węzłowe są od razu ustalone przez źródła idealne, a tylko jeden węzeł jest niewiadomą. Zamiast przekształcać złożony układ trójkątny, wystarcza jedno równanie KCL. To dobry przykład zasady: wybierz metodę, która daje najmniej niewiadomych."),
              PageBreak()]

    # Summary.
    story += [H1("Tabela wyników i ściąga na kolokwium"),
              P("Poniższa tabela zbiera wyniki końcowe wszystkich unikatowych zadań z analizowanych PDF-ów. W przypadku modeli źródłowych podano parametry w odniesieniach przyjętych w rysunkach."),
              info_table([
                  ["Zadanie / źródło", "Wynik końcowy"],
                  ["Przykład superpozycji, skan s. 5–6", "I = 1 mA"],
                  ["Zestaw K, zad. 1", "I = 2 mA"],
                  ["Zestaw L, zad. 1", "I = 3 mA"],
                  ["Zestaw O, zad. 1", "U = 2 V"],
                  ["Zestaw P, zad. 1", "I = 3,2 mA"],
                  ["Mostek, skan s. 18", "U = 2 V"],
                  ["Zestaw K, zad. 2", "R_w=R₁(r+R₂)/(R₁+R₂); E_T=R₁rJ/(R₁+R₂); J_N=Jr/(r+R₂)"],
                  ["Zestaw L, zad. 2", "R_w=(R₁+R₂)/(1+R₁g); E_T=ER₁g/(1+R₁g); J_N=gR₁E/(R₁+R₂)"],
                  ["Notatki αI₁, s. 7–9", "J_N=4/3 mA; R_w=6 kΩ; E_T=8 V"],
                  ["Zestaw O, zad. 2", "E_T=6 V; R_w=4 kΩ; J_N=1,5 mA"],
                  ["Zestaw P, zad. 2", "E_T=3 V; R_w=3 kΩ; J_N=1 mA"],
                  ["Obciążenie R₅, skan s. 14–15", "E_T=14 V; R_w=3 kΩ; U=8 V"],
                  ["Źródło g·u₂, skan s. 16–17", "E_T=−10 V; R_w=2 kΩ; J_N=−5 mA"],
                  ["Prąd I, skan s. 19–21", "E_T=−0,5 V; R_w=1 kΩ; J_N=−0,5 mA; I=−0,25 mA"],
                  ["Norton A–B, skan s. 23/25", "E_T=6 V; R_w=1 kΩ; J_N=6 mA (strzałka B→A)"],
                  ["Trójkąt, skan s. 22/24", "V_C=9 V; I=−4 A"],
              ], [57*mm, CONTENT_W-57*mm]),
              Spacer(1,8),
              H2("Pięć kontroli przed oddaniem rozwiązania"),
              bullet("Czy wszystkie prądy/napięcia mają podpisane zwroty odniesienia?"),
              bullet("Czy dla R_w wyłączono tylko źródła niezależne, a sterowane pozostawiono?"),
              bullet("Czy w superpozycji źródło napięciowe zastąpiono zwarciem, a prądowe rozwarciem?"),
              bullet("Czy rachunek jednostek zgadza się z szukaną wielkością?"),
              bullet("Czy wartość ujemna została zinterpretowana jako kierunek przeciwny, a nie „poprawiona” bez uzasadnienia?"),
              callout("Najkrótsza ściąga", "KCL w węźle; KVL w oczku; u=Ri; szereg — sumuj R; równolegle — sumuj G; superpozycja — wyłączaj tylko źródła niezależne; Thevenin — E_T=U_oc; Norton — J_N=I_sc; R_w=E_T/J_N."),
              Spacer(1,5),
              P("Koniec opracowania. Rozwiązania są samodzielnym wyprowadzeniem i kontrolą obliczeń, a nie przepisaniem układu stron z oryginalnych plików.", "SmallPL")]
    return story


def main():
    doc = ManualDocTemplate(
        str(OUTPUT), pagesize=A4,
        leftMargin=LEFT, rightMargin=RIGHT, topMargin=TOP, bottomMargin=BOTTOM,
        title="PLP K1 — samouczek i autorskie rozwiązania",
        author="Opracowanie własne",
        subject="Podstawy analizy liniowych obwodów prądu stałego",
        keywords="PLP K1, obwody, superpozycja, Thevenin, Norton, samouczek",
    )
    doc.multiBuild(build_story())
    print(f"Zapisano: {OUTPUT}")


if __name__ == "__main__":
    main()
