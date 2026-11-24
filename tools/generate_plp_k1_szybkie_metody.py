#!/usr/bin/env python3
"""Generate a standalone Polish guide to quick circuit-analysis shortcuts.

Requires ReportLab and the DejaVu fonts used by generate_plp_k1_guide.py.
Run from the repository root:
    python tools/generate_plp_k1_szybkie_metody.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import NextPageTemplate, PageBreak, Spacer

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "PLP_K1_szybkie_metody_i_skroty.pdf"
sys.path.insert(0, str(ROOT))

from tools import generate_plp_k1_metody_analizy as common  # noqa: E402

base = common.base
PAGE_W, PAGE_H = common.PAGE_W, common.PAGE_H
LEFT, RIGHT, TOP, BOTTOM = common.LEFT, common.RIGHT, common.TOP, common.BOTTOM
CONTENT_W = common.CONTENT_W
NAVY, TEAL, TEAL_DARK = common.NAVY, common.TEAL, common.TEAL_DARK
GOLD, INK, MUTED, LINE, WHITE = common.GOLD, common.INK, common.MUTED, common.LINE, common.WHITE


class MillmanDiagram(base.Flowable):
    """Three branches meeting at one unknown node: two voltage branches and J."""

    def __init__(self, width=CONTENT_W, height=105):
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
        ytop, ybottom = 75, 22
        xsrc, xnode, xr, xj = 63, self.width * 0.49, self.width * 0.72, self.width - 63
        c.setStrokeColor(NAVY)
        c.setLineWidth(1.2)
        c.line(xsrc, ybottom, xj, ybottom)
        common.voltage_source(c, xsrc, ybottom, ytop, "E₁", plus_top=True, radius=9)
        common.resistor_h(c, xsrc, xnode, ytop, "R₁=3 kΩ")
        c.line(xnode, ytop, xj, ytop)
        common.resistor_v(c, xr, ybottom, ytop, "R₂=3 kΩ", width=18)
        c.line(xj, ybottom, xj, ytop - 10)
        c.circle(xj, (ybottom + ytop) / 2, 9, fill=1, stroke=1)
        common.arrow(c, xj, (ybottom + ytop) / 2 - 5, xj, (ybottom + ytop) / 2 + 5,
                     TEAL_DARK, head=3.7, width=1.0)
        c.line(xj, ytop - 10, xj, ytop)
        common.node_dot(c, xnode, ytop, "X", base.NODE_C, dx=5, dy=4)
        c.setFillColor(INK)
        c.setFont("DejaVu-Bold", 7.2)
        c.drawString(xsrc + 12, ytop - 10, "V₁=15 V")
        c.drawString(xj + 12, (ybottom + ytop) / 2 - 2, "J=1 mA")
        c.setFillColor(MUTED)
        c.setFont("DejaVu", 6.7)
        c.drawString(xsrc + 9, ybottom - 10, "węzeł odniesienia 0 V")
        c.drawCentredString(self.width / 2, 6, "Strzałka źródła J jest skierowana do węzła X.")
        c.restoreState()


class BalancedBridgeDiagram(base.Flowable):
    """Wheatstone bridge with matched divider ratios."""

    def __init__(self, width=CONTENT_W, height=132):
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
        xs, xl, xr = 58, self.width * 0.40, self.width * 0.76
        yt, ym, yb = 103, 65, 27
        c.setStrokeColor(NAVY)
        c.setLineWidth(1.2)
        common.voltage_source(c, xs, yb, yt, "18 V", plus_top=True, radius=9)
        c.line(xs, yt, xl, yt)
        c.line(xl, yt, xr, yt)
        c.line(xs, yb, xl, yb)
        c.line(xl, yb, xr, yb)
        # Four arms of the bridge; resistor names and values sit outside symbols.
        common.resistor_v(c, xl, ym, yt, "", width=16)
        common.resistor_v(c, xl, yb, ym, "", width=16)
        common.resistor_v(c, xr, ym, yt, "", width=16)
        common.resistor_v(c, xr, yb, ym, "", width=16)
        common.resistor_h(c, xl, xr, ym, "R_b", height=12)
        common.node_dot(c, xl, ym, "L", base.NODE_A, dx=-10, dy=5)
        common.node_dot(c, xr, ym, "R", base.NODE_B, dx=4, dy=5)
        c.setFillColor(INK)
        c.setFont("DejaVu-Bold", 7.0)
        c.drawRightString(xl - 10, 83, "R₁=2 kΩ")
        c.drawRightString(xl - 10, 43, "R₂=4 kΩ")
        c.drawString(xr + 10, 83, "R₃=3 kΩ")
        c.drawString(xr + 10, 43, "R₄=6 kΩ")
        c.setFillColor(MUTED)
        c.setFont("DejaVu", 6.7)
        c.drawCentredString(self.width / 2, 7, "Gałąź R_b łączy środki dwóch dzielników napięcia.")
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
        canvas.drawString(LEFT + 7 * mm, 43 * mm, "PRAKTYCZNA ŚCIĄGA • PLP K1")
        canvas.drawString(LEFT + 7 * mm, 34 * mm, "Skróty rachunkowe z warunkami stosowania i przykładami")
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
        canvas.drawRightString(PAGE_W - RIGHT, PAGE_H - 7.5 * mm, "Szybkie metody i skróty")
        canvas.line(LEFT, 10 * mm, PAGE_W - RIGHT, 10 * mm)
        canvas.setFont("DejaVu", 7.2)
        canvas.setFillColor(MUTED)
        canvas.drawString(LEFT, 6.5 * mm, "Najpierw sprawdź warunki skrótu; na końcu skontroluj KCL lub KVL.")
        canvas.drawRightString(PAGE_W - RIGHT, 6.5 * mm, f"str. {doc.page}")
        canvas.restoreState()


def P(text, style="BodyPL"):
    return base.P(text, style)


def build_story():
    story = [
        Spacer(1, 26 * mm),
        P("PLP K1 · PRAKTYCZNA ANALIZA OBWODÓW", "CoverKicker"),
        P("Szybkie metody i skróty w obwodach", "CoverTitle"),
        P("Jak rozpoznać strukturę, ograniczyć liczbę równań i sprawdzić wynik", "CoverSub"),
        Spacer(1, 10 * mm),
        base.callout(
            "Zasada przewodnia",
            "Skrót jest bezpieczny tylko wtedy, gdy spełnione są jego warunki. Najpierw rozpoznaj topologię i zwroty, potem użyj krótszego rachunku, a na koniec sprawdź wynik jednym równaniem Kirchhoffa.",
        ),
        Spacer(1, 7 * mm),
        P("Opracowanie rozwija przede wszystkim wzór Millmana, dzielniki, równowagę mostka i transformację źródeł. Zakres: liniowe obwody rezystancyjne prądu stałego.", "CoverMeta"),
        NextPageTemplate("Body"),
        PageBreak(),

        base.H1("1. Najpierw rozpoznaj układ"),
        P("Zanim zapiszesz pełny układ równań, sprawdź, czy schemat ma prostą strukturę. Kolejność poniżej często oszczędza najwięcej pracy."),
        base.info_table([
            ["Co widzisz?", "Najszybszy pierwszy ruch", "Warunek / uwaga"],
            ["Elementy szeregowe", "Zastąp je sumą rezystancji.", "Wspólny węzeł między nimi nie może mieć odgałęzienia."],
            ["Elementy równoległe", "Dodaj konduktancje: G_zast=ΣG.", "Końce elementów muszą należeć do tych samych dwóch węzłów."],
            ["Jeden nieznany węzeł", "KCL; jeśli gałęzie mają źródła i rezystory — użyj Millmana.", "Potencjały drugich końców gałęzi muszą być znane."],
            ["Dwa ramiona z gałęzią poprzeczną", "Sprawdź warunek równowagi mostka.", "Porównaj stosunki rezystancji w obu dzielnikach."],
            ["Jedno obciążenie przy zaciskach A–B", "Zastąp resztę obwodu Théveninem lub Nortonem.", "Szczególnie korzystne, gdy zmienia się R_L."],
            ["Kilka niezależnych źródeł", "Rozważ superpozycję, jeśli źródeł jest niewiele.", "Wkłady napięć/prądów dodawaj ze znakami; mocy nie superponuj."],
        ], [39 * mm, 63 * mm, CONTENT_W - 102 * mm]),
        base.H2("Czterokrokowy skrót"),
        base.info_table([
            ["Krok", "Co zrobić"],
            ["1", "Połącz przewody w węzły i ustal, które potencjały są znane."],
            ["2", "Zredukuj tylko pewne szeregi/równoległości; sprawdź, czy gdzieś nie ma odgałęzienia."],
            ["3", "Wybierz najmniejszy model: dzielnik, jedno równanie KCL/Millmana, równowaga mostka albo port Thévenina/Nortona."],
            ["4", "Sprawdź jednostki, znak oraz jedno KCL/KVL w oryginalnym układzie."],
        ], [20 * mm, CONTENT_W - 20 * mm]),
        base.callout("Nie licz szybciej, niż pozwala schemat", "Jeśli skrót wymaga założenia o równych potencjałach lub braku obciążenia, najpierw je udowodnij. Gdy warunek nie zachodzi, wróć do metody węzłowej albo oczkowej."),
        PageBreak(),

        base.H1("2. Dzielniki i redukcje"),
        P("Dzielniki są krótką postacią prawa Ohma i Kirchhoffa — nie osobnym prawem. Zawsze sprawdź, czy elementy rzeczywiście tworzą szereg lub równoległość."),
        base.H2("Dzielnik napięcia"),
        base.eqbox("Dwa rezystory szeregowe:   U₂ = E · R₂/(R₁+R₂).\nJeśli do R₂ dołączono R_L:   R₂* = R₂ ∥ R_L,   U_wyj = E · R₂*/(R₁+R₂*)."),
        P("<b>Przykład.</b> E=18 V, R₁=3 kΩ, R₂=6 kΩ. Bez obciążenia U₂=18·6/(3+6)=12 V. Po dołączeniu R_L=6 kΩ dolna gałąź ma R₂*=6∥6=3 kΩ, więc U_wyj=18·3/(3+3)=9 V; prąd obciążenia I_L=9/6=1,5 mA."),
        base.callout("Działa / nie działa", "Dzielnik napięcia działa dla elementów szeregowych, przez które płynie ten sam prąd. Jeśli wyjście obciąża dodatkowa gałąź, najpierw włącz ją do R₂*. Użycie wzoru bez obciążenia dałoby tu błędne 12 V zamiast 9 V.", "warn"),
        base.H2("Dzielnik prądu"),
        base.eqbox("Dwie gałęzie równoległe R₁ i R₂, prąd całkowity I:   I₁ = I · R₂/(R₁+R₂),   I₂ = I · R₁/(R₁+R₂).\nPrąd w danej gałęzi jest proporcjonalny do jej konduktancji, czyli odwrotnie proporcjonalny do R."),
        P("<b>Przykład.</b> Prąd 6 mA wpływa do równoległych R₁=2 kΩ i R₂=4 kΩ. I₁=6·4/(2+4)=4 mA, I₂=6·2/(2+4)=2 mA. Kontrola: napięcie obu gałęzi wynosi 8 V."),
        base.callout("Warunek dzielnika prądu", "Najpierw upewnij się, że znany I jest prądem wpływającym do całego zestawu gałęzi równoległych. Jeśli są trzy lub więcej gałęzi, użyj I_k=I·G_k/ΣG albo rozwiąż KCL w węźle."),
        PageBreak(),

        base.H1("3. Wzór Millmana — szybkie KCL w jednym węźle"),
        P("Millman jest skróconym zapisem KCL dla jednego węzła połączonego przez rezystory ze źródłami napięcia o znanych potencjałach. Zamiast pisać i rozwiązywać osobne równanie, od razu uśredniasz potencjały z wagami równymi konduktancjom."),
        base.eqbox("V_X = [Σ(G_k E_k) + ΣJ_do_X − ΣJ_z_X] / ΣG_k,    gdzie G_k=1/R_k.\nRównoważnie:   V_X = [Σ(E_k/R_k) + ΣJ_do_X − ΣJ_z_X] / [Σ(1/R_k)]."),
        P("Znaki źródeł prądu wynikają z przyjętej konwencji: J_do_X jest skierowane do węzła, J_z_X od węzła. Wartości E_k są potencjałami drugich końców gałęzi względem tej samej masy."),
        MillmanDiagram(),
        base.H2("Przykład z kontrolą KCL"),
        P("Dane: E₁=15 V przez R₁=3 kΩ, gałąź R₂=3 kΩ do masy oraz źródło J=1 mA skierowane do X."),
        base.eqbox("V_X = [15/3 + 0/3 + 1] / [1/3 + 1/3] = 6/0,667 = 9 V.\nI_R₁=(9−15)/3=−2 mA;   I_R₂=9/3=3 mA.\nKCL, prądy wypływające: −2 + 3 − 1 = 0."),
        base.callout("Działa / nie działa", "Działa, gdy wszystkie gałęzie pasywne kończą się w jednym nieznanym węźle i w znanych potencjałach, a ich zależności są liniowe. Nie zastępuje superwęzła: idealne źródło napięcia bez rezystancji między dwoma nieznanymi węzłami wymaga dodatkowego warunku napięciowego. Dla elementu nieliniowego trzeba wrócić do jego charakterystyki.", "warn"),
        base.callout("Szybka kontrola jednostek", "E/R ma jednostkę prądu, a G sumuje się w siemensach; iloraz sum prądów i konduktancji daje wolty. Przy kΩ i mA pamiętaj: mA/mS=V."),
        PageBreak(),

        base.H1("4. Mostek zrównoważony i symetria"),
        P("W mostku Wheatstone’a gałąź poprzeczna znika z obliczeń, jeśli jej końce mają ten sam potencjał. Najszybciej sprawdzić to przez porównanie dwóch dzielników napięcia."),
        BalancedBridgeDiagram(),
        base.eqbox("Warunek równowagi (R_b łączy środki ramion):   R₁/R₂ = R₃/R₄.\nWtedy V_L=V_R, więc U_b=0 i I_b=0 — niezależnie od wartości skończonego R_b."),
        base.H2("Przykład: 18 V na zrównoważonym moście"),
        P("R₁=2 kΩ, R₂=4 kΩ, R₃=3 kΩ, R₄=6 kΩ. Stosunki są równe: 2/4=3/6=1/2. Lewa gałąź ma 6 kΩ i płynie w niej 3 mA; prawa ma 9 kΩ i płynie w niej 2 mA."),
        base.eqbox("V_L = 3 mA · 4 kΩ = 12 V;   V_R = 2 mA · 6 kΩ = 12 V.\nI_b = (V_L−V_R)/R_b = 0.\nR_zast = (R₁+R₂) ∥ (R₃+R₄) = 6 ∥ 9 = 3,6 kΩ;   I_źr=18/3,6=5 mA."),
        base.callout("Działa / nie działa", "Można pominąć R_b tylko po wykazaniu równowagi lub symetrii wymuszającej V_L=V_R. Jeśli R₁/R₂ ≠ R₃/R₄, przez R_b na ogół płynie prąd — nie usuwaj go. Użyj wtedy metody węzłowej albo transformacji Δ–Y.", "warn"),
        base.P("Ta sama idea działa w innych symetrycznych sieciach: równe potencjały węzłów oznaczają zerowy prąd w łączącej je gałęzi. Równość trzeba uzasadnić symetrią całego układu, nie samym podobieństwem rysunku.", "SmallPL"),
        PageBreak(),

        base.H1("5. Zamiana źródeł i szybki model obciążenia"),
        P("Źródło napięcia E z rezystorem R w szeregu można zastąpić źródłem prądu J=E/R z tym samym R równolegle. Zamiana działa w obie strony i zachowuje napięcie oraz prąd widziane na tych samych dwóch zaciskach."),
        base.SourceConversionDiagram(),
        base.eqbox("E szeregowo z R   ⇔   J=E/R równolegle z R.\nJeśli biegun + źródła E jest przy A, strzałka J w modelu Nortona jest skierowana B→A."),
        base.H2("Przykład: E=12 V, R=3 kΩ, R_L=6 kΩ"),
        P("W modelu Thévenina prąd obciążenia wynosi I_L=12/(3+6)=1,33 mA, a U_L=I_L·6=8 V. Po zamianie: J=12/3=4 mA. Prąd obciążenia w modelu Nortona to podział prądu między R=3 kΩ i R_L=6 kΩ: I_L=4·3/(3+6)=1,33 mA; U_L=8 V."),
        base.H2("Kiedy warto użyć równoważnika portu"),
        base.eqbox("Jeśli znasz E_T i R_T:   I_L=E_T/(R_T+R_L),   U_L=E_T·R_L/(R_T+R_L).\nW modelu Nortona:   I_L=J_N·R_T/(R_T+R_L),   U_L=I_L R_L."),
        base.callout("Działa / nie działa", "Zamiana zachowuje charakterystykę wyłącznie na tych samych zaciskach; rezystor musi pozostać w modelu. Nie zamieniaj samego idealnego źródła E na skończone J bez rezystancji. Przy źródłach zależnych pilnuj, aby transformacja nie zmieniła wielkości sterującej.", "warn"),
        base.callout("Najkrótszy skrót dla jednego obciążenia", "Jeżeli obwód widziany od A–B łatwo sprowadzić do E_T i R_T, nie rozwiązuj całej sieci ponownie po dołączeniu R_L — użyj dzielnika Thévenina. Dla wielu różnych obciążeń ten sam model portu daje każdy wynik."),
        PageBreak(),

        base.H1("6. Karta skrótów: działa, gdy…"),
        base.info_table([
            ["Skrót", "Sprawdź przed użyciem", "Jeśli warunek nie zachodzi"],
            ["Szereg / równolegle", "Węzeł szeregowy nie ma odgałęzienia; elementy równoległe mają te same dwa węzły.", "Narysuj węzły ponownie lub użyj KCL/KVL."],
            ["Dzielnik napięcia", "Elementy są szeregowe; dla obciążonego wyjścia uwzględnij R₂∥R_L.", "Policz obciążoną gałąź albo użyj Thévenina."],
            ["Dzielnik prądu", "Znany prąd wpływa do równoległych gałęzi; użyj konduktancji lub oporu pozostałych gałęzi.", "Zapisz KCL w węźle rozgałęzienia."],
            ["Millman", "Jeden nieznany węzeł; znane potencjały po drugiej stronie gałęzi; liniowe R i źródła.", "Zapisz pełne KCL lub utwórz superwęzeł."],
            ["Mostek zrównoważony", "Stosunki R₁/R₂ i R₃/R₄ są równe albo symetria dowodzi równych potencjałów.", "Nie usuwaj gałęzi poprzecznej; użyj węzłów lub Δ–Y."],
            ["Zamiana źródeł", "E z R szeregowym albo J z tym samym R równoległym; analizujesz te same zaciski.", "Pozostaw źródło i zastosuj KCL/KVL lub równoważnik portu."],
            ["Superpozycja", "Obwód jest liniowy i liczba źródeł nie czyni kolejnych przypadków uciążliwymi.", "Użyj jednej metody węzłowej/oczkowej; mocy nie dodawaj wkładami."],
        ], [34 * mm, 79 * mm, CONTENT_W - 113 * mm]),
        base.H2("Kontrola w 10 sekund"),
        base.bullet("Czy zidentyfikowałem węzły, a nie tylko wyglądające na szeregowe symbole?"),
        base.bullet("Czy uwzględniłem obciążenie i właściwe biegunowości źródeł?"),
        base.bullet("Czy wartość ujemna oznacza tylko zwrot przeciwny do strzałki?"),
        base.bullet("Czy jeden wynik spełnia KCL lub KVL w oryginalnym układzie?"),
        base.callout("Wybór awaryjny", "Gdy nie ma oczywistego skrótu, metoda węzłowa jest bezpiecznym punktem wyjścia. Skrót ma zmniejszać rachunek, nie zastępować sprawdzenia topologii."),
    ]
    return story


def main():
    doc = QuickDocTemplate(
        str(OUTPUT), pagesize=base.A4,
        leftMargin=LEFT, rightMargin=RIGHT, topMargin=TOP, bottomMargin=BOTTOM,
        title="PLP K1 — szybkie metody i skróty w obwodach",
        author="Opracowanie własne",
        subject="Millman, dzielniki, mostek zrównoważony i zamiana źródeł",
        keywords="PLP K1, Millman, dzielnik napięcia, dzielnik prądu, mostek, zamiana źródeł",
    )
    doc.multiBuild(build_story())
    print(f"Zapisano: {OUTPUT}")


if __name__ == "__main__":
    main()
