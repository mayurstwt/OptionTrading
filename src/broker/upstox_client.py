import os
import requests
import json
import logging
from typing import Dict, List, Any, Optional
from src.broker.broker_interface import BrokerInterface
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class UpstoxClient(BrokerInterface):
    """
    Implementation of Upstox API client.
    Handles REST API calls and manages WebSocket connections.
    """

    def __init__(self, api_key: str = None, api_secret: str = None, access_token: str = None, sandbox: bool = True):
        self.api_key = api_key or os.getenv("UPSTOX_API_KEY")
        self.api_secret = api_secret or os.getenv("UPSTOX_API_SECRET")
        self.access_token = access_token or os.getenv("UPSTOX_ACCESS_TOKEN")
        self.sandbox = sandbox or os.getenv("UPSTOX_SANDBOX_MODE", "true").lower() == "true"
        
        self.base_url = "https://sandbox.upstox.com/v2" if self.sandbox else "https://api.upstox.com/v2"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }

    def authenticate(self) -> bool:
        """
        In this implementation, we assume the access token is already available.
        Future enhancement: Implement OAuth2 flow.
        """
        if not self.access_token:
            logger.error("Access token missing for UpstoxClient")
            return False
        
        # Simple health check call
        try:
            response = requests.get(f"{self.base_url}/user/profile", headers=self.headers)
            if response.status_code == 200:
                logger.info("Successfully authenticated with Upstox")
                return True
            else:
                logger.error(f"Authentication failed: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error during authentication: {str(e)}")
            return False

    def get_instruments(self, segment: str = "NSE_FO") -> List[Dict[str, Any]]:
        """Fetch instruments from Upstox."""
        url = f"{self.base_url}/market/instruments/{segment}"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                # Upstox returns CSV-like data for instruments sometimes, or JSON.
                # Assuming JSON for now based on MASTER_PROMPT.
                return response.json().get("data", [])
            else:
                logger.error(f"Failed to fetch instruments: {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error fetching instruments: {str(e)}")
            return []

    def get_option_chain(self, underlying: str, expiry: str) -> List[Dict[str, Any]]:
        """Fetch option chain."""
        url = f"{self.base_url}/option/chain"
        params = {"instrument_key": underlying, "expiry_date": expiry}
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json().get("data", [])
            else:
                logger.error(f"Failed to fetch option chain: {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error fetching option chain: {str(e)}")
            return []

    def get_market_quote(self, instrument_keys: List[str]) -> Dict[str, Any]:
        """Fetch quotes."""
        url = f"{self.base_url}/market-quote/quotes"
        params = {"instrument_key": ",".join(instrument_keys)}
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json().get("data", {})
            else:
                logger.error(f"Failed to fetch quotes: {response.text}")
                return {}
        except Exception as e:
            logger.error(f"Error fetching quotes: {str(e)}")
            return {}

    def subscribe_market_data(self, instrument_keys: List[str], callback: Any) -> None:
        """
        Implementation for WebSocket subscription.
        This would typically start a background thread or async loop.
        """
        logger.info(f"Subscribing to market data for {len(instrument_keys)} instruments")
        # Placeholder for actual WebSocket implementation
        pass

    def place_order(self, order_details: Dict[str, Any]) -> Dict[str, Any]:
        """Place an order."""
        url = f"{self.base_url}/order/place"
        try:
            response = requests.post(url, headers=self.headers, json=order_details)
            if response.status_code == 200:
                return response.json().get("data", {})
            else:
                logger.error(f"Failed to place order: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"Error placing order: {str(e)}")
            return {"error": str(e)}

    def get_positions(self) -> List[Dict[str, Any]]:
        """Fetch positions."""
        url = f"{self.base_url}/portfolio/positions"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json().get("data", [])
            else:
                logger.error(f"Failed to fetch positions: {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error fetching positions: {str(e)}")
            return []
