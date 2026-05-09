import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from src.market_data.market_cache import MarketCache

logger = logging.getLogger(__name__)

class RulesEngine:
    """
    Evaluates trading rules against current market state.
    """

    def __init__(self, config: Dict[str, Any], market_cache: MarketCache):
        self.config = config
        self.market_cache = market_cache

    def evaluate_entry_rules(self) -> List[Dict[str, Any]]:
        """
        Evaluate all enabled entry rules and return triggered signals.
        """
        signals = []
        entry_rules = self.config.get("entry_rules", [])
        
        for rule in entry_rules:
            if not rule.get("enabled", False):
                continue
            
            if self._evaluate_rule(rule):
                signals.append(rule)
        
        return signals

    def evaluate_exit_rules(self, open_positions: List[Any]) -> List[Dict[str, Any]]:
        """
        Evaluate exit rules for all open positions.
        """
        signals = []
        exit_rules = self.config.get("exit_rules", [])
        
        for position in open_positions:
            for rule in exit_rules:
                if not rule.get("enabled", False):
                    continue
                
                if self._evaluate_exit_condition(rule, position):
                    signals.append({"rule": rule, "position": position})
                    break # One exit rule is enough
        
        return signals

    def _evaluate_rule(self, rule: Dict[str, Any]) -> bool:
        """
        Evaluate a single rule's conditions.
        """
        # 1. Time Window Check
        if not self._check_time_window(rule.get("time_window")):
            return False

        # 2. Underlying Conditions
        if not self._check_underlying_conditions(rule.get("underlying_conditions")):
            return False

        # 3. Options Conditions
        # (This would involve more complex logic to select the right strike)
        # For simplicity in v1, we check if generic conditions match.
        
        return True

    def _check_time_window(self, window: Optional[List[str]]) -> bool:
        if not window or len(window) != 2:
            return True
        
        now = datetime.now().time()
        start = datetime.strptime(window[0], "%H:%M").time()
        end = datetime.strptime(window[1], "%H:%M").time()
        
        return start <= now <= end

    def _check_underlying_conditions(self, conditions: Optional[List[Dict[str, Any]]]) -> bool:
        if not conditions:
            return True
        
        for cond in conditions:
            metric = cond.get("metric")
            operator = cond.get("operator")
            values = cond.get("values")
            
            # Fetch current value for metric
            # In a real system, we'd have a mapping of metric names to data points
            current_val = self._get_metric_value(metric)
            if current_val is None:
                return False
            
            if not self._compare(current_val, operator, values):
                return False
        
        return True

    def _get_metric_value(self, metric: str) -> Optional[float]:
        # For now, only 'price' is supported for underlying
        if metric == "price":
            # Matches the symbol used in main.py cache
            return self.market_cache.get_ltp("NIFTY")
        return None

    def _compare(self, val: Any, operator: str, target: Any) -> bool:
        if operator == "==": return val == target
        if operator == "!=": return val != target
        if operator == ">": return val > target
        if operator == "<": return val < target
        if operator == ">=": return val >= target
        if operator == "<=": return val <= target
        if operator == "between": 
            return target[0] <= val <= target[1]
        return False

    def _evaluate_exit_condition(self, rule: Dict[str, Any], position: Any) -> bool:
        """
        Evaluate if a position should be exited based on the rule.
        """
        trigger = rule.get("trigger")
        
        if trigger == "absolute_time":
            exit_time = datetime.strptime(rule.get("time"), "%H:%M").time()
            return datetime.now().time() >= exit_time
        
        if trigger == "any":
            for cond in rule.get("conditions", []):
                if self._check_position_condition(cond, position):
                    return True
        
        return False

    def _check_position_condition(self, cond: Dict[str, Any], position: Any) -> bool:
        metric = cond.get("metric")
        operator = cond.get("operator")
        threshold = cond.get("threshold")
        
        if metric == "premium_change":
            # (current_ltp - entry_price) / entry_price * 100
            current_ltp = self.market_cache.get_ltp(position.instrument_key)
            if current_ltp is None: return False
            
            change_pct = (current_ltp - position.avg_entry_price) / position.avg_entry_price * 100
            # For short positions, change_pct < 0 means profit
            return self._compare(change_pct, operator, threshold)
            
        return False
