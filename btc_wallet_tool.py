from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit, QMessageBox, QComboBox,
    QFrame, QTabWidget, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon
from bit import Key
import sys
import os
import requests
import logging

# ── Отключаем авто-масштабирование Qt — должно быть ДО создания QApplication ──
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0"
os.environ["QT_SCALE_FACTOR"] = "1"
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"

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

DARK_STYLE = """
QWidget {
    background-color: #0a0a0f;
    color: #e8e8f0;
    font-family: 'Courier New', monospace;
    font-size: 12px;
}

QTabWidget::pane {
    border: 1px solid #1e1e2e;
    background-color: #0d0d18;
    border-radius: 8px;
}

QTabBar::tab {
    background-color: #111120;
    color: #6666aa;
    padding: 10px 24px;
    border: none;
    font-size: 12px;
    letter-spacing: 2px;
    text-transform: uppercase;
}

QTabBar::tab:selected {
    background-color: #0d0d18;
    color: #f7931a;
    border-bottom: 2px solid #f7931a;
}

QTabBar::tab:hover {
    color: #ffb347;
}

QLabel {
    color: #8888bb;
    font-size: 11px;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding-bottom: 2px;
}

QLabel#value_label {
    color: #f7931a;
    font-size: 18px;
    font-weight: bold;
    letter-spacing: 1px;
    text-transform: none;
    padding: 0px;
}

QLabel#title_label {
    color: #f7931a;
    font-size: 17px;
    font-weight: bold;
    letter-spacing: 4px;
    padding: 0px;
}

QLabel#sub_label {
    color: #444466;
    font-size: 10px;
    letter-spacing: 3px;
    text-transform: uppercase;
    padding: 0px;
}

QLineEdit {
    background-color: #111120;
    border: 1px solid #222244;
    border-radius: 6px;
    color: #e8e8f0;
    padding: 7px 12px;
    font-family: 'Courier New', monospace;
    font-size: 11px;
    selection-background-color: #f7931a;
    selection-color: #0a0a0f;
}

QLineEdit:focus {
    border: 1px solid #f7931a;
    background-color: #14141f;
}

QLineEdit:hover {
    border: 1px solid #333366;
}

QPushButton {
    background-color: #111120;
    color: #8888bb;
    border: 1px solid #222244;
    border-radius: 6px;
    padding: 7px 14px;
    font-family: 'Courier New', monospace;
    font-size: 11px;
    letter-spacing: 1px;
    text-transform: uppercase;
}

QPushButton:hover {
    background-color: #1a1a2e;
    border: 1px solid #f7931a;
    color: #f7931a;
}

QPushButton:pressed {
    background-color: #f7931a;
    color: #0a0a0f;
}

QPushButton#primary_btn {
    background-color: #f7931a;
    color: #0a0a0f;
    border: none;
    font-weight: bold;
    font-size: 11px;
    letter-spacing: 2px;
    padding: 9px 16px;
}

QPushButton#primary_btn:hover {
    background-color: #ffb347;
    color: #0a0a0f;
}

QPushButton#primary_btn:pressed {
    background-color: #d4791a;
}

QPushButton#danger_btn {
    background-color: #1a0a0a;
    color: #ff4444;
    border: 1px solid #441111;
    font-size: 11px;
    letter-spacing: 2px;
}

QPushButton#danger_btn:hover {
    background-color: #2a0a0a;
    border: 1px solid #ff4444;
}

QPushButton#danger_btn:pressed {
    background-color: #ff4444;
    color: #0a0a0f;
}

QPushButton#copy_btn {
    background-color: transparent;
    color: #444466;
    border: none;
    padding: 4px 8px;
    font-size: 14px;
    border-radius: 4px;
    min-width: 32px;
    max-width: 32px;
}

QPushButton#copy_btn:hover {
    color: #f7931a;
    background-color: #111120;
}

QTextEdit {
    background-color: #080810;
    border: 1px solid #1a1a2e;
    border-radius: 6px;
    color: #6666aa;
    font-family: 'Courier New', monospace;
    font-size: 11px;
    padding: 8px;
}

QComboBox {
    background-color: #111120;
    border: 1px solid #222244;
    border-radius: 6px;
    color: #e8e8f0;
    padding: 7px 14px;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    min-height: 20px;
}

QComboBox:hover {
    border: 1px solid #f7931a;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #111120;
    border: 1px solid #f7931a;
    color: #e8e8f0;
    selection-background-color: #f7931a;
    selection-color: #0a0a0f;
}

QFrame#separator {
    background-color: #1a1a2e;
    max-height: 1px;
    margin: 2px 0px;
}

QFrame#card {
    background-color: #0d0d18;
    border: 1px solid #1a1a2e;
    border-radius: 10px;
    padding: 12px;
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
    lbl.setFixedHeight(16)
    return lbl


def make_copy_btn(parent, get_text_fn):
    btn = QPushButton("⎘")
    btn.setObjectName("copy_btn")
    btn.setToolTip("Копировать")
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setFixedSize(32, 32)

    def do_copy():
        val = get_text_fn()
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
        self.initUI()

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
        self.setWindowTitle('⟐ BTC TX CONSOLE')
        # FIXED SIZE — ресайз отключён, окно больше не тянется и не ломает layout
        self.setFixedSize(680, 940)
        self.setStyleSheet(DARK_STYLE)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 14, 18, 14)
        root.setSpacing(0)

        # ── Header ──────────────────────────────────────────────────────────
        title = QLabel("⟐ BTC TX")
        title.setObjectName("title_label")
        title.setFixedHeight(26)
        sub = QLabel("BITCOIN TRANSACTION CONSOLE  //  OFFLINE & BROADCAST")
        sub.setObjectName("sub_label")
        sub.setFixedHeight(14)
        root.addWidget(title)
        root.addWidget(sub)
        root.addSpacing(8)
        root.addWidget(make_separator())
        root.addSpacing(8)

        # ── Private Key ─────────────────────────────────────────────────────
        root.addWidget(make_label("PRIVATE KEY  (HEX  или  WIF)"))
        root.addSpacing(4)
        key_row = QHBoxLayout()
        key_row.setSpacing(6)
        self.input_priv_key = QLineEdit()
        self.input_priv_key.setPlaceholderText("HEX (1–64 символа, auto zero-pad)  OR  WIF: 5... / K... / L...")
        self.input_priv_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_priv_key.setFixedHeight(32)
        key_row.addWidget(self.input_priv_key)
        self.btn_show_key = QPushButton("👁")
        self.btn_show_key.setObjectName("copy_btn")
        self.btn_show_key.setFixedSize(32, 32)
        self.btn_show_key.setToolTip("Показать/скрыть ключ")
        self.btn_show_key.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_show_key.clicked.connect(self.toggle_key_visibility)
        key_row.addWidget(self.btn_show_key)
        root.addLayout(key_row)
        root.addSpacing(7)

        self.btn_recover = QPushButton("⟳  RECOVER ADDRESSES")
        self.btn_recover.setObjectName("primary_btn")
        self.btn_recover.setFixedHeight(34)
        self.btn_recover.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_recover.clicked.connect(self.recover_addresses)
        root.addWidget(self.btn_recover)
        root.addSpacing(8)
        root.addWidget(make_separator())
        root.addSpacing(8)

        # ── Address selector ────────────────────────────────────────────────
        root.addWidget(make_label("ADDRESS"))
        root.addSpacing(4)
        addr_row = QHBoxLayout()
        addr_row.setSpacing(6)
        self.address_selector = QComboBox()
        self.address_selector.setFixedHeight(34)
        self.address_selector.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        addr_row.addWidget(self.address_selector)
        addr_row.addWidget(make_copy_btn(self, self.get_selected_address))
        root.addLayout(addr_row)
        root.addSpacing(8)

        # ── Verify card ─────────────────────────────────────────────────────
        verify_frame = QFrame()
        verify_frame.setObjectName("card")
        # Убрали жёсткое setFixedHeight/setMinimumHeight — фрейм сам
        # растягивается по контенту, иначе при любом DPI элементы налезали друг на друга.
        # setMaximumHeight — чтобы не отъедал место у табов ниже
        verify_frame.setMaximumHeight(125)
        vfl = QVBoxLayout(verify_frame)
        vfl.setContentsMargins(12, 10, 12, 10)
        vfl.setSpacing(7)

        vf_title = QLabel("⚑  VERIFICATION")
        vf_title.setStyleSheet("color:#8888bb;font-size:10px;letter-spacing:2px;text-transform:uppercase;")
        vfl.addWidget(vf_title)

        _TAG_SS  = "color:#555577;font-size:10px;letter-spacing:0px;text-transform:none;min-width:120px;max-width:120px;"
        _VAL_SS  = "color:#aaaacc;font-size:10px;font-family:'Courier New';text-transform:none;letter-spacing:0px;"
        _WIF_SS  = "color:#aaaacc;font-size:10px;font-family:'Courier New';text-transform:none;letter-spacing:0px;"

        # Legacy row — убрали setFixedHeight чтобы не обрезало при HiDPI
        lr = QHBoxLayout(); lr.setSpacing(4); lr.setContentsMargins(0, 0, 0, 0)
        t = QLabel("Legacy (P2PKH):"); t.setStyleSheet(_TAG_SS)
        t.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.lbl_legacy_val = QLabel("—")
        self.lbl_legacy_val.setStyleSheet(_VAL_SS)
        self.lbl_legacy_val.setMinimumHeight(18)
        self.lbl_legacy_val.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.lbl_legacy_ok = QLabel("")
        self.lbl_legacy_ok.setFixedSize(16, 18)
        lr.addWidget(t); lr.addWidget(self.lbl_legacy_val, 1)
        lr.addWidget(self.lbl_legacy_ok)
        lr.addWidget(make_copy_btn(self, lambda: self.lbl_legacy_val.text()))
        vfl.addLayout(lr)

        # SegWit row
        sr = QHBoxLayout(); sr.setSpacing(4); sr.setContentsMargins(0, 0, 0, 0)
        t2 = QLabel("SegWit (bech32):"); t2.setStyleSheet(_TAG_SS)
        t2.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.lbl_segwit_val = QLabel("—")
        self.lbl_segwit_val.setStyleSheet(_VAL_SS)
        self.lbl_segwit_val.setMinimumHeight(18)
        self.lbl_segwit_val.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.lbl_segwit_ok = QLabel("")
        self.lbl_segwit_ok.setFixedSize(16, 18)
        sr.addWidget(t2); sr.addWidget(self.lbl_segwit_val, 1)
        sr.addWidget(self.lbl_segwit_ok)
        sr.addWidget(make_copy_btn(self, lambda: self.lbl_segwit_val.text()))
        vfl.addLayout(sr)

        # Key format + WIF — разделены горизонтально, минимальные высоты убраны
        bot_row = QHBoxLayout(); bot_row.setSpacing(12); bot_row.setContentsMargins(0, 0, 0, 0)
        kt_col = QVBoxLayout(); kt_col.setSpacing(2)
        t3 = QLabel("Key format:"); t3.setStyleSheet(_TAG_SS)
        self.lbl_key_type = QLabel("—")
        self.lbl_key_type.setStyleSheet(
            "color:#555577;font-size:10px;font-family:'Courier New';"
            "text-transform:none;letter-spacing:0px;"
        )
        kt_col.addWidget(t3); kt_col.addWidget(self.lbl_key_type)
        bot_row.addLayout(kt_col)

        wif_col = QVBoxLayout(); wif_col.setSpacing(2)
        t4 = QLabel("WIF:"); t4.setStyleSheet(_TAG_SS)
        wif_inner = QHBoxLayout(); wif_inner.setSpacing(4); wif_inner.setContentsMargins(0, 0, 0, 0)
        self.lbl_wif_val = QLabel("—")
        self.lbl_wif_val.setStyleSheet(_WIF_SS)
        self.lbl_wif_val.setMinimumHeight(16)
        self.lbl_wif_val.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        wif_inner.addWidget(self.lbl_wif_val, 1)
        wif_inner.addWidget(make_copy_btn(self, lambda: self.lbl_wif_val.text()))
        wif_col.addWidget(t4); wif_col.addLayout(wif_inner)
        bot_row.addLayout(wif_col, 1)
        vfl.addLayout(bot_row)

        root.addWidget(verify_frame)
        root.addSpacing(8)

        # ── Balance ──────────────────────────────────────────────────────────
        bal_row = QHBoxLayout()
        bal_row.setSpacing(6)
        bal_left = QVBoxLayout(); bal_left.setSpacing(2)
        bal_left.addWidget(make_label("BALANCE"))
        self.output_balance = QLabel("—")
        self.output_balance.setObjectName("value_label")
        self.output_balance.setFixedHeight(28)
        bal_left.addWidget(self.output_balance)
        bal_row.addLayout(bal_left)
        bal_row.addStretch()

        btn_bal = QPushButton("↻  CHECK BALANCE")
        btn_bal.setFixedHeight(32)
        btn_bal.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_bal.clicked.connect(self.check_balance)
        bal_row.addWidget(btn_bal)
        bal_row.addWidget(make_copy_btn(self, lambda: self.output_balance.text().replace(' BTC', '')))
        root.addLayout(bal_row)
        root.addSpacing(8)
        root.addWidget(make_separator())
        root.addSpacing(8)

        # ── Tabs ─────────────────────────────────────────────────────────────
        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        # [FIX-UI] убрал setFixedHeight(300) — при нестандартном шрифте
        # контент вылезал за границы или обрезался
        tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        tabs.setMinimumHeight(280)

        # ── Tab 1: BROADCAST ─────────────────────────────────────────────────
        tab_send = QWidget()
        tsl = QVBoxLayout(tab_send)
        tsl.setContentsMargins(6, 10, 6, 4)
        tsl.setSpacing(4)

        tsl.addWidget(make_label("DESTINATION ADDRESS"))
        self.input_dest_address = QLineEdit()
        self.input_dest_address.setPlaceholderText("bc1q... or 1... or 3...")
        self.input_dest_address.setFixedHeight(28)
        tsl.addWidget(self.input_dest_address)

        tsl.addWidget(make_label("AMOUNT (BTC)  —  комиссия вычитается из суммы"))
        amt_row = QHBoxLayout(); amt_row.setSpacing(6)
        self.input_amount = QLineEdit()
        self.input_amount.setPlaceholderText("0.00000000  (пусто = весь баланс)")
        self.input_amount.setFixedHeight(28)
        self.input_amount.textChanged.connect(self._recalc_net)
        amt_row.addWidget(self.input_amount)
        self.btn_max = QPushButton("MAX")
        self.btn_max.setFixedSize(52, 28)
        self.btn_max.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_max.clicked.connect(self._fill_max_amount)
        amt_row.addWidget(self.btn_max)
        tsl.addLayout(amt_row)

        tsl.addWidget(make_label("FEE (SAT/BYTE)"))
        fee_row = QHBoxLayout(); fee_row.setSpacing(6)
        self.input_fee = QLineEdit()
        self.input_fee.setPlaceholderText("напр. 20")
        self.input_fee.setFixedHeight(28)
        self.input_fee.textChanged.connect(self._recalc_net)
        fee_row.addWidget(self.input_fee)
        self.btn_suggest_fee = QPushButton("⚡ SUGGEST")
        self.btn_suggest_fee.setFixedHeight(28)
        self.btn_suggest_fee.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_suggest_fee.clicked.connect(self.suggest_fee)
        fee_row.addWidget(self.btn_suggest_fee)
        tsl.addLayout(fee_row)

        self.lbl_net_send = QLabel("К отправке: —  |  Комиссия: —")
        self.lbl_net_send.setFixedHeight(14)
        self.lbl_net_send.setStyleSheet(
            "color:#555577;font-size:10px;letter-spacing:0px;"
            "text-transform:none;padding:0px;"
        )
        tsl.addWidget(self.lbl_net_send)

        self.btn_send = QPushButton("▶  BROADCAST TRANSACTION")
        self.btn_send.setObjectName("danger_btn")
        self.btn_send.setFixedHeight(30)
        self.btn_send.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_send.clicked.connect(self.send_transaction)
        tsl.addWidget(self.btn_send)

        tsl.addWidget(make_label("TXID"))
        txid_row = QHBoxLayout(); txid_row.setSpacing(6)
        self.output_txid = QLabel("—")
        self.output_txid.setFixedHeight(28)
        self.output_txid.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.output_txid.setStyleSheet(
            "color:#f7931a;font-size:11px;font-family:'Courier New';"
            "padding:4px 8px;background:#080810;"
            "border:1px solid #1a1a2e;border-radius:6px;"
        )
        txid_row.addWidget(self.output_txid)
        txid_row.addWidget(make_copy_btn(self, lambda: self._last_txid))
        tsl.addLayout(txid_row)
        tsl.addStretch()

        # ── Tab 2: OFFLINE / RAW HEX ─────────────────────────────────────────
        tab_offline = QWidget()
        tol = QVBoxLayout(tab_offline)
        tol.setContentsMargins(6, 10, 6, 4)
        tol.setSpacing(4)

        info = QLabel("Build signed TX without broadcasting. Paste HEX → mempool.space/tx/push")
        info.setFixedHeight(14)
        info.setStyleSheet("color:#555577;font-size:10px;text-transform:none;letter-spacing:0px;")
        tol.addWidget(info)

        tol.addWidget(make_label("DESTINATION ADDRESS"))
        self.input_dest_offline = QLineEdit()
        self.input_dest_offline.setPlaceholderText("bc1q... or 1... or 3...")
        self.input_dest_offline.setFixedHeight(28)
        tol.addWidget(self.input_dest_offline)

        tol.addWidget(make_label("AMOUNT (BTC)  —  комиссия вычитается из суммы"))
        amt_off_row = QHBoxLayout(); amt_off_row.setSpacing(6)
        self.input_amount_offline = QLineEdit()
        self.input_amount_offline.setPlaceholderText("0.00000000  (пусто = весь баланс)")
        self.input_amount_offline.setFixedHeight(28)
        self.input_amount_offline.textChanged.connect(self._recalc_net_offline)
        amt_off_row.addWidget(self.input_amount_offline)
        self.btn_max_offline = QPushButton("MAX")
        self.btn_max_offline.setFixedSize(52, 28)
        self.btn_max_offline.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_max_offline.clicked.connect(self._fill_max_amount_offline)
        amt_off_row.addWidget(self.btn_max_offline)
        tol.addLayout(amt_off_row)

        tol.addWidget(make_label("FEE (SAT/BYTE)"))
        fee_off_row = QHBoxLayout(); fee_off_row.setSpacing(6)
        self.input_fee_offline = QLineEdit()
        self.input_fee_offline.setPlaceholderText("напр. 20")
        self.input_fee_offline.setFixedHeight(28)
        self.input_fee_offline.textChanged.connect(self._recalc_net_offline)
        fee_off_row.addWidget(self.input_fee_offline)
        self.btn_suggest_fee2 = QPushButton("⚡ SUGGEST")
        self.btn_suggest_fee2.setFixedHeight(28)
        self.btn_suggest_fee2.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_suggest_fee2.clicked.connect(self.suggest_fee_offline)
        fee_off_row.addWidget(self.btn_suggest_fee2)
        tol.addLayout(fee_off_row)

        self.lbl_net_offline = QLabel("К отправке: —  |  Комиссия: —")
        self.lbl_net_offline.setFixedHeight(14)
        self.lbl_net_offline.setStyleSheet(
            "color:#555577;font-size:10px;letter-spacing:0px;"
            "text-transform:none;padding:0px;"
        )
        tol.addWidget(self.lbl_net_offline)

        self.btn_build = QPushButton("⬡  BUILD RAW TX  (NO BROADCAST)")
        self.btn_build.setObjectName("primary_btn")
        self.btn_build.setFixedHeight(30)
        self.btn_build.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_build.clicked.connect(self.build_raw_tx)
        tol.addWidget(self.btn_build)

        tol.addWidget(make_label("RAW HEX (SIGNED TX)"))
        raw_row = QHBoxLayout(); raw_row.setSpacing(6)
        self.output_raw = QTextEdit()
        self.output_raw.setReadOnly(True)
        self.output_raw.setFixedHeight(56)
        self.output_raw.setPlaceholderText("Signed transaction hex will appear here...")
        raw_row.addWidget(self.output_raw)
        raw_row.addWidget(make_copy_btn(self, lambda: self._last_raw_hex))
        tol.addLayout(raw_row)
        tol.addStretch()

        tabs.addTab(tab_send,    "BROADCAST")
        tabs.addTab(tab_offline, "OFFLINE / RAW HEX")
        root.addWidget(tabs, 1)   # stretch=1 — tabs забирают свободное пространство
        root.addSpacing(8)

        # ── Log ──────────────────────────────────────────────────────────────
        log_hdr = QHBoxLayout()
        log_hdr.addWidget(make_label("LOG"))
        log_hdr.addStretch()
        btn_clear = QPushButton("✕ CLEAR")
        btn_clear.setFixedHeight(24)
        btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear.clicked.connect(lambda: self.log_output.clear())
        log_hdr.addWidget(btn_clear)
        log_hdr.addWidget(make_copy_btn(self, lambda: self.log_output.toPlainText()))
        root.addLayout(log_hdr)
        root.addSpacing(4)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumHeight(100)
        self.log_output.setMaximumHeight(130)
        root.addWidget(self.log_output)

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
                "color:#f7931a;font-size:10px;font-family:'Courier New';"
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
                "color:#ff4444;font-size:10px;font-family:'Courier New';"
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
        try:
            amt_btc  = float(amt_input.text().strip() or "0")
            fee_pb   = int(fee_input.text().strip() or "0")
            fee_sats = self._estimated_fee_sats(fee_pb)
            net_sats = int(amt_btc * 1e8) - fee_sats
            n        = self._utxo_count
            note     = f" ({n} UTXO)" if n > 1 else ""
            if net_sats > 0:
                label.setText(
                    f"<span style='color:#e8e8f0'>К отправке: </span>"
                    f"<span style='color:#44ff88'>{net_sats/1e8:.8f} BTC</span>"
                    f"  <span style='color:#444466'>|</span>  "
                    f"<span style='color:#e8e8f0'>Комиссия: </span>"
                    f"<span style='color:#f7931a'>{fee_sats} sat{note}</span>"
                )
            else:
                label.setText(
                    "<span style='color:#ff4444'>Недостаточно для покрытия комиссии</span>"
                )
        except Exception:
            label.setText(
                "<span style='color:#444466'>К отправке: —  |  Комиссия: —</span>"
            )

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
        utxos          = self._get_utxos(from_address)
        if not utxos:
            raise ValueError("Нет доступных UTXO")
        total_sats     = sum(u["value"] for u in utxos)
        estimated_size = 180 * len(utxos) + 34 + 10
        fee            = estimated_size * fee_per_byte

        if amount_btc is None:
            send_amount = total_sats - fee
        else:
            send_amount = int(amount_btc * 1e8) - fee

        if send_amount <= 546:
            raise ValueError(
                f"Недостаточно после комиссии: {send_amount} sat (dust limit = 546)"
            )
        if send_amount > total_sats - fee:
            raise ValueError(
                f"Сумма превышает баланс: max={(total_sats - fee)/1e8:.8f} BTC"
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
            dest     = self.input_dest_address.text().strip()
            fee_str  = self.input_fee.text().strip()
            amt_str  = self.input_amount.text().strip()

            if not dest:
                raise ValueError("Укажи адрес получателя")
            if not fee_str:
                raise ValueError("Укажи комиссию (sat/byte)")

            fee_per_byte = int(fee_str)
            amount_btc   = float(amt_str) if amt_str else None
            from_address = self.get_selected_address()

            utxos       = self._get_utxos(from_address)
            total_btc   = sum(u["value"] for u in utxos) / 1e8
            send_label  = f"{amount_btc:.8f} BTC" if amount_btc else f"{total_btc:.8f} BTC (MAX)"

            confirm = QMessageBox(self)
            confirm.setWindowTitle("ПОДТВЕРЖДЕНИЕ")
            confirm.setText(
                f"Подтвердить транзакцию?\n\n"
                f"  От:     {from_address[:28]}…\n"
                f"  Кому:   {dest[:28]}…\n"
                f"  Сумма:  {send_label}\n"
                f"  Fee:    {fee_per_byte} sat/byte"
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

            self.log_ok("Raw TX built (NOT broadcast)")
            self.log_msg(
                f"Total: {total_sats/1e8:.8f} BTC  |  "
                f"Fee: {fee} sat  |  Send: {send_amount/1e8:.8f} BTC"
            )
            self.log_msg(f"Size: {len(tx_hex)//2} bytes")
            self.log_msg("→ Вставь hex на mempool.space/tx/push")

        except Exception as e:
            self.log_error(f"build_raw_tx: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = BTCTransactionApp()
    window.show()
    sys.exit(app.exec())
