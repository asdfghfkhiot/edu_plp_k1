#!/usr/bin/env python3
"""Build a Polish PLP K1 workbook of fresh problem variants and a separate key.

Requires ReportLab and the fonts used by generate_plp_k1_guide.py.
Run from the repository root:
    python tools/generate_plp_k1_nowe_warianty.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import Flowable, NextPageTemplate, PageBreak, Spacer

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "PLP_K1_nowe_warianty_zadan.pdf"
sys.path.insert(0, str(ROOT))

from tools import generate_plp_k1_guide as base  # noqa: E402

NAVY = base.NAVY
TEAL = base.TEAL
TEAL_DARK = base.TEAL_DARK
GOLD = base.GOLD
INK = base.INK
MUTED = base.MUTED
LINE = base.LINE
PALE = base.PALE
WHITE = base.WHITE


def wire(c, p1, p2, width=1.3, color=NAVY):
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(p1[0], p1[1], p2[0], p2[1])


def arrow(c, p1, p2, color=GOLD, head=5.0, width=1.5):
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    angle = math.atan2(dy, dx)
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(width)
    c.line(p1[0], p1[1], p2[0], p2[1])
    left = (p2[0] - head * math.cos(angle - 0.48), p2[1] - head * math.sin(angle - 0.48))
    right = (p2[0] - head * math.cos(angle + 0.48), p2[1] - head * math.sin(angle + 0.48))
    path = c.beginPath()
    path.moveTo(p2[0], p2[1])
    path.lineTo(*left)
    path.lineTo(*right)
    path.close()
    c.drawPath(path, fill=1, stroke=0)


def dot(c, x, y, color=base.NODE_A, radius=3.2):
    c.setFillColor(color)
    c.setStrokeColor(WHITE)
    c.setLineWidth(0.8)
    c.circle(x, y, radius, fill=1, stroke=1)


def node(c, x, y, label, color, dx=5, dy=4):
    base.paint_node(c, x, y, label, color, dx=dx, dy=dy, radius=3.2)


def resistor_between(c, p1, p2, label, length=42, height=14):
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    distance = math.hypot(dx, dy)
    if distance < 3:
        raise ValueError("A resistor needs two distinct terminals")
    length = min(length, max(14, distance * 0.62))
    ux, uy = dx / distance, dy / distance
    cx, cy = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
    half = length / 2
    wire(c, p1, (cx - ux * half, cy - uy * half))
    wire(c, (cx + ux * half, cy + uy * half), p2)
    c.saveState()
    c.translate(cx, cy)
    c.rotate(math.degrees(math.atan2(dy, dx)))
    c.setFillColor(WHITE)
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.1)
    c.roundRect(-half, -height / 2, length, height, 2, fill=1, stroke=1)
    c.setFillColor(INK)
    c.setFont("DejaVu-Bold", 6.8)
    c.drawCentredString(0, -2.3, label)
    c.restoreState()


def voltage_source_vertical(c, x, y_bottom, y_top, label, plus_at_top=True, radius=11):
    cy = (y_bottom + y_top) / 2
    wire(c, (x, y_bottom), (x, cy - radius))
    wire(c, (x, cy + radius), (x, y_top))
    c.setFillColor(WHITE)
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.25)
    c.circle(x, cy, radius, fill=1, stroke=1)
    c.setFillColor(TEAL_DARK)
    c.setFont("DejaVu-Bold", 8)
    c.drawCentredString(x, cy + 1.5, "+" if plus_at_top else "−")
    c.drawCentredString(x, cy - 8, "−" if plus_at_top else "+")
    c.setFillColor(INK)
    c.setFont("DejaVu-Bold", 7.2)
    c.drawRightString(x - radius - 4, cy - 2.5, label)


def current_source_between(c, p1, p2, label, direction=1, radius=10):
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    distance = math.hypot(dx, dy)
    ux, uy = dx / distance, dy / distance
    cx, cy = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
    wire(c, p1, (cx - ux * radius, cy - uy * radius))
    wire(c, (cx + ux * radius, cy + uy * radius), p2)
    c.setFillColor(WHITE)
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.25)
    c.circle(cx, cy, radius, fill=1, stroke=1)
    start = (cx - direction * ux * 5.5, cy - direction * uy * 5.5)
    end = (cx + direction * ux * 5.5, cy + direction * uy * 5.5)
    arrow(c, start, end, TEAL_DARK, head=4.2, width=1.1)
    c.setFillColor(INK)
    c.setFont("DejaVu-Bold", 7.1)
    c.drawCentredString(cx, cy + radius + 7, label)


def current_source_vertical(c, x, y_bottom, y_top, label, arrow_up=True, radius=11):
    direction = 1 if arrow_up else -1
    current_source_between(c, (x, y_bottom), (x, y_top), label, direction=direction, radius=radius)


def dependent_current_vertical(c, x, y_bottom, y_top, label, arrow_down=True, half_w=12, half_h=17):
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
    p1, p2 = ((x, cy + 7), (x, cy - 7)) if arrow_down else ((x, cy - 7), (x, cy + 7))
    arrow(c, p1, p2, TEAL_DARK, head=4.2, width=1.1)
    c.setFillColor(INK)
    c.setFont("DejaVu-Bold", 7.0)
    c.drawString(x + half_w + 4, cy - 2, label)


def ground_rail(c, x, y, width=18, label="0 V"):
    wire(c, (x, y), (x, y - 5))
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.0)
    c.line(x - width / 2, y - 5, x + width / 2, y - 5)
    c.line(x - width * 0.32, y - 9, x + width * 0.32, y - 9)
    c.line(x - width * 0.14, y - 13, x + width * 0.14, y - 13)
    c.setFont("DejaVu", 6.7)
    c.setFillColor(MUTED)
    c.drawString(x + width / 2 + 4, y - 8, label)


def panel(c, width, height, note=None):
    c.setFillColor(PALE)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.8)
    c.roundRect(0, 0, width, height, 6, fill=1, stroke=1)
    if note:
        c.setFont("DejaVu", 7.1)
        c.setFillColor(MUTED)
        c.drawCentredString(width / 2, 8, note)


class SuperpositionDiagram(Flowable):
    def __init__(self, width=base.CONTENT_W, height=178):
        super().__init__()
        self.width, self.height = width, height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        panel(c, self.width, self.height, "E ma biegunowość dodatnią u góry; J wtłacza prąd do X; I₃ przyjęto w dół.")
        y_top, y_bottom = 133, 38
        x_e, x_x, x_r1, x_r3, x_j = 58, 194, 275, 355, self.width - 50

        wire(c, (x_e, y_bottom), (x_j, y_bottom))
        voltage_source_vertical(c, x_e, y_bottom, y_top, "E")
        resistor_between(c, (x_e, y_top), (x_x, y_top), "R₂", length=45)
        wire(c, (x_x, y_top), (x_j, y_top))
        resistor_between(c, (x_r1, y_top), (x_r1, y_bottom), "R₁", length=42, height=15)
        resistor_between(c, (x_r3, y_top), (x_r3, y_bottom), "R₃", length=42, height=15)
        current_source_vertical(c, x_j, y_bottom, y_top, "J", arrow_up=True)

        for nx in (x_x, x_r1, x_r3):
            dot(c, nx, y_top, base.NODE_A)
            dot(c, nx, y_bottom, base.NODE_D)
        node(c, x_x, y_top, "X", base.NODE_A, dx=5, dy=4)
        arrow(c, (x_r3 + 22, 108), (x_r3 + 22, 71), GOLD, head=4.5)
        c.setFillColor(INK)
        c.setFont("DejaVu-Bold", 7.2)
        c.drawString(x_r3 + 27, 88, "I₃")
        ground_rail(c, x_j, y_bottom, label="0")
        c.restoreState()


class BridgeDiagram(Flowable):
    def __init__(self, width=base.CONTENT_W, height=210):
        super().__init__()
        self.width, self.height = width, height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        panel(c, self.width, self.height, "U = V_L − V_R; źródło J jest skierowane od dolnego węzła do L.")
        top = (self.width / 2, 166)
        left = (self.width / 2 - 112, 91)
        right = (self.width / 2 + 112, 91)
        bottom = (self.width / 2, 25)
        ex = 34

        resistor_between(c, top, left, "R", length=40)
        resistor_between(c, top, right, "R", length=40)
        resistor_between(c, right, bottom, "R", length=40)
        resistor_between(c, left, right, "R₀", length=44)
        current_source_between(c, bottom, left, "J", direction=1, radius=10)

        wire(c, (ex, top[1]), top)
        wire(c, (ex, bottom[1]), bottom)
        voltage_source_vertical(c, ex, bottom[1], top[1], "E")

        node(c, *top, "T", base.NODE_A)
        node(c, *left, "L", base.NODE_C, dx=-13)
        node(c, *right, "R", base.NODE_B)
        node(c, *bottom, "0", base.NODE_D, dy=-10)
        arrow(c, (right[0] - 32, 111), (left[0] + 32, 111), GOLD, head=4.5)
        c.setFillColor(INK)
        c.setFont("DejaVu-Bold", 7.2)
        c.drawCentredString(self.width / 2, 118, "U")
        c.restoreState()


class NodalDiagram(Flowable):
    def __init__(self, width=base.CONTENT_W, height=222):
        super().__init__()
        self.width, self.height = width, height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        panel(c, self.width, self.height, "E_L ustala V_L=+8 V; E_R ma biegunowość przeciwną i ustala V_R=−4 V.")
        left = (88, 147)
        right = (self.width - 88, 147)
        center = (self.width / 2, 77)
        y_ground = 28

        wire(c, (left[0], y_ground), (right[0], y_ground))
        voltage_source_vertical(c, left[0], y_ground, left[1], "E_L", plus_at_top=True)
        voltage_source_vertical(c, right[0], y_ground, right[1], "E_R", plus_at_top=False)
        resistor_between(c, left, center, "R₁", length=41)
        resistor_between(c, center, right, "R₃", length=41)
        resistor_between(c, center, (center[0], y_ground), "R₂", length=38, height=14)

        # A current source lies directly between the two voltage-clamped nodes.
        y_j = 188
        wire(c, left, (left[0], y_j))
        wire(c, right, (right[0], y_j))
        current_source_between(c, (left[0], y_j), (right[0], y_j), "J", direction=1, radius=10)

        node(c, *left, "L", base.NODE_A, dx=-13)
        node(c, *right, "R", base.NODE_B)
        node(c, *center, "C", base.NODE_C)
        dot(c, center[0], y_ground, base.NODE_D)
        dx, dy = center[0] - right[0], center[1] - right[1]
        length = math.hypot(dx, dy)
        ux, uy = dx / length, dy / length
        nx, ny = -uy, ux
        start = (right[0] + 18 * ux + 16 * nx, right[1] + 18 * uy + 16 * ny)
        end = (right[0] + 92 * ux + 16 * nx, right[1] + 92 * uy + 16 * ny)
        arrow(c, start, end, GOLD, head=4.5)
        c.setFillColor(INK)
        c.setFont("DejaVu-Bold", 7.2)
        c.drawString(start[0] - 25, start[1] + 5, "I")
        ground_rail(c, center[0], y_ground, label="0")
        c.restoreState()


class TheveninDiagram(Flowable):
    def __init__(self, width=base.CONTENT_W, height=175):
        super().__init__()
        self.width, self.height = width, height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        panel(c, self.width, self.height, "Odłącz R_L, aby wyznaczyć E_T; B jest zaciskiem odniesienia.")
        y_top, y_bottom = 133, 37
        x_e, x_a, x_load = 82, 258, self.width - 96
        wire(c, (x_e, y_bottom), (x_load, y_bottom))
        voltage_source_vertical(c, x_e, y_bottom, y_top, "E")
        resistor_between(c, (x_e, y_top), (x_a, y_top), "R₁", length=48)
        wire(c, (x_a, y_top), (x_load, y_top))
        resistor_between(c, (x_a, y_top), (x_a, y_bottom), "R₂", length=43, height=15)
        resistor_between(c, (x_load, y_top), (x_load, y_bottom), "R_L", length=45, height=15)
        dot(c, x_a, y_top, base.NODE_A)
        node(c, x_load, y_top, "A", base.NODE_A, dx=5, dy=4)
        node(c, x_load, y_bottom, "B", base.NODE_B, dy=-10)
        arrow(c, (x_load + 22, 111), (x_load + 22, 62), GOLD, head=4.5)
        c.setFillColor(INK)
        c.setFont("DejaVu-Bold", 7.2)
        c.drawString(x_load + 27, 85, "I_L")
        ground_rail(c, x_e, y_bottom, label="0")
        c.restoreState()


class VCCSDiagram(Flowable):
    """Port with a dependent current source g·u controlled by V_X−V_B."""

    def __init__(self, width=base.CONTENT_W, height=205):
        super().__init__()
        self.width, self.height = width, height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        panel(c, self.width, self.height, "J_d=g·u, u=V_X−V_B; strzałka źródła zależnego X→B.")
        y_top, y_bottom = 151, 34
        x_e, x_x, x_r2, x_dep, x_r4, x_a = 62, 184, 254, 324, 386, self.width - 38

        wire(c, (x_e, y_bottom), (x_a + 13, y_bottom))
        voltage_source_vertical(c, x_e, y_bottom, y_top, "E")
        resistor_between(c, (x_e, y_top), (x_x, y_top), "R₁", length=42)
        wire(c, (x_x, y_top), (x_r4, y_top))
        resistor_between(c, (x_x, y_top), (x_x, y_bottom), "R₂", length=42, height=15)
        dependent_current_vertical(c, x_dep, y_bottom, y_top, "g·u", arrow_down=True)
        resistor_between(c, (x_r4, y_top), (x_a, y_top), "R₄", length=42)
        wire(c, (x_a, y_top), (x_a + 13, y_top))
        wire(c, (x_a, y_bottom), (x_a + 13, y_bottom))
        c.setStrokeColor(NAVY)
        c.setFillColor(WHITE)
        c.circle(x_a + 13, y_top, 3.2, fill=1, stroke=1)
        c.circle(x_a + 13, y_bottom, 3.2, fill=1, stroke=1)

        dot(c, x_x, y_top, base.NODE_C)
        node(c, x_x, y_top, "X", base.NODE_C)
        node(c, x_a + 13, y_top, "A", base.NODE_A)
        node(c, x_a + 13, y_bottom, "B", base.NODE_B, dy=-10)
        ground_rail(c, x_e, y_bottom, label="0")
        c.restoreState()


class CCCSDiagram(Flowable):
    """Port with a dependent current source βi, controlled by current in R₁."""

    def __init__(self, width=base.CONTENT_W, height=200):
        super().__init__()
        self.width, self.height = width, height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        panel(c, self.width, self.height, "i przyjęto od źródła E przez R₁ do A; źródło βi wskazuje A→B.")
        y_top, y_bottom = 145, 35
        x_e, x_a, x_r2, x_dep, x_port = 70, 220, 306, 390, self.width - 43

        wire(c, (x_e, y_bottom), (x_port, y_bottom))
        voltage_source_vertical(c, x_e, y_bottom, y_top, "E")
        resistor_between(c, (x_e, y_top), (x_a, y_top), "R₁", length=48)
        wire(c, (x_a, y_top), (x_port, y_top))
        resistor_between(c, (x_r2, y_top), (x_r2, y_bottom), "R₂", length=44, height=15)
        dependent_current_vertical(c, x_dep, y_bottom, y_top, "βi", arrow_down=True)
        dot(c, x_a, y_top, base.NODE_A)
        node(c, x_port, y_top, "A", base.NODE_A)
        node(c, x_port, y_bottom, "B", base.NODE_B, dy=-10)
        arrow(c, (133, 166), (183, 166), GOLD, head=4.3)
        c.setFillColor(INK)
        c.setFont("DejaVu-Bold", 7.0)
        c.drawCentredString(158, 170, "i")
        ground_rail(c, x_e, y_bottom, label="0")
        c.restoreState()


class PracticeSpace(Flowable):
    def __init__(self, width=base.CONTENT_W, height=210):
        super().__init__()
        self.width, self.height = width, height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        c.setFillColor(MUTED)
        c.setFont("DejaVu-Bold", 7.1)
        c.drawString(0, self.height - 10, "MIEJSCE NA PLAN, RACHUNEK I WYNIK")
        c.setStrokeColor(LINE)
        c.setLineWidth(0.55)
        y = self.height - 28
        while y > 5:
            c.line(0, y, self.width, y)
            y -= 23
        c.restoreState()


class VariantDocTemplate(base.ManualDocTemplate):
    def draw_cover(self, canvas, doc):
        canvas.saveState()
        canvas.setFillColor(colors.HexColor("#F7FAFC"))
        canvas.rect(0, 0, base.PAGE_W, base.PAGE_H, fill=1, stroke=0)
        canvas.setFillColor(NAVY)
        canvas.rect(0, base.PAGE_H - 105 * mm, base.PAGE_W, 105 * mm, fill=1, stroke=0)
        canvas.setFillColor(TEAL)
        canvas.rect(0, base.PAGE_H - 108 * mm, base.PAGE_W, 3 * mm, fill=1, stroke=0)

        # A small circuit trace echoes the course handouts without crowding the cover.
        canvas.setStrokeColor(colors.HexColor("#3A657E"))
        canvas.setLineWidth(1.1)
        points = [
            (base.PAGE_W - 79 * mm, base.PAGE_H - 22 * mm),
            (base.PAGE_W - 46 * mm, base.PAGE_H - 22 * mm),
            (base.PAGE_W - 46 * mm, base.PAGE_H - 58 * mm),
            (base.PAGE_W - 18 * mm, base.PAGE_H - 58 * mm),
        ]
        for a, b in zip(points, points[1:]):
            canvas.line(a[0], a[1], b[0], b[1])
        for i, (x, y) in enumerate(points):
            canvas.setFillColor(GOLD if i == 2 else TEAL)
            canvas.circle(x, y, 2.3 * mm, fill=1, stroke=0)

        canvas.setFillColor(TEAL_DARK)
        canvas.roundRect(base.LEFT, 25 * mm, base.PAGE_W - base.LEFT - base.RIGHT, 28 * mm, 4 * mm, fill=1, stroke=0)
        canvas.setFont("DejaVu-Bold", 8.1)
        canvas.setFillColor(WHITE)
        canvas.drawString(base.LEFT + 7 * mm, 43 * mm, "OPRACOWANIE WŁASNE  ·  PLP K1")
        canvas.setFont("DejaVu", 8.0)
        canvas.drawString(base.LEFT + 7 * mm, 34 * mm, "Nowe dane wejściowe  ·  zadania i osobny klucz")
        canvas.setFont("DejaVu", 7.4)
        canvas.setFillColor(MUTED)
        canvas.drawRightString(base.PAGE_W - base.RIGHT, 14 * mm, "Zestaw treningowy")
        canvas.restoreState()

    def draw_body(self, canvas, doc):
        canvas.saveState()
        canvas.setFillColor(WHITE)
        canvas.rect(0, 0, base.PAGE_W, base.PAGE_H, fill=1, stroke=0)
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.6)
        canvas.line(base.LEFT, base.PAGE_H - 10 * mm, base.PAGE_W - base.RIGHT, base.PAGE_H - 10 * mm)
        canvas.setFont("DejaVu-Bold", 7.4)
        canvas.setFillColor(NAVY)
        canvas.drawString(base.LEFT, base.PAGE_H - 7.5 * mm, "PLP K1  ·  NOWE WARIANTY ZADAŃ")
        canvas.setFont("DejaVu", 7.2)
        canvas.setFillColor(MUTED)
        canvas.drawRightString(base.PAGE_W - base.RIGHT, base.PAGE_H - 7.5 * mm, "Ćwiczenia / klucz")
        canvas.line(base.LEFT, 10 * mm, base.PAGE_W - base.RIGHT, 10 * mm)
        canvas.setFont("DejaVu", 7.2)
        canvas.setFillColor(MUTED)
        canvas.drawString(base.LEFT, 6.5 * mm, "Zapisz zwroty i jednostki; nie poprawiaj wyniku ujemnego bez uzasadnienia.")
        canvas.drawRightString(base.PAGE_W - base.RIGHT, 6.5 * mm, f"str. {doc.page}")
        canvas.restoreState()


TASKS = [
    {
        "title": "Wariant 1 — Superpozycja w układzie jednowęzłowym",
        "method": "Metoda: superpozycja · wielkość szukana: prąd I₃ w zwrocie w dół.",
        "data": "E=12 V; J=1 mA; R₁=3 kΩ, R₂=6 kΩ, R₃=2 kΩ. Źródło E ma plus u góry, źródło J wtłacza prąd do węzła X.",
        "diagram": SuperpositionDiagram,
        "prompt": "Wyznacz I₃, licząc osobno wkład źródła E i źródła J. Przy każdym wkładzie zapisz, jak zastępujesz drugie źródło niezależne.",
    },
    {
        "title": "Wariant 2 — Mostek i superpozycja",
        "method": "Metoda: superpozycja po właściwej redukcji topologicznej.",
        "data": "Wszystkie trzy ramiona oznaczone R mają R=2 kΩ; mostek poprzeczny R₀=2 kΩ. E=15 V (plus przy T), J=2,5 mA od dolnego węzła do L. Szukane U=V_L−V_R.",
        "diagram": BridgeDiagram,
        "prompt": "Oblicz U. Dla wkładu E nazwij połączenia równoległe i szeregowe; dla wkładu J pokaż podział prądu. Zachowaj zwrot U=V_L−V_R.",
    },
    {
        "title": "Wariant 3 — Metoda węzłowa i znak prądu",
        "method": "Metoda: KCL w nieznanym węźle C.",
        "data": "Źródła idealne ustalają V_L=+8 V i V_R=−4 V względem masy. Między L i R płynie J=3 mA od L do R. R₁=1 kΩ (L–C), R₂=2 kΩ (C–0), R₃=2 kΩ (C–R).",
        "diagram": NodalDiagram,
        "prompt": "Wyznacz V_C oraz prąd I przez R₃ przy zwrocie R→C. Zapisz równanie KCL w C i wyjaśnij, czy źródło J występuje w tym równaniu.",
    },
    {
        "title": "Wariant 4 — Thévenin, Norton i obciążenie",
        "method": "Metoda: najpierw parametry portu A–B, potem ponownie dołączone obciążenie.",
        "data": "E=20 V; R₁=4 kΩ, R₂=12 kΩ, R_L=6 kΩ. Biegunowość E jest dodatnia u góry; R_L jest podłączony między A i B.",
        "diagram": TheveninDiagram,
        "prompt": "Wyznacz E_T, R_w i J_N. Następnie oblicz napięcie U_L oraz prąd I_L. Podaj zwrot strzałki idealnego źródła Nortona dla U_AB=V_A−V_B.",
    },
    {
        "title": "Wariant 5 — Źródło zależne g·u i R_w",
        "method": "Metoda: napięcie jałowe oraz źródło testowe; źródło zależne pozostaje aktywne.",
        "data": "E=18 V; R₁=2 kΩ, R₂=4 kΩ, R₄=3 kΩ; źródło prądowe sterowane ma wartość g·u, g=0,25 mS, u=V_X−V_B, a strzałka jest skierowana X→B.",
        "diagram": VCCSDiagram,
        "prompt": "Wyznacz E_T i R_w widziane z portu A–B, a następnie J_N. Pokaż, jak źródło testowe pozwala policzyć R_w, i nie wyłączaj źródła g·u.",
    },
    {
        "title": "Wariant 6 — Źródło zależne β·i i Norton",
        "method": "Metoda: KCL przy rozwarciu portu i źródło testowe przy wyznaczaniu R_w.",
        "data": "E=16 V; R₁=4 kΩ, R₂=2 kΩ, β=0,5. Prąd i płynie przez R₁ od źródła E do A; źródło zależne β·i jest skierowane od A do B.",
        "diagram": CCCSDiagram,
        "prompt": "Wyznacz parametry Thévenina i Nortona portu A–B. Przy obliczaniu R_w wyzeruj E, pozostaw źródło β·i i użyj testowego napięcia 1 V.",
    },
]


def add_task_page(story, task):
    story.extend([
        base.H1(task["title"]),
        base.P(task["method"], "BodyCompact"),
        base.callout("Dane i oznaczenia", task["data"]),
        Spacer(1, 5),
        task["diagram"](),
        Spacer(1, 5),
        base.P(f"<b>Polecenie.</b> {task['prompt']}"),
        Spacer(1, 4),
        PracticeSpace(),
        PageBreak(),
    ])


def build_story():
    story = [
        Spacer(1, 25 * mm),
        base.P("ZESTAW TRENINGOWY  ·  PLP K1", "CoverKicker"),
        base.P("Nowe warianty zadań", "CoverTitle"),
        base.P("Inne liczby. Ta sama metoda. Osobny klucz odpowiedzi.", "CoverSub"),
        Spacer(1, 8 * mm),
        base.callout(
            "Jak pracować z zestawem",
            "Najpierw rozwiąż wszystkie sześć zadań bez zaglądania do końcowej części PDF-u. Zapisz równania, zwroty odniesienia i jednostki. Dopiero potem otwórz osobny klucz i porównaj tok rozwiązania, nie tylko wynik liczbowy.",
        ),
        Spacer(1, 7 * mm),
        base.P(
            "Zakres: superpozycja w układzie i mostku, metoda węzłowa, obciążony równoważnik Thévenina, źródło sterowane napięciem g·u oraz źródło sterowane prądem β·i.",
            "CoverMeta",
        ),
        base.P(
            "Wartości wejściowe i wyniki są nowe względem omawianych przykładów. Rysunki podają zwroty oraz połączenia; w razie wątpliwości nazwij węzły przed redukcją.",
            "CoverMeta",
        ),
        NextPageTemplate("Body"),
        PageBreak(),
    ]

    for task in TASKS:
        add_task_page(story, task)

    story.extend([
        base.H1("Klucz odpowiedzi"),
        base.P("Rozwiązania są oddzielone od zestawu zadań. W każdym przykładzie podano kroki, znaki i kontrolę wyniku."),
        base.callout("Przed sprawdzeniem", "Upewnij się, że przyjęte biegunowości i strzałki są takie same jak na schemacie. Wynik ujemny oznacza zwrot przeciwny do przyjętego odniesienia."),
        base.H2("Zadanie 1 — Superpozycja w układzie jednowęzłowym"),
        base.P("Konduktancja trzech gałęzi widzianych z X wynosi 1/R₁+1/R₂+1/R₃=1/3+1/6+1/2=1 mS."),
        base.H3("Wkład źródła E"),
        base.P("J zerujemy rozwarciem. Źródło E=12 V zasila węzeł X przez R₂, więc V_X,E=(E/R₂)/(1 mS)=2 mA/1 mS=2 V. Stąd I₃,E=V_X,E/R₃=2 V/2 kΩ=1 mA."),
        base.H3("Wkład źródła J"),
        base.P("E zerujemy zwarciem, więc R₂ pozostaje między X a masą. V_X,J=J/(1 mS)=1 V, a I₃,J=1 V/2 kΩ=0,5 mA."),
        base.eqbox("I₃=I₃,E+I₃,J=1+0,5=<b>1,5 mA w dół</b>."),
        base.callout("Kontrola", "Z KCL dla pełnego układu: V_X·1 mS=E/R₂+J=2 mA+1 mA, więc V_X=3 V i I₃=3 V/2 kΩ=1,5 mA.", "answer"),
        PageBreak(),

        base.H2("Zadanie 2 — Mostek i superpozycja"),
        base.P("Przyjęto U=V_L−V_R. Wkłady obu niezależnych źródeł mają w tym zadaniu dodatni zwrot."),
        base.H3("Wkład E: J zastąp rozwarciem"),
        base.P("Od T do R są dwie drogi: bezpośrednio przez R oraz przez szereg R+R₀. Zatem R_TR=R∥(R+R₀)=2∥4=4/3 kΩ. Ten blok jest szeregowy z dolnym R=2 kΩ."),
        base.eqbox("U_TR=15·(4/3)/(4/3+2)=6 V;\nU_E=U_TR·R₀/(R+R₀)=6·2/4=3 V."),
        base.H3("Wkład J: E zastąp zwarciem"),
        base.P("Top i dół stają się jednym węzłem. Z R widzianego z prawego węzła powstaje R∥R=1 kΩ; droga alternatywna od L przez R₀ ma łącznie 3 kΩ. Równolegle z nią jest lewa gałąź R=2 kΩ."),
        base.P("Prąd w drodze zawierającej R₀ wynosi I₀=J·2/(2+3)=2,5·2/5=1 mA. Dlatego U_J=I₀R₀=2 V."),
        base.eqbox("U=U_E+U_J=3+2=<b>5 V</b>."),
        base.callout("Kontrola topologii", "R₀ nie jest szeregowo z najbliższym rezystorem w pełnym mostku. Redukcje wykonuj dopiero po wyzerowaniu źródła i ponownym ustaleniu węzłów."),
        PageBreak(),

        base.H2("Zadanie 3 — Metoda węzłowa i znak prądu"),
        base.P("Idealne źródła ustalają V_L=+8 V i V_R=−4 V. Źródło J łączy L z R, ale nie jest połączone z C."),
        base.H3("KCL w węźle C"),
        base.P("Sumujemy prądy wypływające z C przez trzy rezystory:"),
        base.eqbox("(V_C−8)/1 kΩ + V_C/2 kΩ + (V_C+4)/2 kΩ=0."),
        base.P("Po wyrażeniu prądów w mA: V_C−8+0,5V_C+0,5(V_C+4)=0, zatem 2V_C−6=0 i V_C=3 V."),
        base.H3("Prąd w zadanym zwrocie R→C"),
        base.P("I=(V_R−V_C)/R₃=(−4−3) V/2 kΩ=−3,5 mA. Rzeczywisty prąd 3,5 mA płynie z C do R."),
        base.callout("Co z J?", "Źródło J nie wchodzi do KCL w C, bo nie styka się z tym węzłem. Zmienia prądy w idealnych źródłach napięcia, ale nie zmienia narzuconych potencjałów V_L i V_R.", "answer"),
        PageBreak(),

        base.H2("Zadanie 4 — Thévenin, Norton i obciążenie"),
        base.H3("Napięcie jałowe E_T"),
        base.P("Odłącz R_L. Dzielnik R₁–R₂ daje napięcie w A względem B:"),
        base.eqbox("E_T=U_AB=20·12/(4+12)=15 V."),
        base.H3("Rezystancja R_w i model Nortona"),
        base.P("Zeruj źródło E, czyli zastąp je zwarciem. Z portu A–B widać R₁∥R₂:"),
        base.eqbox("R_w=4∥12=4·12/(4+12)=3 kΩ;\nJ_N=E_T/R_w=15 V/3 kΩ=5 mA, strzałka źródła B→A."),
        base.H3("Przywróć R_L"),
        base.eqbox("U_L=E_T·R_L/(R_w+R_L)=15·6/(3+6)=10 V;\nI_L=U_L/R_L=10/6=5/3 mA≈1,67 mA."),
        base.callout("Kontrola bezpośrednia", "W oryginalnym układzie R₂∥R_L=12∥6=4 kΩ. Dzielnik z R₁=4 kΩ daje U_L=20·4/(4+4)=10 V, ten sam wynik.", "answer"),
        PageBreak(),

        base.H2("Zadanie 5 — Źródło zależne g·u i R_w"),
        base.H3("Napięcie jałowe"),
        base.P("Przy rozwarciu A–B prąd przez R₄ jest zerowy, więc V_A=V_X. KCL w X:"),
        base.eqbox("(V_X−18)/2 kΩ + V_X/4 kΩ + 0,25 mS·V_X=0."),
        base.P("Konduktancja przy V_X wynosi 0,5+0,25+0,25=1 mS, a E/R₁=9 mA. Stąd V_X=9 V i E_T=9 V."),
        base.H3("Rezystancja widziana z portu"),
        base.P("Zeruj E zwarciem, lecz pozostaw źródło g·u aktywne. G_X=1/R₁+1/R₂+g=1 mS. Przyłóż test U_t=1 V do A–B. KCL w X: (V_X−1 V)/3 kΩ+1 mS·V_X=0, więc V_X=0,25 V."),
        base.eqbox("I_t=(1−0,25)/3 kΩ=0,25 mA;   R_w=U_t/I_t=4 kΩ;\nJ_N=E_T/R_w=9/4=<b>2,25 mA</b>, strzałka B→A."),
        base.callout("Kluczowa zasada", "Źródło zależne nie zostało wyzerowane. Przy teście jego prąd nadal wynosi g·u i zmienia się razem z napięciem węzła X."),
        PageBreak(),

        base.H2("Zadanie 6 — Źródło zależne β·i i Norton"),
        base.H3("Napięcie jałowe E_T"),
        base.P("Przy rozwarciu portu prąd R₁ spełnia i=(E−V_A)/R₁. KCL w A daje i=V_A/R₂+βi, czyli V_A=R₂(1−β)i."),
        base.P("Z KVL: E=[R₁+R₂(1−β)]i=[4+2·0,5]kΩ·i=5 kΩ·i, więc i=16/5=3,2 mA."),
        base.eqbox("E_T=V_A=R₂(1−β)i=2·0,5·3,2=<b>3,2 V</b>."),
        base.H3("Rezystancja testowa R_w"),
        base.P("Zeruj E zwarciem, pozostaw βi i przyłóż U_x=1 V od A do B. Wtedy prąd odniesienia i przez R₁ wynosi (0−1)/4 kΩ=−0,25 mA. Prąd testowy pobierany przez port:"),
        base.eqbox("I_x=1/2 kΩ + 1/4 kΩ + βi\n=0,5+0,25−0,125=0,625 mA;\nR_w=U_x/I_x=1/0,625=<b>1,6 kΩ</b>."),
        base.H3("Model Nortona i kontrola"),
        base.eqbox("J_N=E_T/R_w=3,2/1,6=<b>2 mA</b>, strzałka źródła B→A;\nJ_N·R_w=2 mA·1,6 kΩ=3,2 V=E_T."),
        base.callout("Znak źródła zależnego", "Przy teście i jest ujemny, więc źródło o strzałce A→B ma ujemny prąd względem tej strzałki. Nie odwracaj go przed zapisaniem KCL.", "answer"),
    ])
    return story


def main():
    doc = VariantDocTemplate(
        str(OUTPUT),
        pagesize=base.A4,
        leftMargin=base.LEFT,
        rightMargin=base.RIGHT,
        topMargin=base.TOP,
        bottomMargin=base.BOTTOM,
        title="PLP K1 — nowe warianty zadań i klucz odpowiedzi",
        author="Opracowanie własne",
        subject="Ćwiczenia z superpozycji, metody węzłowej, Thévenina/Nortona i źródeł zależnych",
        keywords="PLP K1, warianty zadań, klucz odpowiedzi, superpozycja, węzły, Thévenin, Norton",
    )
    doc.multiBuild(build_story())
    print(f"Zapisano: {OUTPUT}")


if __name__ == "__main__":
    main()
