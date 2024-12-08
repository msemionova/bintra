class RiskManager:
    def __init__(self, stop_loss: float, take_profit: float):
        self.stop_loss = stop_loss
        self.take_profit = take_profit

    def manage_risk(self, entry_price, current_price):
        if current_price <= entry_price * (1 - self.stop_loss):
            return "SELL"
        elif current_price >= entry_price * (1 + self.take_profit):
            return "SELL"
        return "HOLD"

    def calculate_position_size(balance, risk_percentage, price):
        """
        Calculates the position size based on account balance and risk.
        """
        risk_amount = balance * (risk_percentage / 100)
        position_size = risk_amount / price
        return round(position_size, 5)  # Round to Binance's precision
