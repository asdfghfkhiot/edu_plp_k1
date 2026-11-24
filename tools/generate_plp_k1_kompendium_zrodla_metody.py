#!/usr/bin/env python3
"""Generate a comprehensive Polish compendium on dependent sources and circuit methods.

Requires ReportLab and the DejaVu fonts used by generate_plp_k1_guide.py.
Run from the repository root:
    python tools/generate_plp_k1_kompendium_zrodla_metody.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import NextPageTemplate, PageBreak, Spacer

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "PLP_K1_kompendium_zrodla_sterowane_i_metody.pdf"
sys.path.insert(0, str(ROOT))

from tools import generate_plp_k1_metody_analizy as common  # noqa: E402
from tools import generate_plp_k1_szybkie_metody as quick  # noqa: E402
from tools import generate_plp_k1_zrodla_sterowane as dependent  # noqa: E402

base = common.base
PAGE_W, PAGE_H = common.PAGE_W, common.PAGE_H
LEFT, RIGHT, TOP, BOTTOM = common.LEFT, common.RIGHT, common.TOP, common.BOTTOM
CONTENT_W = common.CONTENT_W
NAVY, TEAL, TEAL_DARK = common.NAVY, common.TEAL, common.TEAL_DARK
GOLD, INK, MUTED, LINE, WHITE = common.GOLD, common.INK, common.MUTED, common.LINE, common.WHITE


class CompendiumDocTemplate(common.GuideDocTemplate):
    def draw_cover(self, canvas, doc):
        canvas.saveState()
        canvas.setFillColor(colors.HexColor("#F7FAFC"))
        canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        canvas.setFillColor(NAVY)
        canvas.rect(0, PAGE_H - 108 * mm, PAGE_W, 108 * mm, fill=1, stroke=0)
        canvas.setFillColor(TEAL)
        canvas.rect(0, PAGE_H - 111 * mm, PAGE_W, 3 * mm, fill=1, stroke=0)
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
        canvas.drawString(LEFT + 7 * mm, 43 * mm, "KOMPENDIUM • PLP K1")
        canvas.drawString(LEFT + 7 * mm, 34 * mm, "Teoria, metody, przykłady i zadania kontrolne")
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
        canvas.drawString(LEFT, PAGE_H - 7.5 * mm, "PLP K1  ·  OBWODY LINIOWE")
        canvas.setFont("DejaVu", 7.2)
        canvas.setFillColor(MUTED)
        canvas.drawRightString(PAGE_W - RIGHT, PAGE_H - 7.5 * mm, "Źródła sterowane i metody")
        canvas.line(LEFT, 10 * mm, PAGE_W - RIGHT, 10 * mm)
        canvas.setFont("DejaVu", 7.2)
        canvas.setFillColor(MUTED)
        canvas.drawString(LEFT, 6.5 * mm, "Źródło zależne pozostaje częścią równań obwodu.")
        canvas.drawRightString(PAGE_W - RIGHT, 6.5 * mm, f"str. {doc.page}")
        canvas.restoreState()


def P(text, style="BodyPL"):
    return base.P(text, style)


def build_story():
    story = [
        Spacer(1, 24 * mm),
        P("KOMPENDIUM ANALIZY OBWODÓW · PLP K1", "CoverKicker"),
        P("Źródła sterowane i metody pracy z obwodami", "CoverTitle"),
        P("Od praw Kirchhoffa i zwrotów odniesienia do superpozycji, modeli portu i źródeł testowych", "CoverSub"),
        Spacer(1, 9 * mm),
        base.callout(
            "Zakres i sposób korzystania",
            "Kompletny przewodnik po liniowych obwodach rezystancyjnych prądu stałego ze szczególnym naciskiem na źródła sterowane. Zawiera algorytmy, przykłady obliczeniowe, skróty, warunki ich stosowania i zadania z odpowiedziami.",
        ),
        Spacer(1, 6 * mm),
        P("Najważniejsza reguła: najpierw zdefiniuj napięcie lub prąd sterujący oraz zwrot źródła, potem wpisz zależność do KCL/KVL. Źródeł zależnych nie wyłącza się przy superpozycji ani przy liczeniu rezystancji Thévenina.", "CoverMeta"),
        NextPageTemplate("Body"),
        PageBreak(),

        base.H1("Mapa kompendium i wybór metody"),
        P("Materiał dotyczy głównie obwodów liniowych DC: rezystorów, niezależnych źródeł oraz źródeł zależnych. W obwodach AC te same zasady KCL/KVL stosuje się w zapisie zespolonym, zastępując rezystancje impedancjami."),
        base.info_table([
            ["Sytuacja", "Dobry punkt startu", "Uważaj na"],
            ["Prosty szereg/równoległość", "Redukcja i prawo Ohma", "Odgałęzienie w węźle pozornie szeregowym"],
            ["Mało nieznanych węzłów", "Metoda węzłowa; dla jednego węzła Millman", "Źródło napięcia między dwoma nieznanymi węzłami"],
            ["Mało oczek, obwód planarny", "Metoda oczkowa", "Źródło prądowe między oczkami"],
            ["Wiele źródeł niezależnych", "Superpozycja dla liniowego obwodu", "Źródła zależne zostają aktywne"],
            ["Port A–B i obciążenie", "Thévenin/Norton", "Przy źródle zależnym użyj źródła testowego do R_T"],
            ["Mostek lub układ symetryczny", "Sprawdź równe potencjały i równowagę", "Nie pomijaj gałęzi poprzecznej bez dowodu"],
        ], [42 * mm, 61 * mm, CONTENT_W - 103 * mm]),
        base.H2("Notacja używana dalej"),
        base.bullet("U_AB=V_A−V_B; dodatnie napięcie oznacza, że A ma wyższy potencjał niż B."),
        base.bullet("Strzałka prądu jest dodatnim zwrotem odniesienia; wynik ujemny oznacza przepływ przeciwny."),
        base.bullet("E, J oznaczają źródła niezależne; u_d, i_d — wielkości wyjściowe źródła zależnego."),
        base.bullet("u_x i i_x to jawnie zdefiniowane wielkości sterujące; zwrot i biegunowość mają znaczenie."),
        base.eqbox("Szybkie jednostki: kΩ·mA=V; mS·V=mA; Ω·A=V; 1 S=1 A/V."),
        PageBreak(),

        base.H1("1. Cztery typy źródeł sterowanych"),
        P("Źródło sterowane (zależne) jest idealnym źródłem, którego wartość określa inna wielkość obwodu. Na schemacie zwykle ma symbol rombu. Współczynnik sterujący może być dodatni, ujemny albo zależny od częstotliwości w modelu AC."),
        base.info_table([
            ["Typ", "Pełna nazwa", "Prawo źródła", "Jednostka współczynnika"],
            ["VCVS", "Napięciowe sterowane napięciem", "u_d=μu_x", "μ: V/V, bezwymiarowy"],
            ["VCCS", "Prądowe sterowane napięciem", "i_d=gu_x", "g: A/V=S"],
            ["CCCS", "Prądowe sterowane prądem", "i_d=βi_x", "β: A/A, bezwymiarowy"],
            ["CCVS", "Napięciowe sterowane prądem", "u_d=ri_x", "r: V/A=Ω"],
        ], [19 * mm, 52 * mm, 42 * mm, CONTENT_W - 113 * mm]),
        base.H2("Jak czytać równanie źródła"),
        P("Najpierw określ wyjście źródła: jego napięcie między zaciskami albo prąd wzdłuż strzałki. Potem określ wielkość sterującą. Jeśli dodatni zwrot sterowania i dodatni zwrot wyjścia są zgodne z definicją współczynnika, użyj znaku plus; odwrócenie jednego zwrotu zmienia znak zależności."),
        base.eqbox("Przykład VCCS: u_x=V_A−V_B.\nStrzałka i_d od A do B:  i_d=g u_x.\nStrzałka i_d od B do A przy tym samym u_x:  i_d=−g u_x."),
        base.H2("Co źródło zależne może modelować?"),
        base.P("To model wzmacniacza, tranzystora w przybliżeniu małosygnałowym, przetwornika lub sprzężenia między częścią sterującą a wyjściową. Źródło zależne może pobierać lub dostarczać moc; nie jest z definicji elementem pasywnym."),
        base.callout("Nie myl typu źródła z jego kontrolą", "VCCS jest źródłem prądu, ale steruje nim napięcie. CCVS jest źródłem napięcia, ale steruje nim prąd."),
        PageBreak(),

        base.H1("2. Zwroty, prawa obwodu i moc"),
        base.H2("Zwroty odniesienia"),
        P("Dla każdego nieznanego prądu wybierz strzałkę. Dla każdego napięcia określ bieguny albo jawnie zdefiniuj U_AB=V_A−V_B. Przy rezystorze najwygodniejsza jest konwencja pasywna: prąd wpływa do dodatniego zacisku napięcia."),
        base.eqbox("Konwencja pasywna:  u=Ri,  p_pobierana=ui≥0.\nJeśli odniesienia u i i są przeciwne:  u=−Ri,  p_pobierana=−ui."),
        base.H2("Prawa Kirchhoffa"),
        base.info_table([
            ["Prawo", "Zapis", "Wskazówka znakowa"],
            ["KCL — prądowe", "Suma algebraiczna prądów w węźle = 0", "Wybierz wszystkie wypływające lub wpływające; przeciwne zwroty mają minus."],
            ["KVL — napięciowe", "Suma algebraiczna napięć w zamkniętym obiegu = 0", "Dla strzałek spadku zgodny obieg to +u, przeciwny to −u."],
        ], [30 * mm, 58 * mm, CONTENT_W - 88 * mm]),
        base.H2("Źródła i znak mocy"),
        P("Dla źródła napięcia E biegunowość określa E=V_+−V_−. Strzałka źródła prądu określa dodatni zwrot J. Jeśli prąd źródła wpływa do jego zacisku dodatniego, źródło pobiera moc według konwencji pasywnej; jeśli wypływa z zacisku dodatniego, dostarcza moc."),
        base.P("Wartość ujemna prądu lub napięcia nie oznacza błędu. Oznacza, że wielkość fizyczna ma zwrot przeciwny do przyjętego odniesienia. Nie zmieniaj po cichu strzałek w trakcie rachunku."),
        base.callout("Kontrola jednostek", "Dla i_d=gu_x współczynnik g ma jednostkę siemensa. Dla u_d=ri_x współczynnik r ma omy. Współczynniki μ i β są bezwymiarowe."),
        PageBreak(),

        base.H1("3. Uniwersalny algorytm i równania źródeł"),
        base.info_table([
            ["Krok", "Działanie"],
            ["1. Topologia", "Zidentyfikuj węzły, gałęzie, zaciski źródeł i węzeł odniesienia."],
            ["2. Niewiadome", "Wybierz napięcia węzłowe albo prądy oczkowe; dodaj prądy idealnych źródeł napięcia, jeśli używasz MNA."],
            ["3. Sterowanie", "Zaznacz u_x/i_x i zapisz równanie źródła ze znakiem wynikającym ze zwrotów."],
            ["4. Kirchhoff", "Napisz KCL/KVL; prądy przez rezystory wyraź przez różnice potencjałów."],
            ["5. Rozwiązanie", "Rozwiąż układ liniowy, odczytaj szukaną wielkość i wróć do pierwotnego schematu."],
            ["6. Kontrola", "Sprawdź KCL/KVL, jednostki, znak, równanie sterujące i sens graniczny."],
        ], [28 * mm, CONTENT_W - 28 * mm]),
        base.H2("Jak źródła pojawiają się w metodach"),
        base.info_table([
            ["Rodzaj źródła", "Metoda węzłowa", "Metoda oczkowa / MNA"],
            ["VCCS / CCCS", "Wartość prądu trafia do KCL; wyraź sterowanie przez węzły lub prądy gałęzi.", "Prąd źródła tworzy więzy, a źródło między oczkami może wymagać superoczka."],
            ["VCVS / CCVS", "Różnica potencjałów jest warunkiem; superwęzeł lub dodatkowy prąd w MNA.", "Napięcie zależne wchodzi do KVL jako wyrażenie w wielkości sterującej."],
        ], [31 * mm, (CONTENT_W - 31 * mm) / 2, (CONTENT_W - 31 * mm) / 2]),
        base.H2("MNA — analiza węzłowa ze źródłami napięcia"),
        P("Modified Nodal Analysis rozszerza KCL o dodatkowe niewiadome: prądy idealnych źródeł napięcia. Do układu dodaje się równanie biegunowości źródła. Dla VCVS między A i B sterowanej napięciem u_x:"),
        base.eqbox("V_A−V_B−μu_x=0.\nPrąd przez idealne źródło napięcia jest osobną niewiadomą; KCL zapisuje się w węzłach, do których źródło jest dołączone."),
        base.callout("Zależność zapisz raz, lecz użyj wszędzie", "Jeśli i_x jest prądem gałęzi, wyraź go z prawa Ohma albo z KCL. Nie traktuj i_x jak kolejnego niezależnego źródła."),
        PageBreak(),

        base.H1("4. Metoda węzłowa z VCCS"),
        P("Metoda węzłowa jest zwykle wygodna, gdy źródła zależne są prądowe albo gdy napięcie sterujące jest różnicą potencjałów. Prąd rezystora od a do b to (V_a−V_b)/R."),
        dependent.VCCSNetworkDiagram(independent_current=False, port=False),
        base.H2("Przykład VCCS: rezystor i źródło g·u_X"),
        P("E=12 V, R₁=3 kΩ, R₂=6 kΩ, VCCS g·u_X skierowana w dół, g=0,5 mS, u_X=V_X względem masy. Szukamy V_X."),
        base.eqbox("KCL — prądy wypływające z X:\n(V_X−12)/3 kΩ + V_X/6 kΩ + gV_X = 0.\nW mA: (V_X−12)/3 + V_X/6 + 0,5V_X=0  ⇒  V_X=4 V.\ni_g=0,5 mS·4 V=2 mA w dół."),
        base.H2("Kontrola"),
        P("Prąd R₁ wypływający z X: (4−12)/3=−2,67 mA. Prąd R₂: 4/6=0,67 mA. VCCS: 2 mA. Suma −2,67+0,67+2=0 mA."),
        base.callout("Znak zależy od przyjętej strzałki", "Gdyby strzałka VCCS była skierowana do X przy tej samej definicji u_X, wkład w sumie prądów wypływających miałby znak −gV_X."),
        base.H2("Zapis macierzowy"),
        P("Dla wielu węzłów VCCS dodaje składnik transkonduktancji do macierzy konduktancyjnej. Jeśli i_d=g(V_c−V_d) płynie od a do b, jego wkład do KCL w a jest dodatni, a w b ujemny; po rozwinięciu pojawiają się wyrazy gV_c i gV_d."),
        PageBreak(),

        base.H1("5. CCCS, CCVS i prąd sterujący"),
        P("W źródłach sterowanych prądem szczególnie ważne jest zdefiniowanie i_x. W metodzie oczkowej i_x może być prądem oczka albo różnicą dwóch prądów oczkowych; w metodzie węzłowej można wyrazić go przez napięcia na rezystorze."),
        dependent.CCCSDiagram(),
        base.H2("CCCS: i_d=βi_x"),
        P("E=10 V, R₁=2 kΩ, R₂=4 kΩ, β=0,5. i_x płynie przez R₁ od źródła do X; źródło βi_x wypływa z X do masy."),
        base.eqbox("i_x=(10−V_X)/2 kΩ. KCL w X:\n(V_X−10)/2 kΩ + V_X/4 kΩ + 0,5(10−V_X)/2 kΩ=0.\nV_X=5 V; i_x=2,5 mA; i_d=1,25 mA; I_R₂=1,25 mA."),
        base.P("Kontrola: przez R₁ do X wpływa 2,5 mA, a z X wypływa 1,25+1,25=2,5 mA.", "SmallPL"),
        base.H2("CCVS: u_d=ri_x w prostym oczku"),
        dependent.CCVSSeriesDiagram(),
        P("Jeśli i_x jest prądem całego oczka, źródło ma biegunowość spadku zgodną z obiegiem, a E=12 V, R=2 kΩ, r=1 kΩ:"),
        base.eqbox("E−RI−rI=0  ⇒  I=E/(R+r)=4 mA;   u_d=rI=4 V."),
        base.callout("To nie jest uniwersalny wzór na każde CCVS", "Uproszczenie R+r działa tylko dlatego, że i_x=I i biegunowość źródła zależnego jest zgodna ze spadkiem w oczku. Przy innym i_x lub zwrocie wróć do pełnego KVL." , "warn"),
        PageBreak(),

        base.H1("6. VCVS i superwęzeł"),
        P("Idealne źródło napięcia zależnego między dwoma nieznanymi węzłami narzuca warunek różnicy potencjałów. Nie da się go zastąpić zwykłym prądem (V_A−V_B)/R. Obejmij źródło i oba zaciski superwęzłem."),
        dependent.VCVSSupernodeDiagram(),
        base.H2("Przykład VCVS: superwęzeł A–B"),
        P("Źródło sterujące ustala V_C=4 V. VCVS ma zależność V_A−V_B=2V_C i plus przy A. Rezystory R_A=R_B=2 kΩ łączą A oraz B z masą."),
        base.eqbox("Warunek źródła: V_A−V_B=2·4=8 V.\nKCL superwęzła A–B: V_A/2 kΩ + V_B/2 kΩ=0  ⇒  V_A+V_B=0.\nV_A=4 V, V_B=−4 V."),
        P("Jeśli potrzebny jest prąd źródła, dopisz KCL dla jednego z węzłów albo użyj MNA. Przy I_s od A do B: V_A/R_A+I_s=0, więc I_s=−2 mA — rzeczywisty kierunek jest B→A.", "SmallPL"),
        base.H2("VCVS w metodzie oczkowej"),
        P("Jeśli źródło VCVS leży w pojedynczym oczku, w KVL wpisz jego napięcie jako μu_x ze znakiem wynikającym z biegunowości i kierunku obiegu. Jeśli źródło łączy dwa nieznane węzły, użyj superwęzła w metodzie węzłowej albo dodatkowego równania w MNA."),
        base.callout("Sprawdź kolejność biegunów", "Równanie V_A−V_B=μu_x zakłada plus przy A i minus przy B. Odwrócenie biegunów zmienia znak lewej strony lub współczynnika." , "warn"),
        PageBreak(),

        base.H1("7. Metoda oczkowa ze źródłami zależnymi"),
        P("Metoda oczkowa wymaga obwodu planarnego. Prądy oczek można przyjąć wszystkie zgodnie z ruchem wskazówek zegara. Prąd w gałęzi wspólnej jest algebraiczną różnicą prądów oczkowych."),
        common.MeshExampleDiagram(),
        base.eqbox("Dla rezystora R₃ wspólnego dla oczek 1 i 2, przy obu prądach zgodnych z ruchem wskazówek zegara:\nI₃=I₁−I₂ w dół. Spadek w równaniu oczka 1: R₃(I₁−I₂); w oczku 2: R₃(I₂−I₁)."),
        base.H2("Jak wstawić źródło sterowane"),
        base.info_table([
            ["Źródło", "W równaniach oczkowych"],
            ["VCVS / CCVS", "Wpisz napięcie źródła do KVL, np. μu_x albo ri_x. Wyraź sterowanie przez prądy oczek lub napięcia gałęzi."],
            ["VCCS / CCCS na brzegu oczka", "Prąd oczkowy jest związany z wartością źródła; dopisz równanie sterujące i pilnuj zwrotu."],
            ["Źródło prądu między oczkami", "Utwórz superoczko: pomiń wewnętrzną gałąź w KVL po obrysie i dodaj więz, np. I₁−I₂=βi_x."],
        ], [45 * mm, CONTENT_W - 45 * mm]),
        base.H2("Macierz oczkowa"),
        P("Dla sieci rezystancyjnej współczynniki diagonalne są sumami rezystancji w oczku; pozadiagonalne to minus rezystancja gałęzi wspólnych. Źródła sterowane mogą wprowadzić dodatkowe składniki poza macierzą rezystancyjną — przenieś je na właściwą stronę lub uwzględnij jako sprzężenie między niewiadomymi."),
        base.callout("Kiedy metoda węzłowa będzie prostsza?", "Jeśli schemat ma dużo źródeł prądu, dużo nieznanych prądów sterujących albo nie jest planarny, zwykle szybciej ułożyć KCL i rozwiązać metodą węzłową/MNA."),
        PageBreak(),

        base.H1("8. Superpozycja — źródła zależne zostają"),
        P("Superpozycja działa dla liniowych obwodów z kilkoma źródłami niezależnymi. Wyznacza się osobny wkład każdego źródła niezależnego do tej samej wielkości, a następnie dodaje wkłady algebraicznie."),
        dependent.VCCSNetworkDiagram(independent_current=True),
        base.P("Dane: E=12 V, R₁=3 kΩ, R₂=6 kΩ, J=1 mA do węzła X, VCCS gV_X=0,5 mS·V_X w dół. Z KCL dla całego układu otrzymuje się V_X=5 V."),
        base.H2("Wkład źródła E"),
        base.P("Źródło J zastępujemy rozwarciem. VCCS pozostaje aktywna:"),
        base.eqbox("(V_X−12)/3 + V_X/6 + 0,5V_X=0  ⇒  V_X,E=4 V."),
        base.H2("Wkład źródła J"),
        base.P("Idealne źródło E zastępujemy zwarciem. VCCS nadal zależy od V_X:"),
        base.eqbox("V_X/3 + V_X/6 + 0,5V_X − 1=0  ⇒  V_X,J=1 V.\nSuma: V_X=V_X,E+V_X,J=4+1=5 V."),
        base.callout("Reguła nie do negocjacji", "Nie wyłączaj źródła zależnego w podproblemie superpozycji. Jego wartość w każdym przypadku oblicza się z aktualnej wielkości sterującej. Nie dodawaj mocy z poszczególnych wkładów." , "warn"),
        PageBreak(),

        base.H1("9. Skróty: redukcje, dzielniki i Millman"),
        base.H2("Połączenia i dzielniki"),
        base.eqbox("Szeregowo: R_z=ΣR.     Równolegle: G_z=ΣG, czyli 1/R_z=Σ(1/R).\nDzielnik napięcia: U₂=E·R₂/(R₁+R₂). Przy obciążeniu: R₂*=R₂∥R_L, użyj R₂* zamiast R₂.\nDzielnik prądu: I_k=I·G_k/ΣG; dla dwóch gałęzi I₁=I·R₂/(R₁+R₂)."),
        P("Przy dzielnikach rozstrzygają węzły, nie geometria rysunku. Jeśli obciążenie dołącza dodatkową gałąź do węzła wyjściowego, nie używaj nieobciążonego dzielnika."),
        base.H2("Wzór Millmana dla jednego węzła"),
        base.eqbox("V_X=[Σ(G_kE_k)+ΣJ_do_X−ΣJ_z_X]/ΣG_k,   gdzie G_k=1/R_k.\nE_k to znane potencjały drugich końców gałęzi; prądy do węzła mają znak plus."),
        P("Przykład: do X prowadzą E₁=15 V przez 3 kΩ i masa przez 3 kΩ; J=1 mA wpływa do X. V_X=[15/3+0/3+1]/[1/3+1/3]=9 V. To skrócony zapis KCL, a nie nowa zasada."),
        P("VCCS sterowana napięciem tego samego węzła można włączyć algebraicznie do konduktancji: strzałka gV_X wypływająca z X dodaje +g do mianownika, a strzałka skierowana do X daje składnik −g. Dla sterowania napięciem innego węzła zapisz pełne KCL lub macierz."),
        base.callout("Millman nie zastępuje superwęzła", "Używaj go, gdy rozpatrujesz jeden nieznany węzeł, a potencjały po drugiej stronie gałęzi są znane. Idealne źródło napięcia między dwoma nieznanymi węzłami wymaga superwęzła lub MNA." , "warn"),
        PageBreak(),

        base.H1("10. Symetria, mostki i zamiana źródeł"),
        P("W mostku Wheatstone’a gałąź poprzeczna nie przewodzi, jeśli jej końce mają ten sam potencjał. Warunek można sprawdzić przez dwa dzielniki napięcia."),
        quick.BalancedBridgeDiagram(),
        base.eqbox("Warunek równowagi: R₁/R₂=R₃/R₄. Wtedy V_L=V_R, U_b=0 i I_b=0; wartość skończonego R_b nie zmienia równowagi.\nPrzykład z rysunku: lewa gałąź 6 kΩ, prawa 9 kΩ; przy 18 V obydwa środki mają 12 V. R_zast=6∥9=3,6 kΩ."),
        base.H2("Zamiana źródeł"),
        base.eqbox("E szeregowo z R  ⇔  J=E/R równolegle z tym samym R.\nJeżeli biegun + źródła E jest przy A, strzałka źródła Norton w równoważniku jest B→A."),
        P("Przykład: E=12 V, R=3 kΩ daje J=4 mA. Dla R_L=6 kΩ model Thévenina daje I_L=12/(3+6)=1,33 mA; Norton daje I_L=4·3/(3+6)=1,33 mA."),
        base.callout("Warunek równoważności", "Zamiana zachowuje zależność napięcie–prąd widzianą z tych samych zacisków; nie usuwaj rezystora. Jeśli warunek równowagi mostka nie zachodzi, gałąź poprzeczna ma zwykle niezerowy prąd — użyj węzłów albo Δ–Y."),
        PageBreak(),

        base.H1("11. Thévenin i Norton przy źródle zależnym"),
        P("Równoważnik portu pozwala zamienić liniowy obwód widziany z A–B na E_T szeregowo z R_T albo J_N równolegle z tym samym R_T. Oba modele dają tę samą odpowiedź dla dowolnego obciążenia liniowego."),
        dependent.VCCSNetworkDiagram(independent_current=False, port=True),
        base.eqbox("E_T=U_oc.     J_N=I_sc (w zewnętrznym zwarciu A→B).\nR_T=R_N.     E_T=J_NR_T.     Jeśli w układzie są źródła zależne, R_T wyznacz przez źródło testowe."),
        base.H2("Przykład ze źródłem VCCS"),
        P("E=12 V, R₁=3 kΩ, R₂=6 kΩ, i_g=0,5 mS·U_AB skierowane A→B. Z otwartego portu z KCL wynika E_T=4 V."),
        base.H3("Źródło testowe 1 V"),
        P("Zerujemy tylko niezależne E, czyli zastępujemy je zwarciem. VCCS zostaje aktywna. Przykładamy U_t=1 V z plusem przy A:"),
        base.eqbox("I_t=1/3 kΩ + 1/6 kΩ + 0,5 mS·1 V=1 mA.\nR_T=U_t/I_t=1 kΩ;   J_N=E_T/R_T=4 mA, strzałka B→A.\nDla R_L=1 kΩ: I_L=4/(1+1)=2 mA, U_L=2 V."),
        base.callout("Nie wyłączaj źródła zależnego", "Gdyby pominąć VCCS, R_T wyszłoby 2 kΩ zamiast 1 kΩ. Źródło testowe mierzy zachowanie całego aktywnego dwójnika po wyzerowaniu wyłącznie źródeł niezależnych.", "warn"),
        base.H2("Kiedy R_T może być ujemne?"),
        P("Źródła zależne mogą dostarczać energię, więc port może wykazywać ujemną rezystancję małosygnałową. Ujemne R_T nie jest automatycznie błędem; sprawdź zwroty U_t/I_t oraz stabilność modelu i zakres jego ważności.", "SmallPL"),
        PageBreak(),

        base.H1("12. Kontrola, typowe błędy i zakres stosowalności"),
        base.info_table([
            ["Błąd", "Jak go wykryć lub poprawić"],
            ["Źródło zależne wyłączone", "Sprawdź superpozycję i R_T: źródła zależne zawsze pozostają aktywne."],
            ["Nieopisane u_x/i_x", "Dopisz biegunowość napięcia albo strzałkę prądu przed równaniem źródła."],
            ["Zły znak w KCL/KVL", "Dla rezystora użyj (V_a−V_b)/R zgodnie ze zwrotem; źródło wstaw z własnym znakiem."],
            ["Źródło napięcia w zwykłym KCL", "Utwórz superwęzeł albo użyj MNA z prądem źródła jako niewiadomą."],
            ["Dzielnik bez obciążenia", "Zastąp dolną gałąź przez R₂∥R_L przed użyciem wzoru."],
            ["Prąd Nortona odwrócony", "Oddziel strzałkę źródła B→A od prądu zewnętrznego zwarcia A→B."],
            ["Minus potraktowany jako błąd", "Zachowaj minus i opisz kierunek przeciwny do strzałki."],
        ], [48 * mm, CONTENT_W - 48 * mm]),
        base.H2("Końcowa lista kontrolna"),
        base.bullet("Czy wszystkie wielkości sterujące mają odniesienia i jednostki?"),
        base.bullet("Czy zależność źródła została wpisana do równań, a nie podstawiona jako stała?"),
        base.bullet("Czy wynik spełnia KCL/KVL oraz prawo źródła sterowanego?"),
        base.bullet("Czy zastosowany skrót spełnia wymagania topologiczne?"),
        base.bullet("Czy w modelu portu pozostawiłem źródła zależne aktywne?"),
        base.H2("Rozszerzenie na prąd przemienny"),
        P("W analizie sinusoidalnej w stanie ustalonym KCL/KVL nadal obowiązują, a liczby zastępuje się fazorami. Rezystor R uogólnia się do impedancji Z, a współczynniki źródeł sterowanych mogą zależeć od częstotliwości. Zasada zwrotów, aktywności źródeł zależnych i źródła testowego pozostaje taka sama.", "SmallPL"),
        base.callout("Gdy układ jest nieliniowy", "Superpozycja i proste modele Thévenina/Nortona obowiązują dla liniowego modelu. Dla diody lub tranzystora nieliniowego najpierw wyznacz punkt pracy albo zastosuj lokalny model małosygnałowy."),
        PageBreak(),

        base.H1("13. Zadania kontrolne"),
        P("Spróbuj rozwiązać bez zaglądania do odpowiedzi. Przyjmij podane zwroty; wyniki ujemne interpretuj jako kierunki przeciwne."),
        base.H2("A. VCCS w węźle"),
        P("E=15 V przez R₁=3 kΩ łączy źródło z X; R₂=6 kΩ łączy X z masą; VCCS i_g=0,5 mS·V_X jest skierowana z X do masy. Wyznacz V_X i i_g."),
        base.H2("B. CCCS sterowana prądem gałęzi"),
        P("E=12 V, R₁=3 kΩ do węzła X, R₂=6 kΩ do masy. Prąd i_X płynie przez R₁ do X, a źródło 0,5i_X wypływa z X. Wyznacz V_X, i_X i prąd źródła zależnego."),
        base.H2("C. VCVS i superwęzeł"),
        P("V_C=2 V. Źródło VCVS narzuca V_A−V_B=3V_C; R_A=R_B=4 kΩ łączą A i B z masą. Wyznacz V_A i V_B."),
        base.H2("D. Rezystancja portu ze źródłem zależnym"),
        P("Po wyzerowaniu źródeł niezależnych przykładasz U_t=1 V. Prąd testowy wpływający do aktywnego układu wynosi 0,75 mA. Wyznacz R_T. Czy źródło zależne powinno pozostać aktywne?"),
        base.callout("Wskazówka", "A–B: KCL z gV_X. C: KCL całego superwęzła plus warunek źródła. D: R_T=U_t/I_t."),
        PageBreak(),

        base.H1("Odpowiedzi do zadań kontrolnych"),
        base.H2("Odpowiedź A. VCCS w węźle"),
        base.eqbox("(V_X−15)/3 + V_X/6 + 0,5V_X=0  ⇒  V_X=5 V.\ni_g=0,5 mS·5 V=2,5 mA w dół."),
        base.H2("Odpowiedź B. CCCS sterowana prądem gałęzi"),
        base.eqbox("i_X=(12−V_X)/3 kΩ.\n(V_X−12)/3 + V_X/6 + 0,5(12−V_X)/3=0  ⇒  V_X=6 V.\ni_X=2 mA;   i_d=1 mA;   I_R₂=1 mA."),
        base.H2("Odpowiedź C. VCVS i superwęzeł"),
        base.eqbox("V_A−V_B=3·2=6 V;   V_A/4 kΩ+V_B/4 kΩ=0.\nV_A=3 V;   V_B=−3 V."),
        base.H2("Odpowiedź D. Rezystancja portu"),
        base.eqbox("R_T=U_t/I_t=1 V/0,75 mA=1,333 kΩ.\nŹródło zależne pozostaje aktywne; zerujemy wyłącznie źródła niezależne."),
        base.H2("Najważniejszy wniosek"),
        P("Każda metoda sprowadza się do praw Kirchhoffa, prawa elementów i równań źródeł. Źródła sterowane nie komplikują obwodu przez sam symbol — wymagają tylko konsekwentnego zdefiniowania wielkości sterujących i dopisania ich zależności."),
        base.callout("Skrócona ściąga", "Zdefiniuj u_x/i_x → zapisz prawo źródła → KCL/KVL/MNA → źródła zależne aktywne → sprawdź znak, jednostkę i równanie sterujące."),
    ]
    return story


def main():
    doc = CompendiumDocTemplate(
        str(OUTPUT), pagesize=base.A4,
        leftMargin=LEFT, rightMargin=RIGHT, topMargin=TOP, bottomMargin=BOTTOM,
        title="PLP K1 — kompendium źródeł sterowanych i metod analizy obwodów",
        author="Opracowanie własne",
        subject="Źródła zależne, KCL/KVL, metody węzłowa i oczkowa, superpozycja, Millman, Thévenin i Norton",
        keywords="PLP K1, źródła sterowane, VCCS, VCVS, CCCS, CCVS, superpozycja, MNA, Thévenin, Norton",
    )
    doc.multiBuild(build_story())
    print(f"Zapisano: {OUTPUT}")


if __name__ == "__main__":
    main()
