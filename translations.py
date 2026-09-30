# -*- coding: utf-8 -*-
"""
RU/EN localization strings for BTC Wallet Tool
"""

TRANSLATIONS = {
    'ru': {
        # Window
        'window_title': 'Bitcoin Wallet Tool',
        'app_title': 'Bitcoin Wallet Tool',

        # Key input section
        'private_key': 'Приватный ключ (HEX или WIF)',
        'priv_key': 'ПРИВАТНЫЙ КЛЮЧ (HEX ИЛИ WIF)',
        'key_placeholder': 'Введи HEX (64 символа) или WIF (5.../K.../L...)',
        'priv_key_ph': 'Введи HEX (64 символа) или WIF (5.../K.../L...)',
        'btn_load': '▶ ЗАГРУЗИТЬ',
        'recover': '▶ ЗАГРУЗИТЬ АДРЕСА',
        'btn_toggle_visibility': '👁',

        # Verification card
        'verification': 'ПРОВЕРКА',
        'wallet_info': 'Информация о кошельке',
        'key_type': 'Тип:',
        'key_format': 'Формат ключа:',
        'legacy': 'Legacy (P2PKH):',
        'legacy_label': 'Legacy:',
        'segwit': 'SegWit (bech32):',
        'segwit_label': 'SegWit (bech32):',
        'wif': 'WIF:',
        'wif_label': 'WIF:',
        'copy_tooltip': 'Копировать',

        # Address selector & balance
        'address': 'АКТИВНЫЙ АДРЕС',
        'address_select': 'АДРЕС',
        'address_type': 'Тип адреса для операций',
        'balance': 'БАЛАНС',
        'btn_check_balance': '⟳ ПРОВЕРИТЬ БАЛАНС',
        'balance_placeholder': '—',

        # Settings toolbar
        'settings': 'НАСТРОЙКИ',
        'theme': 'Тема',
        'theme_dark': 'Тёмная',
        'theme_light': 'Светлая',
        'language': 'Язык',
        'help': 'Помощь',
        'btn_help': 'Помощь',

        # Tabs
        'tab_broadcast': 'ОТПРАВКА (BROADCAST)',
        'tab_offline': 'ОФФЛАЙН РЕЖИМ',

        # Send transaction (broadcast)
        'dest_address': 'АДРЕС ПОЛУЧАТЕЛЯ',
        'dest_placeholder': 'bc1q... или 1... или 3...',
        'amount': 'СУММА (BTC) — БЕЗ комиссии',
        'amount_placeholder': 'Пусто = отправить весь баланс',
        'btn_max': 'MAX',
        'fee': 'КОМИССИЯ (sat/byte)',
        'fee_ph': 'напр. 5',
        'suggest': '⚡ ПРЕДЛОЖИТЬ',
        'net_send': 'ЧИСТАЯ ОТПРАВКА',
        'net_send_placeholder': 'Получатель: — | Спишется с баланса: —',
        'btn_send': '▶ ОТПРАВИТЬ ТРАНЗАКЦИЮ',
        'btn_check': '⟳ ПРОВЕРИТЬ БАЛАНС',
        'txid': 'TXID',
        'txid_placeholder': 'Появится после отправки',

        # Offline mode
        'dest_address_offline': 'АДРЕС ПОЛУЧАТЕЛЯ',
        'amount_offline': 'СУММА (BTC) — БЕЗ комиссии',
        'fee_offline': 'КОМИССИЯ (sat/byte)',
        'build_raw': '⬡ ПОСТРОИТЬ RAW TX (НЕ ОТПРАВЛЯТЬ)',
        'raw_hex': 'RAW HEX (ПОДПИСАННАЯ TX)',
        'raw_hex_ph': 'Подписанная транзакция в HEX-формате появится здесь',

        # Log
        'log': 'ЛОГ ОПЕРАЦИЙ',
        'clear': 'Очистить',

        # Help dialog
        'help_title': 'Справка — Bitcoin Wallet Tool',
        'help_content': '''
<h2 style="color:#fbbf24;margin-top:0;">Как использовать</h2>

<h3>1. Загрузка приватного ключа</h3>
<p>Вставьте ваш приватный ключ в формате:</p>
<ul>
<li><b>HEX:</b> 1-64 символа (автоматически дополняется нулями слева)</li>
<li><b>WIF:</b> начинается с 5 (uncompressed) или K/L (compressed)</li>
</ul>
<p>Нажмите <b>▶ ЗАГРУЗИТЬ</b> для генерации адресов.</p>

<h3>2. Проверка адресов</h3>
<p>Карточка проверки показывает:</p>
<ul>
<li>Тип ключа (WIF compressed/uncompressed или HEX)</li>
<li>Legacy адрес (P2PKH, начинается с 1...)</li>
<li>SegWit адрес (bech32, начинается с bc1...)</li>
<li>WIF представление (с кнопкой копирования)</li>
</ul>

<h3>3. Проверка баланса</h3>
<p>Выберите тип адреса в выпадающем списке (Legacy или SegWit) и нажмите <b>⟳ ПРОВЕРИТЬ БАЛАНС</b>.</p>
<p>Баланс загружается через mempool.space API.</p>

<h3>4. Отправка транзакции</h3>
<p><b>Режим Broadcast (отправка в сеть):</b></p>
<ul>
<li>Введите адрес получателя</li>
<li>Укажите сумму в BTC (оставьте пустым для MAX)</li>
<li>Укажите комиссию sat/byte (или нажмите ⚡ для автоподбора)</li>
<li>Нажмите <b>▶ ОТПРАВИТЬ</b> и подтвердите в диалоге</li>
</ul>

<p><b>Оффлайн режим (без broadcast):</b></p>
<ul>
<li>Те же данные, но нажмите <b>⬡ ПОСТРОИТЬ RAW TX</b></li>
<li>Скопируйте подписанный HEX</li>
<li>Вставьте в mempool.space/tx/push для ручной отправки</li>
</ul>

<h3>Безопасность</h3>
<ul>
<li>Приватный ключ <b>никогда не покидает ваш компьютер</b></li>
<li>Все транзакции требуют явного подтверждения</li>
<li>Лог-файл маскирует WIF/HEX паттерны перед записью</li>
<li>Используйте на защищённой системе (обновлённая ОС, антивирус)</li>
</ul>

<h3>Автор</h3>
<p>Franklin Systems<br>
<a href="https://franklin-sys.vercel.app/" style="color:#fbbf24;">franklin-sys.vercel.app</a></p>

<p style="color:#6b7280;font-size:9px;margin-top:20px;">
⚠ Bitcoin транзакции необратимы. Всегда проверяйте адрес получателя перед отправкой.<br>
Используйте на свой риск. Тестируйте с малыми суммами.
</p>
''',
    },
    'en': {
        # Window
        'window_title': 'Bitcoin Wallet Tool',
        'app_title': 'Bitcoin Wallet Tool',

        # Key input section
        'private_key': 'Private Key (HEX or WIF)',
        'priv_key': 'PRIVATE KEY (HEX OR WIF)',
        'key_placeholder': 'Enter HEX (64 chars) or WIF (5.../K.../L...)',
        'priv_key_ph': 'Enter HEX (64 chars) or WIF (5.../K.../L...)',
        'btn_load': '▶ LOAD',
        'recover': '▶ LOAD ADDRESSES',
        'btn_toggle_visibility': '👁',

        # Verification card
        'verification': 'VERIFICATION',
        'wallet_info': 'Wallet Information',
        'key_type': 'Type:',
        'key_format': 'Key Format:',
        'legacy': 'Legacy (P2PKH):',
        'legacy_label': 'Legacy:',
        'segwit': 'SegWit (bech32):',
        'segwit_label': 'SegWit (bech32):',
        'wif': 'WIF:',
        'wif_label': 'WIF:',
        'copy_tooltip': 'Copy',

        # Address selector & balance
        'address': 'ACTIVE ADDRESS',
        'address_select': 'ADDRESS',
        'address_type': 'Address type for operations',
        'balance': 'BALANCE',
        'btn_check_balance': '⟳ CHECK BALANCE',
        'balance_placeholder': '—',

        # Settings toolbar
        'settings': 'SETTINGS',
        'theme': 'Theme',
        'theme_dark': 'Dark',
        'theme_light': 'Light',
        'language': 'Language',
        'help': 'Help',
        'btn_help': 'Help',

        # Tabs
        'tab_broadcast': 'SEND (BROADCAST)',
        'tab_offline': 'OFFLINE MODE',

        # Send transaction (broadcast)
        'dest_address': 'RECIPIENT ADDRESS',
        'dest_placeholder': 'bc1q... or 1... or 3...',
        'amount': 'AMOUNT (BTC) — EXCLUDING FEE',
        'amount_placeholder': 'Empty = send all balance',
        'btn_max': 'MAX',
        'fee': 'FEE (sat/byte)',
        'fee_ph': 'e.g. 5',
        'suggest': '⚡ SUGGEST',
        'net_send': 'NET SEND',
        'net_send_placeholder': 'Recipient gets: — | Debit from balance: —',
        'btn_send': '▶ SEND TRANSACTION',
        'btn_check': '⟳ CHECK BALANCE',
        'txid': 'TXID',
        'txid_placeholder': 'Will appear after broadcast',

        # Offline mode
        'dest_address_offline': 'RECIPIENT ADDRESS',
        'amount_offline': 'AMOUNT (BTC) — EXCLUDING FEE',
        'fee_offline': 'FEE (sat/byte)',
        'build_raw': '⬡ BUILD RAW TX (NO BROADCAST)',
        'raw_hex': 'RAW HEX (SIGNED TX)',
        'raw_hex_ph': 'Signed transaction hex will appear here',

        # Log
        'log': 'OPERATION LOG',
        'clear': 'Clear',

        # Help dialog
        'help_title': 'Help — Bitcoin Wallet Tool',
        'help_content': '''
<h2 style="color:#fbbf24;margin-top:0;">How to Use</h2>

<h3>1. Load Private Key</h3>
<p>Paste your private key in one of these formats:</p>
<ul>
<li><b>HEX:</b> 1-64 characters (auto-padded with leading zeros)</li>
<li><b>WIF:</b> starts with 5 (uncompressed) or K/L (compressed)</li>
</ul>
<p>Click <b>▶ LOAD</b> to generate addresses.</p>

<h3>2. Verify Addresses</h3>
<p>The verification card displays:</p>
<ul>
<li>Key type (WIF compressed/uncompressed or HEX)</li>
<li>Legacy address (P2PKH, starts with 1...)</li>
<li>SegWit address (bech32, starts with bc1...)</li>
<li>WIF representation (with copy button)</li>
</ul>

<h3>3. Check Balance</h3>
<p>Select address type from dropdown (Legacy or SegWit) and click <b>⟳ CHECK BALANCE</b>.</p>
<p>Balance is fetched via mempool.space API.</p>

<h3>4. Send Transaction</h3>
<p><b>Broadcast mode (send to network):</b></p>
<ul>
<li>Enter recipient address</li>
<li>Specify amount in BTC (leave empty for MAX)</li>
<li>Set fee in sat/byte (or click ⚡ for auto-suggestion)</li>
<li>Click <b>▶ SEND</b> and confirm in dialog</li>
</ul>

<p><b>Offline mode (no broadcast):</b></p>
<ul>
<li>Same inputs, but click <b>⬡ BUILD RAW TX</b></li>
<li>Copy the signed HEX</li>
<li>Paste into mempool.space/tx/push for manual broadcast</li>
</ul>

<h3>Security</h3>
<ul>
<li>Private key <b>never leaves your computer</b></li>
<li>All transactions require explicit confirmation</li>
<li>Log file masks WIF/HEX patterns before writing</li>
<li>Use on a secure system (updated OS, antivirus)</li>
</ul>

<h3>Author</h3>
<p>Franklin Systems<br>
<a href="https://franklin-sys.vercel.app/" style="color:#fbbf24;">franklin-sys.vercel.app</a></p>

<p style="color:#6b7280;font-size:9px;margin-top:20px;">
⚠ Bitcoin transactions are irreversible. Always verify recipient address before sending.<br>
Use at your own risk. Test with small amounts first.
</p>
''',
    }
}


def get_translation(lang_code: str, key: str) -> str:
    """Get translated string for given language and key."""
    lang = TRANSLATIONS.get(lang_code, TRANSLATIONS['en'])
    return lang.get(key, key)
