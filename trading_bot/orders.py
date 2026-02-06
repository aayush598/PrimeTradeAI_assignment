from binance.exceptions import BinanceAPIException, BinanceRequestException
from typing import Dict, Any, Optional
from .client import BinanceFuturesClient
from .validators import OrderRequest
from .logging_config import logger
import json

class OrderManager:
    """Handles order placement and management"""
    
    def __init__(self, client: BinanceFuturesClient):
        self.client = client
    
    def place_market_order(self, symbol: str, side: str, quantity: float) -> Dict[str, Any]:
        """Place a MARKET order"""
        try:
            logger.info(f"Placing MARKET order: {side} {quantity} {symbol}")
            
            order = self.client.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=quantity
            )
            
            logger.info(f"MARKET order placed successfully: OrderID={order['orderId']}, Status={order['status']}")
            logger.info(f"Order response: {json.dumps(order, indent=2)}")
            
            return order
        except BinanceAPIException as e:
            logger.error(f"Binance API error placing MARKET order: {e.status_code} - {e.message}")
            raise Exception(f"API Error: {e.message}")
        except BinanceRequestException as e:
            logger.error(f"Binance request error: {str(e)}")
            raise Exception(f"Request Error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error placing MARKET order: {str(e)}")
            raise
    
    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float, time_in_force: str = 'GTC') -> Dict[str, Any]:
        """Place a LIMIT order"""
        try:
            logger.info(f"Placing LIMIT order: {side} {quantity} {symbol} @ {price}")
            
            order = self.client.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='LIMIT',
                timeInForce=time_in_force,
                quantity=quantity,
                price=price
            )
            
            logger.info(f"LIMIT order placed successfully: OrderID={order['orderId']}, Status={order['status']}")
            logger.info(f"Order response: {json.dumps(order, indent=2)}")
            
            return order
        except BinanceAPIException as e:
            logger.error(f"Binance API error placing LIMIT order: {e.status_code} - {e.message}")
            raise Exception(f"API Error: {e.message}")
        except BinanceRequestException as e:
            logger.error(f"Binance request error: {str(e)}")
            raise Exception(f"Request Error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error placing LIMIT order: {str(e)}")
            raise
    

    
    def place_order(self, order_request: OrderRequest) -> Dict[str, Any]:
        """Place an order based on OrderRequest"""
        # Validate price fields
        order_request.validate_price_fields()
        
        order_type = order_request.order_type
        
        if order_type == "MARKET":
            return self.place_market_order(
                symbol=order_request.symbol,
                side=order_request.side,
                quantity=order_request.quantity
            )
        elif order_type == "LIMIT":
            return self.place_limit_order(
                symbol=order_request.symbol,
                side=order_request.side,
                quantity=order_request.quantity,
                price=order_request.price
            )
        else:
            raise ValueError(f"Unsupported order type: {order_type}")
    
    def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """Cancel an open order"""
        try:
            logger.info(f"Cancelling order {order_id} for {symbol}")
            result = self.client.client.futures_cancel_order(
                symbol=symbol,
                orderId=order_id
            )
            logger.info(f"Order cancelled successfully: {order_id}")
            return result
        except Exception as e:
            logger.error(f"Error cancelling order: {str(e)}")
            raise
    
    def get_order_status(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """Get order status"""
        try:
            logger.info(f"Fetching status for order {order_id}")
            order = self.client.client.futures_get_order(
                symbol=symbol,
                orderId=order_id
            )
            return order
        except Exception as e:
            logger.error(f"Error fetching order status: {str(e)}")
            raise
