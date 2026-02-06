from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from typing import Dict, Any, Optional
import os
from .logging_config import logger

class BinanceFuturesClient:
    """Wrapper for Binance Futures API client with error handling"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        """
        Initialize Binance Futures client
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            testnet: Use testnet if True, mainnet if False
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        
        try:
            self.client = Client(api_key, api_secret, testnet=testnet)
            if testnet:
                self.client.API_URL = 'https://testnet.binancefuture.com'
            
            logger.info(f"Initialized Binance Futures client (testnet={testnet})")
        except Exception as e:
            logger.error(f"Failed to initialize Binance client: {str(e)}")
            raise
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get futures account information"""
        try:
            logger.info("Fetching account information")
            account = self.client.futures_account()
            logger.info("Successfully fetched account information")
            return account
        except BinanceAPIException as e:
            logger.error(f"Binance API error: {e.status_code} - {e.message}")
            raise
        except BinanceRequestException as e:
            logger.error(f"Binance request error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching account info: {str(e)}")
            raise
    
    def get_exchange_info(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Get exchange information for futures"""
        try:
            logger.info(f"Fetching exchange info for {symbol or 'all symbols'}")
            info = self.client.futures_exchange_info()
            
            if symbol:
                symbols_info = [s for s in info['symbols'] if s['symbol'] == symbol]
                if not symbols_info:
                    raise ValueError(f"Symbol {symbol} not found")
                return symbols_info[0]
            
            return info
        except BinanceAPIException as e:
            logger.error(f"Binance API error: {e.status_code} - {e.message}")
            raise
        except Exception as e:
            logger.error(f"Error fetching exchange info: {str(e)}")
            raise
    
    def get_ticker_price(self, symbol: str) -> Dict[str, Any]:
        """Get current ticker price for a symbol"""
        try:
            logger.info(f"Fetching ticker price for {symbol}")
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            logger.info(f"Current price for {symbol}: {ticker['price']}")
            return ticker
        except BinanceAPIException as e:
            logger.error(f"Binance API error: {e.status_code} - {e.message}")
            raise
        except Exception as e:
            logger.error(f"Error fetching ticker price: {str(e)}")
            raise
    
    def get_balance(self) -> list:
        """Get futures account balance"""
        try:
            logger.info("Fetching account balance")
            account = self.client.futures_account()
            balances = [b for b in account['assets'] if float(b['walletBalance']) > 0]
            logger.info(f"Found {len(balances)} assets with non-zero balance")
            return balances
        except Exception as e:
            logger.error(f"Error fetching balance: {str(e)}")
            raise
    
    def get_open_orders(self, symbol: Optional[str] = None) -> list:
        """Get open orders"""
        try:
            logger.info(f"Fetching open orders for {symbol or 'all symbols'}")
            if symbol:
                orders = self.client.futures_get_open_orders(symbol=symbol)
            else:
                orders = self.client.futures_get_open_orders()
            logger.info(f"Found {len(orders)} open orders")
            return orders
        except Exception as e:
            logger.error(f"Error fetching open orders: {str(e)}")
            raise
    
    def test_connectivity(self) -> bool:
        """Test API connectivity"""
        try:
            logger.info("Testing connectivity to Binance Futures API")
            self.client.futures_ping()
            logger.info("Successfully connected to Binance Futures API")
            return True
        except Exception as e:
            logger.error(f"Connectivity test failed: {str(e)}")
            return False
