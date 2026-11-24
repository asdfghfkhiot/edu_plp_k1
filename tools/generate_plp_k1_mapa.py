#!/usr/bin/env python3
"""Build the PLP K1 decision map for choosing a circuit-analysis method.

Requires ReportLab and the fonts used by generate_plp_k1_guide.py.
Run from the repository root:
    python tools/generate_plp_k1_mapa.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    PageBreak,
    PageTemplate,
    Spacer,
)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import generate_plp_k1_guide as base

OUTPUT = ROOT / "PLP_K1_mapa_rozpoznawania_zadan.pdf"


class RecognitionMapDiagram(Flowable):
    """Three-way visual selector; the test source is nested under port analysis."""

    def __init__(self, width=base.CONTENT_W, height=154):
        super().__init__()
        self.width, self.height = width, height

    def wrap(self, available_width, available_height):
        self.width = min(self.width, available_width)
        return self.width, self.height

    @staticmethod
    def _arrow(canvas, x1, y1, x2, y2, color, head=4.5):
        import math

        canvas.setStrokeColor(color)
        canvas.setFillColor(color)
        canvas.setLineWidth(1.2)
        canvas.line(x1, y1, x2, y2)
        angle = math.atan2(y2 - y1, x2 - x1)
        p1 = (x2 - head * math.cos(angle - 0.5), y2 - head * math.sin(angle - 0.5))
        p2 = (x2 - head * math.cos(angle + 0.5), y2 - head * math.sin(angle + 0.5))
        path = canvas.beginPath()
        path.moveTo(x2, y2)
        path.lineTo(*p1)
        path.lineTo(*p2)
        path.close()
        canvas.drawPath(path, fill=1, stroke=0)

    def _card(self, canvas, x, y, width, height, title, lines, accent):
        canvas.setFillColor(base.WHITE)
        canvas.setStrokeColor(base.LINE)
        canvas.setLineWidth(0.8)
        canvas.roundRect(x, y, width, height, 5, fill=1, stroke=1)
        canvas.setFillColor(accent)
        canvas.roundRect(x, y + height - 5, width, 5, 2, fill=1, stroke=0)
        canvas.setFont("DejaVu-Bold", 8.4)
        canvas.setFillColor(accent)
        canvas.drawCentredString(x + width / 2, y + height - 19, title)
        canvas.setFont("DejaVu", 7.15)
        canvas.setFillColor(base.INK)
        line_y = y + height - 34
        for line in lines:
            canvas.drawCentredString(x + width / 2, line_y, line)
            line_y -= 11

    def draw(self):
        canvas = self.canv
        canvas.saveState()
        canvas.setFillColor(base.PALE)
        canvas.setStrokeColor(base.LINE)
        canvas.roundRect(0, 0, self.width, self.height, 6, fill=1, stroke=1)

        root_width, root_height = 290, 28
        root_x = (self.width - root_width) / 2
        root_y = self.height - 39
        canvas.setFillColor(base.WHITE)
        canvas.setStrokeColor(base.NAVY)
        canvas.roundRect(root_x, root_y, root_width, root_height, 5, fill=1, stroke=1)
        canvas.setFont("DejaVu-Bold", 8.6)
        canvas.setFillColor(base.NAVY)
        canvas.drawCentredString(self.width / 2, root_y + 16, "Najpierw ustal, czego wymaga polecenie")
        canvas.setFont("DejaVu", 7.2)
        canvas.setFillColor(base.MUTED)
        canvas.drawCentredString(self.width / 2, root_y + 5, "I/U w obwodzie  •  potencjały węzłów  •  model portu A–B")

        gap = 10
        side = 7
        card_width = (self.width - 2 * side - 2 * gap) / 3
        card_y, card_height = 22, 72
        xs = [side + i * (card_width + gap) for i in range(3)]
        centers = [x + card_width / 2 for x in xs]
        bus_y = root_y - 15
        canvas.setStrokeColor(base.MUTED)
        canvas.setLineWidth(0.9)
        canvas.line(self.width / 2, root_y, self.width / 2, bus_y)
        canvas.line(centers[0], bus_y, centers[-1], bus_y)
        accents = [base.TEAL, base.NODE_C, base.GOLD]
        for center, accent in zip(centers, accents):
            self._arrow(canvas, center, bus_y, center, card_y + card_height + 3, accent, head=4)

        self._card(
            canvas, xs[0], card_y, card_width, card_height,
            "SUPERPOZYCJA",
            ["I lub U w układzie liniowym", "kilka źródeł niezależnych", "wkłady da się liczyć osobno"],
            base.TEAL,
        )
        self._card(
            canvas, xs[1], card_y, card_width, card_height,
            "METODA WĘZŁOWA",
            ["szukane potencjały węzłów", "źródła prądowe, mostek, G", "mało niewiadomych węzłowych"],
            base.NODE_C,
        )
        self._card(
            canvas, xs[2], card_y, card_width, card_height,
            "THÉVENIN / NORTON",
            ["port A–B lub obciążenie", "wyznacz E_T i R_w", "zależne źródło przy R_w? → test"],
            base.GOLD,
        )
        canvas.setFont("DejaVu", 7.2)
        canvas.setFillColor(base.MUTED)
        canvas.drawCentredString(
            self.width / 2, 8,
            "Źródło testowe jest krokiem do R_w, a nie osobnym modelem końcowym.",
        )
        canvas.restoreState()


class MethodMapDocTemplate(BaseDocTemplate):
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
        canvas.drawRightString(base.PAGE_W - base.RIGHT, base.PAGE_H - 7.5 * base.mm, "Mapa metod")
        canvas.line(base.LEFT, 10 * base.mm, base.PAGE_W - base.RIGHT, 10 * base.mm)
        canvas.drawString(base.LEFT, 6.5 * base.mm, "Najpierw zwrot odniesienia, potem równanie i kontrola.")
        canvas.drawRightString(base.PAGE_W - base.RIGHT, 6.5 * base.mm, f"str. {doc.page}")
        canvas.restoreState()

    def afterFlowable(self, flowable):
        base.ManualDocTemplate.afterFlowable(self, flowable)


def build_story():
    story = [
        base.H1("Mapa rozpoznawania zadań"),
        base.P(
            "Najpierw ustal, <b>co jest szukane</b> i czy chodzi o cały obwód, czy o port A–B. "
            "Nie wybieraj metody wyłącznie po wyglądzie rysunku: kilka metod może być poprawnych, "
            "ale zwykle jedna daje mniej niewiadomych i prostsze sprawdzenie."
        ),
        RecognitionMapDiagram(),
        Spacer(1, 5),
        base.info_table([
            ["Sygnał w treści zadania", "Pierwszy krok", "Kontrola wyniku"],
            [
                "Wiele źródeł niezależnych; szukamy I lub U w liniowym obwodzie.",
                "Zostaw jedno źródło niezależne aktywne. Pozostałe E→zwarcie, J→rozwarcie; źródła zależne zostają.",
                "Dodaj wkłady algebraicznie; sprawdź zwrot, jednostki i KCL/KVL. Nie sumuj mocy cząstkowych.",
            ],
            [
                "Szukamy potencjałów węzłów; układ ma źródła prądowe, konduktancje lub mostek.",
                "Wybierz węzeł odniesienia, oznacz nieznane V_i i napisz KCL.",
                "Suma prądów w węźle ma wynosić zero; sprawdź ograniczenia źródeł i znak szukanego prądu.",
            ],
            [
                "Polecenie prosi o model widziany z A–B albo o odpowiedź dla obciążenia.",
                "Oznacz A–B i odłącz obciążenie. Dla E_T rozewrzyj port; dla J_N zewrzyj A–B.",
                "Sprawdź E_T=J_N·R_w przy zgodnych zwrotach oraz wynik po ponownym dołączeniu R_L.",
            ],
            [
                "Trzeba wyznaczyć R_w, a w sieci jest źródło zależne (lub redukcja nie jest prosta).",
                "Wyzeruj źródła niezależne, zostaw zależne i przyłóż źródło testowe U_x albo I_x.",
                "R_w=U_x/I_x; jednostką jest Ω. Zależność sterująca musi pozostać w równaniu.",
            ],
        ], [47 * base.mm, 69 * base.mm, base.CONTENT_W - 116 * base.mm]),
        Spacer(1, 6),
        base.callout(
            "Ważne: to są narzędzia, które można łączyć",
            "Thévenin/Norton to <b>cel</b> (model portu); do obliczenia E_T możesz użyć superpozycji albo KCL. "
            "Źródło testowe jest sposobem wyznaczania R_w, szczególnie gdy źródło zależne nie pozwala "
            "po prostu zredukować rezystancji.",
        ),
        PageBreak(),
        base.H1("Szukasz prądu lub napięcia w całym obwodzie"),
        base.H2("Superpozycja — rozdziel wpływ źródeł"),
        base.P(
            "Stosuj ją w <b>liniowym</b> obwodzie z kilkoma niezależnymi źródłami, gdy każdy przypadek "
            "pojedynczego źródła daje się łatwo rozwiązać. Jest szczególnie wygodna, gdy da się użyć "
            "dzielnika prądu lub napięcia. Jeśli jeden układ równań węzłowych jest krótszy, wybierz KCL zamiast mnożyć przypadki."
        ),
        base.info_table([
            ["Krok", "Co zrobić"],
            ["1. Odniesienie", "Ustal zwrot szukanego I/U raz i zachowaj go we wszystkich konfiguracjach."],
            ["2. Jedno źródło", "Pozostaw aktywne jedno źródło niezależne; inne E zastąp zwarciem, inne J — rozwarciem."],
            ["3. Zależne źródła", "Nie wyłączaj źródeł sterowanych. Ich wartość zmienia się razem z wielkością sterującą."],
            ["4. Suma", "Policz tę samą szukaną wielkość dla każdego źródła i dodaj wyniki ze znakami."],
        ], [34 * base.mm, base.CONTENT_W - 34 * base.mm]),
        base.eqbox("I = Σ I_k     albo     U = Σ U_k;     P liczymy dopiero z końcowego I lub U."),
        base.callout(
            "Kontrola superpozycji",
            "Wynik ujemny oznacza wkład przeciwny do przyjętej strzałki — nie zmieniaj jej w połowie rachunku. "
            "Na końcu sprawdź równanie Kirchhoffa lub rozwiąż cały obwód inną metodą jako kontrolę.",
        ),
        base.P(
            "<b>Rozpoznane przykłady:</b> zestawy K1, L1, O1 i P1 oraz mostek ze skanu s. 18. "
            "Punkt kontrolny: wyniki całkowite to odpowiednio I=2 mA, I=3 mA, U=2 V, I=3,2 mA i U=2 V.",
            "SmallPL",
        ),
        Spacer(1, 5),
        base.H2("Metoda węzłowa — zapisuj KCL dla potencjałów"),
        base.P(
            "Wybierz ją, gdy szukane są napięcia węzłowe, w obwodzie jest dużo źródeł prądowych lub "
            "konduktancji, występuje mostek albo nie widać bezpiecznych redukcji szeregowych/równoległych. "
            "Najlepsza, gdy liczba nieznanych potencjałów jest mała."
        ),
        base.info_table([
            ["Pierwszy ruch", "Równanie", "Kontrola"],
            [
                "Wybierz masę. Wpisz znane potencjały narzucone przez źródła napięcia względem tej masy.",
                "Dla każdej gałęzi użyj i=(V_a−V_b)/R albo i=G(V_a−V_b); przyrównaj sumę prądów w węźle do zera.",
                "Podstaw otrzymane V do KCL; w gałęzi sprawdź zwrot i znak prądu. Źródło między dwoma nieznanymi węzłami daje superwęzeł.",
            ],
        ], [47 * base.mm, 68 * base.mm, base.CONTENT_W - 115 * base.mm]),
        base.P(
            "<b>Rozpoznany przykład:</b> trójkąt ze skanu s. 22/24. Dolny węzeł przyjęto za 0 V, "
            "a jedyną niewiadomą było V_C; KCL daje V_C=9 V i I=−4 A (rzeczywisty prąd płynie "
            "przeciwnie do strzałki).",
            "SmallPL",
        ),
        PageBreak(),
        base.H1("Szukasz modelu portu A–B: Thévenin / Norton"),
        base.P(
            "Wybierz ten tok, gdy trzeba zastąpić całą sieć źródłem równoważnym albo obliczyć odpowiedź "
            "dla jednego lub wielu obciążeń. Zaciski A–B muszą być wskazane; cały pozostały obwód traktuj jako dwójnik.",
        ),
        base.info_table([
            ["Etap", "Pierwszy krok i dalsze działanie"],
            ["1. E_T", "Odłącz R_L. Napięcie jałowe U_AB jest napięciem Thévenina: E_T=U_AB."],
            ["2. R_w bez źródeł zależnych", "Wyzeruj źródła niezależne: idealne E→zwarcie, idealne J→rozwarcie. Policz rezystancję widzianą z A–B."],
            ["3. R_w ze źródłem zależnym", "Nie wyłączaj go. Po wyzerowaniu źródeł niezależnych przyłóż U_x lub I_x i policz R_w=U_x/I_x."],
            ["4. Norton", "Znajdź prąd zwarcia przy ustalonym zwrocie albo użyj J_N=E_T/R_w. Zapisz strzałkę źródła; nie pomyl jej z kierunkiem prądu w zewnętrznym zwarciu."],
            ["5. Obciążenie", "Przywróć R_L. Dla źródła Thévenina: I_L=E_T/(R_w+R_L), U_L=E_T·R_L/(R_w+R_L)."],
        ], [49 * base.mm, base.CONTENT_W - 49 * base.mm]),
        base.H2("Źródło testowe — procedura do wyznaczenia R_w"),
        base.info_table([
            ["Krok", "Zasada"],
            ["1", "Wyzeruj tylko źródła niezależne; źródła zależne i ich sterowanie zostają w układzie."],
            ["2", "Przyłóż niezerowe U_x (plus przy A) i oblicz I_x wchodzący do sieci przy A; albo wstrzyknij I_x od B do A i oblicz U_x."],
            ["3", "Policz R_w=U_x/I_x. Jeśli używasz G_w, sprawdź, że G_w=I_x/U_x i R_w=1/G_w."],
        ], [24 * base.mm, base.CONTENT_W - 24 * base.mm]),
        base.eqbox("U_x=1 V  ⇒  R_w=1 V/I_x;      I_x=1 A  ⇒  R_w=U_x/1 A.\nDla dodatniego E_T=U_AB i dodatniego R_w równoważne źródło Nortona ma strzałkę B→A, aby E_T=J_N·R_w."),
        base.callout(
            "Kontrola i przykłady z zadań",
            "Sprawdź E_T=J_N·R_w przy zgodnych zwrotach, jednostki oraz wynik po dołączeniu obciążenia. "
            "Zadanie R₅: E_T=14 V, R_w=3 kΩ, U=8 V. Zadanie z g·u₂: źródło zależne zostaje aktywne, "
            "E_T=−10 V, R_w=2 kΩ. Zadanie A–B: E_T=6 V, R_w=1 kΩ, a strzałka Nortona B→A.",
        ),
        Spacer(1, 5),
        base.callout(
            "Mini-checklista przed oddaniem",
            "□ Czy wybrałem metodę od celu zadania, a nie od kształtu rysunku?  "
            "□ Czy zachowałem strzałki i znaki?  "
            "□ Czy przy R_w pozostawiłem źródła zależne?  "
            "□ Czy sprawdziłem KCL/KVL, jednostki i E_T=J_N·R_w?",
            "answer",
        ),
    ]
    return story


def main():
    doc = MethodMapDocTemplate(
        str(OUTPUT),
        pagesize=base.A4,
        leftMargin=base.LEFT,
        rightMargin=base.RIGHT,
        topMargin=base.TOP,
        bottomMargin=base.BOTTOM,
        title="PLP K1 — mapa rozpoznawania zadań",
        author="Opracowanie własne",
        subject="Wybór metody analizy obwodów i kontrola wyników",
        keywords="PLP K1, superpozycja, metoda węzłowa, Thévenin, Norton, źródło testowe",
    )
    doc.multiBuild(build_story())
    print(f"Zapisano: {OUTPUT}")


if __name__ == "__main__":
    main()
