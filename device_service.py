"""
Device Service for detecting browser, OS, and device information.
Uses the user-agents library for parsing User-Agent strings.
"""

from flask import request
from user_agents import parse


class DeviceService:
    """Service for detecting device and browser information."""
    
    @staticmethod
    def get_client_ip() -> str:
        """
        Get the client's IP address.
        Handles proxy headers (X-Forwarded-For) for reverse proxy setups.
        
        Returns:
            Client IP address as string
        """
        # Check for proxy headers first
        if request.headers.get('X-Forwarded-For'):
            # X-Forwarded-For can contain multiple IPs, take the first one
            ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            ip = request.headers.get('X-Real-IP')
        else:
            ip = request.remote_addr or '127.0.0.1'
        
        return ip
    
    @staticmethod
    def get_user_agent_string() -> str:
        """
        Get the raw User-Agent string from request.
        
        Returns:
            User-Agent string
        """
        return request.headers.get('User-Agent', '')
    
    @staticmethod
    def parse_user_agent(user_agent_string: str = None) -> dict:
        """
        Parse User-Agent string to extract device information.
        
        Args:
            user_agent_string: Optional UA string, uses request if not provided
            
        Returns:
            Dictionary with browser, os, device_type, and is_mobile
        """
        if user_agent_string is None:
            user_agent_string = DeviceService.get_user_agent_string()
        
        # Parse the user agent
        ua = parse(user_agent_string)
        
        # Get browser name and version
        browser_name = ua.browser.family or 'Unknown'
        browser_version = ua.browser.version_string
        browser = f"{browser_name} {browser_version}" if browser_version else browser_name
        
        # Get OS name and version
        os_name = ua.os.family or 'Unknown'
        os_version = ua.os.version_string
        os_info = f"{os_name} {os_version}" if os_version else os_name
        
        # Determine device type
        is_mobile = ua.is_mobile or ua.is_tablet
        device_type = 'mobile' if is_mobile else 'desktop'
        
        return {
            'browser': browser,
            'browser_family': ua.browser.family or 'Unknown',
            'browser_version': browser_version,
            'os': os_info,
            'os_family': ua.os.family or 'Unknown',
            'os_version': os_version,
            'device_type': device_type,
            'is_mobile': is_mobile,
            'is_tablet': ua.is_tablet,
            'is_pc': ua.is_pc,
            'is_bot': ua.is_bot,
            'device_brand': ua.device.brand or 'Unknown',
            'device_model': ua.device.model or 'Unknown'
        }
    
    @staticmethod
    def get_device_info() -> dict:
        """
        Get complete device information from current request.
        
        Returns:
            Dictionary with IP, browser, OS, device type, and all parsed info
        """
        device_info = DeviceService.parse_user_agent()
        device_info['ip_address'] = DeviceService.get_client_ip()
        return device_info
    
    @staticmethod
    def is_chrome() -> bool:
        """
        Check if the browser is Google Chrome.
        
        Returns:
            True if Chrome, False otherwise
        """
        device_info = DeviceService.parse_user_agent()
        browser_family = device_info.get('browser_family', '').lower()
        return 'chrome' in browser_family and 'edge' not in browser_family
    
    @staticmethod
    def is_edge() -> bool:
        """
        Check if the browser is Microsoft Edge.
        
        Returns:
            True if Edge, False otherwise
        """
        device_info = DeviceService.parse_user_agent()
        browser_family = device_info.get('browser_family', '').lower()
        return 'edge' in browser_family
    
    @staticmethod
    def is_mobile() -> bool:
        """
        Check if the device is mobile or tablet.
        
        Returns:
            True if mobile/tablet, False otherwise
        """
        device_info = DeviceService.parse_user_agent()
        return device_info.get('is_mobile', False)
    
    @staticmethod
    def get_login_info() -> dict:
        """
        Get information needed for login history recording.
        
        Returns:
            Dictionary with ip_address, browser, os, device_type
        """
        device_info = DeviceService.get_device_info()
        return {
            'ip_address': device_info['ip_address'],
            'browser': device_info['browser'],
            'os': device_info['os'],
            'device_type': device_info['device_type']
        }
