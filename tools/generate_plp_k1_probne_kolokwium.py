#!/usr/bin/env python3
"""Generate a Polish PLP K1 mock exam with a timed task section and solutions at the end.

Requires ReportLab and the fonts used by generate_plp_k1_guide.py.
Run from the repository root:
    python tools/generate_plp_k1_probne_kolokwium.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import Flowable, NextPageTemplate, PageBreak, Spacer

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "PLP_K1_probne_kolokwium.pdf"
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


POINTS_BY_TASK = (10, 20, 15, 20, 25, 10)
MINUTES_BY_TASK = (8, 18, 14, 19, 23, 8)
assert sum(POINTS_BY_TASK) == 100
assert sum(MINUTES_BY_TASK) == 90


def wire(c, p1, p2, width=1.3, color=NAVY):
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(p1[0], p1[1], p2[0], p2[1])


def arrow(c, p1, p2, color=GOLD, head=4.8, width=1.45):
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


def dot(c, x, y, color=base.NODE_A, radius=3.1):
    c.setFillColor(color)
    c.setStrokeColor(WHITE)
    c.setLineWidth(0.8)
    c.circle(x, y, radius, fill=1, stroke=1)


def node(c, x, y, label, color, dx=5, dy=4):
    base.paint_node(c, x, y, label, color, dx=dx, dy=dy, radius=3.1)


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


def voltage_source_vertical(c, x, y_bottom, y_top, label, plus_at_top=True, radius=10.5):
    cy = (y_bottom + y_top) / 2
    wire(c, (x, y_bottom), (x, cy - radius))
    wire(c, (x, cy + radius), (x, y_top))
    c.setFillColor(WHITE)
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.2)
    c.circle(x, cy, radius, fill=1, stroke=1)
    c.setFillColor(TEAL_DARK)
    c.setFont("DejaVu-Bold", 8)
    c.drawCentredString(x, cy + 1.5, "+" if plus_at_top else "−")
    c.drawCentredString(x, cy - 8, "−" if plus_at_top else "+")
    c.setFillColor(INK)
    c.setFont("DejaVu-Bold", 7.0)
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
    c.setLineWidth(1.2)
    c.circle(cx, cy, radius, fill=1, stroke=1)
    start = (cx - direction * ux * 5.2, cy - direction * uy * 5.2)
    end = (cx + direction * ux * 5.2, cy + direction * uy * 5.2)
    arrow(c, start, end, TEAL_DARK, head=4, width=1.05)
    c.setFillColor(INK)
    c.setFont("DejaVu-Bold", 7)
    c.drawCentredString(cx, cy + radius + 6, label)


def current_source_vertical(c, x, y_bottom, y_top, label, arrow_up=True, radius=10.5):
    current_source_between(
        c, (x, y_bottom), (x, y_top), label,
        direction=1 if arrow_up else -1, radius=radius,
    )


def dependent_current_vertical(c, x, y_bottom, y_top, label, arrow_down=True, half_w=11, half_h=16):
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
    arrow(c, p1, p2, TEAL_DARK, head=3.8, width=1.0)
    c.setFillColor(INK)
    c.setFont("DejaVu-Bold", 7)
    c.drawString(x + half_w + 4, cy - 2.5, label)


def ground_symbol(c, x, y, label="0"):
    wire(c, (x, y), (x, y - 5))
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.0)
    c.line(x - 9, y - 5, x + 9, y - 5)
    c.line(x - 6, y - 9, x + 6, y - 9)
    c.line(x - 3, y - 13, x + 3, y - 13)
    c.setFillColor(MUTED)
    c.setFont("DejaVu", 6.5)
    c.drawString(x + 12, y - 8, label)


def diagram_panel(c, width, height, caption):
    c.setFillColor(PALE)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.8)
    c.roundRect(0, 0, width, height, 6, fill=1, stroke=1)
    c.setFillColor(MUTED)
    c.setFont("DejaVu", 7.0)
    c.drawCentredString(width / 2, 7, caption)


class TopologyDiagram(Flowable):
    def __init__(self, width=base.CONTENT_W, height=156):
        super().__init__()
        self.width, self.height = width, height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        diagram_panel(c, self.width, self.height, "Badany port ma zaciski A–B; M jest wspólnym węzłem gałęzi.")
        x_a, x_m, x_b = 54, 174, self.width - 52
        y_mid, y_top, y_bottom = 87, 126, 48

        node(c, x_a, y_mid, "A", base.NODE_A, dx=5, dy=4)
        resistor_between(c, (x_a, y_mid), (x_m, y_mid), "R₁", length=43)
        wire(c, (x_m, y_bottom), (x_m, y_top))
        wire(c, (x_b, y_bottom), (x_b, y_top))
        resistor_between(c, (x_m, y_top), (x_b, y_top), "R₂", length=45)
        resistor_between(c, (x_m, y_bottom), (x_b, y_bottom), "R₃", length=45)
        node(c, x_m, y_mid, "M", base.NODE_C)
        node(c, x_b, y_mid, "B", base.NODE_B)
        dot(c, x_m, y_top, base.NODE_C)
        dot(c, x_m, y_bottom, base.NODE_C)
        dot(c, x_b, y_top, base.NODE_B)
        dot(c, x_b, y_bottom, base.NODE_B)
        c.restoreState()


class SuperpositionDiagram(Flowable):
    def __init__(self, width=base.CONTENT_W, height=174):
        super().__init__()
        self.width, self.height = width, height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        diagram_panel(c, self.width, self.height, "E ma plus u góry; J wtłacza prąd do X; I₃ przyjęto w dół.")
        y_top, y_bottom = 130, 36
        x_e, x_x, x_r1, x_r3, x_j = 56, 185, 268, 350, self.width - 48

        wire(c, (x_e, y_bottom), (x_j, y_bottom))
        voltage_source_vertical(c, x_e, y_bottom, y_top, "E")
        resistor_between(c, (x_e, y_top), (x_x, y_top), "R₂", length=44)
        wire(c, (x_x, y_top), (x_j, y_top))
        resistor_between(c, (x_r1, y_top), (x_r1, y_bottom), "R₁", length=42, height=15)
        resistor_between(c, (x_r3, y_top), (x_r3, y_bottom), "R₃", length=42, height=15)
        current_source_vertical(c, x_j, y_bottom, y_top, "J", arrow_up=True)
        for nx in (x_x, x_r1, x_r3):
            dot(c, nx, y_top, base.NODE_A)
            dot(c, nx, y_bottom, base.NODE_D)
        node(c, x_x, y_top, "X", base.NODE_A)
        arrow(c, (x_r3 + 22, 104), (x_r3 + 22, 70), GOLD, head=4.3)
        c.setFillColor(INK)
        c.setFont("DejaVu-Bold", 7.1)
        c.drawString(x_r3 + 27, 85, "I₃")
        ground_symbol(c, x_j, y_bottom, "0")
        c.restoreState()


class NodalDiagram(Flowable):
    def __init__(self, width=base.CONTENT_W, height=220):
        super().__init__()
        self.width, self.height = width, height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        diagram_panel(c, self.width, self.height, "E_L ustala V_L=+12 V; E_R ma biegunowość przeciwną i ustala V_R=−4 V.")
        left = (86, 146)
        right = (self.width - 86, 146)
        center = (self.width / 2, 75)
        y_ground = 27

        wire(c, (left[0], y_ground), (right[0], y_ground))
        voltage_source_vertical(c, left[0], y_ground, left[1], "E_L", plus_at_top=True)
        voltage_source_vertical(c, right[0], y_ground, right[1], "E_R", plus_at_top=False)
        resistor_between(c, left, center, "R₁", length=40)
        resistor_between(c, center, right, "R₃", length=40)
        resistor_between(c, center, (center[0], y_ground), "R₂", length=38, height=14)

        y_j = 187
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
        start = (right[0] + 18 * ux + 17 * nx, right[1] + 18 * uy + 17 * ny)
        end = (right[0] + 92 * ux + 17 * nx, right[1] + 92 * uy + 17 * ny)
        arrow(c, start, end, GOLD, head=4.3)
        c.setFillColor(INK)
        c.setFont("DejaVu-Bold", 7.0)
        c.drawString(start[0] - 23, start[1] + 5, "I")
        ground_symbol(c, center[0], y_ground, "0")
        c.restoreState()


class TheveninDiagram(Flowable):
    def __init__(self, width=base.CONTENT_W, height=172):
        super().__init__()
        self.width, self.height = width, height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        diagram_panel(c, self.width, self.height, "Odłącz R_L przy wyznaczaniu E_T; B jest zaciskiem odniesienia.")
        y_top, y_bottom = 131, 35
        x_e, x_a, x_load = 74, 248, self.width - 91
        wire(c, (x_e, y_bottom), (x_load, y_bottom))
        voltage_source_vertical(c, x_e, y_bottom, y_top, "E")
        resistor_between(c, (x_e, y_top), (x_a, y_top), "R₁", length=45)
        wire(c, (x_a, y_top), (x_load, y_top))
        resistor_between(c, (x_a, y_top), (x_a, y_bottom), "R₂", length=42, height=15)
        resistor_between(c, (x_load, y_top), (x_load, y_bottom), "R_L", length=43, height=15)
        dot(c, x_a, y_top, base.NODE_A)
        node(c, x_load, y_top, "A", base.NODE_A)
        node(c, x_load, y_bottom, "B", base.NODE_B, dy=-10)
        arrow(c, (x_load + 22, 106), (x_load + 22, 62), GOLD, head=4.2)
        c.setFillColor(INK)
        c.setFont("DejaVu-Bold", 7.0)
        c.drawString(x_load + 27, 82, "I_L")
        ground_symbol(c, x_e, y_bottom, "0")
        c.restoreState()


class VCCSDiagram(Flowable):
    """Port with a dependent current source g·u, where u=V_X−V_B."""

    def __init__(self, width=base.CONTENT_W, height=194):
        super().__init__()
        self.width, self.height = width, height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        diagram_panel(c, self.width, self.height, "J_d=g·u; u=V_X−V_B; strzałka źródła zależnego X→B.")
        y_top, y_bottom = 143, 33
        x_e, x_x, x_r2, x_dep, x_r4, x_a = 56, 166, 235, 303, 370, self.width - 38

        wire(c, (x_e, y_bottom), (x_a + 13, y_bottom))
        voltage_source_vertical(c, x_e, y_bottom, y_top, "E")
        resistor_between(c, (x_e, y_top), (x_x, y_top), "R₁", length=42)
        wire(c, (x_x, y_top), (x_r4, y_top))
        resistor_between(c, (x_x, y_top), (x_x, y_bottom), "R₂", length=40, height=15)
        dependent_current_vertical(c, x_dep, y_bottom, y_top, "g·u", arrow_down=True)
        resistor_between(c, (x_r4, y_top), (x_a, y_top), "R₄", length=40)
        wire(c, (x_a, y_top), (x_a + 13, y_top))
        wire(c, (x_a, y_bottom), (x_a + 13, y_bottom))
        c.setStrokeColor(NAVY)
        c.setFillColor(WHITE)
        c.circle(x_a + 13, y_top, 3.0, fill=1, stroke=1)
        c.circle(x_a + 13, y_bottom, 3.0, fill=1, stroke=1)
        dot(c, x_x, y_top, base.NODE_C)
        node(c, x_x, y_top, "X", base.NODE_C)
        node(c, x_a + 13, y_top, "A", base.NODE_A)
        node(c, x_a + 13, y_bottom, "B", base.NODE_B, dy=-10)
        ground_symbol(c, x_e, y_bottom, "0")
        c.restoreState()


class CCCSDiagram(Flowable):
    """Port with a current-controlled current source βi."""

    def __init__(self, width=base.CONTENT_W, height=190):
        super().__init__()
        self.width, self.height = width, height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        diagram_panel(c, self.width, self.height, "i wskazuje od źródła E przez R₁ do A; źródło βi wskazuje A→B.")
        y_top, y_bottom = 139, 34
        x_e, x_a, x_r2, x_dep, x_port = 68, 210, 300, 382, self.width - 42

        wire(c, (x_e, y_bottom), (x_port, y_bottom))
        voltage_source_vertical(c, x_e, y_bottom, y_top, "E")
        resistor_between(c, (x_e, y_top), (x_a, y_top), "R₁", length=45)
        wire(c, (x_a, y_top), (x_port, y_top))
        resistor_between(c, (x_r2, y_top), (x_r2, y_bottom), "R₂", length=42, height=15)
        dependent_current_vertical(c, x_dep, y_bottom, y_top, "βi", arrow_down=True)
        dot(c, x_a, y_top, base.NODE_A)
        node(c, x_port, y_top, "A", base.NODE_A)
        node(c, x_port, y_bottom, "B", base.NODE_B, dy=-10)
        arrow(c, (124, 159), (173, 159), GOLD, head=4.1)
        c.setFillColor(INK)
        c.setFont("DejaVu-Bold", 7)
        c.drawCentredString(148, 163, "i")
        ground_symbol(c, x_e, y_bottom, "0")
        c.restoreState()


class WorkSpace(Flowable):
    def __init__(self, width=base.CONTENT_W, height=205, label="Miejsce na obliczenia"):
        super().__init__()
        self.width, self.height, self.label = width, height, label

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        c.setFillColor(MUTED)
        c.setFont("DejaVu-Bold", 7.0)
        c.drawString(0, self.height - 10, self.label.upper())
        c.setStrokeColor(LINE)
        c.setLineWidth(0.55)
        y = self.height - 28
        while y > 5:
            c.line(0, y, self.width, y)
            y -= 23
        c.restoreState()


class MockExamDocTemplate(base.ManualDocTemplate):
    def draw_cover(self, canvas, doc):
        canvas.saveState()
        canvas.setFillColor(colors.HexColor("#F7FAFC"))
        canvas.rect(0, 0, base.PAGE_W, base.PAGE_H, fill=1, stroke=0)
        canvas.setFillColor(NAVY)
        canvas.rect(0, base.PAGE_H - 105 * mm, base.PAGE_W, 105 * mm, fill=1, stroke=0)
        canvas.setFillColor(TEAL)
        canvas.rect(0, base.PAGE_H - 108 * mm, base.PAGE_W, 3 * mm, fill=1, stroke=0)
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
        canvas.drawString(base.LEFT + 7 * mm, 43 * mm, "SYMULACJA  ·  PLP K1")
        canvas.setFont("DejaVu", 8.0)
        canvas.drawString(base.LEFT + 7 * mm, 34 * mm, "90 minut  ·  100 punktów  ·  rozwiązania na końcu")
        canvas.setFont("DejaVu", 7.4)
        canvas.setFillColor(MUTED)
        canvas.drawRightString(base.PAGE_W - base.RIGHT, 14 * mm, "Próbne kolokwium")
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
        canvas.drawString(base.LEFT, base.PAGE_H - 7.5 * mm, "PLP K1  ·  PRÓBNE KOLOKWIUM")
        canvas.setFont("DejaVu", 7.2)
        canvas.setFillColor(MUTED)
        canvas.drawRightString(base.PAGE_W - base.RIGHT, base.PAGE_H - 7.5 * mm, "Zadania / rozwiązania")
        canvas.line(base.LEFT, 10 * mm, base.PAGE_W - base.RIGHT, 10 * mm)
        canvas.setFont("DejaVu", 7.2)
        canvas.setFillColor(MUTED)
        canvas.drawString(base.LEFT, 6.5 * mm, "90 min · 100 pkt · zapisuj zwroty, jednostki i tok rozumowania.")
        canvas.drawRightString(base.PAGE_W - base.RIGHT, 6.5 * mm, f"str. {doc.page}")
        canvas.restoreState()


TASKS = [
    {
        "title": "Zadanie 1 — Topologia i redukcja",
        "time": 8,
        "points": 10,
        "method": "Sprawdzenie warunków połączenia szeregowego i równoległego.",
        "data": "R₁=2 kΩ między A–M; R₂=6 kΩ i R₃=3 kΩ między M–B. Szukamy rezystancji zastępczej widzianej z A–B.",
        "diagram": TopologyDiagram,
        "parts": [
            "<b>a) (4 pkt)</b> Wskaż, które rezystory są połączone równolegle.",
            "<b>b) (3 pkt)</b> Czy R₁ i R₂ są bezpośrednio szeregowo? Uzasadnij, odwołując się do węzła M.",
            "<b>c) (3 pkt)</b> Oblicz rezystancję zastępczą R_AB.",
        ],
        "space": 205,
    },
    {
        "title": "Zadanie 2 — Superpozycja",
        "time": 18,
        "points": 20,
        "method": "W obwodzie liniowym wyznacz prąd I₃ metodą superpozycji.",
        "data": "E=16 V; J=1 mA; R₁=4 kΩ, R₂=4 kΩ, R₃=2 kΩ. Plus E jest u góry, J wtłacza prąd do X, a I₃ ma zwrot w dół.",
        "diagram": SuperpositionDiagram,
        "parts": [
            "<b>a) (4 pkt)</b> Zapisz, jak zastępujesz nieaktywne źródło niezależne w każdym przypadku.",
            "<b>b) (10 pkt)</b> Oblicz osobno wkład E i wkład J do I₃.",
            "<b>c) (6 pkt)</b> Zsumuj wkłady algebraicznie i sprawdź wynik krótkim równaniem KCL w X.",
        ],
        "space": 205,
    },
    {
        "title": "Zadanie 3 — Metoda węzłowa",
        "time": 14,
        "points": 15,
        "method": "Zapisz KCL w nieznanym węźle C; zachowaj zadany zwrot prądu.",
        "data": "Źródła idealne ustalają V_L=+12 V i V_R=−4 V względem masy. J=2 mA płynie od L do R. R₁=2 kΩ (L–C), R₂=4 kΩ (C–0), R₃=4 kΩ (C–R).",
        "diagram": NodalDiagram,
        "parts": [
            "<b>a) (6 pkt)</b> Zapisz równanie KCL w C, używając prądów wypływających z tego węzła.",
            "<b>b) (5 pkt)</b> Oblicz V_C i prąd I przez R₃ ze zwrotem R→C.",
            "<b>c) (4 pkt)</b> Zinterpretuj znak I i wyjaśnij, czy J występuje w równaniu KCL w C.",
        ],
        "space": 205,
    },
    {
        "title": "Zadanie 4 — Thévenin, Norton i obciążenie",
        "time": 19,
        "points": 20,
        "method": "Znajdź model portu A–B, a potem przywróć obciążenie.",
        "data": "E=24 V; R₁=6 kΩ, R₂=18 kΩ, R_L=9 kΩ. Źródło E ma plus u góry; R_L jest podłączony między A i B.",
        "diagram": TheveninDiagram,
        "parts": [
            "<b>a) (4 pkt)</b> Odłącz R_L i wyznacz napięcie Thévenina E_T.",
            "<b>b) (6 pkt)</b> Wyznacz R_w i prąd Nortona J_N; podaj strzałkę źródła Nortona dla U_AB=V_A−V_B.",
            "<b>c) (6 pkt)</b> Po ponownym dołączeniu R_L oblicz U_L i I_L.",
            "<b>d) (4 pkt)</b> Wykonaj jedną kontrolę wyniku dla obciążenia.",
        ],
        "space": 195,
    },
    {
        "title": "Zadanie 5 — Źródło zależne g·u",
        "time": 23,
        "points": 25,
        "method": "Wyznacz E_T i R_w portu; źródło zależne pozostaw aktywne.",
        "data": "E=12 V; R₁=4 kΩ, R₂=4 kΩ, R₄=3 kΩ; J_d=g·u, g=0,5 mS, u=V_X−V_B, a strzałka J_d wskazuje X→B.",
        "diagram": VCCSDiagram,
        "parts": [
            "<b>a) (5 pkt)</b> Przy rozwarciu A–B oblicz napięcie Thévenina E_T.",
            "<b>b) (12 pkt)</b> Wyzeruj E, pozostaw J_d aktywne i użyj testu U_t=1 V do znalezienia R_w.",
            "<b>c) (4 pkt)</b> Oblicz J_N i podaj kierunek jego strzałki.",
            "<b>d) (4 pkt)</b> Krótko wyjaśnij, dlaczego J_d pozostaje aktywne przy wyznaczaniu R_w.",
        ],
        "space": 190,
    },
    {
        "title": "Zadanie 6 — Znaki i jednostki",
        "time": 8,
        "points": 10,
        "method": "Trzy krótkie kontrole; nie zmieniaj zwrotów odniesienia w połowie rachunku.",
        "data": "W podpunkcie b) strzałkę źródła Nortona przyjmij od B do A.",
        "diagram": None,
        "parts": [
            "<b>a) (4 pkt)</b> Jeśli U_AB=V_A−V_B=−2,5 V, który zacisk ma wyższy potencjał i o ile?",
            "<b>b) (4 pkt)</b> Dla E_T=−6 V i R_w=3 kΩ oblicz J_N. Co oznacza znak względem przyjętej strzałki B→A?",
            "<b>c) (2 pkt)</b> Oblicz 3 mS·4 V i podaj jednostkę wyniku.",
        ],
        "space": 315,
    },
]


def add_task_page(story, task):
    story.extend([
        base.H1(task["title"]),
        base.P(f"<b>{task['points']} punktów</b> · sugerowany czas {task['time']} min · {task['method']}", "BodyCompact"),
        base.callout("Dane", task["data"]),
        Spacer(1, 5),
    ])
    if task["diagram"]:
        story.extend([task["diagram"](), Spacer(1, 5)])
    for part in task["parts"]:
        story.append(base.P(part, "BodyCompact"))
    story.extend([Spacer(1, 4), WorkSpace(height=task["space"]), PageBreak()])


def build_story():
    story = [
        Spacer(1, 24 * mm),
        base.P("SYMULACJA EGZAMINU  ·  PLP K1", "CoverKicker"),
        base.P("Próbne kolokwium", "CoverTitle"),
        base.P("90 minut · 100 punktów · rozwiązania schowane na końcu", "CoverSub"),
        Spacer(1, 7 * mm),
        base.callout(
            "Warunki pracy",
            "Ustaw limit 90 minut. Kalkulator prosty jest dozwolony. Rozwiąż najpierw zadania 1–6; nie przewijaj do końcowej sekcji przed upływem czasu. Pokaż tok obliczeń, zwroty odniesienia i jednostki — sam wynik bez uzasadnienia może nie dać pełnych punktów.",
        ),
        Spacer(1, 5 * mm),
        base.info_table(
            [
                ["Zadanie", "Temat", "Czas", "Punkty"],
                ["1", "Topologia i redukcja", "8 min", "10"],
                ["2", "Superpozycja", "18 min", "20"],
                ["3", "Metoda węzłowa", "14 min", "15"],
                ["4", "Thévenin / Norton", "19 min", "20"],
                ["5", "Źródło zależne g·u", "23 min", "25"],
                ["6", "Znaki i jednostki", "8 min", "10"],
                ["Suma", "", "90 min", "100"],
            ],
            [18 * mm, 95 * mm, 30 * mm, 25 * mm],
        ),
        NextPageTemplate("Body"),
        PageBreak(),
    ]

    for task in TASKS:
        add_task_page(story, task)

    story.extend([
        base.H1("Rozwiązania — otwórz po zakończeniu"),
        base.P("Klucz zaczyna się po wszystkich zadaniach. Porównaj założenia, równania, znaki i jednostki — nie tylko liczby końcowe."),
        base.callout("Samoocena", "Przyznawaj punkty za poprawną metodę i uzasadnione kroki. Jeśli wynik różni się, sprawdź najpierw topologię, zwroty źródeł i jednostki."),
        base.H2("Rozwiązanie 1 — Topologia i redukcja"),
        base.P("R₂ i R₃ mają oba końce przyłączone do tej samej pary węzłów M–B, więc są równolegle."),
        base.eqbox("R₂₃=R₂∥R₃=6·3/(6+3)=2 kΩ."),
        base.P("R₁ i R₂ nie są bezpośrednio szeregowo: węzeł M jest połączony również z R₃, więc prąd przez R₁ rozdziela się między dwie gałęzie. Po zastąpieniu R₂∥R₃ ich równoważnikiem pozostaje już szereg z R₁."),
        base.eqbox("R_AB=R₁+R₂₃=2+2=<b>4 kΩ</b>."),
        PageBreak(),

        base.H2("Rozwiązanie 2 — Superpozycja"),
        base.P("Suma konduktancji gałęzi z X do masy wynosi G_Σ=1/R₁+1/R₂+1/R₃=0,25+0,25+0,5=1 mS."),
        base.H3("Wkład źródła E"),
        base.P("J zastępujemy rozwarciem. Prąd przez R₂ wynosi E/R₂=16 V/4 kΩ=4 mA. Zatem V_X,E=4 mA/1 mS=4 V i I₃,E=4 V/2 kΩ=2 mA."),
        base.H3("Wkład źródła J"),
        base.P("E zastępujemy zwarciem, a R₂ pozostaje w układzie. V_X,J=J/G_Σ=1 mA/1 mS=1 V, więc I₃,J=1 V/2 kΩ=0,5 mA."),
        base.eqbox("I₃=I₃,E+I₃,J=2+0,5=<b>2,5 mA w dół</b>."),
        base.callout("Kontrola KCL", "W pełnym układzie E/R₂+J=4+1=5 mA, zatem V_X=5 V. I₃=V_X/R₃=5/2=2,5 mA."),
        PageBreak(),

        base.H2("Rozwiązanie 3 — Metoda węzłowa"),
        base.P("Przyjmij prądy wypływające z C. Ponieważ V_L=12 V, V_R=−4 V, a masa ma 0 V:"),
        base.eqbox("(V_C−12)/2 kΩ + V_C/4 kΩ + (V_C+4)/4 kΩ=0."),
        base.P("Po wyrażeniu prądów w mA: 0,5(V_C−12)+0,25V_C+0,25(V_C+4)=0. Po zebraniu składników otrzymujemy V_C−5=0, więc V_C=5 V."),
        base.eqbox("I_{R→C}=(V_R−V_C)/R₃=(−4−5)/4 kΩ=<b>−2,25 mA</b>."),
        base.callout("Interpretacja", "Rzeczywisty prąd ma wartość 2,25 mA i płynie od C do R. Źródło J leży między L i R, nie styka się z C, więc nie występuje w KCL w C. Ponadto V_L i V_R są już narzucone przez idealne źródła napięcia."),
        PageBreak(),

        base.H2("Rozwiązanie 4 — Thévenin, Norton i obciążenie"),
        base.H3("Napięcie jałowe"),
        base.P("Po odłączeniu R_L napięcie A–B jest spadkiem na R₂ z dzielnika R₁–R₂:"),
        base.eqbox("E_T=24·18/(6+18)=18 V."),
        base.H3("Rezystancja i źródło Nortona"),
        base.P("Po zwarciu idealnego źródła E z portu widać R₁∥R₂."),
        base.eqbox("R_w=6∥18=6·18/(6+18)=4,5 kΩ;\nJ_N=E_T/R_w=18/4,5=4 mA, strzałka źródła B→A."),
        base.H3("Napięcie i prąd obciążenia"),
        base.eqbox("U_L=18·9/(4,5+9)=12 V;   I_L=12/9=4/3 mA≈1,33 mA."),
        base.callout("Kontrola w oryginalnym układzie", "R₂∥R_L=18∥9=6 kΩ. Dzielnik E=24 V ma więc R₁=6 kΩ i obciążenie równoważne 6 kΩ; napięcie na nim wynosi 12 V."),
        PageBreak(),

        base.H2("Rozwiązanie 5 — Źródło zależne g·u"),
        base.H3("E_T przy rozwarciu portu"),
        base.P("Przy otwartym A–B przez R₄ nie płynie prąd, więc V_A=V_X. KCL w X:"),
        base.eqbox("(V_X−12)/4 kΩ + V_X/4 kΩ + 0,5 mS·V_X=0."),
        base.P("G_Σ=0,25+0,25+0,5=1 mS, a E/R₁=3 mA. Stąd V_X=3 V i E_T=3 V."),
        base.H3("R_w z testem 1 V"),
        base.P("Zerujemy E zwarciem, ale źródło zależne zostawiamy. Wewnętrzna konduktancja w X wynosi G_X=1/R₁+1/R₂+g=1 mS. Przy U_t=1 V na A–B KCL w X daje (V_X−1)/3+V_X=0, więc V_X=0,25 V."),
        base.eqbox("I_t=(1−0,25)/3 kΩ=0,25 mA;   R_w=1/0,25=<b>4 kΩ</b>."),
        base.eqbox("J_N=E_T/R_w=3/4=<b>0,75 mA</b>, strzałka źródła B→A."),
        base.callout("Dlaczego J_d zostaje?", "J_d=g·u jest częścią równania obwodu. Przy teście jego wartość nadal zależy od V_X; wyłączenie go zmieniłoby badaną sieć."),
        PageBreak(),

        base.H2("Rozwiązanie 6 — Znaki i jednostki"),
        base.H3("a) Ujemne napięcie"),
        base.P("U_AB=V_A−V_B=−2,5 V oznacza V_A=V_B−2,5 V. Zacisk B ma potencjał wyższy o 2,5 V."),
        base.H3("b) Znak prądu Nortona"),
        base.eqbox("J_N=E_T/R_w=−6 V/3 kΩ=−2 mA."),
        base.P("Wynik jest ujemny względem strzałki B→A, więc rzeczywisty prąd źródła Nortona ma wartość 2 mA i zwrot A→B."),
        base.H3("c) Kontrola jednostek"),
        base.eqbox("3 mS·4 V=<b>12 mA</b>."),
        base.callout("Podsumowanie", "Minus pozostaje w rachunku; dopiero na końcu opisujemy rzeczywisty zwrot. Jednostka konduktancja razy napięcie daje prąd."),
    ])
    return story


def main():
    doc = MockExamDocTemplate(
        str(OUTPUT),
        pagesize=base.A4,
        leftMargin=base.LEFT,
        rightMargin=base.RIGHT,
        topMargin=base.TOP,
        bottomMargin=base.BOTTOM,
        title="PLP K1 — próbne kolokwium",
        author="Opracowanie własne",
        subject="Próbne kolokwium z analizy obwodów: zadania, punktacja i rozwiązania",
        keywords="PLP K1, próbne kolokwium, czas, superpozycja, węzły, Thévenin, Norton",
    )
    doc.multiBuild(build_story())
    print(f"Zapisano: {OUTPUT}")


if __name__ == "__main__":
    main()
