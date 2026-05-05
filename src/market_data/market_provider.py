import logging
import requests
import re
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import yfinance as yf
from requests import Session

# Suppress noisy yfinance logs
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

logger = logging.getLogger(__name__)

class MarketDataProvider(ABC):
    """Abstract interface for market data providers."""
    @abstractmethod
    def get_quote(self, symbol: str) -> Optional[float]: pass
    @abstractmethod
    def get_option_chain(self, symbol: str) -> List[Dict[str, Any]]: pass

class NiftyIndicesProvider(MarketDataProvider):
    """
    Official Nifty Indices API (niftyindices.com).
    """
    def get_quote(self, symbol: str) -> Optional[float]:
        # Note: This endpoint is very picky about headers
        url = "https://www.niftyindices.com/Home/getNiftyIndexTodayVal"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Referer": "https://www.niftyindices.com/",
            "X-Requested-With": "XMLHttpRequest"
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                target = "Nifty 50" if symbol == "NIFTY" else "Nifty Bank" if symbol == "BANKNIFTY" else symbol
                for item in data:
                    name = item.get('indexName') or item.get('Index_Name') or item.get('index')
                    if name and target.lower() in name.lower():
                        price = item.get('lastPrice') or item.get('Last_Traded_Price') or item.get('last')
                        if price: return float(str(price).replace(',', ''))
            return None
        except Exception as e:
            logger.debug(f"NiftyIndicesProvider error: {e}")
            return None

    def get_option_chain(self, symbol: str) -> List[Dict[str, Any]]: return []

class GoogleFinanceProvider(MarketDataProvider):
    """
    Scrapes price from Google Finance.
    """
    def __init__(self):
        self.symbol_map = {"NIFTY": "NIFTY_50:INDEXNSE", "BANKNIFTY": "NIFTY_BANK:INDEXNSE"}

    def get_quote(self, symbol: str) -> Optional[float]:
        gf_symbol = self.symbol_map.get(symbol, symbol)
        url = f"https://www.google.com/finance/quote/{gf_symbol}"
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36"}, timeout=10)
            if response.status_code == 200:
                # Look for data-last-price or use the previous regex
                match = re.search(r'data-last-price="([^"]+)"', response.text)
                if match:
                    return float(match.group(1).replace(',', ''))
                
                # Fallback regex for display price
                match = re.search(r'class="YMl-9e[^>]*>([^<]+)<', response.text)
                if match:
                    price_str = match.group(1).replace(',', '').replace('₹', '').replace('$', '').strip()
                    return float(price_str)
            return None
        except Exception as e:
            logger.debug(f"GoogleFinanceProvider error: {e}")
            return None

    def get_option_chain(self, symbol: str) -> List[Dict[str, Any]]: return []

class YahooFinanceProvider(MarketDataProvider):
    """Yahoo Finance with simple session."""
    def __init__(self):
        self.symbol_map = {"NIFTY": "^NSEI", "BANKNIFTY": "^NSEBANK"}
        self.session = Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36"})

    def get_quote(self, symbol: str) -> Optional[float]:
        yf_symbol = self.symbol_map.get(symbol, symbol)
        try:
            ticker = yf.Ticker(yf_symbol, session=self.session)
            # Try history as it's often more reliable than fast_info for indices
            hist = ticker.history(period="1d")
            if not hist.empty: return float(hist['Close'].iloc[-1])
            return None
        except Exception as e:
            logger.debug(f"YahooFinanceProvider error: {e}")
            return None

    def get_option_chain(self, symbol: str) -> List[Dict[str, Any]]: return []

class NSEScraperProvider(MarketDataProvider):
    """Standard NSE Scraper."""
    def __init__(self):
        self.session = requests.Session()
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36", "Referer": "https://www.nseindia.com/"}

    def get_quote(self, symbol: str) -> Optional[float]:
        try:
            self.session.get("https://www.nseindia.com", headers=self.headers, timeout=5)
            url = f"https://www.nseindia.com/api/allIndices"
            response = self.session.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                target = "NIFTY 50" if symbol == "NIFTY" else "NIFTY BANK" if symbol == "BANKNIFTY" else symbol
                for index in data.get('data', []):
                    if index.get('index') == target: return float(index.get('last'))
            return None
        except Exception as e:
            logger.debug(f"NSEScraperProvider error: {e}")
            return None

    def get_option_chain(self, symbol: str) -> List[Dict[str, Any]]: return []

class MultiMarketProvider(MarketDataProvider):
    """Orchestrates multiple fallbacks."""
    def __init__(self, providers: List[MarketDataProvider]):
        self.providers = providers

    def get_quote(self, symbol: str) -> Optional[float]:
        for provider in self.providers:
            try:
                price = provider.get_quote(symbol)
                if price is not None:
                    # Log success only once to keep it clean
                    logger.info(f"Successfully fetched {symbol} price using {provider.__class__.__name__}")
                    return price
            except Exception:
                continue
        logger.error(f"ALL providers failed for {symbol}")
        return None

    def get_option_chain(self, symbol: str) -> List[Dict[str, Any]]:
        for provider in self.providers:
            try:
                chain = provider.get_option_chain(symbol)
                if chain: return chain
            except Exception:
                continue
        return []
