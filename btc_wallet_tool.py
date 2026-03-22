from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit, QMessageBox, QComboBox,
    QFrame, QTabWidget, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QPalette, QClipboard, QIcon
from bit import Key
import sys
import requests
import logging
import json


logging.basicConfig(
    filename='btc_transaction.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
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
    padding: 4px 0px;
}

QLabel#title_label {
    color: #f7931a;
    font-size: 17px;
    font-weight: bold;
    letter-spacing: 4px;
    text-transform: uppercase;
    text-transform: none;
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
    padding: 10px;
    line-height: 1.6;
}

QComboBox {
    background-color: #111120;
    border: 1px solid #222244;
    border-radius: 6px;
    color: #e8e8f0;
    padding: 10px 14px;
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

QComboBox::down-arrow {
    color: #f7931a;
    width: 12px;
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
    margin: 4px 0px;
}

QFrame#card {
    background-color: #0d0d18;
    border: 1px solid #1a1a2e;
    border-radius: 10px;
    padding: 16px;
}
"""


def make_separator():
    sep = QFrame()
    sep.setObjectName("separator")
    sep.setFrameShape(QFrame.Shape.HLine)
    return sep


def make_label(text):
    lbl = QLabel(text)
    return lbl


def make_copy_btn(parent, get_text_fn):
    btn = QPushButton("⎘")
    btn.setObjectName("copy_btn")
    btn.setToolTip("Копировать")
    btn.setCursor(Qt.CursorShape.PointingHandCursor)

    def do_copy():
        val = get_text_fn()
        if val and val not in ('-', '', ' '):
            QApplication.clipboard().setText(val)
            btn.setText("✓")
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(1200, lambda: btn.setText("⎘"))

    btn.clicked.connect(do_copy)
    return btn


class FetchWorker(QThread):
    result = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            r = requests.get(self.url, timeout=10)
            self.result.emit(r.json())
        except Exception as e:
            self.error.emit(str(e))


class BTCTransactionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.legacy_address = ''
        self.segwit_address = ''
        self._last_txid = ''
        self._last_raw_hex = ''
        self._balance_sats = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('⟐ BTC TX CONSOLE')
        self.setFixedSize(620, 780)
        self.setStyleSheet(DARK_STYLE)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(0)

        # ── Header ──────────────────────────────────────────────────────
        hdr = QVBoxLayout()
        hdr.setSpacing(2)
        title = QLabel("⟐ BTC TX")
        title.setObjectName("title_label")
        sub = QLabel("BITCOIN TRANSACTION CONSOLE  //  OFFLINE & BROADCAST")
        sub.setObjectName("sub_label")
        hdr.addWidget(title)
        hdr.addWidget(sub)
        root.addLayout(hdr)
        root.addSpacing(12)
        root.addWidget(make_separator())
        root.addSpacing(10)

        # ── Key section ─────────────────────────────────────────────────
        root.addWidget(make_label("PRIVATE KEY  (HEX  или  WIF)"))
        root.addSpacing(4)
        key_row = QHBoxLayout()
        self.input_priv_key = QLineEdit()
        self.input_priv_key.setPlaceholderText("64 hex chars  OR  WIF: 5... / K... / L...")
        self.input_priv_key.setEchoMode(QLineEdit.EchoMode.Password)
        key_row.addWidget(self.input_priv_key)
        self.btn_show_key = QPushButton("👁")
        self.btn_show_key.setObjectName("copy_btn")
        self.btn_show_key.setToolTip("Показать/скрыть ключ")
        self.btn_show_key.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_show_key.clicked.connect(self.toggle_key_visibility)
        key_row.addWidget(self.btn_show_key)
        root.addLayout(key_row)
        root.addSpacing(8)

        self.btn_recover = QPushButton("⟳  RECOVER ADDRESSES")
        self.btn_recover.setObjectName("primary_btn")
        self.btn_recover.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_recover.clicked.connect(self.recover_addresses)
        root.addWidget(self.btn_recover)
        root.addSpacing(10)
        root.addWidget(make_separator())
        root.addSpacing(10)

        # ── Address section ─────────────────────────────────────────────
        root.addWidget(make_label("ADDRESS"))
        root.addSpacing(4)
        addr_row = QHBoxLayout()
        self.address_selector = QComboBox()
        self.address_selector.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        addr_row.addWidget(self.address_selector)
        addr_row.addWidget(make_copy_btn(self, self.get_selected_address))
        root.addLayout(addr_row)
        root.addSpacing(10)

        # ── Verify block ─────────────────────────────────────────────────
        verify_frame = QFrame()
        verify_frame.setObjectName("card")
        vfl = QVBoxLayout(verify_frame)
        vfl.setContentsMargins(12, 10, 12, 10)
        vfl.setSpacing(6)

        vf_title = QLabel("⚑  VERIFICATION")
        vf_title.setStyleSheet("color:#8888bb;font-size:10px;letter-spacing:2px;")
        vfl.addWidget(vf_title)

        # Legacy row
        legacy_row = QHBoxLayout()
        lbl_legacy_tag = QLabel("Legacy (P2PKH):")
        lbl_legacy_tag.setStyleSheet("color:#555577;font-size:10px;letter-spacing:0px;text-transform:none;min-width:120px;")
        self.lbl_legacy_val = QLabel("—")
        self.lbl_legacy_val.setStyleSheet("color:#aaaacc;font-size:11px;font-family:'Courier New';text-transform:none;letter-spacing:0px;")
        self.lbl_legacy_val.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.lbl_legacy_ok = QLabel("")
        self.lbl_legacy_ok.setFixedWidth(20)
        legacy_row.addWidget(lbl_legacy_tag)
        legacy_row.addWidget(self.lbl_legacy_val, 1)
        legacy_row.addWidget(self.lbl_legacy_ok)
        legacy_row.addWidget(make_copy_btn(self, lambda: self.lbl_legacy_val.text()))
        vfl.addLayout(legacy_row)

        # SegWit row
        segwit_row = QHBoxLayout()
        lbl_segwit_tag = QLabel("SegWit (bech32):")
        lbl_segwit_tag.setStyleSheet("color:#555577;font-size:10px;letter-spacing:0px;text-transform:none;min-width:120px;")
        self.lbl_segwit_val = QLabel("—")
        self.lbl_segwit_val.setStyleSheet("color:#aaaacc;font-size:11px;font-family:'Courier New';text-transform:none;letter-spacing:0px;")
        self.lbl_segwit_val.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.lbl_segwit_ok = QLabel("")
        self.lbl_segwit_ok.setFixedWidth(20)
        segwit_row.addWidget(lbl_segwit_tag)
        segwit_row.addWidget(self.lbl_segwit_val, 1)
        segwit_row.addWidget(self.lbl_segwit_ok)
        segwit_row.addWidget(make_copy_btn(self, lambda: self.lbl_segwit_val.text()))
        vfl.addLayout(segwit_row)

        # Key type indicator
        kt_row = QHBoxLayout()
        lbl_kt_tag = QLabel("Key format:")
        lbl_kt_tag.setStyleSheet("color:#555577;font-size:10px;letter-spacing:0px;text-transform:none;min-width:120px;")
        self.lbl_key_type = QLabel("—")
        self.lbl_key_type.setStyleSheet("color:#555577;font-size:10px;font-family:'Courier New';text-transform:none;letter-spacing:0px;")
        kt_row.addWidget(lbl_kt_tag)
        kt_row.addWidget(self.lbl_key_type, 1)
        vfl.addLayout(kt_row)

        # WIF export row
        wif_row = QHBoxLayout()
        lbl_wif_tag = QLabel("WIF:")
        lbl_wif_tag.setStyleSheet("color:#555577;font-size:10px;letter-spacing:0px;text-transform:none;min-width:120px;")
        self.lbl_wif_val = QLabel("—")
        self.lbl_wif_val.setStyleSheet("color:#aaaacc;font-size:11px;font-family:'Courier New';text-transform:none;letter-spacing:0px;")
        self.lbl_wif_val.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        wif_row.addWidget(lbl_wif_tag)
        wif_row.addWidget(self.lbl_wif_val, 1)
        wif_row.addWidget(make_copy_btn(self, lambda: self.lbl_wif_val.text()))
        vfl.addLayout(wif_row)

        root.addWidget(verify_frame)
        root.addSpacing(6)

        # ── Balance section ─────────────────────────────────────────────
        bal_row = QHBoxLayout()
        bal_left = QVBoxLayout()
        bal_left.setSpacing(2)
        bal_left.addWidget(make_label("BALANCE"))
        self.output_balance = QLabel("—")
        self.output_balance.setObjectName("value_label")
        bal_left.addWidget(self.output_balance)
        bal_row.addLayout(bal_left)
        bal_row.addStretch()
        btn_bal = QPushButton("↻  CHECK BALANCE")
        btn_bal.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_bal.clicked.connect(self.check_balance)
        bal_row.addWidget(btn_bal)
        bal_row.addWidget(make_copy_btn(self, lambda: self.output_balance.text().replace(' BTC', '')))
        root.addLayout(bal_row)
        root.addSpacing(10)
        root.addWidget(make_separator())
        root.addSpacing(10)

        # ── Tabs: Send / Offline ─────────────────────────────────────────
        tabs = QTabWidget()
        tabs.setDocumentMode(True)

        # ─ Tab 1: BROADCAST ─────────────────────────────────────
        tab_send = QWidget()
        tsl = QVBoxLayout(tab_send)
        tsl.setContentsMargins(0, 16, 0, 0)
        tsl.setSpacing(10)

        tsl.addWidget(make_label("DESTINATION ADDRESS"))
        self.input_dest_address = QLineEdit()
        self.input_dest_address.setPlaceholderText("bc1q... or 1... or 3...")
        tsl.addWidget(self.input_dest_address)

        tsl.addWidget(make_label("AMOUNT (BTC)"))
        amt_row = QHBoxLayout()
        self.input_amount = QLineEdit()
        self.input_amount.setPlaceholderText("0.00000000  или нажми MAX")
        self.input_amount.textChanged.connect(self._recalc_net)
        amt_row.addWidget(self.input_amount)
        self.btn_max = QPushButton("MAX")
        self.btn_max.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_max.clicked.connect(self._fill_max_amount)
        amt_row.addWidget(self.btn_max)
        tsl.addLayout(amt_row)

        tsl.addWidget(make_label("FEE (SAT/BYTE)"))
        fee_row = QHBoxLayout()
        self.input_fee = QLineEdit()
        self.input_fee.setPlaceholderText("e.g. 20")
        self.input_fee.textChanged.connect(self._recalc_net)
        fee_row.addWidget(self.input_fee)
        self.btn_suggest_fee = QPushButton("⚡ SUGGEST")
        self.btn_suggest_fee.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_suggest_fee.clicked.connect(self.suggest_fee)
        fee_row.addWidget(self.btn_suggest_fee)
        tsl.addLayout(fee_row)

        # Net receive label
        self.lbl_net_send = QLabel("К отправке: —  |  Комиссия: —")
        self.lbl_net_send.setStyleSheet("color:#555577;font-size:10px;letter-spacing:0px;text-transform:none;padding:2px 0px;")
        tsl.addWidget(self.lbl_net_send)

        tsl.addSpacing(6)
        self.btn_send = QPushButton("▶  BROADCAST TRANSACTION")
        self.btn_send.setObjectName("danger_btn")
        self.btn_send.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_send.clicked.connect(self.send_transaction)
        tsl.addWidget(self.btn_send)

        tsl.addSpacing(8)
        tsl.addWidget(make_label("TXID"))
        txid_row = QHBoxLayout()
        self.output_txid = QLabel("—")
        self.output_txid.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.output_txid.setWordWrap(True)
        self.output_txid.setStyleSheet("color:#f7931a;font-size:11px;font-family:'Courier New';padding:8px;background:#080810;border:1px solid #1a1a2e;border-radius:6px;")
        txid_row.addWidget(self.output_txid)
        txid_row.addWidget(make_copy_btn(self, lambda: self._last_txid))
        tsl.addLayout(txid_row)
        tsl.addStretch()

        # ─ Tab 2: OFFLINE / RAW HEX ─────────────────────────────
        tab_offline = QWidget()
        tol = QVBoxLayout(tab_offline)
        tol.setContentsMargins(0, 16, 0, 0)
        tol.setSpacing(10)

        info = QLabel("Build a signed raw transaction WITHOUT broadcasting.\nPaste the HEX into mempool.space/tx/push manually.")
        info.setStyleSheet("color:#555577;font-size:11px;line-height:1.6;text-transform:none;letter-spacing:0px;")
        info.setWordWrap(True)
        tol.addWidget(info)

        tol.addWidget(make_label("DESTINATION ADDRESS"))
        self.input_dest_offline = QLineEdit()
        self.input_dest_offline.setPlaceholderText("bc1q... or 1... or 3...")
        tol.addWidget(self.input_dest_offline)

        tol.addWidget(make_label("AMOUNT (BTC)"))
        amt_off_row = QHBoxLayout()
        self.input_amount_offline = QLineEdit()
        self.input_amount_offline.setPlaceholderText("0.00000000  или нажми MAX")
        self.input_amount_offline.textChanged.connect(self._recalc_net_offline)
        amt_off_row.addWidget(self.input_amount_offline)
        self.btn_max_offline = QPushButton("MAX")
        self.btn_max_offline.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_max_offline.clicked.connect(self._fill_max_amount_offline)
        amt_off_row.addWidget(self.btn_max_offline)
        tol.addLayout(amt_off_row)

        tol.addWidget(make_label("FEE (SAT/BYTE)"))
        fee_off_row = QHBoxLayout()
        self.input_fee_offline = QLineEdit()
        self.input_fee_offline.setPlaceholderText("e.g. 20")
        self.input_fee_offline.textChanged.connect(self._recalc_net_offline)
        fee_off_row.addWidget(self.input_fee_offline)
        self.btn_suggest_fee2 = QPushButton("⚡ SUGGEST")
        self.btn_suggest_fee2.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_suggest_fee2.clicked.connect(self.suggest_fee_offline)
        fee_off_row.addWidget(self.btn_suggest_fee2)
        tol.addLayout(fee_off_row)

        # Net receive label
        self.lbl_net_offline = QLabel("К отправке: —  |  Комиссия: —")
        self.lbl_net_offline.setStyleSheet("color:#555577;font-size:10px;letter-spacing:0px;text-transform:none;padding:2px 0px;")
        tol.addWidget(self.lbl_net_offline)

        tol.addSpacing(6)
        self.btn_build = QPushButton("⬡  BUILD RAW TX  (NO BROADCAST)")
        self.btn_build.setObjectName("primary_btn")
        self.btn_build.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_build.clicked.connect(self.build_raw_tx)
        tol.addWidget(self.btn_build)

        tol.addSpacing(8)
        tol.addWidget(make_label("RAW HEX (SIGNED TX)"))
        raw_row = QHBoxLayout()
        self.output_raw = QTextEdit()
        self.output_raw.setReadOnly(True)
        self.output_raw.setPlaceholderText("Signed transaction hex will appear here...")
        self.output_raw.setMaximumHeight(100)
        raw_row.addWidget(self.output_raw)
        raw_row.addWidget(make_copy_btn(self, lambda: self._last_raw_hex))
        tol.addLayout(raw_row)

        tol.addWidget(make_label("PUSH URL"))
        push_url = QLabel("mempool.space/tx/push")
        push_url.setStyleSheet("color:#4444aa;font-size:11px;text-decoration:underline;cursor:pointer;text-transform:none;letter-spacing:0px;")
        tol.addWidget(push_url)
        tol.addStretch()

        tabs.addTab(tab_send, "BROADCAST")
        tabs.addTab(tab_offline, "OFFLINE / RAW HEX")
        root.addWidget(tabs)
        root.addSpacing(16)

        # ── Log ─────────────────────────────────────────────────────────
        log_hdr = QHBoxLayout()
        log_hdr.addWidget(make_label("LOG"))
        log_hdr.addStretch()
        btn_clear = QPushButton("✕ CLEAR")
        btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear.clicked.connect(lambda: self.log_output.clear())
        log_hdr.addWidget(btn_clear)
        log_hdr.addWidget(make_copy_btn(self, lambda: self.log_output.toPlainText()))
        root.addLayout(log_hdr)
        root.addSpacing(4)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(160)
        root.addWidget(self.log_output)

    # ── Helpers ─────────────────────────────────────────────────────────────

    def toggle_key_visibility(self):
        if self.input_priv_key.echoMode() == QLineEdit.EchoMode.Password:
            self.input_priv_key.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.input_priv_key.setEchoMode(QLineEdit.EchoMode.Password)

    def log_msg(self, msg, color="#6666aa"):
        self.log_output.append(f'<span style="color:{color};font-family:Courier New;">{msg}</span>')
        logging.info(msg)

    def log_error(self, msg):
        self.log_output.append(f'<span style="color:#ff4444;font-family:Courier New;">✗ {msg}</span>')
        logging.error(msg)

    def log_ok(self, msg):
        self.log_output.append(f'<span style="color:#44ff88;font-family:Courier New;">✓ {msg}</span>')
        logging.info(msg)

    def get_selected_address(self):
        text = self.address_selector.currentText()
        if ': ' in text:
            return text.split(': ', 1)[1].strip()
        return text.strip()

    def _is_wif(self, s: str) -> bool:
        """Return True if the string looks like a WIF private key."""
        # WIF mainnet: starts with 5 (uncompressed, 51 chars) or K/L (compressed, 52 chars)
        if len(s) == 51 and s[0] == '5':
            return True
        if len(s) == 52 and s[0] in ('K', 'L'):
            return True
        return False

    def _get_key(self):
        pk = self.input_priv_key.text().strip()
        if not pk:
            raise ValueError("Введи приватный ключ (HEX или WIF)")
        if self._is_wif(pk):
            return Key(pk)          # bit принимает WIF напрямую
        else:
            return Key.from_hex(pk)

    def _get_utxos(self, address):
        r = requests.get(f"{API_URL}/address/{address}/utxo", timeout=10)
        r.raise_for_status()
        return r.json()

    # ── Actions ─────────────────────────────────────────────────────────────

    def recover_addresses(self):
        try:
            pk = self.input_priv_key.text().strip()
            if not pk:
                raise ValueError("Введи приватный ключ")

            is_wif = self._is_wif(pk)
            key = Key(pk) if is_wif else Key.from_hex(pk)

            self.legacy_address = key.address
            self.segwit_address = key.segwit_address

            # ── populate selector ──
            self.address_selector.clear()
            self.address_selector.addItem(f"Legacy: {self.legacy_address}")
            self.address_selector.addItem(f"SegWit (bech32): {self.segwit_address}")

            # ── populate verify panel ──
            self.lbl_legacy_val.setText(self.legacy_address)
            self.lbl_segwit_val.setText(self.segwit_address)
            self.lbl_legacy_ok.setText("✓")
            self.lbl_legacy_ok.setStyleSheet("color:#44ff88;font-size:13px;")
            self.lbl_segwit_ok.setText("✓")
            self.lbl_segwit_ok.setStyleSheet("color:#44ff88;font-size:13px;")

            fmt = f"WIF ({'compressed' if is_wif and pk[0] in ('K','L') else 'uncompressed' if is_wif else 'HEX'})"
            self.lbl_key_type.setText(fmt)
            self.lbl_key_type.setStyleSheet("color:#f7931a;font-size:10px;font-family:'Courier New';text-transform:none;letter-spacing:0px;")

            # Show WIF (so user can cross-check when input was HEX)
            wif = key.to_wif()
            self.lbl_wif_val.setText(wif)

            self.log_ok(f"Format:  {fmt}")
            self.log_ok(f"Legacy:  {self.legacy_address}")
            self.log_ok(f"SegWit:  {self.segwit_address}")
            self.log_ok(f"WIF:     {wif}")
        except Exception as e:
            # Mark verify cells as failed
            self.lbl_legacy_ok.setText("✗")
            self.lbl_legacy_ok.setStyleSheet("color:#ff4444;font-size:13px;")
            self.lbl_segwit_ok.setText("✗")
            self.lbl_segwit_ok.setStyleSheet("color:#ff4444;font-size:13px;")
            self.lbl_key_type.setText("ERROR")
            self.lbl_key_type.setStyleSheet("color:#ff4444;font-size:10px;font-family:'Courier New';text-transform:none;letter-spacing:0px;")
            self.log_error(f"recover_addresses: {e}")

    def check_balance(self):
        try:
            addr = self.get_selected_address()
            if not addr:
                self.log_error("Сначала восстанови адрес")
                return
            utxos = self._get_utxos(addr)
            self._balance_sats = sum(u["value"] for u in utxos)
            total = self._balance_sats / 1e8
            self.output_balance.setText(f"{total:.8f} BTC")
            self.log_ok(f"Balance [{addr[:12]}…] → {total:.8f} BTC  ({len(utxos)} UTXO)")
            self._recalc_net()
            self._recalc_net_offline()
        except Exception as e:
            self.log_error(f"check_balance: {e}")

    def _estimated_fee_sats(self, fee_per_byte: int) -> int:
        """Estimate fee in satoshis for a typical 1-input 1-output tx."""
        return (180 + 34 + 10) * fee_per_byte

    def _recalc_net(self):
        self._recalc_net_label(self.input_amount, self.input_fee, self.lbl_net_send)

    def _recalc_net_offline(self):
        self._recalc_net_label(self.input_amount_offline, self.input_fee_offline, self.lbl_net_offline)

    def _recalc_net_label(self, amt_input, fee_input, label):
        try:
            amt_btc = float(amt_input.text().strip() or "0")
            fee_pb  = int(fee_input.text().strip() or "0")
            fee_sats = self._estimated_fee_sats(fee_pb)
            net_sats = int(amt_btc * 1e8) - fee_sats
            if net_sats > 0:
                label.setText(
                    f"К отправке: <span style='color:#44ff88'>{net_sats/1e8:.8f} BTC</span>"
                    f"  |  Комиссия: <span style='color:#f7931a'>{fee_sats} sat</span>"
                )
                label.setStyleSheet("font-size:10px;letter-spacing:0px;text-transform:none;padding:2px 0px;")
            else:
                label.setText("К отправке: — (недостаточно для покрытия комиссии)")
                label.setStyleSheet("color:#ff4444;font-size:10px;letter-spacing:0px;text-transform:none;padding:2px 0px;")
        except Exception:
            label.setText("К отправке: —  |  Комиссия: —")
            label.setStyleSheet("color:#555577;font-size:10px;letter-spacing:0px;text-transform:none;padding:2px 0px;")

    def _fill_max_amount(self):
        self._fill_max(self.input_amount, self.input_fee, self.lbl_net_send)

    def _fill_max_amount_offline(self):
        self._fill_max(self.input_amount_offline, self.input_fee_offline, self.lbl_net_offline)

    def _fill_max(self, amt_input, fee_input, label):
        try:
            fee_pb = int(fee_input.text().strip() or "0")
            if fee_pb <= 0:
                self.log_error("Сначала укажи fee (sat/byte) чтобы рассчитать MAX")
                return
            bal = getattr(self, '_balance_sats', None)
            if bal is None:
                self.log_error("Сначала проверь баланс (CHECK BALANCE)")
                return
            amt_input.setText(f"{bal / 1e8:.8f}")
        except Exception as e:
            self.log_error(f"fill_max: {e}")

    def suggest_fee(self):
        self._do_suggest_fee(self.input_fee)

    def suggest_fee_offline(self):
        self._do_suggest_fee(self.input_fee_offline)

    def _do_suggest_fee(self, target_input):
        try:
            r = requests.get(f"{API_URL}/v1/fees/recommended", timeout=8)
            fees = r.json()
            medium = fees.get("halfHourFee", fees.get("hourFee", 20))
            target_input.setText(str(medium))
            self.log_msg(f"Suggested fee: {medium} sat/byte  (fastest={fees.get('fastestFee')}  hour={fees.get('hourFee')})")
        except Exception as e:
            self.log_error(f"suggest_fee: {e}")

    def _build_tx(self, key, from_address, dest_address, fee_per_byte, amount_btc=None):
        utxos = self._get_utxos(from_address)
        if not utxos:
            raise ValueError("Нет доступных UTXO")
        total_sats = sum(u["value"] for u in utxos)
        estimated_size = 180 * len(utxos) + 34 + 10
        fee = estimated_size * fee_per_byte
        if amount_btc is None:
            send_amount = total_sats - fee
        else:
            send_amount = int(amount_btc * 1e8) - fee
        if send_amount <= 546:
            raise ValueError(f"Недостаточно после комиссии: {send_amount} sat (dust limit = 546)")
        if send_amount > total_sats - fee:
            raise ValueError(f"Сумма превышает баланс за вычетом комиссии: max={( total_sats - fee)/1e8:.8f} BTC")
        tx = key.create_transaction(
            [(dest_address, send_amount, "satoshi")],
            fee=fee,
            replace_by_fee=False
        )
        return tx, total_sats, fee, send_amount

    def send_transaction(self):
        try:
            key = self._get_key()
            dest = self.input_dest_address.text().strip()
            fee_str = self.input_fee.text().strip()
            amt_str = self.input_amount.text().strip()
            if not dest:
                raise ValueError("Укажи адрес получателя")
            if not fee_str:
                raise ValueError("Укажи комиссию")
            fee_per_byte = int(fee_str)
            amount_btc = float(amt_str) if amt_str else None
            from_address = self.get_selected_address()

            utxos = self._get_utxos(from_address)
            total_btc = sum(u["value"] for u in utxos) / 1e8

            send_label = f"{amount_btc:.8f} BTC" if amount_btc else f"{total_btc:.8f} BTC (MAX)"
            confirm = QMessageBox(self)
            confirm.setWindowTitle("ПОДТВЕРЖДЕНИЕ")
            confirm.setText(
                f"Подтвердить транзакцию?\n\n"
                f"  От:     {from_address[:24]}…\n"
                f"  Кому:   {dest[:24]}…\n"
                f"  Сумма:  {send_label}\n"
                f"  Fee:    {fee_per_byte} sat/byte"
            )
            confirm.setStyleSheet(DARK_STYLE)
            confirm.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm.exec() != QMessageBox.StandardButton.Yes:
                return

            tx, total_sats, fee, send_amount = self._build_tx(key, from_address, dest, fee_per_byte, amount_btc)
            r = requests.post(f"{API_URL}/tx", data=tx, timeout=15)

            if r.status_code == 200:
                txid = r.text.strip()
                self._last_txid = txid
                self.output_txid.setText(txid)
                self.log_ok(f"TX отправлена!")
                self.log_ok(f"TXID: {txid}")
                self.log_msg(f"Sent: {send_amount/1e8:.8f} BTC  Fee: {fee} sat")
            else:
                self.log_error(f"API error {r.status_code}: {r.text[:200]}")
        except Exception as e:
            self.log_error(f"send_transaction: {e}")

    def build_raw_tx(self):
        try:
            key = self._get_key()
            dest = self.input_dest_offline.text().strip()
            fee_str = self.input_fee_offline.text().strip()
            amt_str = self.input_amount_offline.text().strip()
            if not dest:
                raise ValueError("Укажи адрес получателя")
            if not fee_str:
                raise ValueError("Укажи комиссию")
            fee_per_byte = int(fee_str)
            amount_btc = float(amt_str) if amt_str else None
            from_address = self.get_selected_address()

            tx_hex, total_sats, fee, send_amount = self._build_tx(key, from_address, dest, fee_per_byte, amount_btc)
            self._last_raw_hex = tx_hex
            self.output_raw.setPlainText(tx_hex)

            self.log_ok(f"Raw TX built (NOT broadcast)")
            self.log_msg(f"Total: {total_sats/1e8:.8f} BTC  |  Fee: {fee} sat  |  Send: {send_amount/1e8:.8f} BTC")
            self.log_msg(f"Hex length: {len(tx_hex)} chars  ({len(tx_hex)//2} bytes)")
            self.log_msg("→ Вставь hex на mempool.space/tx/push вручную")
        except Exception as e:
            self.log_error(f"build_raw_tx: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = BTCTransactionApp()
    window.show()
    sys.exit(app.exec())
