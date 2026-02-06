import React, { useState, useEffect } from "react";
import { api } from "@/App";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { TrendingUp, TrendingDown, DollarSign, Activity, CheckCircle2, AlertCircle } from "lucide-react";

export const TradingDashboard = () => {
  const [formData, setFormData] = useState({
    symbol: "BTCUSDT",
    side: "BUY",
    orderType: "MARKET",
    quantity: "",
    price: "",
    stopPrice: "",
  });

  const [loading, setLoading] = useState(false);
  const [balance, setBalance] = useState([]);
  const [orderHistory, setOrderHistory] = useState([]);
  const [currentPrice, setCurrentPrice] = useState(null);
  const [healthStatus, setHealthStatus] = useState(null);

  useEffect(() => {
    fetchHealthStatus();
    fetchBalance();
    fetchOrderHistory();
    fetchPrice();
  }, []);

  const fetchHealthStatus = async () => {
    try {
      const response = await api.get("/health");
      setHealthStatus(response.data);
    } catch (error) {
      console.error("Error fetching health status:", error);
    }
  };

  const fetchBalance = async () => {
    try {
      const response = await api.get("/balance");
      setBalance(response.data.balances || []);
    } catch (error) {
      console.error("Error fetching balance:", error);
    }
  };

  const fetchOrderHistory = async () => {
    try {
      const response = await api.get("/orders/history");
      setOrderHistory(response.data || []);
    } catch (error) {
      console.error("Error fetching order history:", error);
    }
  };

  const fetchPrice = async () => {
    try {
      const response = await api.get(`/ticker/${formData.symbol}`);
      setCurrentPrice(parseFloat(response.data.price));
    } catch (error) {
      console.error("Error fetching price:", error);
    }
  };

  useEffect(() => {
    if (formData.symbol) {
      fetchPrice();
    }
  }, [formData.symbol]);

  const handleInputChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handlePlaceOrder = async () => {
    if (!formData.quantity || parseFloat(formData.quantity) <= 0) {
      toast.error("Please enter a valid quantity");
      return;
    }

    if (formData.orderType === "LIMIT" && (!formData.price || parseFloat(formData.price) <= 0)) {
      toast.error("Please enter a valid price for LIMIT order");
      return;
    }

    if (formData.orderType === "STOP_LIMIT" && (!formData.price || !formData.stopPrice)) {
      toast.error("Please enter both price and stop price for STOP_LIMIT order");
      return;
    }

    setLoading(true);
    try {
      const payload = {
        symbol: formData.symbol,
        side: formData.side,
        orderType: formData.orderType,
        quantity: parseFloat(formData.quantity),
      };

      if (formData.orderType === "LIMIT") {
        payload.price = parseFloat(formData.price);
      }

      if (formData.orderType === "STOP_LIMIT") {
        payload.price = parseFloat(formData.price);
        payload.stopPrice = parseFloat(formData.stopPrice);
      }

      const response = await api.post("/orders/place", payload);
      
      if (response.data.success) {
        toast.success(`Order placed successfully! Order ID: ${response.data.order_id}`);
        setFormData({
          ...formData,
          quantity: "",
          price: "",
          stopPrice: "",
        });
        fetchOrderHistory();
        fetchBalance();
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message || "Failed to place order";
      toast.error(errorMsg);
      console.error("Error placing order:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-4xl sm:text-5xl font-bold text-white mb-2" style={{ fontFamily: "'Exo 2', sans-serif" }}>
              Binance Futures Trading
            </h1>
            <p className="text-slate-400" style={{ fontFamily: "'Inter', sans-serif" }}>
              Professional Trading Bot Dashboard
            </p>
          </div>
          
          {healthStatus && (
            <div className="flex items-center gap-2 glass-card px-4 py-2">
              {healthStatus.binance_connected ? (
                <>
                  <CheckCircle2 className="w-5 h-5 text-green-400 status-pulse" />
                  <span className="text-green-400 font-medium">Connected</span>
                  {healthStatus.testnet && (
                    <Badge variant="outline" className="ml-2 border-yellow-400 text-yellow-400">
                      Testnet
                    </Badge>
                  )}
                </>
              ) : (
                <>
                  <AlertCircle className="w-5 h-5 text-red-400" />
                  <span className="text-red-400 font-medium">Disconnected</span>
                </>
              )}
            </div>
          )}
        </div>

        {/* Main Grid */}
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Order Form */}
          <div className="lg:col-span-2">
            <Card className="trading-card border-2" data-testid="order-form-card">
              <CardHeader>
                <CardTitle className="text-2xl text-white flex items-center gap-2">
                  <Activity className="w-6 h-6 text-blue-400" />
                  Place Order
                </CardTitle>
                <CardDescription className="text-slate-400">
                  Execute trades on Binance Futures Testnet
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid sm:grid-cols-2 gap-4">
                  {/* Symbol */}
                  <div className="space-y-2">
                    <Label htmlFor="symbol" className="text-slate-300">
                      Trading Pair
                    </Label>
                    <Input
                      id="symbol"
                      data-testid="symbol-input"
                      value={formData.symbol}
                      onChange={(e) => handleInputChange("symbol", e.target.value.toUpperCase())}
                      placeholder="BTCUSDT"
                      className="bg-slate-800/50 border-slate-600 text-white"
                    />
                    {currentPrice && (
                      <p className="text-sm text-slate-400">
                        Current Price: <span className="text-green-400 font-bold">${currentPrice.toLocaleString()}</span>
                      </p>
                    )}
                  </div>

                  {/* Side */}
                  <div className="space-y-2">
                    <Label htmlFor="side" className="text-slate-300">
                      Side
                    </Label>
                    <Select value={formData.side} onValueChange={(value) => handleInputChange("side", value)}>
                      <SelectTrigger
                        data-testid="side-select"
                        className="bg-slate-800/50 border-slate-600 text-white"
                      >
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="BUY" data-testid="side-buy">
                          <div className="flex items-center gap-2">
                            <TrendingUp className="w-4 h-4 text-green-400" />
                            <span>BUY</span>
                          </div>
                        </SelectItem>
                        <SelectItem value="SELL" data-testid="side-sell">
                          <div className="flex items-center gap-2">
                            <TrendingDown className="w-4 h-4 text-red-400" />
                            <span>SELL</span>
                          </div>
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Order Type */}
                  <div className="space-y-2">
                    <Label htmlFor="orderType" className="text-slate-300">
                      Order Type
                    </Label>
                    <Select value={formData.orderType} onValueChange={(value) => handleInputChange("orderType", value)}>
                      <SelectTrigger
                        data-testid="order-type-select"
                        className="bg-slate-800/50 border-slate-600 text-white"
                      >
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="MARKET" data-testid="order-type-market">MARKET</SelectItem>
                        <SelectItem value="LIMIT" data-testid="order-type-limit">LIMIT</SelectItem>
                        <SelectItem value="STOP_LIMIT" data-testid="order-type-stop-limit">STOP LIMIT</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Quantity */}
                  <div className="space-y-2">
                    <Label htmlFor="quantity" className="text-slate-300">
                      Quantity
                    </Label>
                    <Input
                      id="quantity"
                      data-testid="quantity-input"
                      type="number"
                      step="0.001"
                      value={formData.quantity}
                      onChange={(e) => handleInputChange("quantity", e.target.value)}
                      placeholder="0.001"
                      className="bg-slate-800/50 border-slate-600 text-white"
                    />
                  </div>

                  {/* Price (for LIMIT and STOP_LIMIT) */}
                  {(formData.orderType === "LIMIT" || formData.orderType === "STOP_LIMIT") && (
                    <div className="space-y-2">
                      <Label htmlFor="price" className="text-slate-300">
                        {formData.orderType === "STOP_LIMIT" ? "Limit Price" : "Price"}
                      </Label>
                      <Input
                        id="price"
                        data-testid="price-input"
                        type="number"
                        step="0.01"
                        value={formData.price}
                        onChange={(e) => handleInputChange("price", e.target.value)}
                        placeholder="50000"
                        className="bg-slate-800/50 border-slate-600 text-white"
                      />
                    </div>
                  )}

                  {/* Stop Price (for STOP_LIMIT) */}
                  {formData.orderType === "STOP_LIMIT" && (
                    <div className="space-y-2">
                      <Label htmlFor="stopPrice" className="text-slate-300">
                        Stop Price
                      </Label>
                      <Input
                        id="stopPrice"
                        data-testid="stop-price-input"
                        type="number"
                        step="0.01"
                        value={formData.stopPrice}
                        onChange={(e) => handleInputChange("stopPrice", e.target.value)}
                        placeholder="49500"
                        className="bg-slate-800/50 border-slate-600 text-white"
                      />
                    </div>
                  )}
                </div>

                <Button
                  data-testid="place-order-button"
                  onClick={handlePlaceOrder}
                  disabled={loading}
                  className={`w-full h-12 text-lg font-semibold ${
                    formData.side === "BUY"
                      ? "bg-green-600 hover:bg-green-700"
                      : "bg-red-600 hover:bg-red-700"
                  } text-white`}
                >
                  {loading ? "Placing Order..." : `${formData.side} ${formData.symbol}`}
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Account Balance */}
          <div className="space-y-6">
            <Card className="trading-card" data-testid="balance-card">
              <CardHeader>
                <CardTitle className="text-xl text-white flex items-center gap-2">
                  <DollarSign className="w-5 h-5 text-green-400" />
                  Account Balance
                </CardTitle>
              </CardHeader>
              <CardContent>
                {balance.length > 0 ? (
                  <div className="space-y-3">
                    {balance.map((asset, index) => (
                      <div
                        key={index}
                        className="p-3 rounded-lg bg-slate-800/30 border border-slate-700"
                        data-testid={`balance-item-${asset.asset}`}
                      >
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-slate-300 font-semibold">{asset.asset}</span>
                          <Badge variant="outline" className="border-blue-400 text-blue-400">
                            Available
                          </Badge>
                        </div>
                        <p className="text-2xl font-bold text-white">
                          {parseFloat(asset.availableBalance).toFixed(4)}
                        </p>
                        <p className="text-sm text-slate-400 mt-1">
                          Wallet: {parseFloat(asset.walletBalance).toFixed(4)}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-slate-400 text-center py-4">No balance data available</p>
                )}
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Order History */}
        <Card className="trading-card" data-testid="order-history-card">
          <CardHeader>
            <CardTitle className="text-2xl text-white">Order History</CardTitle>
            <CardDescription className="text-slate-400">Recent trading activity</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left py-3 px-4 text-slate-300 font-semibold">Time</th>
                    <th className="text-left py-3 px-4 text-slate-300 font-semibold">Symbol</th>
                    <th className="text-left py-3 px-4 text-slate-300 font-semibold">Side</th>
                    <th className="text-left py-3 px-4 text-slate-300 font-semibold">Type</th>
                    <th className="text-right py-3 px-4 text-slate-300 font-semibold">Quantity</th>
                    <th className="text-right py-3 px-4 text-slate-300 font-semibold">Price</th>
                    <th className="text-left py-3 px-4 text-slate-300 font-semibold">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {orderHistory.length > 0 ? (
                    orderHistory.map((order, index) => (
                      <tr
                        key={index}
                        className="border-b border-slate-800 order-row"
                        data-testid={`order-history-row-${index}`}
                      >
                        <td className="py-3 px-4 text-slate-400 text-sm">
                          {new Date(order.timestamp).toLocaleString()}
                        </td>
                        <td className="py-3 px-4 text-white font-medium">{order.symbol}</td>
                        <td className="py-3 px-4">
                          <Badge
                            variant="outline"
                            className={
                              order.side === "BUY"
                                ? "border-green-400 text-green-400"
                                : "border-red-400 text-red-400"
                            }
                          >
                            {order.side}
                          </Badge>
                        </td>
                        <td className="py-3 px-4 text-slate-300">{order.order_type}</td>
                        <td className="py-3 px-4 text-right text-white">{order.quantity}</td>
                        <td className="py-3 px-4 text-right text-white">
                          {order.price ? `$${parseFloat(order.price).toLocaleString()}` : "MARKET"}
                        </td>
                        <td className="py-3 px-4">
                          <Badge
                            variant={order.status === "FILLED" ? "default" : "outline"}
                            className={
                              order.status === "FILLED"
                                ? "bg-green-600"
                                : "border-yellow-400 text-yellow-400"
                            }
                          >
                            {order.status}
                          </Badge>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="7" className="py-8 text-center text-slate-400">
                        No order history available
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
