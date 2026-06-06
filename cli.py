"""
Interactive CLI for USDT to TRX Exchange
"""
import logging
import sys
import os
from tron_client import TronClient
from exchange_client import ExchangeClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('exchange.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def print_banner():
    """Print program banner"""
    print("\n" + "="*60)
    print("  USDT ↔ TRX Exchange Program")
    print("="*60 + "\n")


def print_menu():
    """Print main menu"""
    print("\n📋 Main Menu:")
    print("1. Check TRX Balance")
    print("2. Check USDT Balance")
    print("3. Get Exchange Rate")
    print("4. Calculate Conversion (USDT → TRX)")
    print("5. Check Network Status")
    print("6. View Help")
    print("7. Exit")
    print("-" * 60)


def check_balance_trx(tron_client):
    """Check TRX balance"""
    try:
        balance = tron_client.get_trx_balance()
        print(f"\n💰 TRX Balance: {balance:.6f} TRX")
        return balance
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None


def check_balance_usdt(tron_client):
    """Check USDT balance"""
    try:
        balance = tron_client.get_usdt_balance()
        print(f"\n💵 USDT Balance: {balance:.2f} USDT")
        return balance
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None


def get_exchange_rate(exchange_client):
    """Get and display exchange rate"""
    try:
        rates = exchange_client.get_exchange_rate()
        print(f"\n📊 Exchange Rates:")
        print(f"   USDT Price: ${rates['usdt_price']:.4f}")
        print(f"   TRX Price:  ${rates['trx_price']:.6f}")
        print(f"   1 USDT = {rates['usdt_to_trx_rate']:.6f} TRX")
        return rates
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None


def calculate_conversion(exchange_client, exchange_rate):
    """Calculate USDT to TRX conversion"""
    try:
        if exchange_rate is None:
            print("⚠️  Please get exchange rate first (option 3)")
            return
        
        usdt_input = input("\nEnter USDT amount: ").strip()
        try:
            usdt_amount = float(usdt_input)
            if usdt_amount < 0:
                print("❌ Amount must be positive")
                return
            
            trx_amount = exchange_client.calculate_trx_amount(usdt_amount, exchange_rate)
            print(f"\n🔄 Conversion Result:")
            print(f"   {usdt_amount:.2f} USDT = {trx_amount:.6f} TRX")
            
        except ValueError:
            print("❌ Invalid amount. Please enter a number.")
    except Exception as e:
        print(f"\n❌ Error: {e}")


def check_network_status(tron_client):
    """Check Tron network connection status"""
    print("\n🔍 Checking network status...")
    if tron_client.is_connected():
        print("✅ Connected to Tron Network")
        try:
            balance = tron_client.get_trx_balance()
            usdt_balance = tron_client.get_usdt_balance()
            print(f"   Wallet: {tron_client.wallet_address}")
            print(f"   TRX Balance: {balance:.6f}")
            print(f"   USDT Balance: {usdt_balance:.2f}")
        except Exception as e:
            print(f"   Warning: Could not fetch balances: {e}")
    else:
        print("❌ Not connected to Tron Network")
        print("   Please check your internet connection or RPC endpoint")


def print_help():
    """Print help information"""
    print("\n" + "="*60)
    print("📚 Help Information")
    print("="*60)
    print("""
This program allows you to:
- Check your TRX and USDT balances on Tron blockchain
- Get real-time exchange rates from CoinGecko
- Calculate conversion amounts between USDT and TRX
- Monitor network connectivity

Configuration (.env file):
- TRON_PRIVATE_KEY: Your Tron wallet private key
- WALLET_ADDRESS: Your Tron wallet address
- TRON_RPC_ENDPOINT: Tron network RPC endpoint

For more information, see README.md

⚠️  Security Notes:
- Never share your private key
- Always verify addresses before transactions
- Test with small amounts first
- Keep your .env file secure
    """)
    print("="*60)


def main():
    """Main CLI function"""
    try:
        print_banner()
        
        # Initialize clients
        print("🔌 Initializing clients...")
        try:
            tron_client = TronClient()
            exchange_client = ExchangeClient()
            print("✅ Clients initialized successfully\n")
        except Exception as e:
            print(f"❌ Failed to initialize: {e}")
            print("Please check your .env configuration")
            return False
        
        exchange_rate = None
        
        # Main loop
        while True:
            print_menu()
            choice = input("Enter your choice (1-7): ").strip()
            
            if choice == "1":
                check_balance_trx(tron_client)
            elif choice == "2":
                check_balance_usdt(tron_client)
            elif choice == "3":
                exchange_rate = get_exchange_rate(exchange_client)
            elif choice == "4":
                calculate_conversion(exchange_client, exchange_rate)
            elif choice == "5":
                check_network_status(tron_client)
            elif choice == "6":
                print_help()
            elif choice == "7":
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-7.")
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n👋 Program interrupted by user")
        return True
    except Exception as e:
        logger.error(f"Program failed with error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
