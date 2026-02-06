#!/usr/bin/env python3
"""
Binance Futures Trading Bot CLI

A modern command-line interface for placing orders on Binance Futures Testnet.
"""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from typing import Optional
import sys
import os
from pathlib import Path
import click

# Fix for typer/click compatibility issue
# Typer < 0.12.3 calls make_metavar without ctx, but Click 8.x requires it
try:
    from click.core import Parameter
    
    def safe_make_metavar(self, ctx=None):
        if self.metavar is not None:
            return self.metavar
        if self.type is not None:
             return self.type.name.upper()
        return self.name.upper()
        
    Parameter.make_metavar = safe_make_metavar

    # Also patch Typer's specific classes which override make_metavar
    import typer.core
    
    def safe_typer_make_metavar(self, ctx=None):
        # Typer's implementation usually just returns None or calls super?
        # We just return a safe string or name
        return self.metavar if self.metavar else (self.name.upper() if self.name else "")

    typer.core.TyperArgument.make_metavar = safe_typer_make_metavar
    typer.core.TyperOption.make_metavar = safe_typer_make_metavar
    
except Exception:
    pass

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from dotenv import load_dotenv
from trading_bot.client import BinanceFuturesClient
from trading_bot.orders import OrderManager
from trading_bot.validators import OrderRequest
from trading_bot.logging_config import logger

# Load environment variables
env_path = Path(__file__).parent / "backend" / ".env"
load_dotenv(env_path)

app = typer.Typer(
    name="trading-bot",
    help="🤖 Binance Futures Trading Bot CLI",
    add_completion=False,
    rich_markup_mode=None
)
console = Console()

def get_client():
    """Initialize and return Binance client"""
    api_key = os.environ.get('BINANCE_API_KEY')
    api_secret = os.environ.get('BINANCE_API_SECRET')
    use_testnet = os.environ.get('USE_TESTNET', 'true').lower() == 'true'
    
    if not api_key or not api_secret:
        console.print("[red]Error: Binance API credentials not found in .env file[/red]")
        console.print("Please set BINANCE_API_KEY and BINANCE_API_SECRET in /app/backend/.env")
        raise typer.Exit(1)
    
    try:
        return BinanceFuturesClient(api_key, api_secret, testnet=use_testnet)
    except Exception as e:
        console.print(f"[red]Error initializing Binance client:[/red] {str(e)}")
        console.print("[yellow]Note: This may be due to geo-restrictions from Binance[/yellow]")
        raise typer.Exit(1)

@app.command("market")
def place_market_order(
    symbol: str = typer.Argument(..., help="Trading pair symbol (e.g., BTCUSDT)"),
    side: str = typer.Argument(..., help="Order side: BUY or SELL"),
    quantity: float = typer.Argument(..., help="Order quantity"),
):
    """
    Place a MARKET order
    
    Example:
        trading-bot market BTCUSDT BUY 0.002
    """
    try:
        console.print(Panel.fit(
            f"[bold cyan]Placing MARKET Order[/bold cyan]\n"
            f"Symbol: [yellow]{symbol.upper()}[/yellow]\n"
            f"Side: [{'green' if side.upper() == 'BUY' else 'red'}]{side.upper()}[/{'green' if side.upper() == 'BUY' else 'red'}]\n"
            f"Quantity: [yellow]{quantity}[/yellow]",
            title="📋 Order Summary"
        ))
        
        client = get_client()
        order_manager = OrderManager(client)
        
        order_request = OrderRequest(
            symbol=symbol.upper(),
            side=side.upper(),
            orderType="MARKET",
            quantity=quantity
        )
        
        result = order_manager.place_order(order_request)
        
        # Display result
        table = Table(title="✅ Order Placed Successfully", show_header=True, header_style="bold magenta")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Order ID", str(result.get('orderId', 'N/A')))
        table.add_row("Symbol", result.get('symbol', 'N/A'))
        table.add_row("Side", result.get('side', 'N/A'))
        table.add_row("Type", result.get('type', 'N/A'))
        table.add_row("Status", result.get('status', 'N/A'))
        table.add_row("Quantity", result.get('origQty', 'N/A'))
        table.add_row("Executed Qty", result.get('executedQty', 'N/A'))
        if result.get('avgPrice'):
            table.add_row("Avg Price", result.get('avgPrice', 'N/A'))
        
        console.print(table)
        console.print(f"\n[green]✅ Success![/green] Order {result.get('orderId')} placed successfully.")
        
    except ValueError as e:
        console.print(f"[red]❌ Validation Error:[/red] {str(e)}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error:[/red] {str(e)}")
        raise typer.Exit(1)

@app.command("limit")
def place_limit_order(
    symbol: str = typer.Argument(..., help="Trading pair symbol (e.g., BTCUSDT)"),
    side: str = typer.Argument(..., help="Order side: BUY or SELL"),
    quantity: float = typer.Argument(..., help="Order quantity"),
    price: float = typer.Argument(..., help="Order price"),
):
    """
    Place a LIMIT order
    
    Example:
        trading-bot limit BTCUSDT BUY 0.002 50000
    """
    try:
        console.print(Panel.fit(
            f"[bold cyan]Placing LIMIT Order[/bold cyan]\n"
            f"Symbol: [yellow]{symbol.upper()}[/yellow]\n"
            f"Side: [{'green' if side.upper() == 'BUY' else 'red'}]{side.upper()}[/{'green' if side.upper() == 'BUY' else 'red'}]\n"
            f"Quantity: [yellow]{quantity}[/yellow]\n"
            f"Price: [yellow]{price}[/yellow]",
            title="📋 Order Summary"
        ))
        
        client = get_client()
        order_manager = OrderManager(client)
        
        order_request = OrderRequest(
            symbol=symbol.upper(),
            side=side.upper(),
            orderType="LIMIT",
            quantity=quantity,
            price=price
        )
        
        result = order_manager.place_order(order_request)
        
        # Display result
        table = Table(title="✅ Order Placed Successfully", show_header=True, header_style="bold magenta")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Order ID", str(result.get('orderId', 'N/A')))
        table.add_row("Symbol", result.get('symbol', 'N/A'))
        table.add_row("Side", result.get('side', 'N/A'))
        table.add_row("Type", result.get('type', 'N/A'))
        table.add_row("Status", result.get('status', 'N/A'))
        table.add_row("Quantity", result.get('origQty', 'N/A'))
        table.add_row("Price", result.get('price', 'N/A'))
        table.add_row("Executed Qty", result.get('executedQty', 'N/A'))
        
        console.print(table)
        console.print(f"\n[green]✅ Success![/green] Order {result.get('orderId')} placed successfully.")
        
    except ValueError as e:
        console.print(f"[red]❌ Validation Error:[/red] {str(e)}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error:[/red] {str(e)}")
        raise typer.Exit(1)

@app.command("stop-limit")
def place_stop_limit_order(
    symbol: str = typer.Argument(..., help="Trading pair symbol (e.g., BTCUSDT)"),
    side: str = typer.Argument(..., help="Order side: BUY or SELL"),
    quantity: float = typer.Argument(..., help="Order quantity"),
    price: float = typer.Argument(..., help="Limit price"),
    stop_price: float = typer.Argument(..., help="Stop trigger price"),
):
    """
    Place a STOP-LIMIT order (Bonus Feature)
    
    Example:
        trading-bot stop-limit BTCUSDT SELL 0.002 49000 49500
    """
    try:
        console.print(Panel.fit(
            f"[bold cyan]Placing STOP-LIMIT Order[/bold cyan]\n"
            f"Symbol: [yellow]{symbol.upper()}[/yellow]\n"
            f"Side: [{'green' if side.upper() == 'BUY' else 'red'}]{side.upper()}[/{'green' if side.upper() == 'BUY' else 'red'}]\n"
            f"Quantity: [yellow]{quantity}[/yellow]\n"
            f"Limit Price: [yellow]{price}[/yellow]\n"
            f"Stop Price: [yellow]{stop_price}[/yellow]",
            title="📋 Order Summary"
        ))
        
        client = get_client()
        order_manager = OrderManager(client)
        
        order_request = OrderRequest(
            symbol=symbol.upper(),
            side=side.upper(),
            orderType="STOP_LIMIT",
            quantity=quantity,
            price=price,
            stopPrice=stop_price
        )
        
        result = order_manager.place_order(order_request)
        
        # Display result
        table = Table(title="✅ Order Placed Successfully", show_header=True, header_style="bold magenta")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Order ID", str(result.get('orderId', 'N/A')))
        table.add_row("Symbol", result.get('symbol', 'N/A'))
        table.add_row("Side", result.get('side', 'N/A'))
        table.add_row("Type", result.get('type', 'N/A'))
        table.add_row("Status", result.get('status', 'N/A'))
        table.add_row("Quantity", result.get('origQty', 'N/A'))
        table.add_row("Price", result.get('price', 'N/A'))
        table.add_row("Stop Price", result.get('stopPrice', 'N/A'))
        
        console.print(table)
        console.print(f"\n[green]✅ Success![/green] Order {result.get('orderId')} placed successfully.")
        
    except ValueError as e:
        console.print(f"[red]❌ Validation Error:[/red] {str(e)}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error:[/red] {str(e)}")
        raise typer.Exit(1)

@app.command("balance")
def check_balance():
    """
    Check account balance
    """
    try:
        client = get_client()
        balances = client.get_balance()
        
        if not balances:
            console.print("[yellow]No assets with non-zero balance found[/yellow]")
            return
        
        table = Table(title="💰 Account Balance", show_header=True, header_style="bold magenta")
        table.add_column("Asset", style="cyan")
        table.add_column("Wallet Balance", style="green", justify="right")
        table.add_column("Available Balance", style="yellow", justify="right")
        
        for balance in balances:
            table.add_row(
                balance['asset'],
                balance['walletBalance'],
                balance['availableBalance']
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]❌ Error:[/red] {str(e)}")
        raise typer.Exit(1)

@app.command("price")
def get_price(
    symbol: str = typer.Argument(..., help="Trading pair symbol (e.g., BTCUSDT)")
):
    """
    Get current price for a symbol
    """
    try:
        client = get_client()
        ticker = client.get_ticker_price(symbol.upper())
        
        console.print(Panel.fit(
            f"[bold cyan]{ticker['symbol']}[/bold cyan]\n"
            f"Price: [bold green]${float(ticker['price']):,.2f}[/bold green]",
            title="📊 Current Price"
        ))
        
    except Exception as e:
        console.print(f"[red]❌ Error:[/red] {str(e)}")
        raise typer.Exit(1)

@app.command("orders")
def list_open_orders(
    symbol: Optional[str] = typer.Argument(None, help="Trading pair symbol (optional)")
):
    """
    List open orders
    """
    try:
        client = get_client()
        orders = client.get_open_orders(symbol.upper() if symbol else None)
        
        if not orders:
            console.print("[yellow]No open orders found[/yellow]")
            return
        
        table = Table(title="📋 Open Orders", show_header=True, header_style="bold magenta")
        table.add_column("Order ID", style="cyan")
        table.add_column("Symbol", style="yellow")
        table.add_column("Side", style="green")
        table.add_column("Type", style="blue")
        table.add_column("Quantity", justify="right")
        table.add_column("Price", justify="right")
        table.add_column("Status")
        
        for order in orders:
            table.add_row(
                str(order['orderId']),
                order['symbol'],
                order['side'],
                order['type'],
                order['origQty'],
                order.get('price', 'MARKET'),
                order['status']
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]❌ Error:[/red] {str(e)}")
        raise typer.Exit(1)

@app.command("test")
def test_connection():
    """
    Test connection to Binance Futures API
    """
    try:
        client = get_client()
        
        with console.status("[bold green]Testing connection..."):
            connected = client.test_connectivity()
        
        if connected:
            console.print("[green]✅ Successfully connected to Binance Futures API[/green]")
            
            # Get account info
            account = client.get_account_info()
            console.print(f"\n[cyan]Account Info:[/cyan]")
            console.print(f"  • Can Trade: {account.get('canTrade', False)}")
            console.print(f"  • Can Deposit: {account.get('canDeposit', False)}")
            console.print(f"  • Can Withdraw: {account.get('canWithdraw', False)}")
        else:
            console.print("[red]❌ Connection test failed[/red]")
            raise typer.Exit(1)
        
    except Exception as e:
        console.print(f"[red]❌ Error:[/red] {str(e)}")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
