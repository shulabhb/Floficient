import requests
from typing import Dict, Any, Optional
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

class HereAPIClient:
    """Client for HERE Real-time Traffic API v7 with error handling."""
    
    def __init__(self):
        self.api_key = settings.HERE_API_KEY
        self.base_url = "https://data.traffic.hereapi.com/v7"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Floficient/1.0'
        })
    
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make a request to the HERE API with error handling."""
        url = f"{self.base_url}/{endpoint}"
        params['apiKey'] = self.api_key
        try:
            logger.info(f"Making request to: {endpoint}")
            logger.info(f"URL: {url}")
            logger.info(f"Params: {params}")
            response = self.session.get(url, params=params, timeout=20)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"{response.status_code} {response.reason} - API key might be invalid or request format incorrect")
                logger.error(f"Response: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Exception during API request: {e}")
            return None

    def get_traffic_flow(self, bbox: str) -> Optional[Dict[str, Any]]:
        # bbox should be in the format: west,south,east,north (comma-separated)
        params = {
            "in": f"bbox:{bbox}",
            "locationReferencing": "shape"
        }
        return self._make_request("flow", params)

    def get_traffic_incidents(self, bbox: str) -> Optional[Dict[str, Any]]:
        params = {
            "in": f"bbox:{bbox}",
            "locationReferencing": "shape"
        }
        return self._make_request("incidents", params) 