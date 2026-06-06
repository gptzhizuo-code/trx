#!/bin/bash
set -euo pipefail

# run_jokes_local.sh
# 本脚本在本地运行 jokes.py：创建 venv、安装依赖、注入 .env，并运行脚本。
# 使用方法：
#   chmod +x run_jokes_local.sh
#   ./run_jokes_local.sh

echo "🚀 Run Jokes Local Script - Starting..."

# Check python3
if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ python3 not found. Install Python 3.8+ first (brew install python)"; exit 1
fi

PY_VER=$(python3 -c 'import sys; print(".".join(map(str,sys.version_info[:2])))')
echo "✅ Python version: $PY_VER"

# Create venv if not exist
if [ ! -d "venv" ]; then
  echo "📦 Creating virtual environment..."
  python3 -m venv venv
else
  echo "ℹ️  Virtual environment 'venv' already exists."
fi

# Activate venv
echo "🔌 Activating virtual environment..."
# shellcheck source=/dev/null
source venv/bin/activate

# Upgrade pip and install deps
echo "🔄 Upgrading pip and installing dependencies..."
python -m pip install --upgrade pip >/dev/null
pip install -r requirements.txt

# Ensure .env exists
if [ ! -f ".env" ]; then
  if [ -f ".env.example" ]; then
    cp .env.example .env
    echo "✅ .env created from .env.example"
  else
    echo "❌ .env.example not found. Create a .env manually."; exit 1
  fi
else
  echo "ℹ️  .env already exists"
fi

# helper to set or replace key in .env (macOS-compatible sed)
set_env() {
  key="$1"
  val="$2"
  if grep -qE "^${key}=" .env; then
    # mac sed requires empty suffix for -i
    sed -i '' "s|^${key}=.*|${key}=${val}|" .env
  else
    echo "${key}=${val}" >> .env
  fi
}

echo "⚠️  Sensitive inputs will NOT be shown on screen."

# Prompt for TRON_PRIVATE_KEY if not present in env or .env
current_tron_key=$(grep -E "^TRON_PRIVATE_KEY=" .env || true)
if [ -z "$current_tron_key" ] || [[ "$current_tron_key" =~ ^= ]]; then
  read -s -p "Enter TRON_PRIVATE_KEY (hidden): " TRON_PRIVATE_KEY_INPUT
  echo
  if [ -z "$TRON_PRIVATE_KEY_INPUT" ]; then
    echo "ℹ️  No input provided. Keeping existing .env value (if any)."
  else
    set_env "TRON_PRIVATE_KEY" "$TRON_PRIVATE_KEY_INPUT"
    echo "✅ TRON_PRIVATE_KEY updated in .env"
  fi
else
  echo "ℹ️  TRON_PRIVATE_KEY already set in .env"
fi

# Prompt for WALLET_ADDRESS if not present
current_addr=$(grep -E "^WALLET_ADDRESS=" .env || true)
if [ -z "$current_addr" ] || [[ "$current_addr" =~ ^= ]]; then
  read -p "Enter WALLET_ADDRESS (your Tron address) [leave empty to skip]: " WALLET_ADDRESS_INPUT
  if [ -n "$WALLET_ADDRESS_INPUT" ]; then
    set_env "WALLET_ADDRESS" "$WALLET_ADDRESS_INPUT"
    echo "✅ WALLET_ADDRESS updated in .env"
  else
    echo "ℹ️  No WALLET_ADDRESS provided"
  fi
else
  echo "ℹ️  WALLET_ADDRESS already set in .env"
fi

# Optional: TELEGRAM_TOKEN for bot usage
current_telegram=$(grep -E "^TELEGRAM_TOKEN=" .env || true)
if [ -z "$current_telegram" ] || [[ "$current_telegram" =~ ^= ]]; then
  read -s -p "Enter TELEGRAM_TOKEN (hidden, optional - press Enter to skip): " TELEGRAM_TOKEN_INPUT
  echo
  if [ -n "$TELEGRAM_TOKEN_INPUT" ]; then
    set_env "TELEGRAM_TOKEN" "$TELEGRAM_TOKEN_INPUT"
    echo "✅ TELEGRAM_TOKEN updated in .env"
  else
    echo "ℹ️  TELEGRAM_TOKEN not provided"
  fi
else
  echo "ℹ️  TELEGRAM_TOKEN already set in .env"
fi

echo "🔐 .env prepared (sensitive values hidden)."

# Run jokes.py
LOGFILE="jokes.log"
echo "🎭 Running jokes.py (output -> ${LOGFILE}) ..."
# Ensure environment variables in current shell are available to Python by exporting key ones
# (Python will read .env via python-dotenv if implemented in code)
export $(grep -E '^(TRON_RPC_ENDPOINT|TRON_PRIVATE_KEY|WALLET_ADDRESS|TELEGRAM_TOKEN)=' .env | xargs)

python jokes.py > "${LOGFILE}" 2>&1 || {
  echo "❌ jokes.py exited with error. See ${LOGFILE} for details."
  tail -n 200 "${LOGFILE}" || true
  exit 1
}

echo "✅ jokes.py completed. Last 200 lines of ${LOGFILE}:"
echo "----"
tail -n 200 "${LOGFILE}"
echo "----"
echo "🎉 Done. If you want to run in background: nohup ./run_jokes_local.sh &"