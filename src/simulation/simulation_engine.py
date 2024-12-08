import pandas as pd

class SimulationEngine:
    def __init__(self, strategy_manager):
        self.strategy_manager = strategy_manager

    def run_backtest(self, data):
        signals = []
        for i in range(len(data)):
            signal = self.strategy_manager.evaluate_signal(data[:i+1])
            signals.append(signal)
        return signals
