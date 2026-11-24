#!/usr/bin/env python3
"""Generate a standalone Polish guide to circuit reference directions and methods.

Requires ReportLab and the DejaVu fonts used by generate_plp_k1_guide.py.
Run from the repository root:
    python tools/generate_plp_k1_metody_analizy.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import Flowable, NextPageTemplate, PageBreak, Spacer

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "PLP_K1_metody_analizy_obwodow.pdf"
sys.path.insert(0, str(ROOT))

from tools import generate_plp_k1_guide as base  # noqa: E402

PAGE_W, PAGE_H = base.PAGE_W, base.PAGE_H
LEFT, RIGHT, TOP, BOTTOM = base.LEFT, base.RIGHT, base.TOP, base.BOTTOM
CONTENT_W = base.CONTENT_W
NAVY, TEAL, TEAL_DARK = base.NAVY, base.TEAL, base.TEAL_DARK
SKY, PALE, GOLD = base.SKY, base.PALE, base.GOLD
INK, MUTED, LINE, WHITE = base.INK, base.MUTED, base.LINE, base.WHITE


def arrow(c, x1, y1, x2, y2, color=GOLD, head=5, width=1.4):
    dx, dy = x2 - x1, y2 - y1
    angle = math.atan2(dy, dx)
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(width)
    c.line(x1, y1, x2, y2)
    left = (x2 - head * math.cos(angle - 0.48), y2 - head * math.sin(angle - 0.48))
    right = (x2 - head * math.cos(angle + 0.48), y2 - head * math.sin(angle + 0.48))
    path = c.beginPath()
    path.moveTo(x2, y2)
    path.lineTo(*left)
    path.lineTo(*right)
    path.close()
    c.drawPath(path, fill=1, stroke=0)


def resistor_h(c, x1, x2, y, label, height=14):
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.25)
    cx = (x1 + x2) / 2
    half = min(23, (x2 - x1) * 0.25)
    c.line(x1, y, cx - half, y)
    c.line(cx + half, y, x2, y)
    c.setFillColor(WHITE)
    c.roundRect(cx - half, y - height / 2, 2 * half, height, 2, fill=1, stroke=1)
    c.setFillColor(INK)
    c.setFont("DejaVu-Bold", 7.2)
    c.drawCentredString(cx, y - 2.4, label)


def resistor_v(c, x, y1, y2, label, width=16):
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.25)
    cy = (y1 + y2) / 2
    half = min(12, (y2 - y1) * 0.22)
    c.line(x, y1, x, cy - half)
    c.line(x, cy + half, x, y2)
    c.setFillColor(WHITE)
    c.roundRect(x - width / 2, cy - half, width, 2 * half, 2, fill=1, stroke=1)
    c.saveState()
    c.translate(x, cy)
    c.rotate(90)
    c.setFillColor(INK)
    c.setFont("DejaVu-Bold", 7.0)
    c.drawCentredString(0, -2.3, label)
    c.restoreState()


def voltage_source(c, x, y1, y2, label, plus_top=True, radius=9):
    cy = (y1 + y2) / 2
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.2)
    c.line(x, y1, x, cy - radius)
    c.line(x, cy + radius, x, y2)
    c.setFillColor(WHITE)
    c.circle(x, cy, radius, fill=1, stroke=1)
    c.setFillColor(TEAL_DARK)
    c.setFont("DejaVu-Bold", 8)
    c.drawCentredString(x, cy + 1.5, "+" if plus_top else "−")
    c.drawCentredString(x, cy - 7.5, "−" if plus_top else "+")
    c.setFillColor(INK)
    c.setFont("DejaVu-Bold", 7.1)
    c.drawRightString(x - radius - 4, cy - 2.5, label)


def node_dot(c, x, y, label=None, color=base.NODE_A, dx=5, dy=4):
    c.setFillColor(color)
    c.setStrokeColor(WHITE)
    c.setLineWidth(0.8)
    c.circle(x, y, 3.0, fill=1, stroke=1)
    if label:
        c.setFillColor(color)
        c.setFont("DejaVu-Bold", 7.2)
        c.drawString(x + dx, y + dy, label)


class CurrentVoltageDiagram(Flowable):
    """Two reference-direction choices on the same resistor."""

    def __init__(self, width=CONTENT_W, height=120):
        super().__init__()
        self.width, self.height = width, height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return self.width, self.height

    def _branch(self, c, x0, x1, y, current_forward, title, formula, ptext):
        c.setFillColor(WHITE)
        c.setStrokeColor(LINE)
        c.roundRect(x0, 7, x1 - x0, self.height - 14, 5, fill=1, stroke=1)
        c.setFillColor(TEAL_DARK)
        c.setFont("DejaVu-Bold", 7.7)
        c.drawCentredString((x0 + x1) / 2, self.height - 18, title)
        a, b = x0 + 22, x1 - 22
        resistor_h(c, a, b, y, "R")
        c.setFillColor(INK)
        c.setFont("DejaVu-Bold", 7.2)
        if current_forward:
            arrow(c, a + 24, y + 23, b - 8, y + 23, TEAL, head=4.5)
            c.drawString(a + 8, y + 21, "i")
        else:
            arrow(c, b - 24, y + 23, a + 8, y + 23, TEAL, head=4.5)
            c.drawRightString(b - 8, y + 21, "i")
        c.setFont("DejaVu-Bold", 8)
        c.drawCentredString(a + 30, y + 4, "+")
        c.drawCentredString(b - 30, y + 4, "−")
        arrow(c, a + 18, y - 23, b - 8, y - 23, GOLD, head=4.5)
        c.setFillColor(GOLD)
        c.setFont("DejaVu-Bold", 7.2)
        c.drawString(a + 3, y - 32, "u")
        c.setFont("DejaVu", 7.2)
        c.setFillColor(NAVY)
        c.drawCentredString((x0 + x1) / 2, 17, formula)
        c.setFillColor(MUTED)
        c.setFont("DejaVu", 6.5)
        c.drawCentredString((x0 + x1) / 2, 9, ptext)

    def draw(self):
        c = self.canv
        c.saveState()
        c.setFillColor(PALE)
        c.setStrokeColor(LINE)
        c.roundRect(0, 0, self.width, self.height, 6, fill=1, stroke=1)
        gap = 8
        col = (self.width - 3 * gap) / 2
        self._branch(c, gap, gap + col, 61, True, "Odniesienia zgodne (konwencja pasywna)",
                     "u = R i     ·     P₍pobierana₎ = u i", "i wpływa do zacisku +")
        self._branch(c, 2 * gap + col, self.width - gap, 61, False, "Odniesienia przeciwne",
                     "u = −R i     ·     P₍pobierana₎ = −u i", "i wpływa do zacisku −")
        c.restoreState()


class NodalExampleDiagram(Flowable):
    """Circuit for the worked one-node KCL example."""

    def __init__(self, width=CONTENT_W, height=111):
        super().__init__()
        self.width, self.height = width, height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        c.setFillColor(PALE)
        c.setStrokeColor(LINE)
        c.roundRect(0, 0, self.width, self.height, 6, fill=1, stroke=1)
        ytop, yground = 77, 21
        xsource, xnode, xr, xj = 68, self.width * 0.49, self.width * 0.70, self.width - 68
        c.setStrokeColor(NAVY)
        c.setLineWidth(1.2)
        # Reference rail and source E=12 V establish the fixed left-hand node.
        c.line(xsource, yground, xj, yground)
        voltage_source(c, xsource, yground, ytop, "E", plus_top=True, radius=9)
        c.setFillColor(MUTED)
        c.setFont("DejaVu", 7.0)
        c.drawString(xsource + 10, ytop + 8, "V_L = 12 V")
        # The unknown node and its three incident branches.
        resistor_h(c, xsource, xnode, ytop, "R₁=4 kΩ")
        c.line(xnode, ytop, xj, ytop)
        node_dot(c, xnode, ytop, "X", base.NODE_C, dx=5, dy=4)
        resistor_v(c, xr, yground, ytop, "R₂=6 kΩ", width=18)
        c.line(xj, yground, xj, ytop - 10)
        c.circle(xj, (yground + ytop) / 2, 9, fill=1, stroke=1)
        arrow(c, xj, (yground + ytop) / 2 - 5, xj, (yground + ytop) / 2 + 5, TEAL_DARK, head=3.7, width=1.0)
        c.line(xj, ytop - 10, xj, ytop)
        c.setFillColor(INK)
        c.setFont("DejaVu-Bold", 7.2)
        c.drawString(xj + 12, (yground + ytop) / 2 - 2, "J=1 mA")
        c.setFillColor(MUTED)
        c.setFont("DejaVu", 6.7)
        c.drawString(xsource + 10, yground - 10, "węzeł odniesienia 0 V")
        c.drawCentredString(self.width / 2, 5, "Strzałka J wstrzykuje prąd do węzła X.")
        c.restoreState()


class MeshExampleDiagram(Flowable):
    """Two adjacent meshes, with a shared resistor and compatible source polarities."""

    def __init__(self, width=CONTENT_W, height=132):
        super().__init__()
        self.width, self.height = width, height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        c.setFillColor(PALE)
        c.setStrokeColor(LINE)
        c.roundRect(0, 0, self.width, self.height, 6, fill=1, stroke=1)
        xl, xm, xr = 60, self.width / 2, self.width - 60
        yt, yb = 105, 23
        # Upper and lower rails with R1 and R2 in the top branches.
        resistor_h(c, xl, xm, yt, "R₁=2 kΩ")
        resistor_h(c, xm, xr, yt, "R₂=4 kΩ")
        c.setStrokeColor(NAVY)
        c.setLineWidth(1.25)
        c.line(xl, yb, xm, yb)
        c.line(xm, yb, xr, yb)
        # Outer source branches and shared resistor.
        voltage_source(c, xl, yb, yt, "E₁", plus_top=True, radius=9)
        resistor_v(c, xm, yb, yt, "R₃=2 kΩ", width=18)
        voltage_source(c, xr, yb, yt, "E₂", plus_top=False, radius=9)
        # Mesh-current labels; both currents are clockwise.
        c.setFillColor(TEAL_DARK)
        c.setFont("DejaVu-Bold", 9.2)
        c.drawCentredString((xl + xm) / 2, 63, "I₁ ↻")
        c.drawCentredString((xm + xr) / 2, 63, "I₂ ↻")
        # Shared-branch reference is downward: I₃ = I₁ - I₂.
        arrow(c, xm + 23, 82, xm + 23, 47, GOLD, head=4.5, width=1.3)
        c.setFillColor(INK)
        c.setFont("DejaVu", 6.8)
        c.drawString(xm + 29, 62, "I₃")
        c.setFillColor(MUTED)
        c.setFont("DejaVu", 6.8)
        c.drawCentredString(self.width / 2, 7, "E₁: plus u góry; E₂: plus na dole; oba źródła wspomagają przyjęte oczka.")
        c.restoreState()


class GuideDocTemplate(base.ManualDocTemplate):
    """Use the repository's typography and bookmarks with a document-specific header."""

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
        canvas.drawString(LEFT + 7 * mm, 34 * mm, "Zwroty odniesienia, równania Kirchhoffa i metody analizy")
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
        canvas.drawRightString(PAGE_W - RIGHT, PAGE_H - 7.5 * mm, "Metody analizy obwodów")
        canvas.line(LEFT, 10 * mm, PAGE_W - RIGHT, 10 * mm)
        canvas.setFont("DejaVu", 7.2)
        canvas.setFillColor(MUTED)
        canvas.drawString(LEFT, 6.5 * mm, "Najpierw ustal zwroty; później zachowaj je konsekwentnie w równaniach.")
        canvas.drawRightString(PAGE_W - RIGHT, 6.5 * mm, f"str. {doc.page}")
        canvas.restoreState()


def build_story():
    story = [
        Spacer(1, 26 * mm),
        base.P("PODSTAWY ANALIZY OBWODÓW · PLP K1", "CoverKicker"),
        base.P("Zwroty i metody", "CoverTitle"),
        base.P("Prądy, napięcia, metoda węzłowa i oczkowa oraz równoważniki Thévenina i Nortona", "CoverSub"),
        Spacer(1, 10 * mm),
        base.callout(
            "Cel opracowania",
            "Zbudować spójny sposób zapisywania znaków i wybrać właściwą metodę obliczeń. Każdy wynik interpretujemy względem wcześniej przyjętych zwrotów — nie poprawiamy strzałek w trakcie rachunku.",
        ),
        Spacer(1, 7 * mm),
        base.P("Przewodnik zawiera krótkie algorytmy, rysunki konwencji oraz trzy przykłady rachunkowe. Zakres: liniowe obwody rezystancyjne prądu stałego.", "CoverMeta"),
        base.P("Najważniejsze równania: u=Ri, KCL w węźle, KVL w oczku; dla portu: E_T=U_oc, J_N=I_sc oraz R_T=R_N.", "CoverMeta"),
        NextPageTemplate("Body"),
        PageBreak(),

        base.H1("Mapa opracowania i wybór metody"),
        base.P("Zacznij od oznaczenia zacisków, węzłów i zwrotów. Następnie wybierz metodę, która wymaga najmniejszej liczby niewiadomych. Nie ma potrzeby używać jednej metody do całego zadania — można je łączyć."),
        base.info_table([
            ["Metoda", "Niewiadome", "Kiedy zwykle wygodna"],
            ["Węzłowa", "Napięcia węzłowe względem masy", "Mało istotnych węzłów, źródła prądowe, wiele gałęzi równoległych"],
            ["Oczkowa", "Prądy oczkowe", "Obwód planarny z małą liczbą oczek i źródeł napięcia"],
            ["Thévenina / Nortona", "Dwa parametry portu", "Ważne jest zachowanie obwodu widzianego przez obciążenie; porównujemy różne obciążenia"],
        ], [34 * mm, 53 * mm, CONTENT_W - 87 * mm]),
        base.H2("Co oznaczają strzałki?"),
        base.bullet("Strzałka prądu jest umownym dodatnim zwrotem. Ujemny wynik oznacza, że prąd płynie przeciwnie."),
        base.bullet("Napięcie definiujemy przez bieguny lub jawnie przyjętą strzałkę. W tym przewodniku strzałka napięcia oznacza spadek od + do −."),
        base.bullet("Wartość źródła, biegunowość i zwrot prądu źródła muszą być czytelne na schemacie."),
        base.callout("Notacja portu", "U_AB = V_A − V_B. Dodatnie U_AB oznacza, że potencjał A jest wyższy niż B. W części Thévenina dodatnie E_T ma biegun + przy A."),
        base.H2("Plan dalszych stron"),
        base.info_table([
            ["Strona", "Temat"],
            ["3", "Zwroty i znaki napięć/prądów; konwencja pasywna"],
            ["4", "KCL, KVL, źródła, jednostki i zapis równań"],
            ["5–6", "Metoda węzłowa i metoda oczkowa — algorytmy z przykładami"],
            ["7–8", "Twierdzenia Thévenina i Nortona — procedura i przykład z obciążeniem"],
            ["9–10", "Porównanie, typowe błędy i karta szybkiej kontroli"],
        ], [25 * mm, CONTENT_W - 25 * mm]),
        PageBreak(),

        base.H1("1. Strzałkowanie prądów i napięć"),
        base.P("Zwroty odniesienia są częścią definicji znaku niewiadomej, a nie próbą zgadnięcia kierunku fizycznego. Dla nieznanego prądu wybierz dowolną strzałkę, podpisz ją i użyj konsekwentnie w KCL, KVL oraz prawie Ohma."),
        CurrentVoltageDiagram(),
        base.H2("Napięcie: biegunowość albo strzałka"),
        base.P("Zapis <b>u_AB=V_A−V_B</b> znaczy, że zacisk A jest biegunem dodatnim względem B. Przy konwencji użytej na rysunku strzałka napięcia biegnie od + do − i wskazuje spadek: u=V_początek−V_koniec. Jeśli inne notatki definiują strzałkę odwrotnie, równanie zmieni znak — fizyczny wynik pozostanie ten sam po konsekwentnej zmianie konwencji."),
        base.H2("Rezystor i moc"),
        base.P("Gdy prąd wpływa do dodatniego zacisku rezystora (konwencja pasywna), u=Ri i P_pobierana=ui=i²R≥0. Jeśli odniesienia i oraz u są przeciwne, to u=−Ri, a moc pobierana wynosi −ui. Moc ujemna oznacza, że element oddaje energię do reszty obwodu według przyjętych znaków."),
        base.eqbox("u_AB=V_A−V_B     ·     I_{A→B}=(V_A−V_B)/R     ·     G=1/R"),
        base.H2("Źródła i znaczenie wyniku"),
        base.P("Źródło napięcia E ustala różnicę potencjałów: E=V_+−V_−. Strzałka źródła prądu ustala dodatni kierunek jego prądu. W obu przypadkach zwrot jest odniesieniem — źródło może przyjmować albo oddawać moc zależnie od pozostałej części obwodu."),
        base.callout("Przykład interpretacji", "Jeśli dla strzałki w prawo otrzymasz I=−0,4 mA, zapisz: prąd ma wartość 0,4 mA i płynie w lewo. Nie zmieniaj po cichu znaku w równaniach; interpretację dopisz na końcu."),
        PageBreak(),

        base.H1("2. KCL, KVL i przygotowanie równań"),
        base.P("Prawa Kirchhoffa wynikają z zachowania ładunku i energii. Można przyjąć dowolne zwroty prądów oraz dowolny kierunek obchodzenia oczka, byle utrzymać te wybory w całym równaniu."),
        base.info_table([
            ["Prawo", "Zapis", "Zasada znaków"],
            ["KCL — prądowe", "Σ i_k = 0 w węźle", "Najpierw wybierz: wszystkie wypływające albo wpływające. W kierunku przeciwnym wpisz znak minus."],
            ["KVL — napięciowe", "Σ u_k = 0 w zamkniętym oczku", "Dla strzałek spadku: przejście zgodne ze strzałką to +u, przeciwne to −u."],
        ], [31 * mm, 43 * mm, CONTENT_W - 74 * mm]),
        base.H2("Praktyczny zapis KCL"),
        base.P("Dla rezystora między węzłami a i b prąd od a do b wynosi (V_a−V_b)/R=G(V_a−V_b). Jeśli węzeł b ma znany potencjał, np. V_b=E, wstaw go bezpośrednio do tego wyrażenia. Źródło prądu skierowane od a do b wnosi +J do sumy prądów wypływających z a i −J do sumy wypływających z b."),
        base.eqbox("Przykład KCL: prądy wypływające z X:  (V_X−V_A)/R₁ + V_X/R₂ − J = 0,\ngdzie strzałka J jest skierowana do X, a dolny węzeł R₂ jest masą."),
        base.H2("Praktyczny zapis KVL"),
        base.P("Obejdź oczko w jednym kierunku. Każdy rezystor zapisz z prądem zgodnym z przyjętym odniesieniem. Źródło napięcia daje spadek +E, jeśli idziesz od + do −; przejście od − do + jest wzrostem potencjału, czyli spadkiem −E."),
        base.eqbox("Przykład: obchodzimy rezystor zgodnie z I (spadek R I), a źródło od − do + (wzrost E):  R I − E = 0."),
        base.H2("Jednostki, zanim policzysz"),
        base.info_table([
            ["Zapis", "Wynik", "Kontrola"],
            ["kΩ · mA", "V", "4 kΩ · 2 mA = 8 V"],
            ["V / kΩ", "mA", "12 V / 3 kΩ = 4 mA"],
            ["mS · V", "mA", "0,5 mS · 6 V = 3 mA"],
        ], [42 * mm, 30 * mm, CONTENT_W - 72 * mm]),
        base.callout("Przed ułożeniem równań", "Zaznacz masę, połącz przewodami tożsamy węzeł, odczytaj biegunowości źródeł i podpisz prądy. Połączenia szeregowe/równoległe rozpoznawaj po węzłach, nie po samym wyglądzie rysunku."),
        PageBreak(),

        base.H1("3. Metoda węzłowa"),
        base.P("Metoda węzłowa wyznacza potencjały węzłów względem jednego wybranego węzła odniesienia. Dla N węzłów zwykle rozwiązuje się N−1 niewiadomych. Po znalezieniu napięć prądy gałęzi oblicza się prawem Ohma."),
        base.H2("Algorytm"),
        base.info_table([
            ["Krok", "Działanie"],
            ["1", "Wybierz węzeł odniesienia 0 V — zwykle taki, który łączy wiele gałęzi."],
            ["2", "Oznacz napięcia wszystkich pozostałych istotnych węzłów."],
            ["3", "Dla każdego nieodniesionego węzła zapisz KCL. Prądy rezystorów wyraź jako (V_węzła−V_drugiego)/R."],
            ["4", "Rozwiąż układ równań; wyznacz szukaną gałąź i zachowaj jej zadany zwrot."],
        ], [16 * mm, CONTENT_W - 16 * mm]),
        base.P("W zapisie macierzowym element diagonalny macierzy konduktancyjnej jest sumą konduktancji dołączonych do danego węzła. Element pozadiagonalny dla dwóch połączonych węzłów to minus suma konduktancji łączących te węzły. Po prawej stronie są źródła prądu i wkłady znanych potencjałów."),
        NodalExampleDiagram(),
        base.H2("Przykład: jedno nieznane napięcie"),
        base.P("W węźle X zapisujemy prądy wypływające. Dla gałęzi R₁ napięcie drugiego końca wynosi 12 V; źródło J=1 mA wstrzykuje prąd do X, więc w równaniu wypływającym ma znak minus."),
        base.eqbox("(V_X−12)/4 kΩ + V_X/6 kΩ − 1 mA = 0.\nW jednostkach mA: (V_X−12)/4 + V_X/6 − 1 = 0  ⇒  3(V_X−12)+2V_X−12=0  ⇒  V_X=9,6 V."),
        base.P("Kontrola prądów: I_R₁=(9,6−12)/4=−0,6 mA (rzeczywiście do X), I_R₂=9,6/6=1,6 mA, a źródło wnosi −1 mA do sumy wypływających. Suma −0,6+1,6−1=0."),
        base.callout("Węzeł super", "Idealnego źródła napięcia między dwoma nieznanymi węzłami nie da się zapisać jako zwykłego prądu (V_a−V_b)/R. Obejmij oba węzły jedną otoczką, napisz dla niej KCL i dodaj warunek V_a−V_b=E zgodnie z biegunowością źródła."),
        PageBreak(),

        base.H1("4. Metoda oczkowa"),
        base.P("Metoda oczkowa wyznacza prądy niezależnych oczek. Jest szczególnie wygodna dla obwodów planarnych z niewielką liczbą oczek. Ustal zwroty prądów oczkowych (często wszystkie zgodnie z ruchem wskazówek zegara), a następnie zapisz KVL."),
        base.H2("Jak zapisać gałąź wspólną"),
        base.P("Jeśli rezystor R₃ leży między oczkami 1 i 2, a oba prądy są zgodne z ruchem wskazówek zegara, to na wspólnej gałęzi mają przeciwne kierunki. Dla odniesienia w dół I₃=I₁−I₂, a spadek w równaniu oczka 1 wynosi R₃(I₁−I₂). W równaniu oczka 2 jest R₃(I₂−I₁)."),
        MeshExampleDiagram(),
        base.H2("Przykład: dwa oczka i wspólny rezystor"),
        base.P("Dane ze schematu: R₁=2 kΩ, R₂=4 kΩ, R₃=2 kΩ, E₁=10 V, E₂=4 V. Przy obu prądach oczkowych zgodnych z ruchem wskazówek zegara źródła pokazano tak, by oba były wzrostem napięcia w przyjętym obiegu."),
        base.eqbox("Oczko 1:  (R₁+R₃)I₁ − R₃I₂ = E₁  ⇒  4I₁−2I₂=10.\nOczko 2:  −R₃I₁ + (R₂+R₃)I₂ = E₂  ⇒  −2I₁+6I₂=4.\nRozwiązanie: I₁=3,4 mA, I₂=1,8 mA; prąd R₃ w dół: I₃=I₁−I₂=1,6 mA."),
        base.H2("Gdy w obwodzie jest źródło prądu"),
        base.bullet("Źródło na zewnętrznym brzegu oczka może od razu określać prąd tego oczka — pilnuj zgodności zwrotu."),
        base.bullet("Źródło między dwoma oczkami: utwórz superoczko, napisz KVL po zewnętrznym obrysie i dodaj równanie więzu dla prądów oczkowych."),
        base.callout("Zakres metody", "Metoda oczkowa w standardowej postaci jest przeznaczona dla obwodów planarnych. Przy wielu źródłach prądu lub nieplanarnym schemacie zwykle wygodniej użyć metody węzłowej."),
        PageBreak(),

        base.H1("5. Twierdzenia Thévenina i Nortona"),
        base.P("Liniowy dwójnik widziany z dwóch zacisków A–B można zastąpić prostym równoważnikiem. Model Thévenina to idealne źródło napięcia E_T połączone szeregowo z R_T; model Nortona to idealne źródło prądu J_N równolegle z tą samą R_N. Oba modele mają tę samą zależność napięcia od prądu na porcie i dają te same wyniki dla dowolnego dołączonego obciążenia."),
        base.SourceConversionDiagram(),
        base.eqbox("E_T = U_oc = U_AB przy rozwarciu.\nJ_N = I_sc — prąd w zewnętrznym zwarciu A→B. W modelu Nortona źródło J_N ma strzałkę B→A.\nR_T = R_N;   E_T = J_N R_T;   J_N = E_T/R_T."),
        base.H2("Procedura wyznaczenia równoważnika"),
        base.info_table([
            ["Wielkość", "Jak ją znaleźć"],
            ["E_T", "Odłącz obciążenie i wyznacz napięcie jałowe U_AB. Zachowaj biegunowość A–B."],
            ["R_T", "Wyzeruj źródła niezależne: idealne E zastąp zwarciem, idealne J — rozwarciem. Policz rezystancję widzianą od A–B."],
            ["J_N", "Wyznacz prąd zwarcia lub oblicz J_N=E_T/R_T. Dodatni J_N płynie wewnątrz źródła Norton B→A."],
        ], [29 * mm, CONTENT_W - 29 * mm]),
        base.H2("Źródła sterowane — ważny wyjątek"),
        base.P("Źródeł zależnych nie wyłączamy. Przy wyznaczaniu R_T zerujemy tylko źródła niezależne, przykładamy do portu źródło testowe U_x albo I_x i liczymy R_T=U_x/I_x. Można też, jeśli prąd zwarcia jest niezerowy, skorzystać z R_T=U_oc/I_sc przy zgodnych zwrotach."),
        base.eqbox("Idealne źródło napięcia wyłączone → zwarcie.\nIdealne źródło prądu wyłączone → rozwarcie.\nŹródła zależne pozostają aktywne; rezystory i obciążenie nie są „wyłączanymi źródłami”."),
        base.H2("Dołączenie obciążenia R_L"),
        base.eqbox("I_L = E_T/(R_T+R_L)     ·     U_L = E_T R_L/(R_T+R_L)\nZ modelu Nortona: I_L = J_N R_T/(R_T+R_L). Kierunek I_L przyjęto od A do B."),
        PageBreak(),

        base.H1("6. Przykład Thévenina i Nortona z obciążeniem"),
        base.P("Źródło E=18 V (biegun + po stronie R₁, biegun − przy B) zasila dzielnik: R₁=3 kΩ w szeregu do zacisku A, R₂=6 kΩ od A do B. Najpierw wyznacz równoważnik widziany z A–B, a potem dołącz R_L=4 kΩ."),
        base.H2("1) Napięcie Thévenina"),
        base.P("Po odłączeniu R_L przez R₁ i R₂ płynie ten sam prąd. Napięcie jałowe na A–B jest napięciem na R₂."),
        base.eqbox("E_T = U_oc = 18 · 6/(3+6) = 12 V."),
        base.H2("2) Rezystancja Thévenina"),
        base.P("Zerujemy niezależne źródło E — idealne źródło napięcia zastępujemy zwarciem. Widziane z A–B rezystory R₁ i R₂ są równoległe."),
        base.eqbox("R_T = R₁ ∥ R₂ = 3 · 6/(3+6) = 2 kΩ."),
        base.H2("3) Norton i odbiornik"),
        base.eqbox("J_N = E_T/R_T = 12/2 = 6 mA, strzałka B→A.\nI_L = 12/(2+4) = 2 mA;   U_L = I_L R_L = 8 V."),
        base.P("Kontrola: w modelu Nortona I_L=J_N·R_T/(R_T+R_L)=6·2/(2+4)=2 mA. Napięcie U_L=8 V jest mniejsze od E_T=12 V, bo część napięcia odkłada się na R_T."),
        base.callout("Sprawdź znaki i zaciski", "Dodatnie E_T=12 V oznacza V_A>V_B. Źródło Nortona ma strzałkę B→A, ale dodatni prąd zwarcia płynie przez zewnętrzne zwarcie od A do B. To są dwa fragmenty tej samej pętli."),
        PageBreak(),

        base.H1("7. Porównanie metod i typowe błędy"),
        base.info_table([
            ["Cecha", "Węzłowa", "Oczkowa", "Thévenin / Norton"],
            ["Niewiadome", "Napięcia węzłów", "Prądy oczek", "E_T i R_T albo J_N i R_N"],
            ["Prawo bazowe", "KCL", "KVL", "Napięcie jałowe / prąd zwarcia i rezystancja portu"],
            ["Najwygodniejsza, gdy…", "Mało węzłów, dużo gałęzi i źródeł prądu", "Układ planarny, mało oczek i źródeł napięcia", "Interesuje nas jedno wyjście i zmieniające się obciążenie"],
            ["Szczególny przypadek", "Źródło napięcia między nieznanymi węzłami → węzeł super", "Źródło prądu wspólne dla oczek → superoczko", "Źródło zależne → aktywne źródło testowe przy R_T"],
        ], [33 * mm, (CONTENT_W - 33 * mm) / 3, (CONTENT_W - 33 * mm) / 3, (CONTENT_W - 33 * mm) / 3]),
        base.H2("Błędy, które najczęściej zmieniają odpowiedź"),
        base.bullet("Zmiana strzałki lub biegunowości w połowie obliczeń bez zmiany znaku w równaniu."),
        base.bullet("Uznanie, że elementy są szeregowe tylko dlatego, że narysowano je jeden za drugim; rozstrzygają węzły i rozgałęzienia."),
        base.bullet("W KCL pominięcie prądu przez gałąź łączącą dwa niezerowe węzły: użyj (V_a−V_b)/R, a nie V_a/R."),
        base.bullet("Utożsamienie metody oczkowej z dowolnym obiegiem — standardowe prądy oczkowe wymagają planarnych oczek; wspólną gałąź zapisuje się jako różnicę prądów."),
        base.bullet("Wyłączenie źródła zależnego przy liczeniu R_T albo rozwarcie źródła napięciowego / zwarcie źródła prądowego."),
        base.bullet("Pomylenie zwrotu J_N z prądem przez obciążenie; zawsze zaznacz, czy mierzysz kierunek wewnętrznego źródła, czy prąd zewnętrzny A→B."),
        base.callout("Test sensowności", "Sprawdź jednostki, znak, skrajne przypadki (np. R_L→0 i R_L→∞) oraz to, czy napięcie i prąd spełniają KCL/KVL. Jeśli wynik jest ujemny, najpierw zinterpretuj zwrot — nie kasuj minusa."),
        PageBreak(),

        base.H1("8. Karta szybkiej kontroli"),
        base.H2("Zapisz przed liczeniem"),
        base.info_table([
            ["Pole", "Co wpisać"],
            ["Odniesienie", "Masa, nazwy węzłów, biegunowość U_AB i zwroty prądów."],
            ["Równania", "KCL albo KVL; prądy przez R jako różnica potencjałów podzielona przez R."],
            ["Jednostki", "Ujednolicić V, kΩ, mA, mS; pamiętać kΩ·mA=V."],
            ["Wynik", "Zachować znak, dopisać kierunek rzeczywisty i jednostkę."],
            ["Kontrola", "KCL/KVL, moc, granice oraz zgodność U_oc=J_N R_T."],
        ], [34 * mm, CONTENT_W - 34 * mm]),
        base.H2("Wzory do zapamiętania"),
        base.eqbox("Rezystor:  u=Ri,  i=(V_a−V_b)/R,  G=1/R.\nKCL:  Σ i_wypływających=0.     KVL:  Σ u_spadków=0 w zamkniętym obiegu.\nWęzłowa:  prądy gałęzi = G(V_a−V_b).     Oczkowa:  prąd wspólnej gałęzi = algebraiczna różnica prądów oczek.\nThévenin:  E_T=U_oc;  Norton:  J_N=I_sc;  R_T=R_N;  E_T=J_N R_T."),
        base.H2("Co warto dołączyć do repozytorium jako następne?"),
        base.P("Po opanowaniu tych metod najbardziej użyteczny będzie zestaw ćwiczeń krok po kroku: superpozycja i zamiana źródeł, obwody z generatorami zależnymi, dzielniki i obciążenie, a następnie mostki i transformacja Δ–Y. Dalej warto rozwinąć elementy nieliniowe i punkt pracy (dioda), wzmacniacz operacyjny oraz obwody prądu przemiennego z fazorami."),
        base.callout("Kolejność nauki", "Podstawy zwrotów → KCL/KVL → metoda węzłowa i oczkowa → superpozycja → Thévenin/Norton → źródła sterowane i testowe → mostki/Δ–Y → diody i wzmacniacze operacyjne → AC/fazory."),
    ]
    return story


def main():
    doc = GuideDocTemplate(
        str(OUTPUT), pagesize=base.A4,
        leftMargin=LEFT, rightMargin=RIGHT, topMargin=TOP, bottomMargin=BOTTOM,
        title="PLP K1 — zwroty i metody analizy obwodów",
        author="Opracowanie własne",
        subject="Strzałkowanie prądów i napięć, KCL/KVL, metody węzłowa i oczkowa, równoważniki Thévenina i Nortona",
        keywords="PLP K1, obwody, strzałkowanie, Kirchhoff, metoda węzłowa, oczkowa, Thevenin, Norton",
    )
    doc.multiBuild(build_story())
    print(f"Zapisano: {OUTPUT}")


if __name__ == "__main__":
    main()
