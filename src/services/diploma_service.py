from datetime import datetime
from pathlib import Path

from PyQt5.QtCore import QMarginsF, QRectF, QSizeF, Qt
from PyQt5.QtGui import QColor, QFont, QPainter, QPen
from PyQt5.QtGui import QPdfWriter


def gerar_diploma_pdf(aluno, curso_nome, total_aulas, total_presencas, destino):
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)

    writer = QPdfWriter(str(destino))
    writer.setPageSizeMM(QSizeF(297, 210))
    writer.setResolution(72)
    writer.setPageMargins(QMarginsF(10, 10, 10, 10))

    painter = QPainter()
    painter.begin(writer)
    rect = writer.pageLayout().paintRectPixels(72)
    painter.scale(rect.width() / 1120, rect.height() / 800)
    _desenhar_diploma(painter, aluno, curso_nome, total_aulas, total_presencas)
    painter.end()
    return destino


def _draw_round(painter, x, y, w, h, color, border=None, radius=18, width=1):
    painter.setBrush(QColor(color))
    painter.setPen(QPen(QColor(border), width) if border else Qt.NoPen)
    painter.drawRoundedRect(QRectF(x, y, w, h), radius, radius)


def _draw_text(painter, x, y, w, h, text, size=18, color="#0f172a", bold=False, align=Qt.AlignCenter):
    font = QFont("Times New Roman", size)
    font.setBold(bold)
    painter.setFont(font)
    painter.setPen(QColor(color))
    painter.drawText(QRectF(x, y, w, h), align | Qt.TextWordWrap, str(text))


def _desenhar_diploma(painter, aluno, curso_nome, total_aulas, total_presencas):
    painter.fillRect(QRectF(0, 0, 1120, 800), QColor("#ffffff"))
    _draw_round(painter, 34, 34, 1052, 732, "#ffffff", "#0f766e", 24, 5)
    _draw_round(painter, 64, 64, 992, 672, "#f8fafc", "#99f6e4", 18, 2)

    _draw_text(painter, 120, 98, 880, 36, "IPI INFORMATICA", 17, "#0f766e", True)
    _draw_text(painter, 120, 150, 880, 74, "Diploma de Conclusao", 42, "#0f172a", True)
    _draw_text(painter, 150, 250, 820, 44, "Certificamos que", 20, "#475569")
    _draw_text(painter, 120, 302, 880, 72, aluno.nome or "", 38, "#111827", True)
    _draw_text(
        painter,
        150,
        392,
        820,
        88,
        f"concluiu o curso {curso_nome or 'Curso Completo IPI'}, com acompanhamento de frequencia e progresso.",
        22,
        "#334155",
    )

    hoje = datetime.now().strftime("%d/%m/%Y")
    _draw_round(painter, 220, 520, 260, 86, "#ecfeff", "#99f6e4", 16)
    _draw_text(painter, 240, 532, 220, 22, "Aulas concluidas", 14, "#64748b", True)
    _draw_text(painter, 240, 558, 220, 34, str(total_aulas), 28, "#0f766e", True)

    _draw_round(painter, 520, 520, 260, 86, "#eff6ff", "#bfdbfe", 16)
    _draw_text(painter, 540, 532, 220, 22, "Presencas registradas", 14, "#64748b", True)
    _draw_text(painter, 540, 558, 220, 34, str(total_presencas), 28, "#1d4ed8", True)

    _draw_text(painter, 130, 650, 330, 30, f"Emitido em {hoje}", 16, "#475569", False, Qt.AlignLeft | Qt.AlignVCenter)
    _draw_text(painter, 720, 650, 260, 30, "IPI Informatica", 16, "#475569", True)
    painter.setPen(QPen(QColor("#94a3b8"), 2))
    painter.drawLine(700, 640, 1000, 640)
