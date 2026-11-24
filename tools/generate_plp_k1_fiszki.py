#!/usr/bin/env python3
"""Generate printable PLP K1 self-check flashcards in Polish.

Requires ReportLab and the fonts used by generate_plp_k1_guide.py.
Run from the repository root:
    python tools/generate_plp_k1_fiszki.py

Each four-card question page is followed by its duplex back. Answer cards are
mirrored left-to-right so they align when printed portrait, double-sided, and
flipped on the long edge.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "PLP_K1_fiszki_do_samosprawdzania.pdf"
sys.path.insert(0, str(ROOT))

from tools import generate_plp_k1_guide as base  # noqa: E402

PAGE_W, PAGE_H = A4
MARGIN_X = 32
GRID_BOTTOM = 34
GRID_TOP = PAGE_H - 103
GAP_X = 12
GAP_Y = 12
COLS = 2
ROWS = 2
CARDS_PER_SHEET = COLS * ROWS
TOTAL_CARDS = 24
TOTAL_SHEETS = TOTAL_CARDS // CARDS_PER_SHEET

CARD_W = (PAGE_W - 2 * MARGIN_X - GAP_X) / COLS
CARD_H = (GRID_TOP - GRID_BOTTOM - GAP_Y) / ROWS

INK = base.INK
NAVY = base.NAVY
MUTED = base.MUTED
LINE = base.LINE
WHITE = base.WHITE
PALE = base.PALE

ACCENTS = {
    "topologia": base.TEAL,
    "źródła": base.GOLD,
    "superpozycja": colors.HexColor("#7353BA"),
    "zależne": colors.HexColor("#7353BA"),
    "Thévenin · Norton": base.NAVY,
    "obciążenie": colors.HexColor("#39845B"),
    "znaki": colors.HexColor("#A44343"),
    "rachunek": base.TEAL_DARK,
}

QUESTION_STYLE = ParagraphStyle(
    "FlashQuestionPL",
    fontName="DejaVu-Bold",
    fontSize=12.5,
    leading=16.5,
    textColor=NAVY,
    alignment=0,
    spaceAfter=0,
    allowWidows=0,
    allowOrphans=0,
)
ANSWER_STYLE = ParagraphStyle(
    "FlashAnswerPL",
    fontName="DejaVu",
    fontSize=9.5,
    leading=13.3,
    textColor=INK,
    alignment=0,
    spaceAfter=0,
    allowWidows=0,
    allowOrphans=0,
)


@dataclass(frozen=True)
class FlashCard:
    number: int
    category: str
    question: str
    answer: str

    @property
    def accent(self):
        return ACCENTS[self.category]


@dataclass(frozen=True)
class CardSet:
    title: str
    cards: tuple[FlashCard, ...]


def make_card(number: int, category: str, question: str, answer: str) -> FlashCard:
    return FlashCard(number, category, question, answer)


CARD_SETS = (
    CardSet(
        "Topologia i podział prądu",
        (
            make_card(
                1, "topologia",
                "Kiedy dwa elementy są rzeczywiście połączone szeregowo?",
                "Ich wspólny węzeł łączy tylko te dwa elementy — nie ma tam trzeciej gałęzi. Płynie przez nie ten sam prąd; dla rezystorów R_eq=R₁+R₂.",
            ),
            make_card(
                2, "topologia",
                "Jak sprawdzić, czy dwa rezystory są połączone równolegle?",
                "Oba końce każdego rezystora muszą należeć do tej samej pary węzłów. Napięcie jest wspólne, a 1/R_eq=1/R₁+1/R₂.",
            ),
            make_card(
                3, "topologia",
                "Dwa przewody krzyżują się na schemacie. Czy na pewno tworzą węzeł?",
                "Nie zakładaj połączenia. Sprawdź kropkę, mostek lub przerwę oraz konwencję rysunku; prześledź ciągłość każdej linii, zanim uprościsz obwód.",
            ),
            make_card(
                4, "topologia",
                "Dwa rezystory R₁ i R₂ są równoległe. Jak wyrazić prąd I₁, gdy do pary wpływa prąd I?",
                "I₁=I·R₂/(R₁+R₂). Prąd dzieli się odwrotnie proporcjonalnie do oporów: większy prąd płynie przez mniejszy opór.",
            ),
        ),
    ),
    CardSet(
        "Źródła idealne i superpozycja",
        (
            make_card(
                5, "źródła",
                "Co zastępuje idealne źródło napięcia po wyzerowaniu?",
                "Zwarcie: E=0 V. Zostają przewody oraz wszystkie pozostałe elementy obwodu.",
            ),
            make_card(
                6, "źródła",
                "Co zastępuje idealne źródło prądu po wyzerowaniu?",
                "Rozwarcie: J=0 A. Nie usuwaj innych elementów ani gałęzi, które nie są tym źródłem.",
            ),
            make_card(
                7, "źródła",
                "Co dzieje się z rezystorem szeregowym z wyzerowanym źródłem napięcia?",
                "Źródło E zastępujesz zwarciem, ale rezystor zostaje w obwodzie. Zerujesz wartość źródła, a nie dowolne elementy z jego otoczenia.",
            ),
            make_card(
                8, "superpozycja",
                "Jak stosować superpozycję i co wolno dodawać?",
                "W obwodzie liniowym licz wkład jednego źródła niezależnego naraz; pozostałe zeruj. Źródła zależne zostają aktywne. Napięcia i prądy sumuj algebraicznie, a moc oblicz dopiero z wyniku końcowego.",
            ),
        ),
    ),
    CardSet(
        "Źródła zależne i rezystancja widziana",
        (
            make_card(
                9, "zależne",
                "Co robisz ze źródłem zależnym podczas superpozycji?",
                "Pozostawiasz je aktywne. W każdym przypadku cząstkowym przeliczasz jego wartość z aktualnej wielkości sterującej, np. napięcia lub prądu.",
            ),
            make_card(
                10, "zależne",
                "Dlaczego źródła zależnego nie wolno wyzerować jak niezależnego?",
                "Jego wartość jest częścią równania obwodu i zależy od innej wielkości w układzie. Wyłączenie źródła usuwa tę zależność i zmienia badany obwód.",
            ),
            make_card(
                11, "zależne",
                "Jak wyznaczyć R_w, jeśli obwód zawiera źródło zależne?",
                "Wyzeruj źródła niezależne, pozostaw zależne aktywne i przyłóż źródło testowe. Przy zgodnych zwrotach U_x i I_x: R_w=U_x/I_x.",
            ),
            make_card(
                12, "zależne",
                "Jak znaleźć R_w, gdy w obwodzie są tylko źródła niezależne?",
                "Wyzeruj je: idealne E zastąp zwarciem, a idealne J — rozwarciem. Następnie oblicz rezystancję widzianą z badanego portu.",
            ),
        ),
    ),
    CardSet(
        "Równoważniki Thévenina i Nortona",
        (
            make_card(
                13, "Thévenin · Norton",
                "Czym jest napięcie Thévenina E_T?",
                "To napięcie jałowe między zaciskami portu: U_AB przy odłączonym obciążeniu. Zapisz przyjętą biegunowość.",
            ),
            make_card(
                14, "Thévenin · Norton",
                "Czym jest prąd Nortona J_N?",
                "To prąd płynący w zewnętrznym zwarciu zacisków portu. Zawsze określ jego zwrot odniesienia i zachowaj znak wyniku.",
            ),
            make_card(
                15, "Thévenin · Norton",
                "Jak sprawdzić, czy równoważniki Thévenina i Nortona są spójne?",
                "Sprawdź E_T=J_N·R_w przy zgodnych biegunowościach i zwrotach. Oba modele muszą mieć to samo R_w i przewidywać te same napięcia oraz prądy obciążenia.",
            ),
            make_card(
                16, "Thévenin · Norton",
                "Jeśli U_AB=V_A−V_B>0 i R_w>0, w którą stronę rysujesz strzałkę źródła Nortona?",
                "Strzałka źródła Nortona wskazuje B→A. Prąd w zewnętrznym zwarciu płynie przeciwnie — od A do B.",
            ),
        ),
    ),
    CardSet(
        "Obciążenie i interpretacja znaków",
        (
            make_card(
                17, "obciążenie",
                "Czy E_T jest napięciem na zaciskach przy dołączonym R_L?",
                "Nie. E_T to napięcie jałowe. Aby je wyznaczyć, odłącz R_L; po ponownym dołączeniu obciążenia napięcie zaciskowe na ogół się zmieni.",
            ),
            make_card(
                18, "obciążenie",
                "Jak obliczyć napięcie U_L na R_L z równoważnika Thévenina?",
                "Dołącz R_L do źródła E_T z szeregowym R_w i użyj dzielnika: U_L=E_T·R_L/(R_w+R_L), przy zgodnej biegunowości napięć.",
            ),
            make_card(
                19, "znaki",
                "Obliczono I=−2 mA, a strzałkę przyjęto od A do B. Co oznacza wynik?",
                "Rzeczywisty prąd ma wartość 2 mA i płynie od B do A — przeciwnie do strzałki odniesienia. Nie usuwaj minusa w trakcie rachunków.",
            ),
            make_card(
                20, "znaki",
                "Jeśli U_AB=V_A−V_B=−3 V, który zacisk ma niższy potencjał?",
                "Zacisk A ma potencjał o 3 V niższy niż B. Ujemny znak informuje o relacji do przyjętej biegunowości.",
            ),
        ),
    ),
    CardSet(
        "Rachunek i kontrola wyniku",
        (
            make_card(
                21, "rachunek",
                "Dane: E_T=−10 V, R_w=2 kΩ. Oblicz J_N i zinterpretuj znak.",
                "J_N=E_T/R_w=−10 V/2 kΩ=−5 mA. Minus oznacza zwrot przeciwny do przyjętego zwrotu prądu Nortona.",
            ),
            make_card(
                22, "rachunek",
                "Dwa rezystory R₁ i R₂ są szeregowo pod napięciem U. Jak obliczyć spadek U₁ na R₁?",
                "U₁=U·R₁/(R₁+R₂). W szeregu napięcie dzieli się proporcjonalnie do rezystancji.",
            ),
            make_card(
                23, "rachunek",
                "Jakie dwie skrócone równości pomagają kontrolować jednostki?",
                "1 kΩ·1 mA=1 V oraz 1 mS·1 V=1 mA. Sprowadzaj jednostki przed mnożeniem lub dzieleniem.",
            ),
            make_card(
                24, "rachunek",
                "Jakie kontrole wykonujesz przed oddaniem rozwiązania?",
                "Sprawdź KCL w węzłach i KVL w oczkach, jednostki, znaki i kierunki odniesienia. Jeśli wyznaczono oba modele źródłowe, sprawdź też E_T=J_N·R_w.",
            ),
        ),
    ),
)


def validate_deck():
    cards = [card for group in CARD_SETS for card in group.cards]
    assert len(cards) == TOTAL_CARDS
    assert [card.number for card in cards] == list(range(1, TOTAL_CARDS + 1))
    assert all(len(group.cards) == CARDS_PER_SHEET for group in CARD_SETS)
    assert len(CARD_SETS) == TOTAL_SHEETS


def _paragraph(text, style, max_width, max_height, card_no, face):
    para = Paragraph(escape(text), style)
    width, height = para.wrap(max_width, max_height)
    if width > max_width + 0.1 or height > max_height + 0.1:
        raise ValueError(
            f"Card {card_no} {face} does not fit: {width:.1f}×{height:.1f} "
            f"in {max_width:.1f}×{max_height:.1f} pt"
        )
    return para, height


def draw_card(c, x, y, card: FlashCard, face: str):
    """Draw one question or answer card inside the same physical cut area."""
    c.saveState()
    c.setFillColor(WHITE)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.75)
    c.setDash(3, 2)
    c.rect(x, y, CARD_W, CARD_H, fill=1, stroke=1)
    c.setDash()

    accent = card.accent
    c.setFillColor(accent)
    c.rect(x, y + CARD_H - 4, CARD_W, 4, fill=1, stroke=0)

    # Number badge and topic label appear on both sides for easy matching.
    badge_x, badge_y = x + 19, y + CARD_H - 22
    c.setFillColor(accent)
    c.circle(badge_x, badge_y, 9, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("DejaVu-Bold", 7.3)
    c.drawCentredString(badge_x, badge_y - 2.5, f"{card.number:02d}")

    c.setFillColor(accent)
    c.setFont("DejaVu-Bold", 7.0)
    c.drawRightString(x + CARD_W - 13, badge_y - 2.2, card.category.upper())
    c.setStrokeColor(LINE)
    c.setLineWidth(0.6)
    c.line(x + 12, y + CARD_H - 38, x + CARD_W - 12, y + CARD_H - 38)

    body_x = x + 15
    body_w = CARD_W - 30
    body_bottom = y + 48
    body_top = y + CARD_H - 51
    body_h = body_top - body_bottom

    if face == "question":
        text = card.question
        style = QUESTION_STYLE
    else:
        text = card.answer
        style = ANSWER_STYLE

    para, text_h = _paragraph(text, style, body_w, body_h, card.number, face)
    text_y = body_bottom + (body_h - text_h) / 2
    para.drawOn(c, body_x, text_y)

    c.setFillColor(MUTED)
    c.setFont("DejaVu", 6.5)
    if face == "question":
        c.drawCentredString(x + CARD_W / 2, y + 17, "ODPOWIEDZ Z PAMIĘCI, ZANIM SPRAWDZISZ REWERS")
    else:
        c.drawCentredString(x + CARD_W / 2, y + 17, "SPRAWDŹ ROZUMOWANIE I ZWROTY, NIE TYLKO WYNIK")
    c.restoreState()


def draw_page_header(c, side: str, set_no: int, set_title: str):
    c.saveState()
    c.setFillColor(NAVY)
    c.setFont("DejaVu-Bold", 7.6)
    c.drawString(MARGIN_X, PAGE_H - 24, "PLP K1  ·  POWTÓRKA DO KOLOKWIUM")
    c.setFillColor(MUTED)
    c.setFont("DejaVu", 7.1)
    c.drawRightString(PAGE_W - MARGIN_X, PAGE_H - 24, f"ZESTAW {set_no:02d}/{TOTAL_SHEETS:02d}")

    c.setFillColor(NAVY)
    if side == "question" and set_no == 1:
        c.setFont("DejaVu-Bold", 17)
        c.drawString(MARGIN_X, PAGE_H - 49, "Fiszki do samosprawdzania")
        c.setFillColor(INK)
        c.setFont("DejaVu", 8.0)
        c.drawString(MARGIN_X, PAGE_H - 64, "24 karty · odpowiedz z pamięci, zanim sprawdzisz drugą stronę.")
        c.setFillColor(MUTED)
        c.setFont("DejaVu", 7.0)
        c.drawString(MARGIN_X, PAGE_H - 78, "Druk dwustronny: skala 100%, obrót po długiej krawędzi; potnij po przerywanych ramkach.")
        c.drawString(MARGIN_X, PAGE_H - 90, "Rewersy są odbite lustrzanie do druku — w PDF dopasuj odpowiedź po numerze karty.")
    elif side == "question":
        c.setFont("DejaVu-Bold", 13.2)
        c.drawString(MARGIN_X, PAGE_H - 49, set_title)
        c.setFillColor(INK)
        c.setFont("DejaVu", 7.7)
        c.drawString(MARGIN_X, PAGE_H - 66, "PYTANIA  ·  Przypomnij odpowiedź z pamięci, zanim odwrócisz stronę.")
    else:
        c.setFont("DejaVu-Bold", 13.2)
        c.drawString(MARGIN_X, PAGE_H - 49, f"Rewersy · {set_title}")
        c.setFillColor(INK)
        c.setFont("DejaVu", 7.6)
        c.drawString(MARGIN_X, PAGE_H - 66, "ODPOWIEDZI  ·  Kolumny lustrzane do druku dwustronnego; dopasuj po numerze.")

    c.setStrokeColor(LINE)
    c.setLineWidth(0.6)
    c.line(MARGIN_X, PAGE_H - 96, PAGE_W - MARGIN_X, PAGE_H - 96)
    c.restoreState()


def draw_footer(c, page_no: int, side: str):
    c.saveState()
    c.setStrokeColor(LINE)
    c.setLineWidth(0.6)
    c.line(MARGIN_X, 24, PAGE_W - MARGIN_X, 24)
    c.setFont("DejaVu", 6.8)
    c.setFillColor(MUTED)
    label = "pytania" if side == "question" else "odpowiedzi"
    c.drawString(MARGIN_X, 13, f"PLP K1 · Fiszki do samosprawdzania · {label}")
    c.drawRightString(PAGE_W - MARGIN_X, 13, f"str. {page_no}/{TOTAL_SHEETS * 2}")
    c.restoreState()


def draw_sheet(c, group: CardSet, set_no: int, side: str, page_no: int):
    draw_page_header(c, side, set_no, group.title)
    if side == "question":
        display_cards = list(group.cards)
    else:
        # A portrait sheet flipped on its long (vertical) edge swaps left/right.
        # Mirror each row so every answer lands behind its matching question.
        display_cards = []
        for row in range(ROWS):
            row_cards = group.cards[row * COLS : (row + 1) * COLS]
            display_cards.extend(reversed(row_cards))

    for index, card in enumerate(display_cards):
        row, col = divmod(index, COLS)
        x = MARGIN_X + col * (CARD_W + GAP_X)
        y = GRID_TOP - (row + 1) * CARD_H - row * GAP_Y
        draw_card(c, x, y, card, side)

    draw_footer(c, page_no, side)

    label = "pytania" if side == "question" else "odpowiedzi"
    dest = f"set_{set_no:02d}_{label}"
    c.bookmarkPage(dest)
    c.addOutlineEntry(f"Zestaw {set_no}: {group.title} — {label}", dest, level=0, closed=False)
    c.showPage()


def main():
    validate_deck()
    c = pdfcanvas.Canvas(str(OUTPUT), pagesize=A4, pageCompression=1)
    c.setTitle("PLP K1 — fiszki do samosprawdzania")
    c.setAuthor("Opracowanie własne")
    c.setSubject("Fiszki o analizie obwodów: topologia, źródła, Thévenin, Norton i znaki")
    c.setKeywords("PLP K1, fiszki, samosprawdzanie, superpozycja, Thévenin, Norton, źródła")

    page_no = 1
    for set_no, group in enumerate(CARD_SETS, start=1):
        draw_sheet(c, group, set_no, "question", page_no)
        page_no += 1
        draw_sheet(c, group, set_no, "answer", page_no)
        page_no += 1

    c.save()
    print(f"Zapisano: {OUTPUT}")


if __name__ == "__main__":
    main()
