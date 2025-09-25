import ipaddress
import re
from typing import Literal, Optional, Tuple
from urllib.parse import ParseResult, urlparse

# IOC type definitions
IOCType = Literal["ipv4", "ipv6", "domain", "url", "hash_md5", "hash_sha1", "hash_sha256"]

# Regular expressions for IOC detection
IPV4_REGEX = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
IPV6_REGEX = r"^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$"
DOMAIN_REGEX = r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]$"
URL_REGEX = r"^(?:https?|ftp)://(?:(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]|localhost|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?(?:/?|[/?]\S+)$"
MD5_REGEX = r"^[a-fA-F0-9]{32}$"
SHA1_REGEX = r"^[a-fA-F0-9]{40}$"
SHA256_REGEX = r"^[a-fA-F0-9]{64}$"

# Maximum lengths for IOCs
MAX_LENGTHS = {
    "ipv4": 15,  # 255.255.255.255
    "ipv6": 39,  # ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff
    "domain": 253,  # Max domain length per RFC 1035
    "url": 2048,  # Common URL length limit
    "hash_md5": 32,
    "hash_sha1": 40,
    "hash_sha256": 64,
}


def is_valid_ipv4(value: str) -> bool:
    """Check if the value is a valid IPv4 address."""
    if not re.match(IPV4_REGEX, value):
        return False
    try:
        ipaddress.IPv4Address(value)
        return True
    except ValueError:
        return False


def is_valid_ipv6(value: str) -> bool:
    """Check if the value is a valid IPv6 address."""
    if not re.match(IPV6_REGEX, value):
        return False
    try:
        ipaddress.IPv6Address(value)
        return True
    except ValueError:
        return False


def is_valid_domain(value: str) -> bool:
    """Check if the value is a valid domain name."""
    if len(value) > MAX_LENGTHS["domain"]:
        return False
    return bool(re.match(DOMAIN_REGEX, value))


def is_valid_url(value: str) -> bool:
    """Check if the value is a valid URL."""
    if len(value) > MAX_LENGTHS["url"]:
        return False
    return bool(re.match(URL_REGEX, value))


def is_valid_md5(value: str) -> bool:
    """Check if the value is a valid MD5 hash."""
    return bool(re.match(MD5_REGEX, value))


def is_valid_sha1(value: str) -> bool:
    """Check if the value is a valid SHA1 hash."""
    return bool(re.match(SHA1_REGEX, value))


def is_valid_sha256(value: str) -> bool:
    """Check if the value is a valid SHA256 hash."""
    return bool(re.match(SHA256_REGEX, value))


def detect_ioc_type(value: str) -> Tuple[Optional[IOCType], Optional[str]]:
    """
    Detect the type of IOC from the given value.
    
    Args:
        value: The IOC value to detect
        
    Returns:
        A tuple of (ioc_type, error_message)
        If the IOC type is detected, error_message is None
        If the IOC type is not detected, ioc_type is None and error_message contains the reason
    """
    if not value:
        return None, "IOC value cannot be empty"

    # Check if the value is too long
    if len(value) > 2048:  # General maximum length
        return None, "IOC value is too long"

    # Detect hash types first as they're most specific
    if is_valid_sha256(value):
        return "hash_sha256", None
    elif is_valid_sha1(value):
        return "hash_sha1", None
    elif is_valid_md5(value):
        return "hash_md5", None
    
    # Detect IP addresses
    if is_valid_ipv4(value):
        return "ipv4", None
    elif is_valid_ipv6(value):
        return "ipv6", None
    
    # Detect URLs
    if is_valid_url(value):
        return "url", None
    
    # Detect domains (least specific)
    if is_valid_domain(value):
        return "domain", None
    
    return None, "Invalid IOC format"


def canonicalize_domain(domain: str) -> str:
    """
    Canonicalize a domain name.
    
    Args:
        domain: The domain name to canonicalize
        
    Returns:
        The canonicalized domain name
    """
    # Convert to lowercase
    domain = domain.lower()
    
    # Strip trailing dot
    if domain.endswith("."):
        domain = domain[:-1]
    
    # TODO: Implement punycode decoding if needed
    
    return domain


def canonicalize_url(url: str) -> str:
    """
    Canonicalize a URL.
    
    Args:
        url: The URL to canonicalize
        
    Returns:
        The canonicalized URL
    """
    parsed_url = urlparse(url)
    
    # Normalize scheme and netloc to lowercase
    scheme = parsed_url.scheme.lower()
    netloc = parsed_url.netloc.lower()
    
    # Keep path, query, and params as-is
    path = parsed_url.path
    params = parsed_url.params
    query = parsed_url.query
    
    # Remove fragment
    fragment = ""
    
    # Reconstruct the URL
    canonicalized = ParseResult(
        scheme=scheme,
        netloc=netloc,
        path=path,
        params=params,
        query=query,
        fragment=fragment
    ).geturl()
    
    return canonicalized


def canonicalize_ip(ip: str) -> str:
    """
    Canonicalize an IP address.
    
    Args:
        ip: The IP address to canonicalize
        
    Returns:
        The canonicalized IP address
    """
    # For IPs, we keep as-is after validation
    return ip


def canonicalize_hash(hash_value: str) -> str:
    """
    Canonicalize a hash value.
    
    Args:
        hash_value: The hash to canonicalize
        
    Returns:
        The canonicalized hash
    """
    # Convert to lowercase
    return hash_value.lower()


def canonicalize_ioc(value: str, ioc_type: IOCType) -> str:
    """
    Canonicalize an IOC value based on its type.
    
    Args:
        value: The IOC value to canonicalize
        ioc_type: The type of the IOC
        
    Returns:
        The canonicalized IOC value
    """
    if ioc_type in ("ipv4", "ipv6"):
        return canonicalize_ip(value)
    elif ioc_type == "domain":
        return canonicalize_domain(value)
    elif ioc_type == "url":
        return canonicalize_url(value)
    elif ioc_type in ("hash_md5", "hash_sha1", "hash_sha256"):
        return canonicalize_hash(value)
    else:
        raise ValueError(f"Unknown IOC type: {ioc_type}")

