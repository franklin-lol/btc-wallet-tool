# ⟐ Bitcoin Wallet Tool

> Secure desktop GUI for Bitcoin wallet operations — address generation, balance checking, transaction signing and broadcasting. No seed phrase, no cloud, no third-party custody.

![Python](https://img.shields.io/badge/Python-3.10+-3572A5?style=flat-square&logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/PyQt6-GUI-41CD52?style=flat-square)
![Bitcoin](https://img.shields.io/badge/Bitcoin-mainnet-F7931A?style=flat-square&logo=bitcoin&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-555?style=flat-square)

---

## Features

A production-ready Bitcoin wallet interface with offline transaction signing capability.

- **Multi-format key support** — HEX (1-64 chars, auto-padded) or WIF (5.../K.../L...)
- **Dual address generation** — Legacy P2PKH (1...) + native SegWit bech32 (bc1...)
- **Live balance checking** — mempool.space API integration (no account required)
- **Broadcast mode** — Send transactions instantly with custom fee control and MAX button
- **Offline mode** — Build signed raw TX hex without broadcasting (air-gap compatible)
- **Network fee suggestions** — Real-time recommended fees from mempool.space
- **Dark + Light themes** — Modern UI with Monster White Energy color palette (light mode)
- **RU/EN localization** — Full UI translation with persistent language settings
- **Built-in help** — Comprehensive guide accessible from toolbar
- **Security hardened** — Private key masking in logs, no external key transmission

---

## Stack

| Component | Implementation |
|---|---|
| GUI Framework | PyQt6 (native desktop) |
| Bitcoin Core | `bit` library (ECDSA secp256k1) |
| API Backend | mempool.space (balance, UTXO, fee estimates) |
| TX Signing | Local UTXO-based raw transaction construction |
| Persistence | QSettings (theme, language preferences) |
| Logging | File-based with WIF/HEX masking filter |

---

## Installation

```bash
git clone https://github.com/franklin-lol/btc-wallet-tool
cd btc-wallet-tool
pip install PyQt6 bit requests
python btc_wallet_tool.py
```

### Build standalone executable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name="BTCWalletTool" btc_wallet_tool.py
```

---

## Usage Guide

### 1. Load Private Key
- Paste HEX (1-64 characters, auto-padded with leading zeros) or WIF format
- Click 👁 to toggle visibility
- Click **▶ LOAD** to generate addresses

### 2. Verify Addresses
- Verification card shows:
  - Key type (WIF compressed/uncompressed or HEX)
  - Legacy address (P2PKH)
  - SegWit address (bech32)
  - WIF representation (with copy button)

### 3. Check Balance
- Select address type from dropdown (Legacy or SegWit)
- Click **⟳ CHECK BALANCE**
- Balance appears with UTXO count

### 4. Send Transaction (Broadcast)
- **Recipient Address:** bc1q.../1.../3...
- **Amount:** BTC value (leave empty for MAX balance)
- **Fee:** sat/byte (click ⚡ SUGGEST for network recommendation)
- Click **▶ SEND TRANSACTION**
- Confirmation dialog shows:
  - From/To addresses
  - Net amount recipient receives
  - Fee breakdown
  - Total debit from balance

### 5. Offline Mode (Raw TX)
- Same inputs as broadcast mode
- Click **⬡ BUILD RAW TX (NO BROADCAST)**
- Signed hex appears in text area
- Copy hex → paste into mempool.space/tx/push for manual broadcast
- Useful for air-gapped signing workflows

---

## UI Features

### Theme Switcher
- **Dark theme:** Slate-dark (#0F1117) with amber accent (#FBBF24)
- **Light theme:** White/gray palette with cyan accent (#00D9FF) — Monster White Energy inspired

### Language Support
- **RU:** Full Russian localization
- **EN:** English translation
- Settings persist across sessions
- Requires app restart to apply language change

### Help Dialog
- Accessible via toolbar **Help** button
- Includes:
  - Workflow explanation
  - Security best practices
  - Author link: [franklin-sys.vercel.app](https://franklin-sys.vercel.app/)

---

## Window Dimensions

- **Size:** 712×955px (~5% narrower, ~5% taller than previous 750×910)
- **Optimized for:** SegWit bech32 addresses (up to 62 characters)
- **HiDPI:** Auto-scaling disabled for consistent layout

---

## Security Architecture

| Layer | Protection |
|---|---|
| Key storage | Never written to disk or transmitted over network |
| Logging | WIF/HEX patterns masked with regex filter before file write |
| API calls | Read-only (balance/UTXO queries) + write-only TX broadcast |
| UI masking | Password field mode for private key input by default |
| Confirmation | Mandatory approval dialog before any broadcast |

**Threat model:** Protects against accidental logging/screenshot leaks. Does NOT protect against:
- Keyloggers or screen capture malware
- Compromised Python environment
- Man-in-the-middle attacks on mempool.space API (use Tor for anonymity)

---

## Fee Estimation

```python
estimated_size = 180 * utxo_count + 34 + 10  # bytes
fee_sats = estimated_size * fee_per_byte
```

- **180 bytes/input:** P2PKH/P2WPKH UTXO consumption
- **34 bytes:** Single output overhead
- **10 bytes:** TX header + change output buffer

Use **⚡ SUGGEST** button to fetch current mempool.space recommended fees:
- `fastestFee` (next block)
- `halfHourFee` (3-6 blocks)
- `hourFee` (6+ blocks)

---

## File Structure

```
btc-wallet-tool/
├── btc_wallet_tool.py       # Main GUI application
├── translations.py          # RU/EN localization strings
├── btc_transaction.log      # Auto-generated transaction log
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

---

## Dependencies

```txt
Python >= 3.10
PyQt6 >= 6.7.0
bit == 0.8.0
requests >= 2.32.0
```

---

## CI/CD

GitHub Actions workflow builds Windows executable on release tags:
```yaml
- PyInstaller packaging
- Artifact upload to release
- Auto-versioning from git tags
```

---

## Roadmap

- [ ] RBF (Replace-By-Fee) support toggle
- [ ] P2SH-P2WPKH nested SegWit (3... addresses)
- [ ] Transaction history with block explorer links
- [ ] Coin selection strategy (largest-first/smallest-first)
- [ ] Testnet/mainnet network switcher
- [ ] Hardware wallet integration (Ledger/Trezor)

---

## Author

**Franklin Systems**  
🌐 [franklin-sys.vercel.app](https://franklin-sys.vercel.app/)

---

## License

MIT License — see LICENSE file for details

---

## Disclaimer

**Use at your own risk.** This software handles Bitcoin private keys — improper use can result in irreversible fund loss.

- Always verify recipient addresses before sending
- Never share your private key with anyone
- Test with small amounts first
- Bitcoin transactions are irreversible
- Keep your system secure (updated OS, antivirus, no pirated software)