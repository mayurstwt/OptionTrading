import logging
from typing import Dict, Any, Optional
from collections import deque
from datetime import datetime

logger = logging.getLogger(__name__)

class MarketCache:
    """
    In-memory cache for market data.
    Stores real-time prices, Greeks, and other metrics.
    """

    def __init__(self, history_size: int = 100):
        # Cache structure: {instrument_key: {data}}
        self._cache: Dict[str, Dict[str, Any]] = {}
        # History for technical analysis: {instrument_key: deque([prices])}
        self._history: Dict[str, deque] = {}
        self.history_size = history_size

    def update(self, instrument_key: str, data: Dict[str, Any]) -> None:
        """
        Update the cache for a given instrument.
        Adds a timestamp to the record.
        """
        if instrument_key not in self._cache:
            self._cache[instrument_key] = {}
            self._history[instrument_key] = deque(maxlen=self.history_size)

        # Update data and add timestamp
        data['timestamp'] = datetime.now()
        self._cache[instrument_key].update(data)

        # Update history if LTP is present
        if 'ltp' in data:
            self._history[instrument_key].append(data['ltp'])

    def get(self, instrument_key: str) -> Optional[Dict[str, Any]]:
        """Get the current data for an instrument."""
        return self._cache.get(instrument_key)

    def get_ltp(self, instrument_key: str) -> Optional[float]:
        """Get the last traded price for an instrument."""
        data = self._cache.get(instrument_key)
        return data.get('ltp') if data else None

    def get_history(self, instrument_key: str) -> Optional[deque]:
        """Get price history for an instrument."""
        return self._history.get(instrument_key)

    def get_all_keys(self) -> list:
        """Get all instrument keys in the cache."""
        return list(self._cache.keys())

    def clear(self) -> None:
        """Clear the cache."""
        self._cache.clear()
        self._history.clear()
        logger.info("Market cache cleared")
