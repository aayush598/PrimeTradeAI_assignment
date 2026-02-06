from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone

from trading_bot.client import BinanceFuturesClient
from trading_bot.orders import OrderManager
from trading_bot.validators import OrderRequest
from trading_bot.logging_config import logger

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Binance Futures Trading Bot API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize Binance client
BINANCE_API_KEY = os.environ.get('BINANCE_API_KEY')
BINANCE_API_SECRET = os.environ.get('BINANCE_API_SECRET')
USE_TESTNET = os.environ.get('USE_TESTNET', 'true').lower() == 'true'
DEMO_MODE = os.environ.get('DEMO_MODE', 'false').lower() == 'true'

binance_client = None
order_manager = None
demo_mode_active = False

if DEMO_MODE:
    logger.warning("DEMO MODE ENABLED - Using simulated orders")
    demo_mode_active = True
elif not BINANCE_API_KEY or not BINANCE_API_SECRET:
    logger.warning("Binance API credentials not found in environment variables - Enabling DEMO MODE")
    demo_mode_active = True
else:
    try:
        binance_client = BinanceFuturesClient(
            api_key=BINANCE_API_KEY,
            api_secret=BINANCE_API_SECRET,
            testnet=USE_TESTNET
        )
        order_manager = OrderManager(binance_client)
        logger.info("Binance client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Binance client: {str(e)}")
        logger.warning("Enabling DEMO MODE due to initialization failure")
        demo_mode_active = True
        binance_client = None
        order_manager = None

# Models
class OrderResponse(BaseModel):
    success: bool
    order_id: Optional[int] = None
    status: Optional[str] = None
    symbol: Optional[str] = None
    side: Optional[str] = None
    type: Optional[str] = None
    quantity: Optional[str] = None
    price: Optional[str] = None
    executed_qty: Optional[str] = None
    avg_price: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None

class OrderHistoryItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    order_id: Optional[int] = None
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    status: str
    executed_qty: Optional[float] = None
    avg_price: Optional[float] = None

# Routes
@api_router.get("/")
async def root():
    return {"message": "Binance Futures Trading Bot API", "status": "active"}

@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    if demo_mode_active:
        return {
            "status": "demo",
            "message": "Running in DEMO MODE - Simulated orders only",
            "binance_connected": False,
            "demo_mode": True,
            "testnet": USE_TESTNET
        }
    
    if not binance_client:
        return {
            "status": "warning",
            "message": "API running but Binance client not initialized",
            "binance_connected": False,
            "demo_mode": False
        }
    
    try:
        connected = binance_client.test_connectivity()
        return {
            "status": "healthy" if connected else "degraded",
            "message": "All systems operational" if connected else "Binance API connection issue",
            "binance_connected": connected,
            "demo_mode": False,
            "testnet": USE_TESTNET
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "binance_connected": False,
            "demo_mode": False
        }

@api_router.get("/account")
async def get_account_info():
    """Get account information"""
    if not binance_client:
        raise HTTPException(status_code=503, detail="Binance client not initialized")
    
    try:
        account = binance_client.get_account_info()
        return account
    except Exception as e:
        logger.error(f"Error fetching account info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/balance")
async def get_balance():
    """Get account balance"""
    if demo_mode_active:
        # Return simulated balance
        demo_balances = [
            {
                "asset": "USDT",
                "walletBalance": "10000.00000000",
                "availableBalance": "9500.00000000"
            },
            {
                "asset": "BTC",
                "walletBalance": "0.05000000",
                "availableBalance": "0.05000000"
            }
        ]
        return {"balances": demo_balances}
    
    if not binance_client:
        raise HTTPException(status_code=503, detail="Binance client not initialized")
    
    try:
        balances = binance_client.get_balance()
        return {"balances": balances}
    except Exception as e:
        logger.error(f"Error fetching balance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/ticker/{symbol}")
async def get_ticker(symbol: str):
    """Get ticker price for a symbol"""
    if not binance_client:
        raise HTTPException(status_code=503, detail="Binance client not initialized")
    
    try:
        ticker = binance_client.get_ticker_price(symbol.upper())
        return ticker
    except Exception as e:
        logger.error(f"Error fetching ticker: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/orders/open")
async def get_open_orders(symbol: Optional[str] = None):
    """Get open orders"""
    if not binance_client:
        raise HTTPException(status_code=503, detail="Binance client not initialized")
    
    try:
        orders = binance_client.get_open_orders(symbol.upper() if symbol else None)
        return {"orders": orders}
    except Exception as e:
        logger.error(f"Error fetching open orders: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/orders/place", response_model=OrderResponse)
async def place_order(order_request: OrderRequest):
    """Place a new order"""
    try:
        logger.info(f"Received order request: {order_request.model_dump()}")
        
        # Demo mode - simulate order placement
        if demo_mode_active:
            import random
            from datetime import datetime
            
            # Simulate order response
            order_id = random.randint(10000000, 99999999)
            
            # Simulate different statuses based on order type
            if order_request.order_type == "MARKET":
                status = "FILLED"
                executed_qty = order_request.quantity
                avg_price = str(50000 + random.uniform(-1000, 1000))  # Simulated price
            else:
                status = "NEW"
                executed_qty = 0
                avg_price = "0"
            
            order_result = {
                "orderId": order_id,
                "symbol": order_request.symbol,
                "status": status,
                "side": order_request.side,
                "type": order_request.order_type,
                "origQty": str(order_request.quantity),
                "executedQty": str(executed_qty),
                "price": str(order_request.price) if order_request.price else "0",
                "stopPrice": str(order_request.stop_price) if order_request.stop_price else "0",
                "avgPrice": avg_price,
            }
            
            logger.info(f"DEMO MODE: Simulated order placed - OrderID={order_id}, Status={status}")
            
            # Save to database
            order_history = OrderHistoryItem(
                order_id=order_id,
                symbol=order_request.symbol,
                side=order_request.side,
                order_type=order_request.order_type,
                quantity=order_request.quantity,
                price=order_request.price,
                stop_price=order_request.stop_price,
                status=status,
                executed_qty=float(executed_qty) if executed_qty else None,
                avg_price=float(avg_price) if avg_price != "0" else None
            )
            
            doc = order_history.model_dump()
            doc['timestamp'] = doc['timestamp'].isoformat()
            await db.order_history.insert_one(doc)
            
            return OrderResponse(
                success=True,
                order_id=order_id,
                status=status,
                symbol=order_request.symbol,
                side=order_request.side,
                type=order_request.order_type,
                quantity=str(order_request.quantity),
                price=str(order_request.price) if order_request.price else None,
                executed_qty=str(executed_qty),
                avg_price=avg_price if avg_price != "0" else None,
                message=f"DEMO MODE: {order_request.order_type} order simulated successfully"
            )
        
        # Real mode - use Binance API
        if not order_manager:
            raise HTTPException(status_code=503, detail="Order manager not initialized")
        
        # Place the order
        order_result = order_manager.place_order(order_request)
        
        # Save to database
        order_history = OrderHistoryItem(
            order_id=order_result.get('orderId'),
            symbol=order_request.symbol,
            side=order_request.side,
            order_type=order_request.order_type,
            quantity=order_request.quantity,
            price=order_request.price,
            stop_price=order_request.stop_price,
            status=order_result.get('status', 'UNKNOWN'),
            executed_qty=float(order_result.get('executedQty', 0)) if order_result.get('executedQty') else None,
            avg_price=float(order_result.get('avgPrice', 0)) if order_result.get('avgPrice') else None
        )
        
        doc = order_history.model_dump()
        doc['timestamp'] = doc['timestamp'].isoformat()
        await db.order_history.insert_one(doc)
        
        return OrderResponse(
            success=True,
            order_id=order_result.get('orderId'),
            status=order_result.get('status'),
            symbol=order_result.get('symbol'),
            side=order_result.get('side'),
            type=order_result.get('type'),
            quantity=order_result.get('origQty'),
            price=order_result.get('price'),
            executed_qty=order_result.get('executedQty'),
            avg_price=order_result.get('avgPrice'),
            message=f"{order_request.order_type} order placed successfully"
        )
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error placing order: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/orders/history", response_model=List[OrderHistoryItem])
async def get_order_history(limit: int = 50):
    """Get order history from database"""
    try:
        orders = await db.order_history.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
        
        # Convert ISO string timestamps back to datetime objects
        for order in orders:
            if isinstance(order['timestamp'], str):
                order['timestamp'] = datetime.fromisoformat(order['timestamp'])
        
        return orders
    except Exception as e:
        logger.error(f"Error fetching order history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/orders/cancel/{symbol}/{order_id}")
async def cancel_order(symbol: str, order_id: int):
    """Cancel an open order"""
    if not order_manager:
        raise HTTPException(status_code=503, detail="Order manager not initialized")
    
    try:
        result = order_manager.cancel_order(symbol.upper(), order_id)
        return {"success": True, "message": "Order cancelled", "result": result}
    except Exception as e:
        logger.error(f"Error cancelling order: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/orders/status/{symbol}/{order_id}")
async def get_order_status(symbol: str, order_id: int):
    """Get order status"""
    if not order_manager:
        raise HTTPException(status_code=503, detail="Order manager not initialized")
    
    try:
        order = order_manager.get_order_status(symbol.upper(), order_id)
        return order
    except Exception as e:
        logger.error(f"Error fetching order status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
