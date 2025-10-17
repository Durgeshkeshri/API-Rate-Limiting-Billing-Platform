"""
API Rate Limiting & Billing Platform

A scalable FastAPI-based platform for monitoring, rate limiting, 
and billing API usage using Redis sliding window algorithm.
"""

__version__ = "1.0.0"
__author__ = "Your Name"

import logging

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)
