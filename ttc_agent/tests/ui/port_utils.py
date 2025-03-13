"""
Utility functions for handling dynamic port detection in UI tests
"""
import os
import logging
from typing import List, Optional

def get_frontend_port() -> Optional[int]:
    """
    Get the frontend port from environment variable or default to 5173
    """
    try:
        # Try to get port from environment variable
        port_str = os.environ.get("FRONTEND_PORT")
        if port_str and port_str.isdigit():
            return int(port_str)
    except Exception as e:
        logging.warning(f"Error getting frontend port from environment: {str(e)}")
    
    return None

def get_ports_to_try() -> List[int]:
    """
    Get a list of ports to try for frontend connection
    If FRONTEND_PORT is set, it will be the first port to try
    """
    default_ports = [5173, 5174, 5175, 5176, 5177, 5178]
    
    # If we have a known port, try it first
    frontend_port = get_frontend_port()
    if frontend_port:
        # Put the known port first in the list
        if frontend_port in default_ports:
            default_ports.remove(frontend_port)
        return [frontend_port] + default_ports
    
    return default_ports
