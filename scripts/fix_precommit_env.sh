#!/usr/bin/env bash
set -euo pipefail

echo "[+] Installing pre-commit via pipx (recommended for externally managed Python)"
pipx install pre-commit --force || {
    echo "[!] pipx failed, trying system packages..."
    sudo apt install python3-pre-commit -y || {
        echo "[!] System packages failed, trying pip with --break-system-packages..."
        python3.12 -m pip install --break-system-packages -U pre-commit
    }
}

echo "[+] Cleaning pre-commit cache..."
rm -rf ~/.cache/pre-commit .cache/pre-commit || true
/home/matt/.local/bin/pre-commit clean || pre-commit clean

echo "[+] Installing hooks..."
/home/matt/.local/bin/pre-commit install --install-hooks -t pre-commit -t pre-push || pre-commit install --install-hooks -t pre-commit -t pre-push

echo "[+] Testing hooks..."
/home/matt/.local/bin/pre-commit run --all-files || pre-commit run --all-files || {
    echo "[!] Some hooks failed, but environment is repaired"
}

echo "[✓] pre-commit repaired - use '/home/matt/.local/bin/pre-commit' or ensure ~/.local/bin is in PATH"
