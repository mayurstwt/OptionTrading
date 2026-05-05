import time
import logging
from datetime import datetime
from src.market_data.market_provider import (
    YahooFinanceProvider, 
    NSEScraperProvider, 
    NiftyIndicesProvider,
    GoogleFinanceProvider,
    MultiMarketProvider, 
    MarketDataProvider
)
from src.market_data.market_cache import MarketCache
from src.rules.rules_engine import RulesEngine
from src.trading.paper_trader import PaperTrader
from src.risk.risk_manager import RiskManager
from src.db.supabase_db import SupabaseDatabase
from src.db.models import DailySummary, MarketSnapshot
from src.utils.config_loader import load_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TradingEngine")

class TradingEngine:
    """
    Main orchestrator for the autonomous trading engine.
    Updated to use Supabase and a Hybrid (NiftyIndices + Google + Yahoo + NSE) market provider.
    """

    def __init__(self, config_path: str = "config/config_v1.yaml", market_provider: MarketDataProvider = None):
        self.config = load_config(config_path)
        self.db = SupabaseDatabase()
        self.market_cache = MarketCache()
        
        # Setup Ultra-Resilient Hybrid Market Provider
        if market_provider is None:
            self.market_provider = MultiMarketProvider([
                NiftyIndicesProvider(),     # 1. Try official Nifty Indices API (fast & reliable)
                GoogleFinanceProvider(),    # 2. Try Google Finance (highly reliable)
                YahooFinanceProvider(),     # 3. Try Yahoo Finance
                NSEScraperProvider()        # 4. Try NSE Scraper (last resort)
            ])
        else:
            self.market_provider = market_provider
            
        self.rules_engine = RulesEngine(self.config, self.market_cache)
        self.paper_trader = PaperTrader(self.db, self.market_cache)
        self.risk_manager = RiskManager(self.config, self.db)
        
        self.is_running = False

    def run_cycle(self):
        """
        Execute one iteration of the trading logic.
        Suitable for being triggered by a cron job/HTTP request.
        """
        logger.info("Starting trading cycle...")
        try:
            # 1. Update Market Data and persist it
            self._update_market_data()

            # 2. Evaluate Exit Rules
            open_positions = self.db.get_positions()
            exit_signals = self.rules_engine.evaluate_exit_rules(open_positions)
            for signal in exit_signals:
                self.paper_trader.close_position(
                    instrument_key=signal['position'].instrument_key,
                    exit_rule=signal['rule']['rule_name']
                )

            # 3. Evaluate Entry Rules
            entry_signals = self.rules_engine.evaluate_entry_rules()
            for signal in entry_signals:
                # Default to symbols mentioned in config or standard ones
                symbol = self.config.get("trading_config", {}).get("default_symbol", "NIFTY")
                
                risk_verdict = self.risk_manager.check_risk(
                    instrument_key=symbol,
                    side="SELL", 
                    quantity=signal['position_sizing']['base_lots']
                )

                if risk_verdict.status == "APPROVED":
                    self.paper_trader.place_order(
                        strategy=signal['strategy_type'],
                        instrument_key=symbol,
                        side="SELL",
                        quantity=signal['position_sizing']['base_lots'],
                        entry_rule=signal['rule_name']
                    )
                elif risk_verdict.status == "REDUCED_SIZE":
                     self.paper_trader.place_order(
                        strategy=signal['strategy_type'],
                        instrument_key=symbol,
                        side="SELL",
                        quantity=risk_verdict.suggested_quantity,
                        entry_rule=signal['rule_name']
                    )
            
            logger.info("Trading cycle completed.")
        except Exception as e:
            logger.error(f"Error in trading cycle: {str(e)}")
            raise e

    def calculate_daily_pnl(self):
        """
        Calculate and store P&L for the current day.
        Includes realized P&L from closed trades and reports unrealized P&L.
        """
        today_str = datetime.now().strftime("%Y-%m-%d")
        trades = self.db.get_trades_by_date(today_str)
        
        closed_trades = [t for t in trades if t.status == "CLOSED"]
        realized_pnl = sum(t.realized_pnl for t in closed_trades)
        wins = len([t for t in closed_trades if t.realized_pnl > 0])
        losses = len([t for t in closed_trades if t.realized_pnl <= 0])
        
        # Calculate unrealized P&L for open positions
        open_positions = self.db.get_positions()
        unrealized_pnl = 0.0
        for pos in open_positions:
            current_ltp = self.market_cache.get_ltp(pos.instrument_key)
            if current_ltp:
                price_diff = current_ltp - pos.avg_entry_price
                pos_pnl = price_diff * pos.net_quantity
                unrealized_pnl += pos_pnl

        summary = DailySummary(
            date=today_str,
            total_trades=len(closed_trades),
            winning_trades=wins,
            losing_trades=losses,
            realized_pnl=realized_pnl,
            max_drawdown_pct=0.0 # Placeholder
        )
        
        self.db.save_daily_summary(summary)
        logger.info(f"Daily Summary for {today_str}: Realized P&L: {realized_pnl}, Unrealized P&L: {unrealized_pnl}. Total Trades: {len(closed_trades)}")
        return summary

    def _update_market_data(self):
        """Fetch latest quotes for subscribed symbols and save snapshot to Supabase."""
        # We can configure symbols in config. For now, default to NIFTY and BANKNIFTY
        symbols = self.config.get("trading_config", {}).get("symbols", ["NIFTY", "BANKNIFTY"])
        
        for symbol in symbols:
            ltp = self.market_provider.get_quote(symbol)
            if ltp:
                self.market_cache.update(symbol, {"ltp": ltp})
                
                # Save snapshot to Supabase as requested ("store it in data")
                snapshot = MarketSnapshot(
                    instrument_key=symbol,
                    ltp=ltp,
                    timestamp=datetime.now()
                )
                self.db.save_market_snapshot(snapshot)
                
                logger.info(f"Updated and persisted LTP for {symbol}: {ltp}")
            else:
                logger.warning(f"Could not update LTP for {symbol}")

    def start(self):
        """Legacy method for local infinite loop."""
        self.is_running = True
        logger.info("Entering main intraday loop.")
        while self.is_running:
            try:
                self.run_cycle()
                time.sleep(30)
            except KeyboardInterrupt:
                self.is_running = False
            except Exception as e:
                logger.error(f"Error in loop: {str(e)}")
                time.sleep(10)

if __name__ == "__main__":
    engine = TradingEngine()
    engine.start()
