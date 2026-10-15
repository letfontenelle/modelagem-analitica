import re
from pathlib import Path
from xml.sax.saxutils import escape

import matplotlib.font_manager as fm
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output/pdf/roteiro_apresentacao.pdf"


def criar():
    source = (ROOT / "docs/roteiro_slides.md").read_text()
    sections = re.findall(r"^## (\d+)\. ([^\n]+)\n\n(.*?)(?=^## |\Z)", source, re.M | re.S)
    if [int(n) for n, _, _ in sections] != list(range(1, 14)):
        raise ValueError("O roteiro deve conter os 13 slides em ordem.")
    for name, weight in [("Guia", "normal"), ("GuiaBold", "bold")]:
        path = fm.findfont(fm.FontProperties(family="DejaVu Sans", weight=weight))
        pdfmetrics.registerFont(TTFont(name, path))
    pdfmetrics.registerFontFamily("Guia", normal="Guia", bold="GuiaBold")
    ink, teal = colors.HexColor("#102E3A"), colors.HexColor("#007F80")
    heading = ParagraphStyle("slide", fontName="GuiaBold", fontSize=13, leading=17,
                             textColor=teal, spaceAfter=9)
    body = ParagraphStyle("body", fontName="Guia", fontSize=10.5, leading=15.5,
                          textColor=ink, spaceAfter=9)
    intro = ParagraphStyle("intro", parent=body, fontSize=9.5, leading=14,
                           textColor=colors.HexColor("#526C76"), spaceAfter=18)
    story = []
    for number, title, content in sections:
        n = int(number)
        if story:
            story.append(PageBreak())
        if n == 1:
            story.append(Paragraph("Um slide por página. Estude a explicação junto com os gráficos. No fim de cada página, ‘O que falar’ traz a fala curta; não é preciso ler todas as explicações durante a apresentação de 15-20 minutos.", intro))
        story.append(Paragraph(f"{n:02d} · {escape(title)}", heading))
        for paragraph in content.strip().split("\n\n"):
            text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", escape(paragraph))
            story.append(Paragraph(text, body))
        story.append(Spacer(1, 13))

    def page(canvas, doc):
        w, h = A4
        canvas.setFillColor(ink)
        canvas.rect(0, h - 67, w, 67, fill=1, stroke=0)
        canvas.setFillColor(colors.white)
        canvas.setFont("GuiaBold", 17)
        canvas.drawString(43, h - 32, "Ilha Solteira | Roteiro de apresentação")
        canvas.setFont("Guia", 9)
        canvas.drawString(43, h - 49, "ARIMA e SARIMA · Explicações simples, exemplos e falas")
        canvas.setFillColor(teal)
        canvas.setFont("Guia", 8)
        canvas.drawString(43, 29, "Leia junto com a apresentação de 13 slides.")
        canvas.drawRightString(w - 43, 29, str(doc.page))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, topMargin=87, bottomMargin=47,
                            leftMargin=43, rightMargin=43,
                            title="Ilha Solteira - Guia dos 13 slides em linguagem simples",
                            author="Projeto Ilha Solteira")
    doc.build(story, onFirstPage=page, onLaterPages=page)
    print(OUTPUT)


if __name__ == "__main__":
    criar()
