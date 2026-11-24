#!/usr/bin/env python3
"""Generate a standalone Polish tutorial on solving circuits with dependent sources.

Requires ReportLab and the DejaVu fonts used by generate_plp_k1_guide.py.
Run from the repository root:
    python tools/generate_plp_k1_zrodla_sterowane.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import Flowable, NextPageTemplate, PageBreak, Spacer

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "PLP_K1_obwody_ze_zrodlami_sterowanymi.pdf"
sys.path.insert(0, str(ROOT))

from tools import generate_plp_k1_metody_analizy as common  # noqa: E402

base = common.base
PAGE_W, PAGE_H = common.PAGE_W, common.PAGE_H
LEFT, RIGHT, TOP, BOTTOM = common.LEFT, common.RIGHT, common.TOP, common.BOTTOM
CONTENT_W = common.CONTENT_W
NAVY, TEAL, TEAL_DARK = common.NAVY, common.TEAL, common.TEAL_DARK
GOLD, INK, MUTED, LINE, WHITE = common.GOLD, common.INK, common.MUTED, common.LINE, common.WHITE


def wire(c, p1, p2, width=1.25, color=NAVY):
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(p1[0], p1[1], p2[0], p2[1])


def dependent_current_vertical(c, x, y_bottom, y_top, label, arrow_down=True, half_w=10, half_h=15):
    cy = (y_bottom + y_top) / 2
    wire(c, (x, y_bottom), (x, cy - half_h))
    wire(c, (x, cy + half_h), (x, y_top))
    c.setFillColor(WHITE)
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.2)
    path = c.beginPath()
    path.moveTo(x, cy + half_h)
    path.lineTo(x + half_w, cy)
    path.lineTo(x, cy - half_h)
    path.lineTo(x - half_w, cy)
    path.close()
    c.drawPath(path, fill=1, stroke=1)
    p1, p2 = ((x, cy + 6), (x, cy - 6)) if arrow_down else ((x, cy - 6), (x, cy + 6))
    common.arrow(c, p1[0], p1[1], p2[0], p2[1], TEAL_DARK, head=3.8, width=1.0)
    c.setFillColor(INK)
    c.setFont("DejaVu-Bold", 7.0)
    c.drawString(x + half_w + 4, cy - 2.5, label)


def dependent_voltage_horizontal(c, x1, x2, y, label, plus_left=True, half_w=12, half_h=15):
    cx = (x1 + x2) / 2
    wire(c, (x1, y), (cx - half_w, y))
    wire(c, (cx + half_w, y), (x2, y))
    c.setFillColor(WHITE)
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.2)
    path = c.beginPath()
    path.moveTo(cx - half_w, y)
    path.lineTo(cx, y + half_h)
    path.lineTo(cx + half_w, y)
    path.lineTo(cx, y - half_h)
    path.close()
    c.drawPath(path, fill=1, stroke=1)
    c.setFillColor(TEAL_DARK)
    c.setFont("DejaVu-Bold", 8)
    c.drawCentredString(cx - 5, y - 2.5, "+" if plus_left else "−")
    c.drawCentredString(cx + 5, y - 2.5, "−" if plus_left else "+")
    c.setFillColor(INK)
    c.setFont("DejaVu-Bold", 7.1)
    c.drawCentredString(cx, y + half_h + 8, label)


class VCCSNetworkDiagram(Flowable):
    """One-node example with an optional independent current source and port labels."""

    def __init__(self, width=CONTENT_W, height=116, independent_current=False, port=False):
        super().__init__()
        self.width, self.height = width, height
        self.independent_current = independent_current
        self.port = port

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        c.setFillColor(common.PALE)
        c.setStrokeColor(LINE)
        c.roundRect(0, 0, self.width, self.height, 6, fill=1, stroke=1)
        ytop, ybottom = 82, 24
        xsrc, xnode = 57, self.width * 0.39
        xr, xdep = self.width * 0.59, self.width * 0.77
        xj = self.width - 47
        wire(c, (xsrc, ybottom), (xj, ybottom))
        common.voltage_source(c, xsrc, ybottom, ytop, "E", plus_top=True, radius=9)
        common.resistor_h(c, xsrc, xnode, ytop, "R₁=3 kΩ")
        wire(c, (xnode, ytop), (xj, ytop))
        common.resistor_v(c, xr, ybottom, ytop, "R₂=6 kΩ", width=17)
        dependent_current_vertical(c, xdep, ybottom, ytop,
                                   "g·u_AB" if self.port else "g·u_X", arrow_down=True)
        if self.independent_current:
            wire(c, (xj, ybottom), (xj, ytop - 10))
            c.setFillColor(WHITE)
            c.setStrokeColor(NAVY)
            c.setLineWidth(1.2)
            c.circle(xj, (ybottom + ytop) / 2, 9, fill=1, stroke=1)
            common.arrow(c, xj, (ybottom + ytop) / 2 - 5, xj, (ybottom + ytop) / 2 + 5,
                         TEAL_DARK, head=3.7, width=1.0)
            wire(c, (xj, ytop - 10), (xj, ytop))
            c.setFillColor(INK)
            c.setFont("DejaVu-Bold", 7.0)
            c.drawString(xj + 11, (ybottom + ytop) / 2 - 2, "J=1 mA")
        label = "A" if self.port else "X"
        color = base.NODE_A if self.port else base.NODE_C
        common.node_dot(c, xnode, ytop, label, color, dx=5, dy=4)
        c.setFillColor(INK)
        c.setFont("DejaVu-Bold", 7.2)
        c.drawString(xsrc + 10, ytop - 11, "12 V")
        c.setFillColor(MUTED)
        c.setFont("DejaVu", 6.7)
        c.drawString(xsrc + 8, ybottom - 10, "B = 0 V" if self.port else "masa 0 V")
        if self.port:
            c.drawCentredString(self.width / 2, 6, "Niezależne źródło E ma plus u góry; u_AB=V_A−V_B.")
        else:
            c.drawCentredString(self.width / 2, 6, "Źródło sterowane g·u_X ma zwrot w dół; u_X=V_X względem masy.")
        c.restoreState()


class CCCSDiagram(Flowable):
    def __init__(self, width=CONTENT_W, height=118):
        super().__init__()
        self.width, self.height = width, height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        c.setFillColor(common.PALE)
        c.setStrokeColor(LINE)
        c.roundRect(0, 0, self.width, self.height, 6, fill=1, stroke=1)
        ytop, ybottom = 77, 22
        xs, xnode, xr, xdep = 55, self.width * 0.40, self.width * 0.66, self.width - 63
        wire(c, (xs, ybottom), (xdep, ybottom))
        common.voltage_source(c, xs, ybottom, ytop, "E", plus_top=True, radius=9)
        common.resistor_h(c, xs, xnode, ytop, "R₁=2 kΩ")
        wire(c, (xnode, ytop), (xdep, ytop))
        common.resistor_v(c, xr, ybottom, ytop, "R₂=4 kΩ", width=17)
        dependent_current_vertical(c, xdep, ybottom, ytop, "β·i_X", arrow_down=True)
        common.node_dot(c, xnode, ytop, "X", base.NODE_C, dx=5, dy=4)
        common.arrow(c, xs + 28, ytop + 14, xnode - 25, ytop + 14, GOLD, head=4.0, width=1.2)
        c.setFillColor(INK)
        c.setFont("DejaVu-Bold", 7.0)
        c.drawCentredString((xs + xnode) / 2, ytop + 23, "i_X")
        c.setFillColor(MUTED)
        c.setFont("DejaVu", 6.7)
        c.drawString(xs + 8, ybottom - 10, "masa 0 V")
        c.drawCentredString(self.width / 2, 6, "i_X przyjęto przez R₁ od źródła E do węzła X.")
        c.restoreState()


class VCVSSupernodeDiagram(Flowable):
    def __init__(self, width=CONTENT_W, height=116):
        super().__init__()
        self.width, self.height = width, height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        c.setFillColor(common.PALE)
        c.setStrokeColor(LINE)
        c.roundRect(0, 0, self.width, self.height, 6, fill=1, stroke=1)
        ytop, ybottom = 82, 23
        xc, xa, xb = 62, self.width * 0.43, self.width * 0.78
        wire(c, (xc, ybottom), (xb, ybottom))
        common.voltage_source(c, xc, ybottom, ytop, "E_C", plus_top=True, radius=9)
        common.resistor_v(c, xa, ybottom, ytop, "", width=17)
        common.resistor_v(c, xb, ybottom, ytop, "", width=17)
        dependent_voltage_horizontal(c, xa, xb, ytop, "μ·u_C", plus_left=True)
        common.node_dot(c, xa, ytop, "A", base.NODE_A, dx=-10, dy=5)
        common.node_dot(c, xb, ytop, "B", base.NODE_B, dx=5, dy=5)
        c.setFillColor(INK)
        c.setFont("DejaVu-Bold", 7.0)
        c.drawString(xc + 12, ytop - 10, "V_C=4 V")
        c.drawRightString(xa - 10, (ybottom + ytop) / 2 - 3, "R_A=2 kΩ")
        c.drawString(xb + 10, (ybottom + ytop) / 2 - 3, "R_B=2 kΩ")
        c.setFillColor(MUTED)
        c.setFont("DejaVu", 6.7)
        c.drawCentredString(self.width / 2, 6, "Źródło VCVS narzuca V_A−V_B=μ·u_C; dolny węzeł jest masą.")
        c.restoreState()


class CCVSSeriesDiagram(Flowable):
    def __init__(self, width=CONTENT_W, height=100):
        super().__init__()
        self.width, self.height = width, height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        c.setFillColor(common.PALE)
        c.setStrokeColor(LINE)
        c.roundRect(0, 0, self.width, self.height, 6, fill=1, stroke=1)
        yb, yt = 22, 61
        x1, x2, x3 = 75, self.width * 0.55, self.width - 85
        wire(c, (x1, yb), (x3, yb))
        wire(c, (x3, yb), (x3, yt))
        common.voltage_source(c, x1, yb, yt, "E=12 V", plus_top=True, radius=8)
        common.resistor_h(c, x1, x2, yt, "R=2 kΩ")
        dependent_voltage_horizontal(c, x2, x3, yt, "r·i", plus_left=True, half_w=10, half_h=12)
        common.arrow(c, x1 + 16, yt + 9, x2 - 17, yt + 9, GOLD, head=3.8, width=1.1)
        c.setFillColor(INK)
        c.setFont("DejaVu-Bold", 7.0)
        c.drawCentredString((x1 + x2) / 2, yt + 16, "i=i_X")
        c.setFillColor(MUTED)
        c.setFont("DejaVu", 6.6)
        c.drawCentredString(self.width / 2, 5, "Biegunowość VCVS/CCVS jest przyjęta jako spadek w kierunku obiegu.")
        c.restoreState()


class QuickDocTemplate(common.GuideDocTemplate):
    def draw_cover(self, canvas, doc):
        canvas.saveState()
        canvas.setFillColor(colors.HexColor("#F7FAFC"))
        canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        canvas.setFillColor(NAVY)
        canvas.rect(0, PAGE_H - 106 * mm, PAGE_W, 106 * mm, fill=1, stroke=0)
        canvas.setFillColor(TEAL)
        canvas.rect(0, PAGE_H - 109 * mm, PAGE_W, 3 * mm, fill=1, stroke=0)
        canvas.setStrokeColor(colors.HexColor("#3A657E"))
        canvas.setLineWidth(1.1)
        points = [
            (PAGE_W - 79 * mm, PAGE_H - 24 * mm),
            (PAGE_W - 45 * mm, PAGE_H - 24 * mm),
            (PAGE_W - 45 * mm, PAGE_H - 58 * mm),
            (PAGE_W - 19 * mm, PAGE_H - 58 * mm),
        ]
        for a, b in zip(points, points[1:]):
            canvas.line(a[0], a[1], b[0], b[1])
        for x, y in points:
            canvas.setFillColor(GOLD if (x, y) == points[2] else TEAL)
            canvas.circle(x, y, 2.5 * mm, fill=1, stroke=0)
        canvas.setFillColor(TEAL_DARK)
        canvas.roundRect(LEFT, 25 * mm, PAGE_W - LEFT - RIGHT, 28 * mm, 4 * mm, fill=1, stroke=0)
        canvas.setFont("DejaVu", 8.2)
        canvas.setFillColor(WHITE)
        canvas.drawString(LEFT + 7 * mm, 43 * mm, "OPRACOWANIE WŁASNE • PLP K1")
        canvas.drawString(LEFT + 7 * mm, 34 * mm, "Zależności źródeł, równania i przykłady obliczeń")
        canvas.setFont("DejaVu", 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawRightString(PAGE_W - RIGHT, 14 * mm, "Lublin · 2026")
        canvas.restoreState()

    def draw_body(self, canvas, doc):
        canvas.saveState()
        canvas.setFillColor(WHITE)
        canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.6)
        canvas.line(LEFT, PAGE_H - 10 * mm, PAGE_W - RIGHT, PAGE_H - 10 * mm)
        canvas.setFont("DejaVu-Bold", 7.4)
        canvas.setFillColor(NAVY)
        canvas.drawString(LEFT, PAGE_H - 7.5 * mm, "PLP K1  ·  OBWODY PRĄDU STAŁEGO")
        canvas.setFont("DejaVu", 7.2)
        canvas.setFillColor(MUTED)
        canvas.drawRightString(PAGE_W - RIGHT, PAGE_H - 7.5 * mm, "Źródła sterowane")
        canvas.line(LEFT, 10 * mm, PAGE_W - RIGHT, 10 * mm)
        canvas.setFont("DejaVu", 7.2)
        canvas.setFillColor(MUTED)
        canvas.drawString(LEFT, 6.5 * mm, "Źródła zależne pozostają aktywne; pilnuj zwrotu wielkości sterującej.")
        canvas.drawRightString(PAGE_W - RIGHT, 6.5 * mm, f"str. {doc.page}")
        canvas.restoreState()


def P(text, style="BodyPL"):
    return base.P(text, style)


def build_story():
    story = [
        Spacer(1, 26 * mm),
        P("PLP K1 · ANALIZA OBWODÓW", "CoverKicker"),
        P("Obwody ze źródłami sterowanymi", "CoverTitle"),
        P("Jak zapisywać zależności, rozwiązywać równania i wyznaczać model portu", "CoverSub"),
        Spacer(1, 10 * mm),
        base.callout(
            "Najważniejsza zasada",
            "Źródło sterowane nie jest źródłem o zadanej, stałej wartości. Jego wartość wynika z napięcia lub prądu w tym samym obwodzie. Zapisz tę zależność i zachowaj źródło aktywne w każdym równaniu.",
        ),
        Spacer(1, 7 * mm),
        P("W środku: cztery typy źródeł, algorytm dla KCL/KVL, przykłady z VCCS, CCCS i VCVS oraz procedura Thévenina/Nortona ze źródłem testowym.", "CoverMeta"),
        NextPageTemplate("Body"),
        PageBreak(),

        base.H1("1. Co oznacza źródło sterowane?"),
        P("Źródło sterowane (zależne) jest idealnym źródłem, którego wartość wyznacza inna wielkość obwodu. Na schemacie rozpoznasz je po symbolu rombu. Wartość źródła nie jest z góry znana — trzeba ją zapisać jako równanie."),
        base.info_table([
            ["Typ", "Zależność", "Współczynnik / jednostka"],
            ["VCVS — napięciowe sterowane napięciem", "u_d = μ · u_x", "μ: V/V, bezwymiarowy"],
            ["VCCS — prądowe sterowane napięciem", "i_d = g · u_x", "g: A/V = S (siemens)"],
            ["CCCS — prądowe sterowane prądem", "i_d = β · i_x", "β: A/A, bezwymiarowy"],
            ["CCVS — napięciowe sterowane prądem", "u_d = r · i_x", "r: V/A = Ω"],
        ], [48 * mm, 54 * mm, CONTENT_W - 102 * mm]),
        base.H2("Najpierw podpisz wielkości sterujące"),
        base.bullet("Napięcie sterujące: zaznacz + i −; przykładowo u_x=V_a−V_b."),
        base.bullet("Prąd sterujący: narysuj strzałkę i_x w konkretnej gałęzi."),
        base.bullet("Zapisz biegunowość lub strzałkę wyjściową źródła zależnego."),
        base.bullet("Jeśli zwrot sterujący albo wyjściowy jest przeciwny do przyjętego, w równaniu pojawia się minus."),
        base.eqbox("Przykład znaku: dla strzałki i_d w dół i dodatniego u_x=V_X−0:   i_d=g u_x.\nJeśli strzałka i_d jest w górę przy tej samej definicji u_x:   i_d=−g u_x."),
        base.H2("Kontrola jednostek"),
        base.info_table([
            ["Wielkość", "Jednostka", "Przykład"],
            ["g·u_x", "S·V=A", "0,5 mS · 4 V = 2 mA"],
            ["r·i_x", "Ω·A=V", "2 kΩ · 1 mA = 2 V"],
            ["μ·u_x", "1·V=V", "3 · 2 V = 6 V"],
            ["β·i_x", "1·A=A", "0,4 · 5 mA = 2 mA"],
        ], [34 * mm, 43 * mm, CONTENT_W - 77 * mm]),
        base.callout("Nie myl ze źródłem niezależnym", "Wartość źródła zależnego może się zmienić między stanami obwodu. Nie wpisuj jej jako stałej, zanim nie obliczysz wielkości sterującej."),
        PageBreak(),

        base.H1("2. Uniwersalny sposób rozwiązywania"),
        base.info_table([
            ["Krok", "Działanie"],
            ["1. Odniesienia", "Nazwij węzły, wybierz masę, podpisz napięcia i prądy sterujące."],
            ["2. Równanie źródła", "Zapisz i_d=g u_x, u_d=μu_x, i_d=βi_x albo u_d=ri_x ze znakami wynikającymi ze strzałek."],
            ["3. Równania obwodu", "Dla prądowych źródeł zależnych wpisz ich wartość do KCL; dla napięciowych dodaj warunek napięciowy do KVL/KCL."],
            ["4. Zamknięcie układu", "Wyraź wielkość sterującą przez napięcia/prądy obwodu. Jeśli potrzeba, dodaj ją jako niewiadomą i użyj MNA."],
            ["5. Kontrola", "Sprawdź KCL/KVL, biegunowość, zwroty i jednostki współczynnika sterującego."],
        ], [31 * mm, CONTENT_W - 31 * mm]),
        base.H2("Które równania wybrać?"),
        base.info_table([
            ["Metoda", "Jak uwzględnić źródło sterowane"],
            ["Węzłowa", "VCCS/CCCS wchodzą do KCL jako prądy; wyraź u_x lub i_x przez napięcia węzłowe."],
            ["Oczkowa", "VCVS/CCVS wchodzą do KVL; źródło prądu między oczkami tworzy więzy lub superoczko."],
            ["MNA", "Dla napięciowego źródła między nieznanymi węzłami wprowadź jego prąd jako niewiadomą i dodaj równanie napięciowe."],
        ], [33 * mm, CONTENT_W - 33 * mm]),
        base.H2("Superpozycja: wyłączaj tylko niezależne źródła"),
        P("W liniowym obwodzie z wieloma źródłami niezależnymi można liczyć jeden wkład naraz. Idealne źródło napięcia niezależne zastąp zwarciem, a idealne źródło prądu niezależne — rozwarciem."),
        base.callout("Źródło zależne pozostaje aktywne", "W każdym podproblemie źródło sterowane nadal spełnia swoją zależność. Jeśli w danym podproblemie jego wielkość sterująca wyjdzie zero, wartość źródła sama stanie się zerowa — nie wyłączaj go ręcznie.", "warn"),
        base.P("Dodawaj algebraicznie szukane napięcia lub prądy. Mocy nie liczy się przez dodanie mocy z poszczególnych przypadków; najpierw zsumuj odpowiedź, potem policz moc.", "SmallPL"),
        PageBreak(),

        base.H1("3. Źródło VCCS w KCL i superpozycji"),
        P("Dane: E=12 V, R₁=3 kΩ, R₂=6 kΩ, źródło J=1 mA wstrzykuje prąd do X, a źródło sterowane ma wartość i_g=g u_X, gdzie g=0,5 mS i strzałka i_g jest skierowana z X do masy."),
        VCCSNetworkDiagram(independent_current=True),
        base.H2("Pełny obwód"),
        base.P("Przyjmujemy prądy wypływające z X. Prąd źródła J wpływa do węzła, więc ma znak minus; VCCS pozostaje w równaniu jako +gV_X."),
        base.eqbox("(V_X−12)/3 kΩ + V_X/6 kΩ + 0,5 mS·V_X − 1 mA = 0.\nW mA: (V_X−12)/3 + V_X/6 + 0,5V_X − 1 = 0  ⇒  V_X=5 V.\ni_g = 0,5 mS · 5 V = 2,5 mA w dół."),
        base.H2("Kontrola KCL"),
        P("I_R₁=(5−12)/3=−2,33 mA, I_R₂=5/6=0,83 mA, i_g=2,5 mA, a źródło J wnosi −1 mA do sumy wypływających. Suma −2,33+0,83+2,5−1=0 mA."),
        base.H2("Ten sam przykład metodą superpozycji"),
        base.eqbox("Tylko E aktywne: J rozwarte, VCCS zostaje → V_X,E=4 V.\nTylko J aktywne: E zwarte, VCCS zostaje → V_X,J=1 V.\nV_X=V_X,E+V_X,J=4+1=5 V."),
        base.callout("Najczęstszy błąd", "Nie usuwaj składnika gV_X w żadnym podproblemie. Źródło sterowane może być zależne właśnie od szukanej odpowiedzi." , "warn"),
        PageBreak(),

        base.H1("4. Źródła sterowane prądem: CCCS i CCVS"),
        P("Dla źródła sterowanego prądem najpierw ustal strzałkę i_X w gałęzi sterującej. Dopiero potem wyraź i_X przez napięcia węzłów lub prądy oczkowe."),
        CCCSDiagram(),
        base.H2("Przykład CCCS: i_d=βi_X"),
        P("E=10 V, R₁=2 kΩ, R₂=4 kΩ, β=0,5. Strzałka i_X biegnie przez R₁ do X, a źródło βi_X wypływa z X do masy."),
        base.eqbox("i_X=(10−V_X)/2 kΩ. KCL wypływających z X:\n(V_X−10)/2 kΩ + V_X/4 kΩ + 0,5·(10−V_X)/2 kΩ = 0.\nV_X=5 V;  i_X=2,5 mA;  i_d=βi_X=1,25 mA;  I_R₂=V_X/4 kΩ=1,25 mA."),
        base.P("Kontrola: przez R₁ do X wpływa 2,5 mA, a z X wypływa 1,25+1,25=2,5 mA.", "SmallPL"),
        base.H2("Przykład CCVS: u_d=ri_X w jednym oczku"),
        CCVSSeriesDiagram(),
        base.P("Jeśli sterujący prąd i_X jest tym samym prądem I w szeregowym oczku, a biegunowość źródła zależnego jest spadkiem zgodnym z obiegiem, KVL daje:"),
        base.eqbox("12 V − (2 kΩ)I − (1 kΩ)I = 0  ⇒  I=4 mA;   u_d=rI=4 V."),
        base.callout("Uwaga na zakres skrótu", "Wzór I=E/(R+r) działa tu dlatego, że i_X=I i źródło zależne ma zgodną biegunowość. Jeśli i_X jest prądem innej gałęzi albo biegunowość jest przeciwna, wpisz osobną zależność i właściwy znak do KCL/KVL.", "warn"),
        PageBreak(),

        base.H1("5. VCVS i metoda superwęzła"),
        P("Idealne źródło napięcia sterowane napięciem narzuca zależność między dwoma potencjałami. Jeśli jest wpięte między dwa nieznane węzły, obejmij je superwęzłem: zapisz KCL dla zewnętrznego obrysu i dodaj równanie źródła."),
        VCVSSupernodeDiagram(),
        base.H2("Przykład: V_A−V_B=2V_C"),
        P("Źródło sterujące ustala V_C=4 V. Rezystory R_A=R_B=2 kΩ łączą odpowiednio A i B z masą. Zależność VCVS ma plus przy A."),
        base.eqbox("Warunek źródła: V_A−V_B=2V_C=8 V.\nKCL superwęzła A–B: V_A/2 kΩ + V_B/2 kΩ = 0  ⇒  V_A+V_B=0.\nRozwiązanie: V_A=4 V, V_B=−4 V."),
        base.P("Jeśli potrzebny jest prąd przez źródło zależne, dopisz KCL w jednym z jego węzłów. Przyjmując I_s od A do B: V_A/R_A+I_s=0, zatem I_s=−2 mA; rzeczywisty kierunek jest od B do A.", "SmallPL"),
        base.callout("Nie skracaj źródła idealnego do rezystora", "VCVS nie jest rezystorem. Jego równanie narzuca różnicę potencjałów; nie wolno wstawiać go do KCL jako (V_A−V_B)/R. Użyj superwęzła albo analizy MNA." , "warn"),
        PageBreak(),

        base.H1("6. Thévenin/Norton ze źródłem sterowanym"),
        P("Rozpatrz port A–B tego samego typu obwodu: E=12 V, R₁=3 kΩ, R₂=6 kΩ oraz VCCS i_g=gU_AB skierowane od A do B, g=0,5 mS. Źródło zależne zostaje aktywne przy obu obliczeniach."),
        VCCSNetworkDiagram(independent_current=False, port=True),
        base.H2("Napięcie jałowe E_T"),
        base.P("Przy otwartym porcie z KCL w A:"),
        base.eqbox("(V_A−12)/3 kΩ + V_A/6 kΩ + 0,5 mS·V_A = 0  ⇒  E_T=U_oc=V_A=4 V."),
        base.H2("Rezystancja R_T: źródło testowe 1 V"),
        P("Zerujemy niezależne E (zastępujemy zwarciem), ale nie gasimy VCCS. Przykładamy U_t=1 V z plusem przy A i liczymy prąd I_t wpływający do obwodu:"),
        base.eqbox("I_t = 1 V/3 kΩ + 1 V/6 kΩ + 0,5 mS·1 V\n    = 0,333 + 0,167 + 0,5 = 1 mA.\nR_T=U_t/I_t=1 V/1 mA=1 kΩ;   J_N=E_T/R_T=4 mA, strzałka B→A."),
        base.H2("Obciążenie R_L=1 kΩ"),
        base.eqbox("I_L=E_T/(R_T+R_L)=4/(1+1)=2 mA;   U_L=2 V."),
        base.callout("Dlaczego źródło zależne musi zostać?", "Gdyby wyłączyć g·U_AB, prąd testowy wyniósłby tylko 0,5 mA, a błędne R_T=2 kΩ. Źródła zależne opisują właściwość portu i pozostają w modelu." , "warn"),
        PageBreak(),

        base.H1("7. Procedura i kontrola wyniku"),
        base.H2("Szybki algorytm"),
        base.info_table([
            ["Pytanie", "Zrób to"],
            ["Co steruje źródłem?", "Wypisz u_x lub i_x, biegunowość/strzałkę i jednostkę współczynnika."],
            ["Jakie równania?", "KCL dla węzłów z VCCS/CCCS; KVL lub warunek superwęzła dla VCVS/CCVS."],
            ["Jest kilka źródeł niezależnych?", "Możesz użyć superpozycji w obwodzie liniowym, ale zależne zostaw aktywne w każdym przypadku."],
            ["Szukasz R_T?", "Wyzeruj tylko niezależne źródła, przyłóż U_t/I_t, policz R_T=U_t/I_t."],
            ["Jaki wynik?", "Sprawdź znak, jednostki i co najmniej jedno KCL/KVL w oryginalnym obwodzie."],
        ], [45 * mm, CONTENT_W - 45 * mm]),
        base.H2("Typowe błędy"),
        base.bullet("Wyłączenie źródła zależnego przy superpozycji albo przy obliczaniu R_T."),
        base.bullet("Użycie napięcia/prądu sterującego bez zaznaczenia jego zwrotu i biegunowości."),
        base.bullet("Pomylenie jednostek: g ma siemensy, a r ma omy; β i μ są bezwymiarowe."),
        base.bullet("Wstawienie napięciowego źródła idealnego do zwykłego KCL bez superwęzła lub dodatkowej niewiadomej prądu."),
        base.bullet("Uznanie, że minus oznacza błąd. Minus mówi, że wynik jest przeciwny do przyjętego odniesienia."),
        base.eqbox("Podsumowanie:   i_d=g u_x;   u_d=μu_x;   i_d=βi_x;   u_d=ri_x.\nNiezależne źródła można zerować według reguł; zależne — nie.\nDla R_T z zależnościami sterowanymi: źródło testowe + wszystkie źródła zależne aktywne."),
        base.callout("Ostatni test", "Po obliczeniu wartości źródła sterowanego wstaw ją z powrotem do równania gałęzi. Jeśli źródło ma 2 mA w dół, a Twoje KCL wymaga 2 mA w górę, sprawdź znak zależności lub zwrot sterujący."),
    ]
    return story


def main():
    doc = QuickDocTemplate(
        str(OUTPUT), pagesize=base.A4,
        leftMargin=LEFT, rightMargin=RIGHT, topMargin=TOP, bottomMargin=BOTTOM,
        title="PLP K1 — obwody ze źródłami sterowanymi",
        author="Opracowanie własne",
        subject="Metody węzłowa i oczkowa, źródła zależne, superpozycja, Thévenin i Norton",
        keywords="PLP K1, źródła sterowane, VCCS, VCVS, CCCS, CCVS, superwęzeł, źródło testowe",
    )
    doc.multiBuild(build_story())
    print(f"Zapisano: {OUTPUT}")


if __name__ == "__main__":
    main()
