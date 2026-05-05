import yaml
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def load_config(file_path: str = "config/config_v1.yaml") -> Dict[str, Any]:
    """
    Load and parse the YAML configuration file.
    """
    if not os.path.exists(file_path):
        logger.error(f"Configuration file not found: {file_path}")
        return {}

    try:
        with open(file_path, 'r') as f:
            config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {file_path}")
            return config
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        return {}
