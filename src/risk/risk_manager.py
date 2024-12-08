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
