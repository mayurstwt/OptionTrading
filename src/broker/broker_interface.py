from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

class BrokerInterface(ABC):
    """
    Abstract interface for broker integrations.
    Ensures that the trading engine can work with different brokers.
    """

    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the broker API."""
        pass

    @abstractmethod
    def get_instruments(self, segment: str) -> List[Dict[str, Any]]:
        """Fetch list of instruments for a given segment (e.g., 'NSE_FO')."""
        pass

    @abstractmethod
    def get_option_chain(self, underlying: str, expiry: str) -> List[Dict[str, Any]]:
        """Fetch option chain for an underlying and expiry."""
        pass

    @abstractmethod
    def get_market_quote(self, instrument_keys: List[str]) -> Dict[str, Any]:
        """Fetch market quotes for specific instruments."""
        pass

    @abstractmethod
    def subscribe_market_data(self, instrument_keys: List[str], callback: Any) -> None:
        """Subscribe to real-time market data via WebSocket."""
        pass

    @abstractmethod
    def place_order(self, order_details: Dict[str, Any]) -> Dict[str, Any]:
        """Place an order with the broker."""
        pass

    @abstractmethod
    def get_positions(self) -> List[Dict[str, Any]]:
        """Fetch current intraday positions."""
        pass
