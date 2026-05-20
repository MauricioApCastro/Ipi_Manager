from datetime import datetime
from html import escape
from pathlib import Path

from PyQt5.QtCore import QMarginsF, QRectF, QSizeF, Qt
from PyQt5.QtGui import QColor, QFont, QPainter, QPen
from PyQt5.QtGui import QPdfWriter


MESES = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]


def gerar_recibo_pagamento(
    aluno,
    turma_texto,
    data_primeiro_pagamento,
    parcelas_pagas,
    valor_mensalidade,
    valor_atraso,
    dia_vencimento,
    pix,
    destino,
    observacoes="",
):
    inicio = datetime.strptime(data_primeiro_pagamento, "%d/%m/%Y")
    parcelas = []

    for index in range(14):
        mes_index = (inicio.month - 1 + index) % 12
        ano = inicio.year + ((inicio.month - 1 + index) // 12)
        parcelas.append({
            "numero": index + 1,
            "mes": MESES[mes_index],
            "ano": ano,
            "status": "PAGO" if index < parcelas_pagas else "a vencer",
        })

    termino = parcelas[-1]
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        _html_recibo(
            aluno=aluno,
            turma_texto=turma_texto,
            data_primeiro_pagamento=data_primeiro_pagamento,
            termino=f"{termino['mes']}/{str(termino['ano'])[-2:]}",
            parcelas=parcelas,
            valor_mensalidade=valor_mensalidade,
            valor_atraso=valor_atraso,
            dia_vencimento=dia_vencimento,
            pix=pix,
            observacoes=observacoes,
        ),
        encoding="utf-8",
    )
    return destino


def gerar_recibo_pagamento_pdf(
    aluno,
    turma_texto,
    data_primeiro_pagamento,
    parcelas_pagas,
    valor_mensalidade,
    valor_atraso,
    dia_vencimento,
    pix,
    destino,
    observacoes="",
):
    inicio = datetime.strptime(data_primeiro_pagamento, "%d/%m/%Y")
    parcelas = []

    for index in range(14):
        mes_index = (inicio.month - 1 + index) % 12
        ano = inicio.year + ((inicio.month - 1 + index) // 12)
        parcelas.append({
            "numero": index + 1,
            "mes": MESES[mes_index],
            "ano": ano,
            "status": "PAGO" if index < parcelas_pagas else "a vencer",
        })

    termino = parcelas[-1]
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)

    writer = QPdfWriter(str(destino))
    writer.setPageSizeMM(QSizeF(210, 297))
    writer.setResolution(72)
    writer.setPageMargins(QMarginsF(12, 12, 12, 12))

    painter = QPainter()
    painter.begin(writer)
    rect = writer.pageLayout().paintRectPixels(72)
    scale_x = rect.width() / 800
    scale_y = rect.height() / 1120
    painter.scale(scale_x, scale_y)
    _desenhar_pdf_moderno(
        painter=painter,
        aluno=aluno,
        turma_texto=turma_texto,
        data_primeiro_pagamento=data_primeiro_pagamento,
        termino=f"{termino['mes']}/{str(termino['ano'])[-2:]}",
        parcelas=parcelas,
        valor_mensalidade=valor_mensalidade,
        valor_atraso=valor_atraso,
        dia_vencimento=dia_vencimento,
        pix=pix,
        observacoes=observacoes,
    )
    painter.end()
    return destino


def _draw_round(painter, x, y, w, h, color, border=None, radius=14):
    painter.setBrush(QColor(color))
    painter.setPen(QPen(QColor(border), 1) if border else Qt.NoPen)
    painter.drawRoundedRect(QRectF(x, y, w, h), radius, radius)


def _draw_text(painter, x, y, w, h, text, size=12, color="#0f172a", bold=False, align=Qt.AlignLeft | Qt.AlignVCenter):
    font = QFont("Arial", size)
    font.setBold(bold)
    painter.setFont(font)
    painter.setPen(QColor(color))
    painter.drawText(QRectF(x, y, w, h), align | Qt.TextWordWrap, str(text))


def _money(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _desenhar_pdf_moderno(
    painter,
    aluno,
    turma_texto,
    data_primeiro_pagamento,
    termino,
    parcelas,
    valor_mensalidade,
    valor_atraso,
    dia_vencimento,
    pix,
    observacoes="",
):
    painter.fillRect(QRectF(0, 0, 800, 1120), QColor("#ffffff"))

    _draw_round(painter, 32, 28, 736, 118, "#0f172a", radius=18)
    _draw_text(painter, 58, 44, 300, 24, "IPI INFORMÁTICA", 10, "#93c5fd", True)
    _draw_text(painter, 58, 68, 560, 42, "Recibo e Controle de Pagamento", 24, "#ffffff", True)
    _draw_text(painter, 58, 108, 520, 24, "Documento de acompanhamento financeiro do curso", 11, "#cbd5e1")

    _draw_round(painter, 32, 164, 736, 126, "#ffffff", "#e2e8f0", radius=16)
    _draw_text(painter, 54, 176, 220, 22, "ALUNO", 9, "#64748b", True)
    _draw_text(painter, 54, 199, 420, 32, aluno.nome or "", 18, "#0f172a", True)
    _draw_text(painter, 520, 176, 110, 22, "1º PAGTO", 9, "#64748b", True)
    _draw_text(painter, 520, 199, 110, 30, data_primeiro_pagamento, 14, "#0f172a", True)
    _draw_text(painter, 650, 176, 80, 22, "TÉRMINO", 9, "#64748b", True)
    _draw_text(painter, 650, 199, 90, 30, termino, 14, "#0f172a", True)
    _draw_text(painter, 54, 238, 500, 24, f"HORÁRIO: {turma_texto or '-'}", 11, "#334155", True)
    _draw_text(painter, 560, 238, 180, 24, f"VENCE TODO DIA {dia_vencimento}", 11, "#334155", True, Qt.AlignRight | Qt.AlignVCenter)

    _draw_text(painter, 32, 314, 220, 26, "PAGAMENTOS", 12, "#334155", True)

    card_w = 96
    card_h = 86
    gap = 8
    start_x = 32
    y1 = 346
    for index, parcela in enumerate(parcelas):
        col = index % 7
        row = index // 7
        x = start_x + col * (card_w + gap)
        y = y1 + row * (card_h + 12)
        pago = parcela["status"] == "PAGO"
        bg = "#dcfce7" if pago else "#fff7ed"
        border = "#86efac" if pago else "#fed7aa"
        status_color = "#15803d" if pago else "#9a3412"
        _draw_round(painter, x, y, card_w, card_h, bg, border, radius=13)
        _draw_text(painter, x, y + 9, card_w, 18, f"{parcela['numero']}/14", 9, "#475569", True, Qt.AlignCenter)
        _draw_text(painter, x, y + 31, card_w, 24, parcela["mes"], 16, "#0f172a", True, Qt.AlignCenter)
        _draw_text(painter, x, y + 58, card_w, 18, parcela["status"], 9, status_color, True, Qt.AlignCenter)

    _draw_round(painter, 32, 552, 736, 136, "#ffffff", "#e2e8f0", radius=16)
    _draw_text(painter, 54, 570, 220, 20, "VALORES", 10, "#64748b", True)
    _draw_text(painter, 54, 600, 230, 24, "Até o vencimento", 11, "#475569", True)
    _draw_text(painter, 54, 626, 230, 34, _money(valor_mensalidade), 20, "#15803d", True)
    _draw_text(painter, 314, 600, 230, 24, "Após vencimento", 11, "#475569", True)
    _draw_text(painter, 314, 626, 230, 34, _money(valor_atraso), 20, "#be123c", True)
    _draw_round(painter, 566, 586, 174, 76, "#eff6ff", "#bfdbfe", radius=14)
    _draw_text(painter, 586, 596, 134, 18, "PIX", 10, "#64748b", True, Qt.AlignCenter)
    _draw_text(painter, 586, 620, 134, 28, pix, 18, "#1d4ed8", True, Qt.AlignCenter)

    pagas = sum(1 for p in parcelas if p["status"] == "PAGO")
    pendentes = 14 - pagas
    _draw_round(painter, 32, 710, 358, 76, "#f8fafc", "#e2e8f0", radius=14)
    _draw_text(painter, 54, 724, 150, 20, "PAGAS", 10, "#64748b", True)
    _draw_text(painter, 54, 748, 180, 28, f"{pagas} parcelas", 18, "#15803d", True)
    _draw_round(painter, 410, 710, 358, 76, "#f8fafc", "#e2e8f0", radius=14)
    _draw_text(painter, 432, 724, 150, 20, "PENDENTES", 10, "#64748b", True)
    _draw_text(painter, 432, 748, 180, 28, f"{pendentes} parcelas", 18, "#9a3412", True)

    aviso_y = 812
    if observacoes:
        _draw_round(painter, 32, 812, 736, 92, "#f8fafc", "#e2e8f0", radius=14)
        _draw_text(painter, 54, 826, 220, 20, "OBSERVACOES", 10, "#64748b", True)
        _draw_text(painter, 54, 850, 690, 42, observacoes, 11, "#334155", False)
        aviso_y = 922

    _draw_round(painter, 32, aviso_y, 736, 66, "#fff1f2", "#fecdd3", radius=14)
    _draw_text(
        painter,
        54,
        aviso_y + 12,
        690,
        42,
        "Em caso de cancelamento, verificar regras contratuais e disponibilidade da vaga da turma.",
        11,
        "#9f1239",
        True,
    )


def _html_recibo(
    aluno,
    turma_texto,
    data_primeiro_pagamento,
    termino,
    parcelas,
    valor_mensalidade,
    valor_atraso,
    dia_vencimento,
    pix,
    observacoes="",
):
    linhas = []
    for bloco in range(0, 14, 7):
        parte = parcelas[bloco:bloco + 7]
        linhas.append("<tr>" + "".join(f"<td class='num'>{p['numero']}/14</td>" for p in parte) + "</tr>")
        linhas.append("<tr>" + "".join(f"<td class='mes'>{p['mes']}</td>" for p in parte) + "</tr>")
        linhas.append(
            "<tr>"
            + "".join(
                f"<td class=\"{'pago' if p['status'] == 'PAGO' else 'vencer'}\">{p['status']}</td>"
                for p in parte
            )
            + "</tr>"
        )

    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
body {{ font-family: Calibri, Arial, sans-serif; }}
table {{ border-collapse: collapse; width: 820px; }}
td {{ border: 1px solid #111; padding: 6px; font-size: 14px; }}
.titulo {{ background: #4b4b4b; color: #fff; font-size: 22px; font-weight: 700; text-align: center; }}
.secao {{ background: #4b4b4b; color: #fff; font-weight: 700; text-align: center; }}
.label {{ background: #f3f4f6; font-weight: 700; }}
.nome {{ font-weight: 700; text-align: center; }}
.num {{ background: #d9d9d9; text-align: center; }}
.mes {{ background: #d9ead3; text-align: center; font-weight: 700; }}
.pago {{ background: #92d050; text-align: center; font-weight: 700; }}
.vencer {{ background: #fce4d6; text-align: center; }}
.pix {{ font-size: 26px; font-weight: 700; text-align: center; }}
.aviso {{ background: #e6b8b7; color: #fff; font-weight: 700; text-align: center; }}
.info {{ background: #ddebf7; font-weight: 700; }}
.valor-ok {{ background: #e2f0d9; }}
.valor-atraso {{ background: #f4cccc; }}
</style>
</head>
<body>
<table>
<tr><td colspan="7" class="titulo">CONTROLE DE PAGAMENTO (VALE COMO RECIBO)</td></tr>
<tr><td class="label">ALUNO</td><td colspan="6" class="nome">{escape(aluno.nome or "")}</td></tr>
<tr><td class="label">1º PAGTO</td><td>{escape(data_primeiro_pagamento)}</td><td class="label">TERMINO</td><td>{escape(termino)}</td><td class="label">VALOR</td><td colspan="2">R$ {valor_mensalidade:,.2f}</td></tr>
<tr><td class="label">vencimento</td><td colspan="2">TODO DIA {dia_vencimento}</td><td class="label">PIX</td><td colspan="3" class="pix">{escape(pix)}</td></tr>
<tr><td colspan="7" class="secao">PAGAMENTOS</td></tr>
{''.join(linhas)}
<tr><td colspan="7" class="info">HORARIO: {escape(turma_texto or '-')}</td></tr>
<tr><td colspan="4" class="valor-ok">PARCELAS PAGAS ATÉ DIA {dia_vencimento}</td><td colspan="3">R$ {valor_mensalidade:,.2f}</td></tr>
<tr><td colspan="4" class="valor-atraso">PARCELAS PAGAS DEPOIS DO VENCIMENTO</td><td colspan="3">R$ {valor_atraso:,.2f}</td></tr>
{f'<tr><td colspan="7" class="info">OBSERVACOES: {escape(observacoes)}</td></tr>' if observacoes else ''}
<tr><td colspan="7" class="aviso">EM CASO DE CANCELAMENTO, VERIFICAR REGRAS CONTRATUAIS E VAGA DA TURMA.</td></tr>
</table>
</body>
</html>
"""


def _html_recibo_moderno(
    aluno,
    turma_texto,
    data_primeiro_pagamento,
    termino,
    parcelas,
    valor_mensalidade,
    valor_atraso,
    dia_vencimento,
    pix,
):
    cards = []
    for parcela in parcelas:
        pago = parcela["status"] == "PAGO"
        cards.append(
            f"""
            <td class="parcela {'pago' if pago else 'pendente'}">
                <div class="parcela-num">{parcela['numero']}/14</div>
                <div class="parcela-mes">{escape(parcela['mes'])}</div>
                <div class="parcela-status">{escape(parcela['status'])}</div>
            </td>
            """
        )

    linhas_parcelas = ""
    for idx in range(0, 14, 7):
        linhas_parcelas += "<tr>" + "".join(cards[idx:idx + 7]) + "</tr>"

    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
body {{
    font-family: Arial, sans-serif;
    color: #0f172a;
    background: #ffffff;
}}
.page {{
    width: 100%;
}}
.hero {{
    background: #0f172a;
    color: #ffffff;
    border-radius: 18px;
    padding: 24px 28px;
}}
.brand {{
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1px;
    color: #93c5fd;
}}
h1 {{
    font-size: 28px;
    margin: 8px 0 4px 0;
}}
.subtitle {{
    color: #cbd5e1;
    font-size: 13px;
}}
.section {{
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    margin-top: 14px;
    padding: 16px;
}}
.section-title {{
    color: #334155;
    font-size: 13px;
    font-weight: 800;
    text-transform: uppercase;
    margin-bottom: 10px;
}}
.grid {{
    width: 100%;
    border-collapse: collapse;
}}
.grid td {{
    padding: 8px 10px;
    vertical-align: top;
}}
.label {{
    color: #64748b;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
}}
.value {{
    color: #0f172a;
    font-size: 16px;
    font-weight: 800;
}}
.muted {{
    color: #475569;
    font-size: 13px;
    font-weight: 600;
}}
.parcelas {{
    width: 100%;
    border-collapse: separate;
    border-spacing: 8px;
}}
.parcela {{
    border-radius: 12px;
    padding: 10px 8px;
    text-align: center;
    width: 14%;
}}
.pago {{
    background: #dcfce7;
    border: 1px solid #86efac;
}}
.pendente {{
    background: #fff7ed;
    border: 1px solid #fed7aa;
}}
.parcela-num {{
    color: #475569;
    font-size: 11px;
    font-weight: 700;
}}
.parcela-mes {{
    color: #0f172a;
    font-size: 15px;
    font-weight: 900;
    margin-top: 4px;
}}
.parcela-status {{
    color: #334155;
    font-size: 11px;
    font-weight: 800;
    margin-top: 4px;
}}
.pix {{
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 16px;
    padding: 16px;
    text-align: center;
}}
.pix-num {{
    font-size: 28px;
    font-weight: 900;
    color: #1d4ed8;
}}
.notice {{
    background: #fff1f2;
    border: 1px solid #fecdd3;
    border-radius: 14px;
    padding: 12px 14px;
    color: #9f1239;
    font-size: 12px;
    font-weight: 800;
    margin-top: 14px;
}}
</style>
</head>
<body>
<div class="page">
    <div class="hero">
        <div class="brand">IPI INFORMÁTICA</div>
        <h1>Recibo e Controle de Pagamento</h1>
        <div class="subtitle">Documento de acompanhamento financeiro do curso</div>
    </div>

    <div class="section">
        <div class="section-title">Aluno</div>
        <table class="grid">
            <tr>
                <td>
                    <div class="label">Nome</div>
                    <div class="value">{escape(aluno.nome or "")}</div>
                </td>
                <td>
                    <div class="label">1º pagamento</div>
                    <div class="value">{escape(data_primeiro_pagamento)}</div>
                </td>
                <td>
                    <div class="label">Término</div>
                    <div class="value">{escape(termino)}</div>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <div class="label">Horário</div>
                    <div class="muted">{escape(turma_texto or "-")}</div>
                </td>
                <td>
                    <div class="label">Vencimento</div>
                    <div class="value">Todo dia {dia_vencimento}</div>
                </td>
            </tr>
        </table>
    </div>

    <div class="section">
        <div class="section-title">Pagamentos</div>
        <table class="parcelas">
            {linhas_parcelas}
        </table>
    </div>

    <div class="section">
        <table class="grid">
            <tr>
                <td>
                    <div class="label">Mensalidade até o vencimento</div>
                    <div class="value">R$ {valor_mensalidade:,.2f}</div>
                </td>
                <td>
                    <div class="label">Mensalidade após vencimento</div>
                    <div class="value">R$ {valor_atraso:,.2f}</div>
                </td>
                <td>
                    <div class="pix">
                        <div class="label">PIX</div>
                        <div class="pix-num">{escape(pix)}</div>
                    </div>
                </td>
            </tr>
        </table>
    </div>

    <div class="notice">
        Em caso de cancelamento, verificar regras contratuais e disponibilidade da vaga da turma.
    </div>
</div>
</body>
</html>
"""
