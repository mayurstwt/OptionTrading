import unittest
from datetime import datetime, time
from src.rules.rules_engine import RulesEngine
from src.market_data.market_cache import MarketCache

class TestRulesEngine(unittest.TestCase):
    def setUp(self):
        self.config = {
            "trading_config": {
                "default_symbol": "NIFTY",
                "paper_capital": 1000000
            },
            "entry_rules": [
                {
                    "rule_name": "test_rule",
                    "enabled": True,
                    "time_window": ["00:00", "23:59"], # All day
                    "underlying_conditions": [
                        {"metric": "price", "operator": ">", "threshold": 20000}
                    ],
                    "options_conditions": []
                }
            ],
            "exit_rules": [
                {
                    "rule_name": "test_exit",
                    "enabled": True,
                    "trigger": "any",
                    "conditions": [
                        {"metric": "position_loss_pct", "operator": "<", "threshold": -5}
                    ]
                }
            ]
        }
        self.market_cache = MarketCache()
        self.rules_engine = RulesEngine(self.config, self.market_cache)

    def test_evaluate_entry_rules(self):
        self.market_cache.update("NIFTY", {"ltp": 25000})
        signals = self.rules_engine.evaluate_entry_rules()
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0]["rule_name"], "test_rule")

    def test_evaluate_exit_rules(self):
        # LTP dropped from 25000 to 23000 (8% loss for BUY)
        self.market_cache.update("NIFTY", {"ltp": 23000})
        # Mock a trade object
        class MockTrade:
            def __init__(self):
                self.instrument_key = "NIFTY"
                self.entry_price = 25000
                self.side = "BUY"
                self.entry_rule = "test_rule"
                self.strategy = "test_strategy"

        trade = MockTrade()
        signals = self.rules_engine.evaluate_exit_rules([trade])
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0]["rule"]["rule_name"], "test_exit")

if __name__ == "__main__":
    unittest.main()
