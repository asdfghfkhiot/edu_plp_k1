#!/usr/bin/env python3
"""Generate extended and concise colored-node variants of the PLP K1 guide.

Requires ReportLab and the fonts used by generate_plp_k1_guide.py.
Run from the repository root:
    python tools/generate_plp_k1_variants.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import Flowable, PageBreak, NextPageTemplate, Spacer, Table, TableStyle

from tools import generate_plp_k1_guide as base


EXTENDED = ROOT / "PLP_K1_poradnik_rozszerzony.pdf"
SHORT = ROOT / "PLP_K1_poradnik_skrocony.pdf"

NAVY = base.NAVY
TEAL = base.TEAL
TEAL_DARK = base.TEAL_DARK
PALE = base.PALE
SKY = base.SKY
GOLD = base.GOLD
INK = base.INK
MUTED = base.MUTED
WHITE = base.WHITE
LINE = base.LINE
NODE_A = base.NODE_A
NODE_B = base.NODE_B
NODE_C = base.NODE_C
NODE_D = base.NODE_D


def line(c, p1, p2, width=1.35, color=NAVY):
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(p1[0], p1[1], p2[0], p2[1])


def arrow(c, p1, p2, color=TEAL, head=5):
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1.5)
    c.line(p1[0], p1[1], p2[0], p2[1])
    a = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    p_left = (p2[0] - head * math.cos(a - 0.48), p2[1] - head * math.sin(a - 0.48))
    p_right = (p2[0] - head * math.cos(a + 0.48), p2[1] - head * math.sin(a + 0.48))
    path = c.beginPath()
    path.moveTo(p2[0], p2[1]); path.lineTo(*p_left); path.lineTo(*p_right); path.close()
    c.drawPath(path, fill=1, stroke=0)


def node(c, x, y, label, color, dx=5, dy=4, radius=3.7):
    base.paint_node(c, x, y, label, color, dx=dx, dy=dy, radius=radius)


def resistor_between(c, p1, p2, label, length=37, height=14):
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    dist = math.hypot(dx, dy)
    if dist < length + 2:
        length = max(14, dist * 0.55)
    ux, uy = dx / dist, dy / dist
    cx, cy = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
    half = length / 2
    line(c, p1, (cx - ux * half, cy - uy * half))
    line(c, (cx + ux * half, cy + uy * half), p2)
    angle = math.degrees(math.atan2(dy, dx))
    c.saveState()
    c.translate(cx, cy); c.rotate(angle)
    c.setFillColor(WHITE); c.setStrokeColor(NAVY); c.setLineWidth(1.2)
    c.roundRect(-half, -height / 2, length, height, 2, fill=1, stroke=1)
    c.setFont("DejaVu-Bold", 7.2); c.setFillColor(INK)
    c.drawCentredString(0, -2.5, label)
    c.restoreState()


def source_between(c, p1, p2, label, direction=1, radius=10):
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    dist = math.hypot(dx, dy)
    ux, uy = dx / dist, dy / dist
    cx, cy = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
    line(c, p1, (cx - ux * radius, cy - uy * radius))
    line(c, (cx + ux * radius, cy + uy * radius), p2)
    c.setFillColor(WHITE); c.setStrokeColor(NAVY); c.setLineWidth(1.25)
    c.circle(cx, cy, radius, fill=1, stroke=1)
    tail = (cx - direction * ux * 5, cy - direction * uy * 5)
    tip = (cx + direction * ux * 5, cy + direction * uy * 5)
    arrow(c, tail, tip, TEAL, 4)
    angle = math.degrees(math.atan2(dy, dx))
    c.saveState(); c.translate(cx, cy); c.rotate(angle)
    c.setFont("DejaVu-Bold", 7); c.setFillColor(INK)
    c.drawCentredString(0, -radius - 11, label)
    c.restoreState()


class NodeLegendDiagram(Flowable):
    """Compact key: same colors mean the same electrical node in each figure."""
    def __init__(self, width=base.CONTENT_W, height=56):
        super().__init__(); self.width, self.height = width, height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return self.width, self.height

    def draw(self):
        c = self.canv; c.saveState()
        c.setFillColor(PALE); c.setStrokeColor(LINE)
        c.roundRect(0, 0, self.width, self.height, 6, fill=1, stroke=1)
        items = [("A", NODE_A, "węzeł A"), ("B", NODE_B, "węzeł B"),
                 ("C", NODE_C, "węzeł C"), ("0", NODE_D, "masa / odniesienie")]
        col = self.width / 4
        for i, (tag, color, label) in enumerate(items):
            x = col * i + 22
            node(c, x, 34, tag, color, dx=7, dy=0, radius=5)
            c.setFont("DejaVu", 7.7); c.setFillColor(INK)
            c.drawString(x + 32, 31, label)
        c.setFont("DejaVu", 7.4); c.setFillColor(MUTED)
        c.drawCentredString(self.width / 2, 10, "Kolor oznacza przynależność do węzła, a nie biegunowość ani wartość napięcia.")
        c.restoreState()


class SeriesParallelDiagram(Flowable):
    """Before/after sketches that name series and parallel connections explicitly."""
    def __init__(self, width=base.CONTENT_W, height=185):
        super().__init__(); self.width, self.height = width, height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return self.width, self.height

    def _panel(self, c, x, title):
        c.setFillColor(WHITE); c.setStrokeColor(LINE)
        c.roundRect(x, 5, self.width / 2 - 7, self.height - 10, 5, fill=1, stroke=1)
        c.setFont("DejaVu-Bold", 8.5); c.setFillColor(TEAL_DARK)
        c.drawCentredString(x + (self.width / 2 - 7) / 2, self.height - 21, title)

    def draw(self):
        c = self.canv; c.saveState()
        half = self.width / 2
        self._panel(c, 3, "SZEREGOWO — ten sam prąd")
        self._panel(c, half + 4, "RÓWNOLEGLE — te same dwa węzły")
        # Series: A -- R1 -- M -- R2 -- B; M has exactly two incident branches.
        y = 119; xa, xm, xb = 27, 111, half - 25
        pA=(xa,y); pM=(xm,y); pB=(xb,y)
        resistor_between(c, pA, pM, "R₁", length=34)
        resistor_between(c, pM, pB, "R₂", length=34)
        node(c, *pA, "A", NODE_A); node(c, *pM, "M", NODE_C); node(c, *pB, "B", NODE_B)
        c.setFont("DejaVu", 7.3); c.setFillColor(MUTED)
        c.drawCentredString(half/2, 96, "M ma tylko dwa połączenia → R₁ i R₂ są szeregowo")
        arrow(c, (half/2, 86), (half/2, 69), GOLD, 4)
        pA2=(xa,46); pB2=(xb,46)
        resistor_between(c,pA2,pB2,"R_z",length=54,height=18)
        node(c,*pA2,"A",NODE_A);node(c,*pB2,"B",NODE_B)
        c.setFont("DejaVu-Bold", 7.7); c.setFillColor(INK)
        c.drawCentredString(half/2, 20, "R_z = R₁ + R₂")
        # Parallel: two branches with exactly the same endpoint nodes A/B.
        x0=half+24; x1=half+half-24; yt=125; yb=66
        line(c,(x0,yt),(x1,yt)); line(c,(x0,yb),(x1,yb))
        for xx, lab in [(half+68,"R₁"),(half+132,"R₂")]:
            resistor_between(c,(xx,yt),(xx,yb),lab,length=30,height=15)
            node(c,xx,yt,"A",NODE_A,dx=4,dy=3,radius=3.1)
            node(c,xx,yb,"B",NODE_B,dx=4,dy=-10,radius=3.1)
        c.setFont("DejaVu",7.3);c.setFillColor(MUTED)
        c.drawCentredString(half+half/2,44,"Każda gałąź zaczyna się w A i kończy w B.")
        c.setFont("DejaVu-Bold",7.7);c.setFillColor(INK)
        c.drawCentredString(half+half/2,25,"G_z = G₁+G₂;   R_z = R₁∥R₂")
        c.restoreState()


class TheveninLoadDiagram(Flowable):
    def __init__(self, width=base.CONTENT_W, height=155):
        super().__init__(); self.width, self.height = width, height

    def wrap(self, aw, ah):
        self.width=min(self.width,aw); return self.width,self.height

    def _box(self,c,x,y,w,h,label):
        c.setFillColor(PALE);c.setStrokeColor(NAVY);c.setLineWidth(1.15)
        c.roundRect(x,y,w,h,4,fill=1,stroke=1)
        c.setFont("DejaVu-Bold",8);c.setFillColor(INK)
        c.drawCentredString(x+w/2,y+h/2-3,label)

    def draw(self):
        c=self.canv;c.saveState()
        c.setFillColor(WHITE);c.setStrokeColor(LINE);c.roundRect(0,4,self.width,self.height-8,6,fill=1,stroke=1)
        half=self.width/2
        c.setFont("DejaVu-Bold",8.4);c.setFillColor(TEAL_DARK)
        c.drawCentredString(half/2, self.height-20, "1. Otwórz obciążenie → E_T")
        self._box(c,28,50,100,55,"sieć liniowa")
        line(c,(128,83),(165,83));line(c,(128,55),(165,55))
        node(c,165,83,"A",NODE_A);node(c,165,55,"B",NODE_B)
        c.setFont("DejaVu",7.3);c.setFillColor(MUTED)
        c.drawCentredString(half/2,26,"E_T = U_AB przy rozwarciu")
        # Equivalent source in series with internal resistance and load.
        x=half+60;y0=48;y1=104;cy=(y0+y1)/2
        c.setFont("DejaVu-Bold",8.4);c.setFillColor(TEAL_DARK)
        c.drawCentredString(half+half/2,self.height-20,"2. Policz R_w, potem dołącz R_L")
        c.setStrokeColor(NAVY);c.setLineWidth(1.25)
        c.line(x,cy-11,x,y0);c.line(x,cy+11,x,y1)
        c.circle(x,cy,11,fill=0,stroke=1)
        c.setFont("DejaVu-Bold",6.8);c.setFillColor(TEAL_DARK)
        c.drawCentredString(x,cy+2.5,"+");c.drawCentredString(x,cy-7.5,"−")
        c.setFont("DejaVu-Bold",7.0);c.setFillColor(INK);c.drawString(x-31,cy-2,"E_T")
        c.line(x,y1,x+32,y1);resistor_between(c,(x+32,y1),(x+92,y1),"R_w",length=42)
        c.line(x+92,y1,x+130,y1);c.line(x+130,y1,x+130,cy+11)
        c.circle(x+130,cy,11,fill=0,stroke=1);c.setFont("DejaVu-Bold",7.2);c.setFillColor(INK);c.drawCentredString(x+130,cy-2,"R_L")
        c.line(x+130,cy-11,x+130,y0);c.line(x+130,y0,x,y0)
        node(c,x+130,y1,"A",NODE_A);node(c,x+130,y0,"B",NODE_B,dy=-10)
        c.setFont("DejaVu",7.3);c.setFillColor(MUTED)
        c.drawCentredString(half+half/2,26,"U_L = E_T · R_L/(R_w+R_L)")
        c.restoreState()


class TaskTriangleDiagram(Flowable):
    """Color-node redrawing of the scanned conductance triangle task."""
    def __init__(self, width=base.CONTENT_W, height=205):
        super().__init__(); self.width,self.height=width,height
    def wrap(self,aw,ah): self.width=min(self.width,aw); return self.width,self.height
    def draw(self):
        c=self.canv;c.saveState()
        c.setFillColor(PALE);c.setStrokeColor(LINE);c.roundRect(0,0,self.width,self.height,6,fill=1,stroke=1)
        L=(48,159);R=(self.width-48,159);C=(self.width/2,97);D=(self.width/2,23)
        source_between(c,L,R,"J",direction=1,radius=10)
        resistor_between(c,L,C,"G₂",length=32,height=14)
        resistor_between(c,C,R,"R₁",length=36,height=15)
        resistor_between(c,C,D,"G₃",length=30,height=14)
        source_between(c,D,L,"E₂",direction=1,radius=10)
        source_between(c,R,D,"E₁",direction=1,radius=10)
        # Current reference on R1 is from the right node toward C; keep the marker off the resistor body.
        arrow(c,(C[0]+65,C[1]+19.5),(C[0]+34,C[1]+10),GOLD,5)
        c.setFont("DejaVu-Bold",7.5);c.setFillColor(INK);c.drawString(C[0]+45,C[1]+24,"I")
        node(c,*L,"L",NODE_A,dx=-13,dy=7)
        node(c,*R,"R",NODE_B,dx=5,dy=7)
        node(c,*C,"C",NODE_C,dx=5,dy=4)
        node(c,*D,"0",NODE_D,dx=5,dy=-10)
        c.setFont("DejaVu",7.3);c.setFillColor(MUTED)
        c.drawString(10,184,"Kolorowe węzły: L, R, C oraz odniesienie 0 V. Źródła E₁/E₂ ustalają V_R i V_L.")
        c.restoreState()


class BridgeDiagram(Flowable):
    """Simplified colored-node drawing of the handwritten bridge problem."""
    def __init__(self,width=base.CONTENT_W,height=190):
        super().__init__();self.width,self.height=width,height
    def wrap(self,aw,ah):self.width=min(self.width,aw);return self.width,self.height
    def draw(self):
        c=self.canv;c.saveState()
        c.setFillColor(PALE);c.setStrokeColor(LINE);c.roundRect(0,0,self.width,self.height,6,fill=1,stroke=1)
        top=(self.width/2,158); left=(self.width/2-110,96); right=(self.width/2+110,96); bottom=(self.width/2,24)
        resistor_between(c,top,left,"R",length=36)
        resistor_between(c,top,right,"R",length=36)
        resistor_between(c,right,bottom,"R",length=36)
        source_between(c,bottom,left,"J",direction=1,radius=10)
        resistor_between(c,left,right,"R₀",length=42,height=15)
        # Ideal voltage source E is across the upper and lower bridge nodes.
        ex=23; c.setStrokeColor(NAVY);c.setLineWidth(1.2)
        c.line(ex,top[1],top[0],top[1]);c.line(ex,bottom[1],bottom[0],bottom[1])
        c.line(ex,bottom[1],ex,83);c.line(ex,108,ex,top[1])
        c.circle(ex,95,12,fill=0,stroke=1)
        c.setFont("DejaVu-Bold",7.2);c.setFillColor(TEAL_DARK)
        c.drawCentredString(ex,98,"+");c.drawCentredString(ex,86,"−")
        c.setFont("DejaVu-Bold",7.0);c.setFillColor(INK);c.drawString(6,92,"E")
        # U is referenced from the right bridge node toward the left, offset from R₀.
        arrow(c,(right[0]-34,110),(left[0]+34,110),GOLD,4)
        c.setFont("DejaVu-Bold",7.4);c.setFillColor(INK);c.drawCentredString(self.width/2,118,"U")
        node(c,*top,"T",NODE_A);node(c,*left,"L",NODE_C,dx=-14);node(c,*right,"R",NODE_B);node(c,*bottom,"0",NODE_D,dx=5,dy=-10)
        c.setFont("DejaVu",7.2);c.setFillColor(MUTED);c.drawCentredString(self.width/2,8,"R₀ łączy L–R; źródło E ustala napięcie między T i 0.")
        c.restoreState()


def make_doc(path: Path, title: str, subject: str):
    return base.ManualDocTemplate(
        str(path), pagesize=base.A4,
        leftMargin=base.LEFT, rightMargin=base.RIGHT,
        topMargin=base.TOP, bottomMargin=base.BOTTOM,
        title=title, author="Opracowanie własne", subject=subject,
        keywords="PLP K1, kolorowe węzły, obwody, samouczek, rozwiązania",
    )


def cover_story(kicker: str, title: str, subtitle: str, note: str):
    return [
        Spacer(1,25*mm),
        base.P(kicker,"CoverKicker"),
        base.P(title,"CoverTitle"),
        base.P(subtitle,"CoverSub"),
        Spacer(1,10*mm),
        base.callout("Jak korzystać z tej wersji",note,"tip"),
        Spacer(1,14*mm),
        base.P("Węzły na schematach dodanych i przeredagowanych w tych wersjach są oznaczone kolorami. W obrębie jednego rysunku powtarzający się kolor oznacza ten sam węzeł; kolor nie koduje polaryzacji.","CoverMeta"),
        NextPageTemplate("Body"),PageBreak(),
    ]


def section_list(rows):
    return [base.P("Plan poradnika","TOCHeading"),
            base.info_table([["Część","Co zawiera"]]+rows,[52*mm,base.CONTENT_W-52*mm]),
            Spacer(1,8),
            base.callout("Kolorystyka", "A — turkus, B — bursztyn, C — fiolet, 0 — grafit. Kolorowe kropki oznaczają węzły; przewody łączące te same kropki tworzą jeden węzeł.")]


def solve_table(rows, widths=None):
    return base.info_table([["Zadanie","Nazwany typ połączenia / uproszczenia","Kroki i wynik"]]+rows,widths or [45*mm,75*mm,base.CONTENT_W-120*mm])


def build_extended_story():
    # Start with the complete original guide, then append a carefully labeled deep-dive.
    story=base.build_story()
    story[1]=base.P("WERSJA ROZSZERZONA", "CoverKicker")
    story[3]=base.P("PLP K1 · schematy kolorowe i kroki bez skrótów", "CoverSub")
    story[5]=base.callout("Co dodaje ta wersja", "Pełny samouczek i wszystkie rozwiązania z wersji podstawowej, a na końcu: kolorowe schematy węzłowe, nazwy połączeń, rysunki przed/po uproszczeniu oraz dokładniejsze uzasadnienie, dlaczego każdy krok jest dozwolony.", "tip")
    # Reword the original closing line because the explanatory appendix follows it.
    for i, flow in enumerate(story):
        if isinstance(flow, base.Paragraph) and flow.getPlainText().startswith("Koniec opracowania."):
            story[i]=base.P("Koniec części podstawowej. Dalej znajduje się dodatek rozszerzony z kolorowymi schematami i pełnym opisem uproszczeń.","SmallPL")
            break

    story += [PageBreak(),
              base.H1("Dodatek rozszerzony: kolorowe węzły i jawne uproszczenia"),
              base.P("Wersja podstawowa podaje rozwiązania; ten dodatek pokazuje, jak samodzielnie czytać topologię, nazywać redukcje i uzasadniać je krok po kroku."),
              NodeLegendDiagram(),Spacer(1,7),
              base.H2("Najpierw rozpoznaj węzły, dopiero potem liczą się kształty"),
              base.P("Węzeł to cały obszar przewodów bez elementu pomiędzy nimi. Jeśli przewód zawraca, rysunek może wyglądać na skomplikowany, ale nadal jest jednym węzłem. Przed redukcją oznacz węzły literami lub kolorami."),
              SeriesParallelDiagram(),
              base.callout("Test dwóch elementów", "Szeregowo: ich wspólny węzeł ma tylko te dwa połączenia, więc prąd jest wspólny. Równolegle: końce obu elementów trafiają do tej samej pary węzłów, więc napięcie jest wspólne. Samo sąsiedztwo symboli na kartce niczego nie dowodzi."),
              base.H2("Nazwy używanych tu uproszczeń"),
              base.info_table([
                  ["Nazwa", "Warunek topologiczny", "Co zastępujemy"],
                  ["Redukcja szeregowa", "Wspólny węzeł bez odgałęzień", "R_z=R₁+R₂; prąd nie zmienia się."],
                  ["Redukcja równoległa", "Te same dwa węzły", "G_z=G₁+G₂ albo R₁∥R₂; napięcie jest wspólne."],
                  ["Dzielnik napięcia", "Rezystory w szeregu", "Napięcie na R₂ to E·R₂/(R₁+R₂)."],
                  ["Dzielnik prądu", "Gałęzie równoległe", "Prąd dzieli się odwrotnie do R; I₁=I·R₂/(R₁+R₂)."],
                  ["Wyzerowanie źródła", "Tylko źródła niezależne", "E→zwarcie, J→rozwarcie; źródła zależne zostają."],
                  ["Źródło Thévenina", "Port liniowego dwójnika", "U_oc=E_T; następnie R_w i obciążenie."],
                  ["Transformacja Δ–Y", "Trzy końcówki wspólnej sieci", "Zastępujemy trójkąt równoważną gwiazdą lub odwrotnie."],
              ],[36*mm,64*mm,base.CONTENT_W-100*mm]),
              PageBreak()]

    story += [base.H1("Superpozycja bez zgadywania znaków: Zestaw K, zadanie 1"),
              base.P("Dane: J₁=5 mA, J₂=1 mA, E=3 V; R₁=1 kΩ, R₂=2 kΩ, R₃=3 kΩ. Szukamy I w narysowanym zwrocie."),
              base.H2("Krok 1 — przygotuj bazowy szereg rezystorów"),
              base.P("W każdej konfiguracji aktywnego źródła prąd I jest związany z tą samą sumą rezystancji: R_Σ=R₁+R₂+R₃=6 kΩ. To jest redukcja szeregowa dla gałęzi, przez którą wyznaczamy prąd."),
              base.H2("Krok 2 — pozostaw tylko J₁"),
              base.P("Pozostałe niezależne źródła: E zastępujemy zwarciem, J₂ rozwarciem. Z układu otrzymujemy dzielnik prądu; wkład do I wynosi I_J₁=J₁·R₂/R_Σ=5·2/6=+5/3 mA."),
              base.H2("Krok 3 — pozostaw tylko E"),
              base.P("Oba źródła prądowe stają się przerwami. Źródło E wywołuje prąd przeciwny do strzałki I, dlatego I_E=−E/R_Σ=−3/6=−1/2 mA. Znak minus jest częścią odpowiedzi cząstkowej."),
              base.H2("Krok 4 — pozostaw tylko J₂ i zsumuj algebraicznie"),
              base.P("E zwieramy, J₁ rozwieramy. Z podziału prądu wkład J₂ to I_J₂=J₂·(R₂+R₃)/R_Σ=1·5/6=+5/6 mA."),
              base.eqbox("I = I_J₁ + I_E + I_J₂ = 5/3 − 1/2 + 5/6 = +2 mA."),
              base.callout("Dlaczego wolno dodawać?", "Sieć jest liniowa, więc odpowiedź na sumę źródeł równa się sumie odpowiedzi cząstkowych. Nie dodajemy mocy — najpierw sumujemy prądy/napięcia, a dopiero potem liczymy moc."),
              PageBreak()]

    story += [base.H1("Obciążenie i redukcje: zadanie U na R₅"),
              base.P("Zadanie ze skanu s. 14–15: J=32 mA, E=2 V; R₁=1 kΩ, R₂=3 kΩ, R₃=4 kΩ, R₄=1 kΩ, R₅=4 kΩ."),
              TheveninLoadDiagram(),
              base.H2("A. Nazwij połączenia przy wyznaczaniu napięcia jałowego"),
              base.P("Odłącz R₅ — to jest rozwarcie portu. Dla wkładu J zwieramy E, więc dolne węzły są wspólne. R₂ i R₃ są <b>szeregowo</b>; ich gałąź jest <b>równoległa</b> do R₁. Dzielnik prądu daje i₂₃=J·R₁/(R₁+R₂+R₃)=32·1/8=4 mA. Na R₃ powstaje 16 V."),
              base.P("Dla wkładu E rozwieramy J. W gałęzi rezystorów nie ma zamkniętego obwodu, więc prąd jest zerowy. Biegunowość E jest przeciwnie skierowana względem U, zatem wkład wynosi −2 V."),
              base.eqbox("E_T = +16 V − 2 V = +14 V."),
              base.H2("B. Nazwij połączenia przy wyznaczaniu R_w"),
              base.P("Wyłączamy źródła niezależne: J→rozwarcie, E→zwarcie. Patrząc do portu R₅, najpierw mamy R₁+R₂ jako <b>połączenie szeregowe</b>; tę gałąź łączymy <b>równolegle</b> z R₃. Na końcu R₄ jest <b>szeregowo</b> z otrzymanym blokiem."),
              base.eqbox("R_w = R₄ + [R₃ ∥ (R₁+R₂)] = 1 + [4 ∥ 4] = 3 kΩ."),
              base.H2("C. Przywróć obciążenie"),
              base.P("R₅ wraca do układu. Teraz to zwykły <b>dzielnik napięcia</b> między R_w i R₅."),
              base.callout("Wynik", "U=E_T·R₅/(R_w+R₅)=14·4/(3+4)=<b>8 V</b>.","answer"),
              PageBreak()]

    story += [base.H1("Mostek: superpozycja po poprawnej redukcji"),
              base.P("Zadanie ze skanu s. 18. R=2 kΩ, R₀=1 kΩ, J=2 mA, E=8 V. Szukane U jest na gałęzi poprzecznej R₀."),
              BridgeDiagram(),
              base.H2("Wkład źródła E: otwórz J"),
              base.P("Gałąź J jest rozwarciem. Od góry do prawego węzła są dwie ścieżki: bezpośredni R oraz szereg R+R₀. To są połączenia równoległe: R∥(R+R₀)=2∥3=1,2 kΩ. Z nim szeregowo łączy się dolny R=2 kΩ. Dzielnik napięcia daje 3 V na równoległym bloku, a wewnątrz gałęzi R+R₀ dzielnik daje U_E=1 V."),
              base.H2("Wkład źródła J: zewrzyj E"),
              base.P("Źródło E staje się przewodem, więc górny i dolny węzeł to ten sam węzeł (kolor odniesienia). Dwa prawe oporniki są <b>równolegle</b>: R∥R=1 kΩ. Ta rezystancja jest <b>szeregowa</b> z R₀, dając 2 kΩ. Równoległa gałąź po lewej też ma 2 kΩ, dlatego dzielnik prądu rozdziela J po równo: przez R₀ płynie 1 mA."),
              base.eqbox("U = U_E + U_J = 1 V + (1 mA)(1 kΩ) = +2 V."),
              base.callout("Nazwa uproszczenia", "To nie jest bezpośredni dzielnik prądu przez R₀: najpierw redukujemy dwa prawe oporniki równolegle, potem łączymy wynik szeregowo z R₀ i dopiero stosujemy dzielnik prądu."),
              PageBreak()]

    story += [base.H1("Źródła sterowane: kiedy nie wolno ich wyłączać"),
              base.P("Zadanie ze skanu s. 16–17: E=10 V, R₁=R₄=1 kΩ, R₂=R₃=0,5 kΩ, g=3 mS. Sterowane źródło prądowe ma wartość g·u₂."),
              NodeLegendDiagram(),Spacer(1,5),
              base.H2("Stan 1 — zaciski wyjściowe rozwarte, wyznacz E_T"),
              base.P("R₄ nie przewodzi przy rozwarciu. Z KCL w węźle wyjściowym: i₃=i₂−g u₂. Dla rezystora R₂ przyjęto u₂=R₂i₂, więc i₃=i₂(1−gR₂). Ponieważ gR₂=3 mS·0,5 kΩ=1,5, i₃=−0,5i₂."),
              base.P("KVL w oczku: E=R₂i₂+R₃i₃=(0,5−0,25)kΩ·i₂; i₂=40 mA, i₃=−20 mA. Ujemny i₃ oznacza kierunek przeciwny do przyjętej strzałki."),
              base.eqbox("E_T=R₃i₃=−10 V."),
              base.H2("Stan 2 — źródła niezależne wyzerowane, źródło sterowane aktywne"),
              base.P("E→zwarcie; rezystor R₁ jest równoległy do tego zwarcia i zostaje ominięty. Źródło g·u₂ pozostaje! Przy wybranej polaryzacji u₂ jest przeciwne do napięcia węzła, dlatego jego wkład do konduktancji portowej ma znak minus: G_wew=1/R₂+1/R₃−g."),
              base.eqbox("G_wew=2+2−3=1 mS;   R_wew=1/G_wew=1 kΩ.\nR_w=R₄+R_wew=2 kΩ;   J_N=E_T/R_w=−5 mA."),
              base.callout("Nazwy kroków", "Najpierw rozwarcie portu (napięcie jałowe). Potem wyzerowanie źródeł niezależnych. Na końcu redukcja równoległych konduktancji i dodanie szeregowego R₄. Źródło zależne pozostaje aktywne w całym rachunku R_w."),
              PageBreak()]

    story += [base.H1("Metoda węzłowa: zadanie trójkątne ze skanu"),
              base.P("Dane: E₁=7 V, E₂=14 V, J=8 A, R₁=4 Ω, G₂=8 S, G₃=4 S. Szukamy I w gałęzi R₁, ze zwrotem z prawego węzła do środka."),
              TaskTriangleDiagram(),
              base.H2("Krok 1 — wybierz masę i wpisz znane potencjały"),
              base.P("Dolny węzeł D jest odniesieniem 0 V. Z grotów źródeł napięcia: V_L=+14 V, V_R=−7 V. Źródło J łączy L i R, których potencjały są już narzucone przez idealne źródła napięcia; J zmienia prądy w gałęziach źródeł napięcia, ale nie zmienia V_L ani V_R."),
              base.H2("Krok 2 — napisz KCL tylko dla nieznanego węzła C"),
              base.P("Prąd z C do L to G₂(V_C−V_L); z C do masy G₃V_C; z C do R (V_C−V_R)/R₁. Sumujemy prądy wypływające i przyrównujemy do zera."),
              base.eqbox("8(V_C−14)+4V_C+(V_C−(−7))/4=0.\n(8+4+0,25)V_C=112−1,75=110,25;   V_C=9 V."),
              base.H2("Krok 3 — wyznacz szukany prąd w zadanym zwrocie"),
              base.P("Strzałka I jest od R do C, więc licznik to V_R−V_C, a nie odwrotnie."),
              base.callout("Wynik", "I=(V_R−V_C)/R₁=(−7−9)/4=<b>−4 A</b>. Rzeczywisty prąd 4 A płynie z C do R.","answer"),
              PageBreak()]

    story += [base.H1("Mapa decyzji: jaką metodę i jakie uproszczenie wybrać?"),
              base.info_table([
                  ["Co widzisz na schemacie?","Najpierw nazwij krok","Potem policz"],
                  ["Jeden szereg rezystorów", "Redukcja szeregowa", "R_z=ΣR; wyznacz wspólny prąd."],
                  ["Gałęzie między tą samą parą węzłów", "Redukcja równoległa", "G_z=ΣG; użyj dzielnika prądu, jeśli trzeba."],
                  ["Kilka niezależnych źródeł w liniowej sieci", "Superpozycja", "Jedno źródło aktywne; pozostałe E zwarciem, J rozwarciem."],
                  ["Wiele niewiadomych węzłowych / źródła prądu", "Metoda węzłowa", "Wybierz masę, napisz KCL."],
                  ["Niewiele oczek i elementy szeregowe", "Metoda oczkowa", "Przyjmij prądy oczkowe, napisz KVL."],
                  ["Obciążenie na końcu dwójnika", "Thévenin/Norton", "Znajdź E_T i R_w, potem ponownie podłącz R_L."],
                  ["Źródło sterowane w dwójniku", "Testowe U_x/I_x", "Źródła zależne zostają aktywne."],
                  ["Mostek bez prostego szeregu/równoległości", "Metoda węzłowa albo Δ–Y", "Nie łącz elementów, których węzły się nie zgadzają."],
              ],[69*mm,67*mm,base.CONTENT_W-136*mm]),
              Spacer(1,8),
              base.H2("Checklista rachunku"),
              base.bullet("Czy każda redukcja ma nazwę i spełnia warunek węzłowy?"),
              base.bullet("Czy kierunki prądów i polaryzacje napięć zostały zachowane od początku do końca?"),
              base.bullet("Czy źródła zależne pozostały włączone przy liczeniu R_w?"),
              base.bullet("Czy jednostki są zgodne: kΩ·mA=V, S·V=A?"),
              base.bullet("Czy wynik ujemny opisano jako kierunek przeciwny, zamiast zmieniać jego znak bez uzasadnienia?"),
              base.callout("Zapamiętaj", "Najpierw węzły, potem typ połączenia; najpierw równanie, potem rachunek. Kolor pomaga rozpoznać węzeł, ale o równoległości i szeregu decyduje topologia."),
              base.P("Koniec wersji rozszerzonej.","SmallPL")]
    return story


def build_short_story():
    story=cover_story(
        "WERSJA SKRÓCONA",
        "PLP K1 · szybki poradnik",
        "Wzory, wybór metody i odpowiedzi z kolorowymi węzłami",
        "Najważniejsze definicje i algorytmy na kilku stronach, a dalej skrócone rozwiązania wszystkich unikatowych zadań. Każdy wiersz podaje nazwę użytego połączenia lub uproszczenia oraz kluczowy rachunek.",
    )
    story += section_list([
        ["1. Start i węzły", "Kolory, zwroty, algorytm 6 kroków"],
        ["2. Ściąga wzorów", "Ohm, Kirchhoff, redukcje, superpozycja, Thévenin/Norton, Δ–Y"],
        ["3. Zestawy K/L/O/P", "Osiem zadań — typ metody i wynik"],
        ["4. Dodatkowe skany", "Sześć unikatowych zadań i dwa przykłady z notatek"],
        ["5. Kontrola", "Najczęstsze pomyłki i lista przed oddaniem"],
    ])
    story.append(PageBreak())

    story += [base.H1("1. Szybki start: oznacz węzły i wybierz metodę"),
              base.P("Przyjmij strzałki prądu jako dodatnie odniesienia. Węzeł to jeden potencjał; jego kształt na kartce nie ma znaczenia. W tych rysunkach A jest turkusowe, B bursztynowe, C fioletowe, a 0 V grafitowe."),
              NodeLegendDiagram(),Spacer(1,7),SeriesParallelDiagram(),
              base.info_table([
                  ["Krok","Co zanotować"],
                  ["1. Oznacz", "Węzły, masę, strzałki prądów i biegunowości napięć."],
                  ["2. Nazwij", "Szereg, równolegle, dzielnik, mostek, źródło sterowane."],
                  ["3. Wybierz", "Wiele źródeł → superpozycja; port → Thévenin/Norton; węzeł → KCL."],
                  ["4. Uprość", "Stosuj tylko redukcję, której warunek topologiczny jest spełniony."],
                  ["5. Sprawdź", "Znak, jednostki, E_T=J_N R_w."],
              ],[25*mm,base.CONTENT_W-25*mm]),
              PageBreak()]

    story += [base.H1("2. Ściąga wzorów i typowych uproszczeń"),
              base.info_table([
                  ["Nazwa kroku","Warunek / wzór"],
                  ["Prawo Ohma", "u=Ri; i=u/R=Gu; G=1/R."],
                  ["Szereg", "Wspólny prąd; R_z=R₁+R₂+… ."],
                  ["Równolegle", "Te same dwa węzły; G_z=G₁+G₂+…; R₁∥R₂=R₁R₂/(R₁+R₂)."],
                  ["Dzielnik napięcia", "U₂=E·R₂/(R₁+R₂); z obciążeniem użyj R₂∥R_L."],
                  ["Dzielnik prądu", "I₁=I·R₂/(R₁+R₂) dla dwóch gałęzi równoległych."],
                  ["Kirchhoff", "KCL: suma prądów w węźle = 0; KVL: suma napięć w oczku = 0."],
                  ["Superpozycja", "Liniowa sieć; E→zwarcie, J→rozwarcie; sterowane zostają."],
                  ["Thévenin/Norton", "E_T=U_oc; J_N=I_sc; R_w=E_T/J_N; źródło zależne → źródło testowe U_x/I_x."],
                  ["Źródła równoważne", "E szeregowo R ↔ J=E/R równolegle R."],
                  ["Δ→Y", "R_A=R_AB·R_CA/ΣR_Δ; analogicznie B,C."],
                  ["Punkt pracy", "R_Q=U_Q/I_Q; r_d≈ΔU/ΔI przy Q."],
                  ["Op-amp idealny", "I₊=I₋=0; przy ujemnym sprzężeniu i braku nasycenia u₊≈u₋."],
              ],[41*mm,base.CONTENT_W-41*mm]),
              Spacer(1,6),
              base.callout("Jednostki", "1 kΩ·1 mA=1 V; 1 V/1 kΩ=1 mA; 1 mS·1 V=1 mA."),
              PageBreak()]

    story += [base.H1("3. Zestawy K, L, O, P — metoda i kluczowe kroki"),
              solve_table([
                  ["K · Z1","Superpozycja; R_Σ=R₁+R₂+R₃=6 kΩ.","J₁: +5/3 mA; E: −1/2 mA; J₂: +5/6 mA. I=<b>2 mA</b>."],
                  ["K · Z2","Źródło napięciowe sterowane prądem r·i; Norton.","R_w=R₁(r+R₂)/(R₁+R₂); E_T=R₁rJ/(R₁+R₂); J_N=Jr/(r+R₂)."],
                  ["L · Z1","Superpozycja; R_Σ=6 kΩ.","J₁: −1/3 mA; E₁: +5/6 mA; J₂: +5/2 mA. I=<b>3 mA</b>."],
                  ["L · Z2","Źródło prądowe sterowane napięciem g·u; metoda źródła testowego.","R_w=(R₁+R₂)/(1+R₁g); E_T=ER₁g/(1+R₁g); J_N=gR₁E/(R₁+R₂)."],
                  ["O · Z1","Superpozycja + dzielniki.","U_E=E/5=0,4 V; U_J=2JR/5=1,6 V. U=<b>2 V</b>."],
                  ["O · Z2","Źródło sterowane k·u; port Thevenina.","R_w=R(3+k)/(2+k)=4 kΩ; E_T=R₃J=6 V; J_N=<b>1,5 mA</b>."],
                  ["P · Z1","Dzielnik prądu i redukcja R∥2R.","I_J=J/5=0,8 mA; I_E=3E/(5R)=2,4 mA. I=<b>3,2 mA</b>."],
                  ["P · Z2","Źródło zależne k·i; KVL + R_w.","i=E/(4R); E_T=3E/4=3 V; R_w=3 kΩ; J_N=<b>1 mA</b>."],
              ],[28*mm,75*mm,base.CONTENT_W-103*mm]),
              Spacer(1,7),
              base.callout("Dwa przykłady z notatek", "Pięć rezystorów, J=3 mA, E=9 V: superpozycja −9/17+26/17 daje I=<b>1 mA</b>. Źródło αI₁ z J=2 mA, R₁=1 kΩ, R₂=2 kΩ, α=1/2: J_N=4/3 mA, R_w=6 kΩ, E_T=<b>8 V</b>."),
              PageBreak()]

    story += [base.H1("4. Dodatkowe skany — krótkie rozwiązania z nazwami kroków"),
              solve_table([
                  ["R₅, s.14–15","Thévenin; szereg, równolegle, dzielnik napięcia.","E_T=16−2=14 V; R_w=R₄+[R₃∥(R₁+R₂)]=3 kΩ; U=<b>8 V</b>."],
                  ["g·u₂, s.16–17","Otwarcie portu; test R_w; źródło zależne aktywne.","E_T=−10 V; G_wew=1/R₂+1/R₃−g=1 mS; R_w=2 kΩ; J_N=<b>−5 mA</b>."],
                  ["Mostek, s.18","Superpozycja; równoległe, szeregowe, dzielnik.","Wkład E=1 V; wkład J=1 V. U=<b>2 V</b>."],
                  ["g·u₁, s.19–21","Norton; portowa konduktancja; dołącz R₁.","E_T=(E−JR₂)/(1+gR₂)=−0,5 V; R_w=R₂/(1+gR₂)=1 kΩ; I=<b>−0,25 mA</b>."],
                  ["A–B Norton, s.23/25","KCL; źródła w szeregu; test portowy.","I′=J₂/(1+β)=0,5 mA; E_T=6 V; R_w=R₁/(1+β)=1 kΩ; J_N=<b>6 mA</b>, strzałka źródła B→A."],
                  ["Trójkąt, s.22/24","Metoda węzłowa; KCL w C.","V_L=14 V, V_R=−7 V; 8(V_C−14)+4V_C+(V_C+7)/4=0 → V_C=9 V; I=<b>−4 A</b>."],
              ],[34*mm,78*mm,base.CONTENT_W-112*mm]),
              Spacer(1,7),
              TaskTriangleDiagram(),
              PageBreak()]

    story += [base.H1("5. Ostatnia kontrola przed oddaniem"),
              base.info_table([
                  ["Pytanie kontrolne","Poprawna decyzja"],
                  ["Czy dwa rezystory są szeregowo?", "Wspólny węzeł nie może mieć trzeciego odgałęzienia."],
                  ["Czy są równolegle?", "Oba końce muszą należeć do tej samej pary węzłów."],
                  ["Jak wyłączam E/J?", "Idealne E zwarciem; idealne J rozwarciem."],
                  ["Czy źródło zależne znika przy liczeniu R_w?", "Nie. Pozostaje, zwykle użyj źródła testowego."],
                  ["Co znaczy wynik ujemny?", "Wartość rzeczywista jest przeciwna do przyjętej strzałki."],
                  ["Czy mogę dodać moce z superpozycji?", "Nie. Najpierw dodaj prądy/napięcia, potem policz moc."],
              ],[62*mm,base.CONTENT_W-62*mm]),
              Spacer(1,8),
              base.callout("Szybka decyzja", "Najpierw kolorami oznacz węzły. Potem nazwij połączenie. Jeśli nie masz pewności co do redukcji, użyj KCL i metody węzłowej — ta metoda nie wymaga zgadywania szeregu ani równoległości."),
              base.P("Koniec wersji skróconej.","SmallPL")]
    return story


def main():
    extended_doc=make_doc(EXTENDED,"PLP K1 — poradnik rozszerzony","Rozszerzony poradnik z kolorowymi węzłami i objaśnionymi krokami")
    extended_doc.multiBuild(build_extended_story())
    short_doc=make_doc(SHORT,"PLP K1 — poradnik skrócony","Kompaktowa ściąga i skrócone rozwiązania zadań")
    short_doc.multiBuild(build_short_story())
    print(f"Zapisano: {EXTENDED}")
    print(f"Zapisano: {SHORT}")


if __name__ == "__main__":
    main()
