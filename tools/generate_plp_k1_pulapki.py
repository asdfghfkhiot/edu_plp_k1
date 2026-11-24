#!/usr/bin/env python3
"""Build the PLP K1 catalog of common circuit-analysis pitfalls.

Requires ReportLab and the fonts used by generate_plp_k1_guide.py.
Run from the repository root:
    python tools/generate_plp_k1_pulapki.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from reportlab.platypus import BaseDocTemplate, Flowable, Frame, PageBreak, PageTemplate, Spacer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import generate_plp_k1_guide as base

OUTPUT = ROOT / "PLP_K1_katalog_typowych_pulapek.pdf"


def draw_wire(canvas, p1, p2, width=1.2, color=None):
    canvas.setStrokeColor(color or base.NAVY)
    canvas.setLineWidth(width)
    canvas.line(p1[0], p1[1], p2[0], p2[1])


def draw_resistor(canvas, x1, y1, x2, y2, label, width=36, height=13):
    import math

    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    half = width / 2
    draw_wire(canvas, (x1, y1), (cx - ux * half, cy - uy * half))
    draw_wire(canvas, (cx + ux * half, cy + uy * half), (x2, y2))
    angle = math.degrees(math.atan2(dy, dx))
    canvas.saveState()
    canvas.translate(cx, cy)
    canvas.rotate(angle)
    canvas.setFillColor(base.WHITE)
    canvas.setStrokeColor(base.NAVY)
    canvas.setLineWidth(1.05)
    canvas.roundRect(-half, -height / 2, width, height, 2, fill=1, stroke=1)
    canvas.setFillColor(base.INK)
    canvas.setFont("DejaVu-Bold", 6.8)
    canvas.drawCentredString(0, -2.4, label)
    canvas.restoreState()


def draw_node(canvas, x, y, label, color, dx=4, dy=3):
    base.paint_node(canvas, x, y, label, color, dx=dx, dy=dy, radius=3.0)


class TopologyTrapDiagram(Flowable):
    """Three visual tests: true series, true parallel, and a false series pair."""

    def __init__(self, width=base.CONTENT_W, height=142):
        super().__init__()
        self.width, self.height = width, height

    def wrap(self, available_width, available_height):
        self.width = min(self.width, available_width)
        return self.width, self.height

    def _panel(self, canvas, x, width, title, note):
        canvas.setFillColor(base.WHITE)
        canvas.setStrokeColor(base.LINE)
        canvas.roundRect(x, 3, width, self.height - 6, 5, fill=1, stroke=1)
        canvas.setFont("DejaVu-Bold", 7.8)
        canvas.setFillColor(base.TEAL_DARK)
        canvas.drawCentredString(x + width / 2, self.height - 17, title)
        canvas.setFont("DejaVu", 6.7)
        canvas.setFillColor(base.MUTED)
        canvas.drawCentredString(x + width / 2, 12, note)

    def draw(self):
        canvas = self.canv
        canvas.saveState()
        canvas.setFillColor(base.PALE)
        canvas.setStrokeColor(base.LINE)
        canvas.roundRect(0, 0, self.width, self.height, 6, fill=1, stroke=1)
        gap = 7
        panel_width = (self.width - 2 * gap - 8) / 3
        xs = [4, 4 + panel_width + gap, 4 + 2 * (panel_width + gap)]

        # Series: the shared node M has only two element terminals.
        x = xs[0]
        self._panel(canvas, x, panel_width, "SZEREGOWO", "M ma tylko dwa przyłącza")
        y = 75
        a, m, b = x + 18, x + panel_width / 2, x + panel_width - 18
        draw_resistor(canvas, a, y, m, y, "R₁", width=31)
        draw_resistor(canvas, m, y, b, y, "R₂", width=31)
        draw_node(canvas, a, y, "A", base.NODE_A)
        draw_node(canvas, m, y, "M", base.NODE_C)
        draw_node(canvas, b, y, "B", base.NODE_B)
        canvas.setFont("DejaVu-Bold", 7.2)
        canvas.setFillColor(base.INK)
        canvas.drawCentredString(x + panel_width / 2, 34, "i₁ = i₂")

        # Parallel: each component touches the same two nodes A and B.
        x = xs[1]
        self._panel(canvas, x, panel_width, "RÓWNOLEGLE", "te same dwa węzły A i B")
        left, right, top, bottom = x + 35, x + panel_width - 35, 86, 59
        draw_wire(canvas, (left, top), (right, top))
        draw_wire(canvas, (left, bottom), (right, bottom))
        draw_resistor(canvas, left + 18, top, left + 18, bottom, "R₁", width=22, height=12)
        draw_resistor(canvas, right - 18, top, right - 18, bottom, "R₂", width=22, height=12)
        for nx in (left + 18, right - 18):
            draw_node(canvas, nx, top, "A", base.NODE_A, dx=4, dy=3)
            draw_node(canvas, nx, bottom, "B", base.NODE_B, dx=4, dy=-9)
        canvas.setFont("DejaVu-Bold", 7.2)
        canvas.setFillColor(base.INK)
        canvas.drawCentredString(x + panel_width / 2, 34, "u₁ = u₂")

        # False series: a third branch from M to the same B node lets current split.
        x = xs[2]
        self._panel(canvas, x, panel_width, "NIE SZEREGOWO", "M ma trzecią gałąź")
        y = 79
        a, m, b = x + 18, x + panel_width / 2, x + panel_width - 18
        draw_resistor(canvas, a, y, m, y, "R₁", width=26)
        draw_resistor(canvas, m, y, b, y, "R₂", width=26)
        branch_y = 38
        draw_wire(canvas, (m, y), (m, 56))
        draw_resistor(canvas, m, 56, m, branch_y, "R₃", width=19, height=10)
        draw_wire(canvas, (m, branch_y), (b, branch_y))
        draw_wire(canvas, (b, branch_y), (b, y))
        draw_node(canvas, a, y, "A", base.NODE_A)
        draw_node(canvas, m, y, "M", base.NODE_C)
        draw_node(canvas, b, y, "B", base.NODE_B)
        draw_node(canvas, m, branch_y, "B", base.NODE_B, dx=5, dy=3)
        canvas.restoreState()


class SourceZeroingDiagram(Flowable):
    """Memory aid for ideal independent-source deactivation."""

    def __init__(self, width=base.CONTENT_W, height=70):
        super().__init__()
        self.width, self.height = width, height

    def wrap(self, available_width, available_height):
        self.width = min(self.width, available_width)
        return self.width, self.height

    def draw(self):
        canvas = self.canv
        canvas.saveState()
        canvas.setFillColor(base.PALE)
        canvas.setStrokeColor(base.LINE)
        canvas.roundRect(0, 0, self.width, self.height, 6, fill=1, stroke=1)
        half = self.width / 2
        y = 45
        canvas.setStrokeColor(base.NAVY)
        canvas.setLineWidth(1.2)

        # Ideal voltage source: a zero-volt source is a continuous wire.
        x = 44
        draw_wire(canvas, (15, y), (x - 10, y))
        canvas.setFillColor(base.WHITE)
        canvas.setStrokeColor(base.NAVY)
        canvas.circle(x, y, 10, fill=1, stroke=1)
        canvas.setFillColor(base.TEAL_DARK)
        canvas.setFont("DejaVu-Bold", 7)
        canvas.drawCentredString(x, y + 2, "+")
        canvas.drawCentredString(x, y - 7, "−")
        draw_wire(canvas, (x + 10, y), (73, y))
        canvas.setFont("DejaVu-Bold", 10)
        canvas.setFillColor(base.TEAL_DARK)
        canvas.drawCentredString(94, y - 3, "→")
        draw_wire(canvas, (116, y), (148, y), width=2)
        canvas.setFont("DejaVu", 7.2)
        canvas.setFillColor(base.MUTED)
        canvas.drawCentredString(half / 2, 16, "E=0 V → zwarcie")

        # Ideal current source: a zero-ampere source leaves an open gap.
        x = half + 44
        draw_wire(canvas, (x - 29, y), (x - 10, y))
        canvas.setFillColor(base.WHITE)
        canvas.setStrokeColor(base.NAVY)
        canvas.circle(x, y, 10, fill=1, stroke=1)
        canvas.setStrokeColor(base.TEAL_DARK)
        canvas.setFillColor(base.TEAL_DARK)
        canvas.setLineWidth(1.2)
        canvas.line(x, y - 4, x, y + 4)
        arrow_head = canvas.beginPath()
        arrow_head.moveTo(x, y + 5)
        arrow_head.lineTo(x - 3, y + 1)
        arrow_head.lineTo(x + 3, y + 1)
        arrow_head.close()
        canvas.drawPath(arrow_head, fill=1, stroke=0)
        draw_wire(canvas, (x + 10, y), (x + 24, y))
        canvas.setFont("DejaVu-Bold", 10)
        canvas.setFillColor(base.TEAL_DARK)
        canvas.drawCentredString(x + 43, y - 3, "→")
        # Two separate terminals make the open circuit explicit.
        draw_wire(canvas, (x + 58, y), (x + 70, y))
        draw_wire(canvas, (x + 94, y), (x + 108, y))
        draw_wire(canvas, (x + 70, y - 5), (x + 70, y + 5))
        draw_wire(canvas, (x + 94, y - 5), (x + 94, y + 5))
        canvas.setFont("DejaVu", 7.2)
        canvas.setFillColor(base.MUTED)
        canvas.drawCentredString(half + half / 2, 16, "J=0 A → rozwarcie")
        canvas.restoreState()


class TrapDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        frame = Frame(
            base.LEFT, base.BOTTOM, base.CONTENT_W, base.PAGE_H - base.TOP - base.BOTTOM,
            leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id="body",
        )
        self.addPageTemplates([PageTemplate(id="Body", frames=[frame], onPage=self.draw_body)])

    @staticmethod
    def draw_body(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(base.WHITE)
        canvas.rect(0, 0, base.PAGE_W, base.PAGE_H, fill=1, stroke=0)
        canvas.setStrokeColor(base.LINE)
        canvas.setLineWidth(0.6)
        canvas.line(base.LEFT, base.PAGE_H - 10 * base.mm, base.PAGE_W - base.RIGHT, base.PAGE_H - 10 * base.mm)
        canvas.setFont("DejaVu-Bold", 7.4)
        canvas.setFillColor(base.NAVY)
        canvas.drawString(base.LEFT, base.PAGE_H - 7.5 * base.mm, "PLP K1  ·  POWTÓRKA DO KOLOKWIUM")
        canvas.setFont("DejaVu", 7.2)
        canvas.setFillColor(base.MUTED)
        canvas.drawRightString(base.PAGE_W - base.RIGHT, base.PAGE_H - 7.5 * base.mm, "Typowe pułapki")
        canvas.line(base.LEFT, 10 * base.mm, base.PAGE_W - base.RIGHT, 10 * base.mm)
        canvas.drawString(base.LEFT, 6.5 * base.mm, "Sprawdź warunek, zachowaj znak, kontroluj jednostki.")
        canvas.drawRightString(base.PAGE_W - base.RIGHT, 6.5 * base.mm, f"str. {doc.page}")
        canvas.restoreState()

    def afterFlowable(self, flowable):
        base.ManualDocTemplate.afterFlowable(self, flowable)


def build_story():
    return [
        base.H1("Katalog typowych pułapek"),
        base.P(
            "Większość błędów w zadaniach K1 bierze się z pominięcia warunku topologicznego, "
            "niewłaściwego wyzerowania źródła albo zgubienia znaku. Ten katalog służy jako "
            "krótka kontrola przed i po rachunkach."
        ),
        TopologyTrapDiagram(),
        base.H2("Pułapki topologiczne"),
        base.info_table([
            ["Pułapka", "Warunek, który trzeba sprawdzić", "Poprawny wniosek"],
            [
                "„Leżą obok siebie, więc są szeregowo”",
                "Wspólny węzeł tych dwóch elementów nie może mieć żadnego trzeciego odgałęzienia.",
                "Tylko wtedy prąd jest wspólny i wolno użyć R_z=R₁+R₂. Dodatkowa gałąź w węźle M wyklucza prostą redukcję szeregową.",
            ],
            [
                "„Są narysowane równolegle, więc są równolegle”",
                "Oba końce każdego elementu muszą należeć do tej samej pary węzłów A i B.",
                "Wtedy napięcie jest wspólne, a G_z=G₁+G₂. Sam kierunek lub bliskość symboli nie wystarcza.",
            ],
            [
                "„Każde przecięcie przewodów to węzeł”",
                "Prześledź, czy przewody są rzeczywiście połączone według rysunku; sprawdź kropkę lub ciągłość linii.",
                "Nie łącz gałęzi, które tylko się krzyżują. Oznacz węzły literami i dopiero wtedy oceniaj szereg/równoległość.",
            ],
            [
                "„Większy R dostaje większy prąd”",
                "Najpierw upewnij się, czy gałęzie są równoległe (te same węzły) czy elementy szeregowe (ten sam prąd).",
                "W równoległych gałęziach prąd dzieli się odwrotnie do R (I₁=I·R₂/(R₁+R₂)); w szeregu napięcie dzieli się proporcjonalnie do R.",
            ],
        ], [48 * base.mm, 63 * base.mm, base.CONTENT_W - 111 * base.mm]),
        Spacer(1, 5),
        base.callout(
            "Przykład z mostka",
            "Rezystor poprzeczny R₀ nie jest „szeregowo z najbliższym R” tylko dlatego, że leży na tej samej linii. "
            "Najpierw zmień źródła zgodnie z superpozycją, a potem sprawdź węzły. Dla wkładu E w zadaniu ze skanu s. 18 "
            "powstaje rzeczywiste R∥(R+R₀).",
        ),
        PageBreak(),
        base.H1("Źródła i superpozycja — co wolno wyłączyć?"),
        base.P(
            "„Wyłączyć źródło” oznacza nadać mu wartość zerową, a nie usuwać dowolne elementy z jego otoczenia. "
            "Reguły poniżej dotyczą idealnych źródeł niezależnych."
        ),
        SourceZeroingDiagram(),
        Spacer(1, 4),
        base.info_table([
            ["Element / sytuacja", "Poprawnie", "Typowy błąd"],
            [
                "Idealne źródło napięcia E",
                "E=0 V, czyli zwarcie. Przewody i pozostałe elementy zostają.",
                "Zastąpienie go przerwą albo skasowanie całej gałęzi.",
            ],
            [
                "Idealne źródło prądu J",
                "J=0 A, czyli rozwarcie. Pozostałe gałęzie zostają w układzie.",
                "Zastąpienie go zwarciem.",
            ],
            [
                "W superpozycji",
                "W obwodzie liniowym aktywne jest jedno źródło niezależne; pozostałe niezależne zerujesz. Elementy pasywne zostają.",
                "Wyzerowanie wszystkich źródeł naraz albo zapomnienie o wkładzie jednego źródła.",
            ],
            [
                "Źródło zależne k·u lub β·i",
                "Pozostaje aktywne w każdym przypadku. Przelicz jego wartość z bieżącego u lub i.",
                "Traktowanie go jak niezależnego i wyłączanie w superpozycji lub przy R_w.",
            ],
        ], [43 * base.mm, 72 * base.mm, base.CONTENT_W - 115 * base.mm]),
        base.callout(
            "Dlaczego źródło zależne zostaje?",
            "Jego wartość jest częścią równania obwodu, np. J_d=g·u. Wyłączenie go usuwa zależność sterującą "
            "i zmienia sam układ. Jeśli liczysz R_w, wyzeruj źródła niezależne, zostaw zależne i przyłóż źródło testowe.",
        ),
        base.H2("Dwie kontrole rachunku R_w"),
        base.info_table([
            ["Sytuacja", "Poprawny ruch"],
            ["Są tylko źródła niezależne", "E→zwarcie, J→rozwarcie; policz rezystancję widzianą z portu."],
            ["Jest źródło zależne", "Nie wyłączaj go; użyj U_x albo I_x i oblicz R_w=U_x/I_x."],
        ], [51 * base.mm, base.CONTENT_W - 51 * base.mm]),
        Spacer(1, 4),
        base.callout(
            "Przykłady z zadań",
            "R₅: po J→rozwarcie i E→zwarcie, wartości (w kΩ): R₁=1, R₂=3, R₃=4, R₄=1; "
            "R_w=R₄+[R₃∥(R₁+R₂)]=3 kΩ.  Źródło g·u₂: R₂=R₃=0,5 kΩ, R₄=1 kΩ, g=3 mS; "
            "źródło zależne zostaje aktywne. Przy zwrotach z rysunku G_wew=1/R₂+1/R₃−g=2+2−3=1 mS, "
            "więc R_w=R₄+1/G_wew=2 kΩ.",
        ),
        PageBreak(),
        base.H1("Znaki, Norton i kontrola wyniku"),
        base.callout(
            "Ujemny wynik nie musi oznaczać błędu",
            "Strzałka prądu i biegunowość napięcia to wybrane zwroty odniesienia. Wynik ujemny oznacza, "
            "że rzeczywista wielkość ma przeciwny zwrot. Zachowaj znak w rachunku, a kierunek opisz dopiero na końcu.",
            "answer",
        ),
        base.info_table([
            ["Pułapka", "Jak czytać wynik / co zrobić"],
            [
                "I<0",
                "Prąd płynie przeciwnie do strzałki. W zadaniu z trójkątem I=−4 A, więc rzeczywisty prąd 4 A płynie z C do R.",
            ],
            [
                "U_AB<0",
                "Jeśli U_AB=V_A−V_B, to A ma niższy potencjał od B. Nie zamieniaj A z B w połowie rozwiązania.",
            ],
            [
                "E_T policzone przy R_L",
                "Najpierw odłącz obciążenie: E_T jest napięciem jałowym U_AB. Napięcie pod obciążeniem oblicz dopiero po przywróceniu R_L.",
            ],
            [
                "Znak w źródle Nortona",
                "Ustal zwrot strzałki osobno. Przy U_AB>0 i R_w>0 równoważne źródło Nortona ma strzałkę B→A; prąd w zewnętrznym zwarciu płynie przeciwnie.",
            ],
            [
                "Moc w superpozycji",
                "Nie dodawaj mocy cząstkowych. Najpierw zsumuj algebraicznie prądy lub napięcia, potem oblicz moc z wyniku końcowego.",
            ],
            [
                "Jednostki",
                "Kontrola pamięciowa: 1 kΩ·1 mA=1 V; 1 mS·1 V=1 mA. Sprowadź jednostki przed dzieleniem lub mnożeniem.",
            ],
        ], [45 * base.mm, base.CONTENT_W - 45 * base.mm]),
        base.eqbox("Kontrola równoważnych źródeł: E_T = J_N·R_w, przy zgodnych znakach i zwrotach."),
        base.callout(
            "Przykłady znaków z Twoich zadań",
            "Trójkąt: I=−4 A oznacza zwrot przeciwny do strzałki. Układ z g·u₂: E_T=−10 V i J_N=−5 mA "
            "oznaczają zwrot przeciwny do przyjętego odniesienia. Zadanie A–B: E_T=6 V, R_w=1 kΩ, "
            "więc J_N=6 mA ze strzałką B→A.",
        ),
        Spacer(1, 5),
        base.callout(
            "Kontrola przed oddaniem",
            "□ Czy seria ma wspólny węzeł bez odgałęzienia?  □ Czy równoległe elementy mają te same dwa węzły?  "
            "□ Czy E wyzerowałem zwarciem, J rozwarciem, a źródła zależne zostawiłem?  "
            "□ Czy wynik ujemny zinterpretowałem zamiast usuwać znak?  □ Czy zgadzają się jednostki i KCL/KVL?",
            "tip",
        ),
    ]



def main():
    doc = TrapDocTemplate(
        str(OUTPUT),
        pagesize=base.A4,
        leftMargin=base.LEFT,
        rightMargin=base.RIGHT,
        topMargin=base.TOP,
        bottomMargin=base.BOTTOM,
        title="PLP K1 — katalog typowych pułapek",
        author="Opracowanie własne",
        subject="Topologia, źródła, znaki i kontrole w analizie obwodów",
        keywords="PLP K1, pułapki, szeregowo, równolegle, superpozycja, źródło zależne, znaki",
    )
    doc.multiBuild(build_story())
    print(f"Zapisano: {OUTPUT}")


if __name__ == "__main__":
    main()
