"""
Bitcoin Wallet Tool - Application Icon Generator
Generates icon using QPainter without SVG dependency
"""
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QBrush, QFont
from PyQt6.QtCore import Qt, QRectF


def get_app_icon():
    """Generate application icon using QPainter."""
    size = 256
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Background circle
    painter.setPen(QPen(QColor("#fbbf24"), 4))
    painter.setBrush(QBrush(QColor("#0f1117")))
    painter.drawEllipse(18, 18, 220, 220)

    # Bitcoin symbol
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(QColor("#fbbf24")))

    # Draw ₿ character
    font = QFont("Arial", 140, QFont.Weight.Bold)
    painter.setFont(font)
    painter.setPen(QColor("#fbbf24"))
    painter.drawText(QRectF(0, 0, size, size), Qt.AlignmentFlag.AlignCenter, "₿")

    # Key accent (bottom right corner)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(QColor(251, 191, 36, 200)))  # #fbbf24 with alpha
    painter.drawEllipse(200, 200, 24, 24)
    painter.drawRoundedRect(194, 212, 24, 30, 3, 3)
    painter.drawEllipse(206, 238, 8, 8)
    painter.drawEllipse(194, 230, 6, 6)
    painter.drawEllipse(212, 230, 6, 6)

    painter.end()
    return QIcon(pixmap)
