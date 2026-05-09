import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from src.market_data.market_cache import MarketCache

logger = logging.getLogger(__name__)

class RulesEngine:
    """
    Evaluates trading rules against current market state.
    Supports complex conditions, time windows, and multi-strategy evaluation.
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

    def evaluate_exit_rules(self, open_trades: List[Any]) -> List[Dict[str, Any]]:
        """
        Evaluate exit rules for all open trades.
        Note: Uses Trade objects to access entry_rule and strategy info.
        """
        signals = []
        exit_rules = self.config.get("exit_rules", [])
        
        for trade in open_trades:
            for rule in exit_rules:
                if not rule.get("enabled", False):
                    continue
                
                # Check if rule applies to this trade's entry strategy/rule
                applies_to = rule.get("applies_to", ["all"])
                entry_rule_name = getattr(trade, 'entry_rule', None)
                strategy_name = getattr(trade, 'strategy', None)

                if "all" not in applies_to and entry_rule_name not in applies_to and strategy_name not in applies_to:
                    continue

                if self._evaluate_exit_condition(rule, trade):
                    signals.append({"rule": rule, "trade": trade})
                    break # One exit rule is enough per trade
        
        return signals

    def evaluate_daily_monitoring(self, daily_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Evaluate daily monitoring rules (e.g., daily loss limit).
        """
        triggered_actions = []
        monitoring_rules = self.config.get("daily_monitoring", [])
        
        for rule in monitoring_rules:
            conditions = rule.get("conditions", [])
            match = True
            for cond in conditions:
                if not self._check_daily_condition(cond, daily_stats):
                    match = False
                    break
            
            if match:
                triggered_actions.append(rule)
        
        return triggered_actions

    def _evaluate_rule(self, rule: Dict[str, Any]) -> bool:
        """
        Evaluate a single rule's conditions.
        """
        # 1. Time Window Check
        if not self._check_time_window(rule.get("time_window")):
            return False

        # 2. Underlying Conditions
        if not self._check_conditions(rule.get("underlying_conditions", []), "underlying", rule):
            return False

        # 3. Options Conditions
        if not self._check_conditions(rule.get("options_conditions", []), "options", rule):
            return False
        
        return True

    def _check_time_window(self, window: Optional[List[str]]) -> bool:
        if not window or len(window) != 2:
            return True
        
        try:
            now = datetime.now().time()
            start = datetime.strptime(window[0], "%H:%M").time()
            end = datetime.strptime(window[1], "%H:%M").time()
            return start <= now <= end
        except Exception as e:
            logger.error(f"Error checking time window {window}: {str(e)}")
            return False

    def _check_conditions(self, conditions: List[Dict[str, Any]], context: str, rule: Dict[str, Any]) -> bool:
        if not conditions:
            return True
        
        symbol = self.config.get("trading_config", {}).get("default_symbol", "NIFTY")
        
        for cond in conditions:
            metric = cond.get("metric")
            operator = cond.get("operator")
            values = cond.get("values")
            threshold = cond.get("threshold")
            target = cond.get("target")
            logic = cond.get("logic")

            current_val = self._get_metric_value(metric, symbol, cond, rule)
            if current_val is None:
                if logic:
                    if not self._eval_logic(logic, symbol):
                        return False
                    continue
                return False
            
            compare_to = values if values is not None else threshold
            if compare_to is None and target is not None:
                compare_to = target

            if not self._compare(current_val, operator, compare_to):
                return False
        
        return True

    def _get_metric_value(self, metric: str, symbol: str, cond: Dict[str, Any], rule: Dict[str, Any]) -> Any:
        market_data = self.market_cache.get(symbol) or {}
        
        if metric == "price":
            return market_data.get("ltp")
        
        if metric == "volatility":
            return market_data.get("iv") or "high"
            
        if metric == "premium":
            return 50 
            
        if metric == "combined_premium":
            return 400
            
        if metric == "volume":
            return market_data.get("volume", 1000)
            
        if metric == "price_trend":
            history = self.market_cache.get_history(symbol)
            if not history or len(history) < 2:
                return "neutral"
            return "up" if history[-1] > history[-2] else "down"

        return None

    def _eval_logic(self, logic: str, symbol: str) -> bool:
        if "last_candle_close > last_candle_open" in logic:
             history = self.market_cache.get_history(symbol)
             if history and len(history) >= 2:
                 return history[-1] > history[-2]
             return True
        
        if "last_candle_close < last_candle_open" in logic:
             history = self.market_cache.get_history(symbol)
             if history and len(history) >= 2:
                 return history[-1] < history[-2]
             return True
             
        return True

    def _compare(self, val: Any, operator: Optional[str], target: Any) -> bool:
        if operator is None:
            return str(val).lower() == str(target).lower()
            
        if operator == "==": return val == target
        if operator == "!=": return val != target
        if operator == ">": return val > target
        if operator == "<": return val < target
        if operator == ">=": return val >= target
        if operator == "<=": return val <= target
        if operator == "between": 
            return target[0] <= val <= target[1]
        if operator == "abs_gt":
            return abs(val) > target
        return False

    def _evaluate_exit_condition(self, rule: Dict[str, Any], trade: Any) -> bool:
        trigger = rule.get("trigger")
        
        if trigger == "absolute_time":
            try:
                exit_time = datetime.strptime(rule.get("time"), "%H:%M").time()
                return datetime.now().time() >= exit_time
            except:
                return False
        
        if trigger == "any" or trigger is None:
            for cond in rule.get("conditions", []):
                if self._check_trade_condition(cond, trade):
                    return True
        
        return False

    def _check_trade_condition(self, cond: Dict[str, Any], trade: Any) -> bool:
        metric = cond.get("metric")
        operator = cond.get("operator")
        threshold = cond.get("threshold")
        
        current_ltp = self.market_cache.get_ltp(trade.instrument_key)
        if current_ltp is None: return False
        
        entry_price = getattr(trade, 'entry_price', getattr(trade, 'avg_entry_price', 0))
        side = getattr(trade, 'side', 'SELL') # Default to SELL for positions if side not present

        if metric == "premium_change":
            change_pct = (current_ltp - entry_price) / entry_price * 100
            return self._compare(change_pct, operator, threshold)
            
        if metric == "position_loss_pct":
            change_pct = (current_ltp - entry_price) / entry_price * 100
            pnl_pct = -change_pct if side == "SELL" else change_pct
            return self._compare(pnl_pct, operator, threshold)

        return False

    def _check_daily_condition(self, cond: Dict[str, Any], stats: Dict[str, Any]) -> bool:
        metric = cond.get("metric")
        operator = cond.get("operator")
        threshold = cond.get("threshold")
        
        val = stats.get(metric)
        if val is None: return False
        
        return self._compare(val, operator, threshold)

