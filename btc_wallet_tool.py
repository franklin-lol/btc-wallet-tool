from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit, QMessageBox, QComboBox,
    QFrame, QTabWidget, QSizePolicy, QDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings
from PyQt6.QtGui import QIcon
from bit import Key
import sys
import os
import requests
import logging
from translations import get_translation
from icon import get_app_icon

logging.basicConfig(
    filename='btc_transaction.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class _PrivKeyMaskFilter(logging.Filter):
    """
    Дополнительная страховка: если в логируемом сообщении встречается
    строка, похожая на WIF (5.../K.../L...) или длинный HEX-ключ — маскируем.
    """
    import re
    _WIF_RE  = re.compile(r'\b[5KL][1-9A-HJ-NP-Za-km-z]{50,51}\b')
    _HEX64   = re.compile(r'\b[0-9a-fA-F]{64}\b')

    def filter(self, record):
        msg = record.getMessage()
        msg = self._WIF_RE.sub('[PRIVATE_KEY_MASKED]', msg)
        msg = self._HEX64.sub('[HEX_KEY_MASKED]', msg)
        record.msg  = msg
        record.args = ()
        return True


for _h in logging.root.handlers:
    _h.addFilter(_PrivKeyMaskFilter())

API_URL = "https://mempool.space/api"

# ── Localization ──────────────────────────────────────────────────────────────
STRINGS = {
    "ru": {
        "title": "⟐ BTC TX",
        "subtitle": "BITCOIN TRANSACTION CONSOLE  //  OFFLINE & BROADCAST",
        "priv_key": "PRIVATE KEY  (HEX  или  WIF)",
        "priv_key_ph": "HEX (1–64 символа, auto zero-pad)  OR  WIF: 5... / K... / L...",
        "recover": "⟳  RECOVER ADDRESSES",
        "address": "ADDRESS",
        "verification": "⚑  VERIFICATION",
        "legacy": "Legacy (P2PKH):",
        "segwit": "SegWit (bech32):",
        "key_format": "Key format:",
        "wif": "WIF:",
        "balance": "BALANCE",
        "check_balance": "↻ CHECK BALANCE",
        "tab_broadcast": "BROADCAST",
        "tab_offline": "OFFLINE / RAW HEX",
        "dest_addr": "DESTINATION ADDRESS",
        "dest_addr_ph": "bc1q... or 1... or 3...",
        "amount": "AMOUNT (BTC) — БЕЗ комиссии",
        "amount_ph": "0.00000000  (пусто = весь баланс)",
        "fee": "FEE (SAT/BYTE)",
        "fee_ph": "напр. 20",
        "suggest": "⚡ SUGGEST",
        "recipient_gets": "Получит адресат:",
        "fee_label": "Комиссия:",
        "broadcast_btn": "▶  BROADCAST TRANSACTION",
        "build_btn": "⚙  BUILD RAW TX",
        "txid": "TXID",
        "raw_hex": "RAW HEX (SIGNED TX)",
        "raw_hex_ph": "Signed transaction hex will appear here...",
        "log": "LOG",
        "clear": "✕ CLEAR",
        "copy_tooltip": "Копировать",
        "help": "HELP",
        "theme": "Theme:",
        "language": "Language:",
        "help_title": "BTC Wallet Tool — Помощь",
        "help_content": """<b>Инструкция:</b><br><br>
1. Введите приватный ключ (HEX или WIF)<br>
2. Нажмите "RECOVER ADDRESSES" для получения адресов<br>
3. Выберите адрес отправителя из выпадающего списка<br>
4. Проверьте баланс кнопкой "CHECK BALANCE"<br><br>

<b>BROADCAST:</b> немедленная отправка в сеть Bitcoin<br>
<b>OFFLINE/RAW HEX:</b> создание подписанной транзакции БЕЗ отправки<br>
(для ручной отправки через mining pool)<br><br>

<b>Автор:</b> <a href='https://franklin-sys.vercel.app/'>franklin-sys.vercel.app</a><br>
<b>GitHub:</b> <a href='https://github.com/franklin-lol/btc-wallet-tool'>franklin-lol/btc-wallet-tool</a>
""",
    },
    "en": {
        "title": "⟐ BTC TX",
        "subtitle": "BITCOIN TRANSACTION CONSOLE  //  OFFLINE & BROADCAST",
        "priv_key": "PRIVATE KEY  (HEX  or  WIF)",
        "priv_key_ph": "HEX (1–64 chars, auto zero-pad)  OR  WIF: 5... / K... / L...",
        "recover": "⟳  RECOVER ADDRESSES",
        "address": "ADDRESS",
        "verification": "⚑  VERIFICATION",
        "legacy": "Legacy (P2PKH):",
        "segwit": "SegWit (bech32):",
        "key_format": "Key format:",
        "wif": "WIF:",
        "balance": "BALANCE",
        "check_balance": "↻ CHECK BALANCE",
        "tab_broadcast": "BROADCAST",
        "tab_offline": "OFFLINE / RAW HEX",
        "dest_addr": "DESTINATION ADDRESS",
        "dest_addr_ph": "bc1q... or 1... or 3...",
        "amount": "AMOUNT (BTC) — NET",
        "amount_ph": "0.00000000  (empty = full balance)",
        "fee": "FEE (SAT/BYTE)",
        "fee_ph": "e.g. 20",
        "suggest": "⚡ SUGGEST",
        "recipient_gets": "Recipient gets:",
        "fee_label": "Fee:",
        "broadcast_btn": "▶  BROADCAST TRANSACTION",
        "build_btn": "⚙  BUILD RAW TX",
        "txid": "TXID",
        "raw_hex": "RAW HEX (SIGNED TX)",
        "raw_hex_ph": "Signed transaction hex will appear here...",
        "log": "LOG",
        "clear": "✕ CLEAR",
        "copy_tooltip": "Copy",
        "help": "HELP",
        "theme": "Theme:",
        "language": "Language:",
        "help_title": "BTC Wallet Tool — Help",
        "help_content": """<b>Instructions:</b><br><br>
1. Enter private key (HEX or WIF)<br>
2. Click "RECOVER ADDRESSES" to derive addresses<br>
3. Select sender address from dropdown<br>
4. Check balance with "CHECK BALANCE" button<br><br>

<b>BROADCAST:</b> immediate broadcast to Bitcoin network<br>
<b>OFFLINE/RAW HEX:</b> build signed transaction WITHOUT broadcasting<br>
(for manual submission via mining pool)<br><br>

<b>Author:</b> <a href='https://franklin-sys.vercel.app/'>franklin-sys.vercel.app</a><br>
<b>GitHub:</b> <a href='https://github.com/franklin-lol/btc-wallet-tool'>franklin-lol/btc-wallet-tool</a>
""",
    }
}

# ── Themes ────────────────────────────────────────────────────────────────────

DARK_STYLE = """
QWidget {
    background-color: #0f1117;
    color: #e8eaed;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    font-size: 11px;
}

QTabWidget::pane {
    border: 1px solid #2a2d35;
    background-color: #171a23;
    border-radius: 6px;
}

QTabBar::tab {
    background-color: #1a1d26;
    color: #9ca3af;
    padding: 8px 20px;
    border: none;
    font-size: 10px;
    letter-spacing: 1px;
    min-width: 80px;
}

QTabBar::tab:selected {
    background-color: #171a23;
    color: #fbbf24;
    border-bottom: 2px solid #fbbf24;
}

QTabBar::tab:hover {
    color: #fcd34d;
    background-color: #1e222e;
}

QLabel {
    color: #d1d5db;
    font-size: 10px;
    letter-spacing: 0.5px;
    padding-bottom: 2px;
}

QLabel#value_label {
    color: #fbbf24;
    font-size: 17px;
    font-weight: bold;
    letter-spacing: 0px;
    text-transform: none;
    padding: 0px;
}

QLabel#title_label {
    color: #fbbf24;
    font-size: 16px;
    font-weight: bold;
    letter-spacing: 2px;
    padding: 0px;
}

QLabel#sub_label {
    color: #6b7280;
    font-size: 9px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 0px;
}

QLineEdit {
    background-color: #1a1d26;
    border: 1px solid #374151;
    border-radius: 5px;
    color: #f3f4f6;
    padding: 4px 8px;
    font-family: 'Courier New', 'Consolas', monospace;
    font-size: 11px;
    selection-background-color: #fbbf24;
    selection-color: #0f1117;
    min-height: 22px;
}

QLineEdit:focus {
    border: 1px solid #fbbf24;
    background-color: #1e222e;
}

QLineEdit:hover {
    border: 1px solid #4b5563;
}

QPushButton {
    background-color: #1a1d26;
    color: #d1d5db;
    border: 1px solid #374151;
    border-radius: 5px;
    padding: 7px 12px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    font-size: 10px;
    letter-spacing: 0.5px;
}

QPushButton:hover {
    background-color: #252935;
    border: 1px solid #fbbf24;
    color: #fbbf24;
}

QPushButton:pressed {
    background-color: #fbbf24;
    color: #0f1117;
}

QPushButton#primary_btn {
    background-color: #fbbf24;
    color: #0f1117;
    border: none;
    font-weight: bold;
    font-size: 11px;
    letter-spacing: 1px;
    padding: 9px 14px;
}

QPushButton#primary_btn:hover {
    background-color: #fcd34d;
    color: #0f1117;
}

QPushButton#primary_btn:pressed {
    background-color: #f59e0b;
}

QPushButton#danger_btn {
    background-color: #7f1d1d;
    color: #fca5a5;
    border: 1px solid #991b1b;
    font-size: 11px;
    letter-spacing: 1px;
}

QPushButton#danger_btn:hover {
    background-color: #991b1b;
    border: 1px solid #ef4444;
    color: #fecaca;
}

QPushButton#danger_btn:pressed {
    background-color: #ef4444;
    color: #0f1117;
}

QPushButton#copy_btn {
    background-color: #1a1d26;
    color: #9ca3af;
    border: 1px solid #374151;
    padding: 3px 5px;
    font-size: 9px;
    border-radius: 4px;
    min-width: 64px;
    min-height: 26px;
    letter-spacing: 0px;
}

QPushButton#copy_btn:hover {
    color: #fbbf24;
    background-color: #252935;
    border: 1px solid #fbbf24;
}

QTextEdit {
    background-color: #0b0e13;
    border: 1px solid #2a2d35;
    border-radius: 5px;
    color: #9ca3af;
    font-family: 'Courier New', 'Consolas', monospace;
    font-size: 10px;
    padding: 6px;
}

QComboBox {
    background-color: #1a1d26;
    border: 1px solid #374151;
    border-radius: 5px;
    color: #f3f4f6;
    padding: 7px 12px;
    font-family: 'Courier New', 'Consolas', monospace;
    font-size: 11px;
    min-height: 18px;
}

QComboBox:hover {
    border: 1px solid #fbbf24;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #1a1d26;
    border: 1px solid #fbbf24;
    color: #f3f4f6;
    selection-background-color: #fbbf24;
    selection-color: #0f1117;
}

QFrame#separator {
    background-color: #2a2d35;
    max-height: 1px;
    margin: 2px 0px;
}

QFrame#card {
    background-color: #171a23;
    border: 1px solid #2a2d35;
    border-radius: 8px;
    padding: 0px;
}

QMessageBox {
    background-color: #0f1117;
}

QMessageBox QLabel {
    color: #e8eaed;
    font-size: 11px;
    text-transform: none;
    letter-spacing: 0px;
}

QMessageBox QPushButton {
    min-width: 80px;
    padding: 7px 14px;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    background-color: #1a1d26;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #374151;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #4b5563;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QDialog {
    background-color: #0f1117;
}
"""

LIGHT_STYLE = """
QWidget {
    background-color: #FFFFFF;
    color: #1A1A1A;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    font-size: 11px;
}

QTabWidget::pane {
    border: 1px solid #D1D1D1;
    background-color: #F5F5F5;
    border-radius: 6px;
}

QTabBar::tab {
    background-color: #E8E8E8;
    color: #6B6B6B;
    padding: 8px 20px;
    border: none;
    font-size: 10px;
    letter-spacing: 1px;
    min-width: 80px;
}

QTabBar::tab:selected {
    background-color: #F5F5F5;
    color: #00D9FF;
    border-bottom: 2px solid #00D9FF;
}

QTabBar::tab:hover {
    color: #00D9FF;
    background-color: #F0F0F0;
}

QLabel {
    color: #1A1A1A;
    font-size: 10px;
    letter-spacing: 0.5px;
    padding-bottom: 2px;
}

QLabel#value_label {
    color: #00D9FF;
    font-size: 17px;
    font-weight: bold;
    letter-spacing: 0px;
    text-transform: none;
    padding: 0px;
}

QLabel#title_label {
    color: #00D9FF;
    font-size: 16px;
    font-weight: bold;
    letter-spacing: 2px;
    padding: 0px;
}

QLabel#sub_label {
    color: #6B6B6B;
    font-size: 9px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 0px;
}

QLineEdit {
    background-color: #F5F5F5;
    border: 1px solid #D1D1D1;
    border-radius: 5px;
    color: #1A1A1A;
    padding: 4px 8px;
    font-family: 'Courier New', 'Consolas', monospace;
    font-size: 11px;
    selection-background-color: #00D9FF;
    selection-color: #FFFFFF;
    min-height: 22px;
}

QLineEdit:focus {
    border: 1px solid #00D9FF;
    background-color: #FFFFFF;
}

QLineEdit:hover {
    border: 1px solid #00D9FF;
}

QPushButton {
    background-color: #F5F5F5;
    color: #1A1A1A;
    border: 1px solid #D1D1D1;
    border-radius: 5px;
    padding: 7px 12px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    font-size: 10px;
    letter-spacing: 0.5px;
}

QPushButton:hover {
    background-color: #E8E8E8;
    border: 1px solid #00D9FF;
    color: #00D9FF;
}

QPushButton:pressed {
    background-color: #00D9FF;
    color: #FFFFFF;
}

QPushButton#primary_btn {
    background-color: #1A1A1A;
    color: #FFFFFF;
    border: none;
    font-weight: bold;
    font-size: 11px;
    letter-spacing: 1px;
    padding: 9px 14px;
}

QPushButton#primary_btn:hover {
    background-color: #2A2A2A;
    color: #FFFFFF;
}

QPushButton#primary_btn:pressed {
    background-color: #00D9FF;
}

QPushButton#danger_btn {
    background-color: #FFE5E5;
    color: #D32F2F;
    border: 1px solid #FFCDD2;
    font-size: 11px;
    letter-spacing: 1px;
}

QPushButton#danger_btn:hover {
    background-color: #FFCDD2;
    border: 1px solid #D32F2F;
    color: #B71C1C;
}

QPushButton#danger_btn:pressed {
    background-color: #D32F2F;
    color: #FFFFFF;
}

QPushButton#copy_btn {
    background-color: #F5F5F5;
    color: #6B6B6B;
    border: 1px solid #D1D1D1;
    padding: 3px 5px;
    font-size: 9px;
    border-radius: 4px;
    min-width: 64px;
    min-height: 26px;
    letter-spacing: 0px;
}

QPushButton#copy_btn:hover {
    color: #00D9FF;
    background-color: #E8E8E8;
    border: 1px solid #00D9FF;
}

QTextEdit {
    background-color: #F5F5F5;
    border: 1px solid #D1D1D1;
    border-radius: 5px;
    color: #1A1A1A;
    font-family: 'Courier New', 'Consolas', monospace;
    font-size: 10px;
    padding: 6px;
}

QComboBox {
    background-color: #F5F5F5;
    border: 1px solid #D1D1D1;
    border-radius: 5px;
    color: #1A1A1A;
    padding: 7px 12px;
    font-family: 'Courier New', 'Consolas', monospace;
    font-size: 11px;
    min-height: 18px;
}

QComboBox:hover {
    border: 1px solid #00D9FF;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #F5F5F5;
    border: 1px solid #00D9FF;
    color: #1A1A1A;
    selection-background-color: #00D9FF;
    selection-color: #FFFFFF;
}

QFrame#separator {
    background-color: #D1D1D1;
    max-height: 1px;
    margin: 2px 0px;
}

QFrame#card {
    background-color: #F5F5F5;
    border: 1px solid #D1D1D1;
    border-radius: 8px;
    padding: 0px;
}

QMessageBox {
    background-color: #FFFFFF;
}

QMessageBox QLabel {
    color: #1A1A1A;
    font-size: 11px;
    text-transform: none;
    letter-spacing: 0px;
}

QMessageBox QPushButton {
    min-width: 80px;
    padding: 7px 14px;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    background-color: #E8E8E8;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #D1D1D1;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #B0B0B0;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QDialog {
    background-color: #FFFFFF;
}

QDialog QLabel {
    color: #1A1A1A;
    font-size: 11px;
    text-transform: none;
    letter-spacing: 0px;
}

QDialog QPushButton {
    background-color: #F5F5F5;
    color: #1A1A1A;
    border: 1px solid #D1D1D1;
    border-radius: 5px;
    padding: 7px 12px;
}

QDialog QPushButton:hover {
    background-color: #E8E8E8;
    border: 1px solid #00D9FF;
    color: #00D9FF;
}
"""


def make_separator():
    sep = QFrame()
    sep.setObjectName("separator")
    sep.setFrameShape(QFrame.Shape.HLine)
    sep.setFixedHeight(1)
    return sep


def make_label(text):
    lbl = QLabel(text)
    lbl.setMinimumHeight(16)
    return lbl


def make_copy_btn(parent, get_text_fn, tooltip_text="Копировать"):
    """Create compact round copy icon button"""
    btn = QPushButton("⎘")
    btn.setObjectName("copy_btn")
    btn.setToolTip(tooltip_text)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setFixedSize(20, 20)
    btn.setStyleSheet("""
        QPushButton#copy_btn {
            background-color: transparent;
            color: #6b7280;
            border: none;
            border-radius: 10px;
            font-size: 11px;
            padding: 0px;
        }
        QPushButton#copy_btn:hover {
            color: #fbbf24;
            background-color: #1a1d26;
        }
    """)

    btn._parent_widget = parent

    def do_copy():
        val = get_text_fn() if callable(get_text_fn) else get_text_fn
        if val and val not in ('-', '', ' '):
            QApplication.clipboard().setText(val)
            btn.setText("✓")
            QTimer.singleShot(1200, lambda: btn.setText("⎘"))

    btn.clicked.connect(do_copy)
    return btn


# ── Async HTTP worker ─────────────────────────────────────────────────────────

class NetWorker(QThread):
    """Generic async HTTP worker — keeps UI thread unblocked."""
    result  = pyqtSignal(object)
    error   = pyqtSignal(str)

    def __init__(self, method: str, url: str, data=None):
        super().__init__()
        self.method = method   # 'GET' | 'POST'
        self.url    = url
        self.data   = data

    def run(self):
        try:
            if self.method == 'POST':
                r = requests.post(self.url, data=self.data, timeout=15)
            else:
                r = requests.get(self.url, timeout=10)
            r.raise_for_status()
            self.result.emit(r)
        except Exception as e:
            self.error.emit(str(e))


class BTCTransactionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.legacy_address  = ''
        self.segwit_address  = ''
        self._last_txid      = ''
        self._last_raw_hex   = ''
        self._balance_sats   = None
        self._utxo_count     = 1
        self._workers        = []
        self._copy_buttons   = []  # Track all copy buttons for language updates

        # Settings
        self.settings = QSettings("FranklinSys", "BTCWalletTool")
        self.current_theme = self.settings.value("theme", "dark")
        self.current_lang = self.settings.value("language", "ru")

        self.initUI()

    def tr(self, key):
        """Get translated string for current language."""
        return get_translation(self.current_lang, key)

    # ── Worker lifecycle ─────────────────────────────────────────────────────

    def _start_worker(self, worker: NetWorker):
        """Register worker, auto-purge finished ones on each new spawn."""
        self._workers = [w for w in self._workers if w.isRunning()]
        worker.finished.connect(lambda: self._purge_workers())
        self._workers.append(worker)
        worker.start()

    def _purge_workers(self):
        self._workers = [w for w in self._workers if w.isRunning()]

    # ────────────────────────────────────────────────────────────────────────
    # UI BUILD
    # ────────────────────────────────────────────────────────────────────────

    def initUI(self):
        self.setWindowTitle(self.tr("app_title"))
        self.setWindowIcon(get_app_icon())
        self.setMinimumWidth(648)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 12, 16, 12)
        root.setSpacing(0)

        # ── Header with controls ────────────────────────────────────────────
        header_row = QHBoxLayout()
        header_row.setSpacing(10)

        title_col = QVBoxLayout()
        title_col.setSpacing(0)
        title = QLabel("BITCOIN WALLET TOOL")
        title.setObjectName("title_label")
        title.setMinimumHeight(22)
        sub = QLabel("SECURE OFFLINE TRANSACTION BUILDER")
        sub.setObjectName("sub_label")
        sub.setMinimumHeight(12)
        title_col.addWidget(title)
        title_col.addWidget(sub)
        header_row.addLayout(title_col, 1)

        # Compact controls row
        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(6)
        ctrl_row.setContentsMargins(0, 0, 0, 0)

        self.theme_selector = QComboBox()
        self.theme_selector.addItems(["Dark", "Light"])
        self.theme_selector.setCurrentIndex(0 if self.current_theme == "dark" else 1)
        self.theme_selector.setFixedHeight(28)
        self.theme_selector.setFixedWidth(72)
        self.theme_selector.setStyleSheet("""
            QComboBox {
                background-color: #1a1d26;
                border: 1px solid #374151;
                border-radius: 4px;
                color: #d1d5db;
                padding: 4px 8px;
                font-size: 10px;
                font-weight: 500;
            }
            QComboBox:hover {
                border: 1px solid #fbbf24;
                color: #fbbf24;
            }
        """)
        self.theme_selector.currentIndexChanged.connect(self.change_theme_by_index)
        ctrl_row.addWidget(self.theme_selector)

        self.lang_selector = QComboBox()
        self.lang_selector.addItems(["RU", "EN"])
        self.lang_selector.setCurrentIndex(0 if self.current_lang == "ru" else 1)
        self.lang_selector.setFixedHeight(28)
        self.lang_selector.setFixedWidth(56)
        self.lang_selector.setStyleSheet("""
            QComboBox {
                background-color: #1a1d26;
                border: 1px solid #374151;
                border-radius: 4px;
                color: #d1d5db;
                padding: 4px 8px;
                font-size: 10px;
                font-weight: 500;
            }
            QComboBox:hover {
                border: 1px solid #fbbf24;
                color: #fbbf24;
            }
        """)
        self.lang_selector.currentIndexChanged.connect(self.change_language_by_index)
        ctrl_row.addWidget(self.lang_selector)

        self.btn_help = QPushButton("?")
        self.btn_help.setFixedSize(28, 28)
        self.btn_help.setToolTip(self.tr("help"))
        self.btn_help.setStyleSheet("""
            QPushButton {
                background-color: #1a1d26;
                color: #fbbf24;
                border: 1px solid #fbbf24;
                border-radius: 14px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #fbbf24;
                color: #0f1117;
            }
        """)
        self.btn_help.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_help.clicked.connect(self.show_help)
        ctrl_row.addWidget(self.btn_help)

        header_row.addLayout(ctrl_row)
        root.addLayout(header_row)
        root.addSpacing(6)
        root.addWidget(make_separator())
        root.addSpacing(6)

        # ── Private Key ─────────────────────────────────────────────────────
        root.addWidget(make_label(self.tr("priv_key")))
        root.addSpacing(3)
        key_row = QHBoxLayout()
        key_row.setSpacing(6)
        self.input_priv_key = QLineEdit()
        self.input_priv_key.setPlaceholderText(self.tr("priv_key_ph"))
        self.input_priv_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_priv_key.setFixedHeight(30)
        self.input_priv_key.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        key_row.addWidget(self.input_priv_key, 1)
        self.btn_show_key = QPushButton("👁")
        self.btn_show_key.setObjectName("copy_btn")
        self.btn_show_key.setStyleSheet('min-width:30px;max-width:30px;min-height:30px;max-height:30px;padding:0;')
        self.btn_show_key.setToolTip(self.tr("copy_tooltip"))
        self.btn_show_key.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_show_key.clicked.connect(self.toggle_key_visibility)
        key_row.addWidget(self.btn_show_key)
        root.addLayout(key_row)
        root.addSpacing(5)

        self.btn_recover = QPushButton(self.tr("recover"))
        self.btn_recover.setObjectName("primary_btn")
        self.btn_recover.setFixedHeight(32)
        self.btn_recover.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_recover.clicked.connect(self.recover_addresses)
        root.addWidget(self.btn_recover)
        root.addSpacing(6)
        root.addWidget(make_separator())
        root.addSpacing(6)

        # ── Address selector ────────────────────────────────────────────────
        root.addWidget(make_label(self.tr("address")))
        root.addSpacing(3)
        addr_row = QHBoxLayout()
        addr_row.setSpacing(6)
        self.address_selector = QComboBox()
        self.address_selector.setFixedHeight(32)
        self.address_selector.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        addr_row.addWidget(self.address_selector)
        addr_row.addWidget(make_copy_btn(self, self.get_selected_address, self.tr("copy_tooltip")))
        root.addLayout(addr_row)
        root.addSpacing(6)

        # ── Verify card ─────────────────────────────────────────────────────
        verify_frame = QFrame()
        verify_frame.setObjectName("card")
        vfl = QVBoxLayout(verify_frame)
        vfl.setContentsMargins(12, 10, 12, 10)
        vfl.setSpacing(5)

        self.vf_title = QLabel(self.tr("verification"))
        self.vf_title.setStyleSheet("color:#d1d5db;font-size:10px;letter-spacing:1px;")
        self.vf_title.setMinimumHeight(16)
        vfl.addWidget(self.vf_title)

        _TAG_SS  = "color:#9ca3af;font-size:10px;letter-spacing:0px;text-transform:none;min-width:115px;max-width:115px;"
        _VAL_SS  = "color:#d1d5db;font-size:10px;font-family:'Courier New','Consolas',monospace;text-transform:none;letter-spacing:0px;"
        _WIF_SS  = "color:#d1d5db;font-size:10px;font-family:'Courier New','Consolas',monospace;text-transform:none;letter-spacing:0px;"

        # Legacy row
        lr = QHBoxLayout(); lr.setSpacing(6); lr.setContentsMargins(0, 0, 0, 0)
        self.lbl_legacy_tag = QLabel(self.tr("legacy")); self.lbl_legacy_tag.setStyleSheet(_TAG_SS)
        self.lbl_legacy_tag.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.lbl_legacy_val = QLabel("—")
        self.lbl_legacy_val.setStyleSheet(_VAL_SS)
        self.lbl_legacy_val.setMinimumHeight(20)
        self.lbl_legacy_val.setWordWrap(False)
        self.lbl_legacy_val.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.lbl_legacy_val.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.lbl_legacy_ok = QLabel("")
        self.lbl_legacy_ok.setFixedSize(16, 20)
        lr.addWidget(self.lbl_legacy_tag)
        lr.addWidget(self.lbl_legacy_val, 1)
        lr.addWidget(self.lbl_legacy_ok)
        lr.addWidget(make_copy_btn(self, lambda: self.lbl_legacy_val.text(), self.tr("copy_tooltip")))
        vfl.addLayout(lr)

        # SegWit row
        sr = QHBoxLayout(); sr.setSpacing(6); sr.setContentsMargins(0, 0, 0, 0)
        self.lbl_segwit_tag = QLabel(self.tr("segwit")); self.lbl_segwit_tag.setStyleSheet(_TAG_SS)
        self.lbl_segwit_tag.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.lbl_segwit_val = QLabel("—")
        self.lbl_segwit_val.setStyleSheet(_VAL_SS)
        self.lbl_segwit_val.setMinimumHeight(20)
        self.lbl_segwit_val.setWordWrap(False)
        self.lbl_segwit_val.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.lbl_segwit_val.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.lbl_segwit_ok = QLabel("")
        self.lbl_segwit_ok.setFixedSize(16, 20)
        sr.addWidget(self.lbl_segwit_tag)
        sr.addWidget(self.lbl_segwit_val, 1)
        sr.addWidget(self.lbl_segwit_ok)
        sr.addWidget(make_copy_btn(self, lambda: self.lbl_segwit_val.text(), self.tr("copy_tooltip")))
        vfl.addLayout(sr)

        # Key format + WIF row
        bot_row = QHBoxLayout(); bot_row.setSpacing(14); bot_row.setContentsMargins(0, 0, 0, 0)
        kt_col = QVBoxLayout(); kt_col.setSpacing(3)
        self.lbl_key_format_tag = QLabel(self.tr("key_format")); self.lbl_key_format_tag.setStyleSheet(_TAG_SS)
        self.lbl_key_format_tag.setFixedHeight(14)
        self.lbl_key_type = QLabel("—")
        self.lbl_key_type.setStyleSheet(
            "color:#9ca3af;font-size:10px;font-family:'Courier New','Consolas',monospace;"
            "text-transform:none;letter-spacing:0px;"
        )
        self.lbl_key_type.setMinimumHeight(18)
        kt_col.addWidget(self.lbl_key_format_tag); kt_col.addWidget(self.lbl_key_type)
        bot_row.addLayout(kt_col)

        wif_col = QVBoxLayout(); wif_col.setSpacing(3)
        self.lbl_wif_tag = QLabel(self.tr("wif")); self.lbl_wif_tag.setStyleSheet(_TAG_SS)
        self.lbl_wif_tag.setFixedHeight(14)
        wif_inner = QHBoxLayout(); wif_inner.setSpacing(6); wif_inner.setContentsMargins(0, 0, 0, 0)
        self.lbl_wif_val = QLabel("—")
        self.lbl_wif_val.setStyleSheet(_WIF_SS)
        self.lbl_wif_val.setMinimumHeight(18)
        self.lbl_wif_val.setWordWrap(False)
        self.lbl_wif_val.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.lbl_wif_val.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        wif_inner.addWidget(self.lbl_wif_val, 1)
        wif_inner.addWidget(make_copy_btn(self, lambda: self.lbl_wif_val.text(), self.tr("copy_tooltip")))
        wif_col.addWidget(self.lbl_wif_tag); wif_col.addLayout(wif_inner)
        bot_row.addLayout(wif_col, 1)
        vfl.addLayout(bot_row)

        root.addWidget(verify_frame)
        root.addSpacing(6)

        # ── Balance ──────────────────────────────────────────────────────────
        bal_row = QHBoxLayout()
        bal_row.setSpacing(6)
        bal_left = QVBoxLayout(); bal_left.setSpacing(2)
        bal_left.addWidget(make_label(self.tr("balance")))
        self.output_balance = QLabel("—")
        self.output_balance.setObjectName("value_label")
        self.output_balance.setFixedHeight(24)
        bal_left.addWidget(self.output_balance)
        bal_row.addLayout(bal_left)
        bal_row.addStretch()

        self.btn_check_balance = QPushButton(self.tr("check_balance"))
        self.btn_check_balance.setFixedHeight(30)
        self.btn_check_balance.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_check_balance.clicked.connect(self.check_balance)
        bal_row.addWidget(self.btn_check_balance)
        bal_row.addWidget(make_copy_btn(self, lambda: self.output_balance.text().replace(' BTC', ''), self.tr("copy_tooltip")))
        root.addLayout(bal_row)
        root.addSpacing(6)
        root.addWidget(make_separator())
        root.addSpacing(6)

        # ── Tabs ─────────────────────────────────────────────────────────────
        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        # ── Tab 1: BROADCAST ─────────────────────────────────────────────────
        tab_send = QWidget()
        tsl = QVBoxLayout(tab_send)
        tsl.setContentsMargins(8, 10, 8, 6)
        tsl.setSpacing(5)

        tsl.addWidget(make_label(self.tr("dest_addr")))
        self.input_dest = QLineEdit()
        self.input_dest.setPlaceholderText(self.tr("dest_placeholder"))
        self.input_dest.setFixedHeight(30)
        self.input_dest.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        tsl.addWidget(self.input_dest)

        tsl.addWidget(make_label(self.tr("amount")))
        amt_row = QHBoxLayout(); amt_row.setSpacing(6)
        self.input_amount = QLineEdit()
        self.input_amount.setPlaceholderText(self.tr("amount_ph"))
        self.input_amount.setFixedHeight(30)
        self.input_amount.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.input_amount.textChanged.connect(self._recalc_net)
        amt_row.addWidget(self.input_amount, 1)
        self.btn_max = QPushButton(self.tr("max"))
        self.btn_max.setFixedSize(52, 30)
        self.btn_max.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_max.clicked.connect(self._fill_max_amount)
        amt_row.addWidget(self.btn_max)
        tsl.addLayout(amt_row)

        tsl.addWidget(make_label(self.tr("fee")))
        fee_row = QHBoxLayout(); fee_row.setSpacing(6)
        self.input_fee = QLineEdit()
        self.input_fee.setPlaceholderText(self.tr("fee_ph"))
        self.input_fee.setFixedHeight(30)
        self.input_fee.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.input_fee.textChanged.connect(self._recalc_net)
        fee_row.addWidget(self.input_fee, 1)
        self.btn_suggest_fee = QPushButton(self.tr("suggest"))
        self.btn_suggest_fee.setFixedHeight(30)
        self.btn_suggest_fee.setMinimumWidth(80)
        self.btn_suggest_fee.setMaximumWidth(110)
        self.btn_suggest_fee.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_suggest_fee.clicked.connect(self.suggest_fee)
        fee_row.addWidget(self.btn_suggest_fee)
        tsl.addLayout(fee_row)

        self.lbl_net_send = QLabel(self.tr("net_send_placeholder"))
        self.lbl_net_send.setMinimumHeight(16)
        self.lbl_net_send.setStyleSheet(
            "color:#9ca3af;font-size:10px;letter-spacing:0px;"
            "padding:0px;"
        )
        tsl.addWidget(self.lbl_net_send)

        self.btn_send = QPushButton(self.tr("broadcast"))
        self.btn_send.setObjectName("danger_btn")
        self.btn_send.setFixedHeight(30)
        self.btn_send.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_send.clicked.connect(self.send_transaction)
        tsl.addWidget(self.btn_send)

        tsl.addWidget(make_label(self.tr("txid")))
        txid_row = QHBoxLayout(); txid_row.setSpacing(6)
        self.output_txid = QLabel("—")
        self.output_txid.setMinimumHeight(28)
        self.output_txid.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.output_txid.setStyleSheet(
            "color:#fbbf24;font-size:10px;font-family:'Courier New','Consolas',monospace;"
            "padding:4px 8px;background:#0b0e13;"
            "border:1px solid #2a2d35;border-radius:5px;"
        )
        txid_row.addWidget(self.output_txid, 1)
        txid_row.addWidget(make_copy_btn(self, lambda: self._last_txid, self.tr("copy_tooltip")))
        tsl.addLayout(txid_row)
        tsl.addStretch()

        # ── Tab 2: OFFLINE / RAW HEX ─────────────────────────────────────────
        tab_offline = QWidget()
        tol = QVBoxLayout(tab_offline)
        tol.setContentsMargins(8, 10, 8, 6)
        tol.setSpacing(5)

        self.lbl_offline_info = QLabel(self.tr("offline_info"))
        self.lbl_offline_info.setMinimumHeight(16)
        self.lbl_offline_info.setStyleSheet("color:#9ca3af;font-size:10px;letter-spacing:0px;")
        tol.addWidget(self.lbl_offline_info)

        tol.addWidget(make_label(self.tr("dest_addr")))
        self.input_dest_offline = QLineEdit()
        self.input_dest_offline.setPlaceholderText(self.tr("dest_addr_ph"))
        self.input_dest_offline.setFixedHeight(30)
        self.input_dest_offline.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        tol.addWidget(self.input_dest_offline)

        tol.addWidget(make_label(self.tr("amount")))
        amt_off_row = QHBoxLayout(); amt_off_row.setSpacing(6)
        self.input_amount_offline = QLineEdit()
        self.input_amount_offline.setPlaceholderText(self.tr("amount_ph"))
        self.input_amount_offline.setFixedHeight(30)
        self.input_amount_offline.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.input_amount_offline.textChanged.connect(self._recalc_net_offline)
        amt_off_row.addWidget(self.input_amount_offline, 1)
        self.btn_max_offline = QPushButton(self.tr("max"))
        self.btn_max_offline.setFixedSize(52, 30)
        self.btn_max_offline.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_max_offline.clicked.connect(self._fill_max_amount_offline)
        amt_off_row.addWidget(self.btn_max_offline)
        tol.addLayout(amt_off_row)

        tol.addWidget(make_label(self.tr("fee")))
        fee_off_row = QHBoxLayout(); fee_off_row.setSpacing(6)
        self.input_fee_offline = QLineEdit()
        self.input_fee_offline.setPlaceholderText(self.tr("fee_ph"))
        self.input_fee_offline.setFixedHeight(30)
        self.input_fee_offline.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.input_fee_offline.textChanged.connect(self._recalc_net_offline)
        fee_off_row.addWidget(self.input_fee_offline, 1)
        self.btn_suggest_fee2 = QPushButton(self.tr("suggest"))
        self.btn_suggest_fee2.setFixedHeight(30)
        self.btn_suggest_fee2.setMinimumWidth(80)
        self.btn_suggest_fee2.setMaximumWidth(110)
        self.btn_suggest_fee2.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_suggest_fee2.clicked.connect(self.suggest_fee_offline)
        fee_off_row.addWidget(self.btn_suggest_fee2)
        tol.addLayout(fee_off_row)

        self.lbl_net_offline = QLabel(self.tr("net_send_placeholder"))
        self.lbl_net_offline.setMinimumHeight(16)
        self.lbl_net_offline.setStyleSheet(
            "color:#9ca3af;font-size:10px;letter-spacing:0px;"
            "padding:0px;"
        )
        tol.addWidget(self.lbl_net_offline)

        self.btn_build = QPushButton(self.tr("build_raw"))
        self.btn_build.setObjectName("primary_btn")
        self.btn_build.setFixedHeight(30)
        self.btn_build.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_build.clicked.connect(self.build_raw_tx)
        tol.addWidget(self.btn_build)

        tol.addWidget(make_label(self.tr("raw_hex")))
        raw_row = QHBoxLayout(); raw_row.setSpacing(6)
        self.output_raw = QTextEdit()
        self.output_raw.setReadOnly(True)
        self.output_raw.setMinimumHeight(56)
        self.output_raw.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.output_raw.setPlaceholderText(self.tr("raw_hex_ph"))
        raw_row.addWidget(self.output_raw, 1)
        raw_row.addWidget(make_copy_btn(self, lambda: self._last_raw_hex, self.tr("copy_tooltip")))
        tol.addLayout(raw_row)
        tol.addStretch()

        tabs.addTab(tab_send,    self.tr("tab_broadcast"))
        tabs.addTab(tab_offline, self.tr("tab_offline"))

        # ── Tab 3: LOG ───────────────────────────────────────────────────────
        tab_log = QWidget()
        tlg = QVBoxLayout(tab_log)
        tlg.setContentsMargins(8, 10, 8, 6)
        tlg.setSpacing(5)

        log_hdr = QHBoxLayout()
        log_hdr.setSpacing(6)
        log_hdr.addWidget(make_label(self.tr("log")))
        log_hdr.addStretch()
        self.btn_clear_log = QPushButton(self.tr("clear"))
        self.btn_clear_log.setFixedHeight(24)
        self.btn_clear_log.setMinimumWidth(70)
        self.btn_clear_log.setMaximumWidth(90)
        self.btn_clear_log.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear_log.clicked.connect(lambda: self.log_output.clear())
        log_hdr.addWidget(self.btn_clear_log)
        log_hdr.addWidget(make_copy_btn(self, lambda: self.log_output.toPlainText(), self.tr("copy_tooltip")))
        tlg.addLayout(log_hdr)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumHeight(70)
        self.log_output.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        tlg.addWidget(self.log_output)

        tabs.addTab(tab_log, self.tr("tab_log"))
        root.addWidget(tabs)

        # Store references to tabs for refresh_ui_text
        self.tabs = tabs

        # Apply theme after all UI elements are created
        self.apply_theme()

        # Size window from real content minimum
        self.setMinimumSize(self.layout().minimumSize())
        self.resize(648, self.layout().minimumSize().height() + 20)

    # ────────────────────────────────────────────────────────────────────────
    # HELPERS
    # ────────────────────────────────────────────────────────────────────────

    def toggle_key_visibility(self):
        mode = self.input_priv_key.echoMode()
        self.input_priv_key.setEchoMode(
            QLineEdit.EchoMode.Normal
            if mode == QLineEdit.EchoMode.Password
            else QLineEdit.EchoMode.Password
        )

    def log_msg(self, msg, color="#6666aa"):
        self.log_output.append(
            f'<span style="color:{color};font-family:Courier New;">{msg}</span>'
        )
        logging.info(msg)

    def log_error(self, msg):
        self.log_output.append(
            f'<span style="color:#ff4444;font-family:Courier New;">✗ {msg}</span>'
        )
        logging.error(msg)

    def log_ok(self, msg):
        self.log_output.append(
            f'<span style="color:#44ff88;font-family:Courier New;">✓ {msg}</span>'
        )
        logging.info(msg)

    def get_selected_address(self):
        text = self.address_selector.currentText()
        if ': ' in text:
            return text.split(': ', 1)[1].strip()
        return text.strip()

    def _is_wif(self, s: str) -> bool:
        if len(s) == 51 and s[0] == '5':
            return True
        if len(s) == 52 and s[0] in ('K', 'L'):
            return True
        return False

    def _get_key(self) -> Key:
        """
        Parse private key from input field.

        Accepts:
          • WIF (5.../K.../L...)    — передаётся в Key() напрямую
          • HEX 1–64 символа       — [FIX] автоматически дополняется нулями
                                     слева до 64 символов (zfill). Это корректно:
                                     приватный ключ «f» = «000...000f» в Bitcoin.
          • HEX с 0x-prefix        — [FIX] префикс отбрасывается
        """
        pk = self.input_priv_key.text().strip()
        if not pk:
            raise ValueError("Введи приватный ключ (HEX или WIF)")

        # WIF-branch
        if self._is_wif(pk):
            return Key(pk)

        # HEX-branch
        cleaned = pk.lower()

        # [FIX] strip optional 0x prefix
        if cleaned.startswith('0x'):
            cleaned = cleaned[2:]

        # validate charset first
        if not cleaned or not all(c in '0123456789abcdef' for c in cleaned):
            raise ValueError(
                "Невалидный ключ: содержит не-шестнадцатеричные символы. "
                "Ожидается HEX (1–64 символа) или WIF (5.../K.../L...)"
            )

        if len(cleaned) > 64:
            raise ValueError(
                f"Невалидный HEX: длина={len(cleaned)} > 64 символов"
            )

        # [FIX] left-pad with zeros — ключ «f» (==15) валиден в Bitcoin,
        # его 32-байтовое представление: 000...000f
        cleaned = cleaned.zfill(64)
        return Key.from_hex(cleaned)

    def _get_utxos(self, address: str) -> list:
        r = requests.get(f"{API_URL}/address/{address}/utxo", timeout=10)
        r.raise_for_status()
        return r.json()

    def _estimated_fee_sats(self, fee_per_byte: int) -> int:
        """Preview fee using stored UTXO count (accurate after Check Balance)."""
        n = max(1, self._utxo_count)
        return (180 * n + 34 + 10) * fee_per_byte

    # ────────────────────────────────────────────────────────────────────────
    # ACTIONS
    # ────────────────────────────────────────────────────────────────────────

    def recover_addresses(self):
        try:
            key = self._get_key()

            self.legacy_address = key.address
            self.segwit_address = key.segwit_address

            self.address_selector.clear()
            self.address_selector.addItem(f"Legacy: {self.legacy_address}")
            self.address_selector.addItem(f"SegWit (bech32): {self.segwit_address}")

            pk     = self.input_priv_key.text().strip()
            is_wif = self._is_wif(pk)
            fmt    = (
                f"WIF ({'compressed' if is_wif and pk[0] in ('K', 'L') else 'uncompressed'})"
                if is_wif else "HEX"
            )

            self.lbl_legacy_val.setText(self.legacy_address)
            self.lbl_segwit_val.setText(self.segwit_address)
            self.lbl_legacy_ok.setText("✓")
            self.lbl_legacy_ok.setStyleSheet("color:#44ff88;font-size:13px;padding:0;")
            self.lbl_segwit_ok.setText("✓")
            self.lbl_segwit_ok.setStyleSheet("color:#44ff88;font-size:13px;padding:0;")
            self.lbl_key_type.setText(fmt)
            self.lbl_key_type.setStyleSheet(
                "color:#fbbf24;font-size:10px;font-family:'Courier New','Consolas',monospace;"
                "text-transform:none;letter-spacing:0px;"
            )
            wif = key.to_wif()
            self.lbl_wif_val.setText(wif)

            self.log_ok(f"Format:  {fmt}")
            self.log_ok(f"Legacy:  {self.legacy_address}")
            self.log_ok(f"SegWit:  {self.segwit_address}")
            # WIF — приватный ключ, в лог НЕ пишем (ни в UI-лог, ни в файл)

        except Exception as e:
            self.lbl_legacy_ok.setText("✗")
            self.lbl_legacy_ok.setStyleSheet("color:#ff4444;font-size:13px;padding:0;")
            self.lbl_segwit_ok.setText("✗")
            self.lbl_segwit_ok.setStyleSheet("color:#ff4444;font-size:13px;padding:0;")
            self.lbl_key_type.setText("ERROR")
            self.lbl_key_type.setStyleSheet(
                "color:#ef4444;font-size:10px;font-family:'Courier New','Consolas',monospace;"
                "text-transform:none;letter-spacing:0px;"
            )
            self.log_error(f"recover_addresses: {e}")

    def check_balance(self):
        addr = self.get_selected_address()
        if not addr:
            self.log_error("Сначала восстанови адрес")
            return
        self.output_balance.setText("…")

        # [FIX-ARCH] вынесено в NetWorker — не блокирует UI thread
        worker = NetWorker('GET', f"{API_URL}/address/{addr}/utxo")

        def on_result(r):
            try:
                utxos = r.json()
                self._balance_sats = sum(u["value"] for u in utxos)
                self._utxo_count   = max(1, len(utxos))
                total = self._balance_sats / 1e8
                self.output_balance.setText(f"{total:.8f} BTC")
                self.log_ok(
                    f"Balance [{addr[:14]}…] → {total:.8f} BTC  "
                    f"({len(utxos)} UTXO)"
                )
                self._recalc_net()
                self._recalc_net_offline()
            except Exception as e:
                self.output_balance.setText("—")
                self.log_error(f"check_balance parse: {e}")

        def on_error(msg):
            self.output_balance.setText("—")
            self.log_error(f"check_balance: {msg}")

        worker.result.connect(on_result)
        worker.error.connect(on_error)
        self._start_worker(worker)

    # ── Fee preview ──────────────────────────────────────────────────────────

    def _recalc_net(self):
        self._recalc_net_label(self.input_amount, self.input_fee, self.lbl_net_send)

    def _recalc_net_offline(self):
        self._recalc_net_label(
            self.input_amount_offline, self.input_fee_offline, self.lbl_net_offline
        )

    def _recalc_net_label(self, amt_input, fee_input, label):
        """
        Preview: показывает что получит адресат и сколько спишется с баланса
        - Получатель получит: amount_btc (как введено в поле)
        - С баланса спишется: amount_btc + fee
        """
        try:
            amt_btc = float(amt_input.text().strip() or "0")
            fee_pb = int(fee_input.text().strip() or "0")
            fee_sats = self._estimated_fee_sats(fee_pb)
            n = self._utxo_count
            note = f" ({n} UTXO)" if n > 1 else ""

            if amt_btc == 0:
                # MAX режим: отправится весь баланс минус комиссия
                if self._balance_sats is not None:
                    send_sats = self._balance_sats - fee_sats
                    if send_sats > 546:
                        label.setText(
                            f"<span style='color:#e8e8f0'>Получит адресат: </span>"
                            f"<span style='color:#44ff88'>{send_sats/1e8:.8f} BTC</span>"
                            f"  <span style='color:#444466'>|</span>  "
                            f"<span style='color:#e8e8f0'>Комиссия: </span>"
                            f"<span style='color:#f7931a'>{fee_sats} sat{note}</span>"
                        )
                    else:
                        label.setText("<span style='color:#ff4444'>Недостаточно для покрытия комиссии</span>")
                else:
                    label.setText("<span style='color:#444466'>Нажми CHECK BALANCE для расчёта MAX</span>")
            else:
                # Пользователь ввёл сумму: она и уйдёт получателю
                send_sats = int(amt_btc * 1e8)
                required_total = send_sats + fee_sats

                if self._balance_sats is not None and required_total > self._balance_sats:
                    label.setText(
                        f"<span style='color:#ff4444'>Недостаточно: нужно {required_total} sat, "
                        f"баланс {self._balance_sats} sat</span>"
                    )
                else:
                    label.setText(
                        f"<span style='color:#e8e8f0'>Получит адресат: </span>"
                        f"<span style='color:#44ff88'>{send_sats/1e8:.8f} BTC</span>"
                        f"  <span style='color:#444466'>|</span>  "
                        f"<span style='color:#e8e8f0'>Комиссия: </span>"
                        f"<span style='color:#f7931a'>{fee_sats} sat{note}</span>"
                    )
        except Exception:
            label.setText("<span style='color:#444466'>К отправке: —  |  Комиссия: —</span>")

    # ── MAX fill ─────────────────────────────────────────────────────────────

    def _fill_max_amount(self):
        self._fill_max(self.input_amount, self.input_fee)

    def _fill_max_amount_offline(self):
        self._fill_max(self.input_amount_offline, self.input_fee_offline)

    def _fill_max(self, amt_input, fee_input):
        try:
            fee_pb = int(fee_input.text().strip() or "0")
            if fee_pb <= 0:
                self.log_error("Сначала укажи fee (sat/byte) для расчёта MAX")
                return
            if self._balance_sats is None:
                self.log_error("Сначала нажми CHECK BALANCE")
                return
            amt_input.setText(f"{self._balance_sats / 1e8:.8f}")
        except Exception as e:
            self.log_error(f"fill_max: {e}")

    # ── Fee suggest ───────────────────────────────────────────────────────────

    def suggest_fee(self):
        self._do_suggest_fee(self.input_fee)

    def suggest_fee_offline(self):
        self._do_suggest_fee(self.input_fee_offline)

    def _do_suggest_fee(self, target_input):
        # [FIX-ARCH] вынесено в NetWorker — не блокирует UI thread
        worker = NetWorker('GET', f"{API_URL}/v1/fees/recommended")

        def on_result(r):
            try:
                fees = r.json()
                mid  = fees.get("halfHourFee", fees.get("hourFee", 20))
                target_input.setText(str(mid))
                self.log_msg(
                    f"Fee: {mid} sat/byte  "
                    f"(fastest={fees.get('fastestFee')}  hour={fees.get('hourFee')})"
                )
            except Exception as e:
                self.log_error(f"suggest_fee parse: {e}")

        def on_error(msg):
            self.log_error(f"suggest_fee: {msg}")

        worker.result.connect(on_result)
        worker.error.connect(on_error)
        self._start_worker(worker)

    # ── TX build ──────────────────────────────────────────────────────────────

    def _build_tx(self, key, from_address, dest_address, fee_per_byte, amount_btc=None):
        """
        Построение транзакции с корректной логикой комиссии:
        - Комиссия ВСЕГДА вычитается из текущего баланса
        - amount_btc — это сколько ПОЛУЧИТ получатель (без комиссии)
        - Если amount_btc=None → отправить весь баланс минус комиссия
        """
        utxos = self._get_utxos(from_address)
        if not utxos:
            raise ValueError("Нет доступных UTXO")

        total_sats = sum(u["value"] for u in utxos)
        estimated_size = 180 * len(utxos) + 34 + 10
        fee = estimated_size * fee_per_byte

        if amount_btc is None:
            # MAX: отправить весь баланс минус комиссия
            send_amount = total_sats - fee
        else:
            # Пользователь указал сумму → это то, что ПОЛУЧИТ адресат
            # Проверяем, хватает ли баланса на (amount + fee)
            send_amount = int(amount_btc * 1e8)
            required_total = send_amount + fee

            if required_total > total_sats:
                raise ValueError(
                    f"Недостаточно средств: нужно {required_total} sat "
                    f"({send_amount} + {fee} комиссия), баланс {total_sats} sat"
                )

        if send_amount <= 546:
            raise ValueError(
                f"Сумма к отправке {send_amount} sat меньше dust limit (546 sat)"
            )

        tx = key.create_transaction(
            [(dest_address, send_amount, "satoshi")],
            fee=fee,
            replace_by_fee=False,
        )
        return tx, total_sats, fee, send_amount

    def send_transaction(self):
        try:
            key      = self._get_key()
            dest     = self.input_dest.text().strip()
            fee_str  = self.input_fee.text().strip()
            amt_str  = self.input_amount.text().strip()

            if not dest:
                raise ValueError("Укажи адрес получателя")
            if not fee_str:
                raise ValueError("Укажи комиссию (sat/byte)")

            fee_per_byte = int(fee_str)
            amount_btc   = float(amt_str) if amt_str else None
            from_address = self.get_selected_address()

            utxos = self._get_utxos(from_address)
            total_sats = sum(u["value"] for u in utxos)
            estimated_size = 180 * len(utxos) + 34 + 10
            fee = estimated_size * fee_per_byte

            if amount_btc is None:
                send_amount = total_sats - fee
                total_debit = total_sats
                send_label = f"{send_amount/1e8:.8f} BTC (весь баланс минус комиссия)"
            else:
                send_amount = int(amount_btc * 1e8)
                total_debit = send_amount + fee
                send_label = f"{send_amount/1e8:.8f} BTC"

            confirm = QMessageBox(self)
            confirm.setWindowTitle("⚠ ПОДТВЕРЖДЕНИЕ ОТПРАВКИ")
            confirm.setText(
                f"ВНИМАНИЕ: Транзакция будет немедленно отправлена в сеть Bitcoin!\n\n"
                f"  От:                {from_address[:32]}…\n"
                f"  Кому:              {dest[:32]}…\n"
                f"  Получит адресат:   {send_label}\n"
                f"  Комиссия:          {fee} sat ({fee_per_byte} sat/byte)\n"
                f"  Спишется с баланса: {total_debit/1e8:.8f} BTC\n\n"
                f"Подтвердить отправку?"
            )
            confirm.setStyleSheet(DARK_STYLE)
            confirm.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if confirm.exec() != QMessageBox.StandardButton.Yes:
                return

            tx, total_sats, fee, send_amount = self._build_tx(
                key, from_address, dest, fee_per_byte, amount_btc
            )
            r = requests.post(f"{API_URL}/tx", data=tx, timeout=15)

            if r.status_code == 200:
                txid = r.text.strip()
                self._last_txid = txid
                disp = txid[:32] + "…" if len(txid) > 32 else txid
                self.output_txid.setText(disp)
                self.log_ok(f"TX отправлена!")
                self.log_ok(f"TXID: {txid}")
                self.log_msg(f"Sent: {send_amount/1e8:.8f} BTC  Fee: {fee} sat")
            else:
                self.log_error(f"API error {r.status_code}: {r.text[:200]}")

        except Exception as e:
            self.log_error(f"send_transaction: {e}")

    def build_raw_tx(self):
        try:
            key          = self._get_key()
            dest         = self.input_dest_offline.text().strip()
            fee_str      = self.input_fee_offline.text().strip()
            amt_str      = self.input_amount_offline.text().strip()

            if not dest:
                raise ValueError("Укажи адрес получателя")
            if not fee_str:
                raise ValueError("Укажи комиссию (sat/byte)")

            fee_per_byte = int(fee_str)
            amount_btc   = float(amt_str) if amt_str else None
            from_address = self.get_selected_address()

            tx_hex, total_sats, fee, send_amount = self._build_tx(
                key, from_address, dest, fee_per_byte, amount_btc
            )
            self._last_raw_hex = tx_hex
            self.output_raw.setPlainText(tx_hex)

            self.log_ok("✓ Raw TX построена (НЕ отправлена в сеть)")
            self.log_msg(
                f"Получит адресат: {send_amount/1e8:.8f} BTC  |  "
                f"Комиссия: {fee} sat  |  "
                f"Баланс: {total_sats/1e8:.8f} BTC"
            )
            self.log_msg(f"Размер TX: {len(tx_hex)//2} байт")
            self.log_msg("⚠ Для отправки: mempool.space/tx/push ИЛИ через mining pool")
            self.log_msg("→ HEX скопирован в буфер (нажми ⎘ справа)")

        except Exception as e:
            self.log_error(f"build_raw_tx: {e}")

    # ── Theme & Language ──────────────────────────────────────────────────────

    def change_theme_by_index(self, index):
        self.current_theme = "dark" if index == 0 else "light"
        self.settings.setValue("theme", self.current_theme)
        self.apply_theme()

    def change_language_by_index(self, index):
        self.current_lang = "ru" if index == 0 else "en"
        self.settings.setValue("language", self.current_lang)
        self.refresh_ui_text()

    def refresh_ui_text(self):
        """Update all UI text elements to current language without restart."""
        self.setWindowTitle(self.tr("app_title"))

        # Update buttons
        self.btn_help.setToolTip(self.tr("help"))
        self.btn_show_key.setToolTip(self.tr("copy_tooltip"))
        self.btn_recover.setText(self.tr("recover"))

        # Update all copy buttons
        for btn in self._copy_buttons:
            if hasattr(btn, 'update_copy_text'):
                btn.update_copy_text()
            btn.setToolTip(self.tr("copy_tooltip"))

        # Verification card
        self.vf_title.setText(self.tr("verification"))
        self.lbl_legacy_tag.setText(self.tr("legacy"))
        self.lbl_segwit_tag.setText(self.tr("segwit"))
        self.lbl_wif_tag.setText(self.tr("wif"))

        # Balance section
        self.btn_check_balance.setText(self.tr("check_balance"))

        # Tabs
        self.tabs.setTabText(0, self.tr("tab_broadcast"))
        self.tabs.setTabText(1, self.tr("tab_offline"))

        # Send tab
        self.btn_max.setText(self.tr("max"))
        self.btn_suggest_fee.setText(self.tr("suggest"))
        self.btn_send.setText(self.tr("btn_send"))

        # Offline tab
        self.btn_max_offline.setText(self.tr("max"))
        self.btn_suggest_fee2.setText(self.tr("suggest"))
        self.btn_build.setText(self.tr("build_raw"))

        # Log
        self.btn_clear_log.setText(self.tr("clear"))

        # Update placeholders
        self.input_priv_key.setPlaceholderText(self.tr("priv_key_ph"))
        self.input_dest.setPlaceholderText(self.tr("dest_placeholder"))
        self.input_amount.setPlaceholderText(self.tr("amount_placeholder"))
        self.input_fee.setPlaceholderText(self.tr("fee_ph"))
        self.input_dest_offline.setPlaceholderText(self.tr("dest_placeholder"))
        self.input_amount_offline.setPlaceholderText(self.tr("amount_placeholder"))
        self.input_fee_offline.setPlaceholderText(self.tr("fee_ph"))
        self.output_raw.setPlaceholderText(self.tr("raw_hex_ph"))

    def apply_theme(self):
        if self.current_theme == "dark":
            self.setStyleSheet(DARK_STYLE)
            # Verification frame inline styles for dark theme
            _TAG_SS  = "color:#9ca3af;font-size:10px;letter-spacing:0px;text-transform:none;"
            _VAL_SS  = "color:#d1d5db;font-size:10px;font-family:'Courier New','Consolas',monospace;text-transform:none;letter-spacing:0px;"
            _WIF_SS  = "color:#d1d5db;font-size:10px;font-family:'Courier New','Consolas',monospace;text-transform:none;letter-spacing:0px;"
            _KEY_SS  = "color:#9ca3af;font-size:10px;font-family:'Courier New','Consolas',monospace;text-transform:none;letter-spacing:0px;"
            _TITLE_SS = "color:#d1d5db;font-size:10px;letter-spacing:1px;text-transform:uppercase;"
            _TXID_SS = "color:#fbbf24;font-size:10px;font-family:'Courier New','Consolas',monospace;padding:4px 8px;background:#0b0e13;border:1px solid #2a2d35;border-radius:5px;"
            _NET_SS = "color:#9ca3af;font-size:10px;letter-spacing:0px;text-transform:none;padding:0px;"
            _OFFLINE_INFO_SS = "color:#9ca3af;font-size:10px;text-transform:none;letter-spacing:0px;"
        else:
            self.setStyleSheet(LIGHT_STYLE)
            # Verification frame inline styles for light theme
            _TAG_SS  = "color:#6B6B6B;font-size:10px;letter-spacing:0px;text-transform:none;"
            _VAL_SS  = "color:#1A1A1A;font-size:10px;font-family:'Courier New','Consolas',monospace;text-transform:none;letter-spacing:0px;"
            _WIF_SS  = "color:#1A1A1A;font-size:10px;font-family:'Courier New','Consolas',monospace;text-transform:none;letter-spacing:0px;"
            _KEY_SS  = "color:#6B6B6B;font-size:10px;font-family:'Courier New','Consolas',monospace;text-transform:none;letter-spacing:0px;"
            _TITLE_SS = "color:#1A1A1A;font-size:10px;letter-spacing:1px;text-transform:uppercase;"
            _TXID_SS = "color:#00A8CC;font-size:10px;font-family:'Courier New','Consolas',monospace;padding:4px 8px;background:#F5F5F5;border:1px solid #D1D1D1;border-radius:5px;"
            _NET_SS = "color:#6B6B6B;font-size:10px;letter-spacing:0px;text-transform:none;padding:0px;"
            _OFFLINE_INFO_SS = "color:#6B6B6B;font-size:10px;text-transform:none;letter-spacing:0px;"

        # Update verification frame styles
        self.vf_title.setStyleSheet(_TITLE_SS)
        self.lbl_legacy_tag.setStyleSheet(_TAG_SS)
        self.lbl_legacy_val.setStyleSheet(_VAL_SS)
        self.lbl_segwit_tag.setStyleSheet(_TAG_SS)
        self.lbl_segwit_val.setStyleSheet(_VAL_SS)
        self.lbl_key_format_tag.setStyleSheet(_TAG_SS)
        self.lbl_key_type.setStyleSheet(_KEY_SS)
        self.lbl_wif_tag.setStyleSheet(_TAG_SS)
        self.lbl_wif_val.setStyleSheet(_WIF_SS)

        # Update TXID output styles
        self.output_txid.setStyleSheet(_TXID_SS)

        # Update net send labels
        self.lbl_net_send.setStyleSheet(_NET_SS)
        self.lbl_net_offline.setStyleSheet(_NET_SS)

        # Update offline info
        self.lbl_offline_info.setStyleSheet(_OFFLINE_INFO_SS)

    def show_help(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(self.tr("help_title"))
        dialog.setWindowIcon(get_app_icon())
        dialog.setFixedSize(522, 589)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        content = QLabel(self.tr("help_content"))
        content.setWordWrap(True)
        content.setTextFormat(Qt.TextFormat.RichText)
        content.setOpenExternalLinks(True)

        # Adaptive text color based on theme
        text_color = "#e8eaed" if self.current_theme == "dark" else "#1A1A1A"
        content.setStyleSheet(
            f"line-height: 1.5; font-size: 11px; color: {text_color};"
            "padding: 0px; margin: 0px;"
        )
        content.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        content.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse |
            Qt.TextInteractionFlag.LinksAccessibleByMouse
        )
        layout.addWidget(content)

        btn_close = QPushButton("OK")
        btn_close.setObjectName("primary_btn")
        btn_close.setFixedHeight(32)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.clicked.connect(dialog.close)
        layout.addWidget(btn_close)

        if self.current_theme == "dark":
            dialog.setStyleSheet(DARK_STYLE)
        else:
            dialog.setStyleSheet(LIGHT_STYLE)

        dialog.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = BTCTransactionApp()
    window.show()
    sys.exit(app.exec())
