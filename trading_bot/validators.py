from typing import Optional, Literal
from pydantic import BaseModel, Field, validator
import re

OrderSide = Literal["BUY", "SELL"]
OrderType = Literal["MARKET", "LIMIT"]

class OrderRequest(BaseModel):
    """Validates order request parameters"""
    symbol: str = Field(..., description="Trading pair symbol, e.g., BTCUSDT")
    side: OrderSide = Field(..., description="Order side: BUY or SELL")
    order_type: OrderType = Field(..., alias="orderType", description="Order type: MARKET or LIMIT")
    quantity: float = Field(..., gt=0, description="Order quantity, must be positive")
    price: Optional[float] = Field(None, gt=0, description="Price for LIMIT orders")
    
    class Config:
        populate_by_name = True
    
    @validator('symbol')
    def validate_symbol(cls, v):
        """Validate symbol format"""
        if not re.match(r'^[A-Z0-9]+$', v):
            raise ValueError('Symbol must contain only uppercase letters and numbers')
        return v
    
    @validator('side')
    def validate_side(cls, v):
        """Validate order side"""
        if v not in ["BUY", "SELL"]:
            raise ValueError('Side must be either BUY or SELL')
        return v
    
    @validator('order_type')
    def validate_order_type(cls, v):
        """Validate order type"""
        valid_types = ["MARKET", "LIMIT"]
        if v not in valid_types:
            raise ValueError(f'Order type must be one of {valid_types}')
        return v
    
    def validate_price_fields(self):
        """Validate price fields based on order type"""
        if self.order_type == "LIMIT":
            if self.price is None:
                raise ValueError("Price is required for LIMIT orders")
        
        return True
