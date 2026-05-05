import logging
import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import yfinance as yf
from requests import Session

logger = logging.getLogger(__name__)

class MarketDataProvider(ABC):
    """
    Abstract interface for market data providers.
    """
    
    @abstractmethod
    def get_quote(self, symbol: str) -> Optional[float]:
        """Fetch the latest Last Traded Price (LTP) for a symbol."""
        pass

    @abstractmethod
    def get_option_chain(self, symbol: str) -> List[Dict[str, Any]]:
        """Fetch the option chain for a symbol."""
        pass

class YahooFinanceProvider(MarketDataProvider):
    """
    Market data provider using yfinance library.
    Uses a custom session to avoid basic bot detection.
    """

    def __init__(self):
        # Map of standard symbols to Yahoo Finance symbols
        self.symbol_map = {
            "NIFTY": "^NSEI",
            "BANKNIFTY": "^NSEBANK"
        }
        self.session = Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        })

    def get_quote(self, symbol: str) -> Optional[float]:
        """Fetch latest price from Yahoo Finance with custom session."""
        yf_symbol = self.symbol_map.get(symbol, symbol)
        try:
            ticker = yf.Ticker(yf_symbol, session=self.session)
            
            # Try fast_info
            fast_info = ticker.fast_info
            if 'last_price' in fast_info and fast_info['last_price'] is not None:
                return float(fast_info['last_price'])
            
            # Fallback to history
            hist = ticker.history(period="1d")
            if not hist.empty:
                return float(hist['Close'].iloc[-1])
            
            # Last ditch attempt with yf.download
            data = yf.download(yf_symbol, period="1d", interval="1m", progress=False, show_errors=False, session=self.session)
            if not data.empty:
                return float(data['Close'].iloc[-1])

            return None
        except Exception as e:
            logger.debug(f"YahooFinanceProvider error for {symbol}: {str(e)}")
            return None

    def get_option_chain(self, symbol: str) -> List[Dict[str, Any]]:
        return []

class NSEScraperProvider(MarketDataProvider):
    """
    Implementation using direct NSE website scraping.
    """

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.nseindia.com/"
        }
        self.session = requests.Session()
        self._init_session()

    def _init_session(self):
        try:
            self.session.get("https://www.nseindia.com", headers=self.headers, timeout=10)
        except Exception as e:
            logger.error(f"Failed to initialize NSE session: {str(e)}")

    def get_quote(self, symbol: str) -> Optional[float]:
        """Fetch quote from NSE API."""
        url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return float(data.get('records', {}).get('underlyingValue'))
            elif response.status_code == 401:
                self._init_session()
                return self.get_quote(symbol)
            return None
        except Exception as e:
            logger.debug(f"NSEScraperProvider error for {symbol}: {str(e)}")
            return None

    def get_option_chain(self, symbol: str) -> List[Dict[str, Any]]:
        url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json().get('records', {}).get('data', [])
            return []
        except Exception as e:
            return []

class MultiMarketProvider(MarketDataProvider):
    """
    Tries multiple providers in order until one succeeds.
    """
    def __init__(self, providers: List[MarketDataProvider]):
        self.providers = providers

    def get_quote(self, symbol: str) -> Optional[float]:
        for provider in self.providers:
            price = provider.get_quote(symbol)
            if price is not None:
                return price
        logger.error(f"All market providers failed for {symbol}")
        return None

    def get_option_chain(self, symbol: str) -> List[Dict[str, Any]]:
        for provider in self.providers:
            chain = provider.get_option_chain(symbol)
            if chain:
                return chain
        return []
