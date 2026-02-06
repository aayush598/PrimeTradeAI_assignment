# Binance Futures Trading Bot (CLI)

A professional, Python-based CLI application for placing orders on the Binance Futures Testnet. Built with modern tooling (`typer`, `rich`, `pydantic`) to ensure robustness, type safety, and a great user experience.

## Features

*   **Order Management**:
    *   Place **MARKET** orders (BUY/SELL)
    *   Place **LIMIT** orders (BUY/SELL)
*   **Account Info**:
    *   Real-time Balance check
    *   Ticker Price lookup
    *   Open Orders listing
*   **Safety & Reliability**:
    *   Input validation (Symbol format, Sides, Quantities)
    *   Detailed error handling for API/Network issues
    *   Connectivity tests
*   **Logging**:
    *   Clean CLI output with valid status messages
    *   Detailed debug logging to file (`logs/`)

## Project Structure

```
trading_bot/
├── trading_bot/           # Application Package
│   ├── __init__.py
│   ├── client.py          # Binance Futures API Wrapper
│   ├── orders.py          # Order placement logic
│   ├── validators.py      # Input validation (Pydantic)
│   └── logging_config.py  # Logging setup
├── cli.py                 # CLI Entry Point
├── .env                   # Configuration
├── requirements.txt       # Dependencies
└── README.md              # Documentation
```

## Setup

### Prerequisites

*   Python 3.9+
*   Binance Futures Testnet Account

### Installation

1.  **Clone the repository/Extract zip**:
    ```bash
    cd trading_bot
    ```

2.  **Create and activate a virtual environment** (recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration**:
    Create a `.env` file in the root directory with your Testnet credentials:
    ```env
    BINANCE_API_KEY=your_api_key_here
    BINANCE_API_SECRET=your_api_secret_here
    USE_TESTNET=true
    ```

## Usage

Run the bot using the `cli.py` script. The CLI offers built-in help for all commands.

### 1. Test Connection
Verify your API keys and connectivity to Binance Testnet.
```bash
python cli.py test
```

### 2. Check Balance
See your current wallet balance.
```bash
python cli.py balance
```

### 3. Place Orders

**Note on Quantities**: Binance Testnet enforces a minimum order value (notional value) of ~$100. For BTC (assuming ~$60k), a quantity of `0.002` is safe. `0.001` is often too small.

*   **Market Order**:
    ```bash
    # Buy 0.002 BTC at market price
    python cli.py market BTCUSDT BUY 0.002
    ```

*   **Limit Order**:
    ```bash
    # Buy 0.002 BTC at $50,000
    python cli.py limit BTCUSDT BUY 0.002 50000
    ```



### 4. Other Commands
*   **Check Price**: `python cli.py price BTCUSDT`
*   **List Open Orders**: `python cli.py orders` (or `python cli.py orders BTCUSDT`)
*   **Help**: `python cli.py --help`

## Logging

*   **File Logs**: All detailed API interactions (requests, answers, full tracebacks) are stored in `logs/` directory, rotated daily.
    *   Example: `logs/trading_bot_20240206.log`
*   **Console**: Only essential information and user-friendly summaries are printed to keep the interface clean.

## Development

*   **Dependencies**: managed in `requirements.txt`.
*   **Linter/Formatter**: Code is typed and structured for readability.

---
**Note**: This is a testnet application. Ensure you are using `https://testnet.binancefuture.com` credentials.
