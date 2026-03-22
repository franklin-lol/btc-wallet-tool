# ⟐ BTC TX Console

> Desktop GUI for signing and broadcasting Bitcoin transactions using a raw private key — no seed phrase, no cloud, no bullshit.

![Python](https://img.shields.io/badge/Python-3.10+-3572A5?style=flat-square&logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/PyQt6-GUI-41CD52?style=flat-square)
![Bitcoin](https://img.shields.io/badge/Bitcoin-mainnet-F7931A?style=flat-square&logo=bitcoin&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-555?style=flat-square)

---

## What it does

A minimal, offline-capable Bitcoin wallet console. You bring the private key — it handles the rest.

- **Recover addresses** from HEX or WIF private key (Legacy P2PKH + SegWit bech32)
- **Check live balance** via mempool.space API
- **Send transactions** with custom fee and amount, with confirmation dialog
- **Offline mode** — build raw TX hex without broadcasting. Paste into mempool.space/tx/push manually
- **Fee suggestions** pulled from mempool.space recommended fees
- Full transaction log written to `btc_transaction.log`

---

## Stack

| Component | Details |
|---|---|
| GUI | PyQt6 |
| Bitcoin logic | `bit` library |
| API | mempool.space (no account needed) |
| Offline signing | UTXO-based raw TX construction |

---

## Install

```bash
git clone https://github.com/franklin-lol/btc-wallet-tool
cd btc-wallet-tool
pip install PyQt6 bit requests
python btc_wallet_tool.py
```

---

## Usage

1. Paste your private key (64-char HEX or WIF format: `5...` / `K...` / `L...`)
2. Click **Recover Addresses** — Legacy and SegWit addresses appear
3. Select which address to use
4. Click **Check Balance** to fetch live UTXOs
5. Choose: **Send** (broadcast now) or **Build Raw TX** (offline, copy hex)

> The key field is masked by default. Click the eye icon to reveal.

---

## Offline mode

Build raw TX hex without an internet connection (UTXO data must be fetched separately).
Useful for air-gapped signing — build the hex, transfer to online machine, broadcast manually.

---

## Security notes

- Private key never leaves your machine
- No external dependencies beyond mempool.space for UTXO and fee data
- All transactions require explicit confirmation before broadcast
- Log file contains TX history but never stores the private key

---

## Fee calculation

Fee is estimated as `(180 * inputs + 34 + 10) * sat_per_byte`.
Use **Suggest Fee** to pull current network recommendations from mempool.space.

---

## Requirements

```
Python >= 3.10
PyQt6
bit
requests
```

---

## License

MIT

---

## Disclaimer

Use at your own risk. Never share your private key.