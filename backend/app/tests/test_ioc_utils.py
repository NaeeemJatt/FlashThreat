import pytest

from app.core.ioc_utils import (
    canonicalize_domain,
    canonicalize_hash,
    canonicalize_ip,
    canonicalize_ioc,
    canonicalize_url,
    detect_ioc_type,
    is_valid_domain,
    is_valid_ipv4,
    is_valid_ipv6,
    is_valid_md5,
    is_valid_sha1,
    is_valid_sha256,
    is_valid_url,
)


class TestIOCValidation:
    """Test IOC validation functions."""

    def test_is_valid_ipv4(self):
        """Test IPv4 validation."""
        # Valid IPv4 addresses
        assert is_valid_ipv4("192.168.1.1") is True
        assert is_valid_ipv4("8.8.8.8") is True
        assert is_valid_ipv4("127.0.0.1") is True
        assert is_valid_ipv4("255.255.255.255") is True
        assert is_valid_ipv4("0.0.0.0") is True

        # Invalid IPv4 addresses
        assert is_valid_ipv4("192.168.1") is False
        assert is_valid_ipv4("192.168.1.256") is False
        assert is_valid_ipv4("192.168.1.1.1") is False
        assert is_valid_ipv4("192.168.1.a") is False
        assert is_valid_ipv4("example.com") is False
        assert is_valid_ipv4("") is False

    def test_is_valid_ipv6(self):
        """Test IPv6 validation."""
        # Valid IPv6 addresses
        assert is_valid_ipv6("2001:0db8:85a3:0000:0000:8a2e:0370:7334") is True
        assert is_valid_ipv6("2001:db8:85a3::8a2e:370:7334") is True
        assert is_valid_ipv6("::1") is True
        assert is_valid_ipv6("::") is True
        assert is_valid_ipv6("fe80::1") is True

        # Invalid IPv6 addresses
        assert is_valid_ipv6("2001:db8:85a3::8a2e:370:7334:1") is False
        assert is_valid_ipv6("2001:db8:85a3::8a2e:370z:7334") is False
        assert is_valid_ipv6("192.168.1.1") is False
        assert is_valid_ipv6("example.com") is False
        assert is_valid_ipv6("") is False

    def test_is_valid_domain(self):
        """Test domain validation."""
        # Valid domains
        assert is_valid_domain("example.com") is True
        assert is_valid_domain("sub.example.com") is True
        assert is_valid_domain("sub-domain.example.co.uk") is True
        assert is_valid_domain("xn--80aswg.xn--p1ai") is True  # Cyrillic domain

        # Invalid domains
        assert is_valid_domain("example") is False
        assert is_valid_domain("example.") is False
        assert is_valid_domain(".example.com") is False
        assert is_valid_domain("example.com/path") is False
        assert is_valid_domain("192.168.1.1") is False
        assert is_valid_domain("") is False

    def test_is_valid_url(self):
        """Test URL validation."""
        # Valid URLs
        assert is_valid_url("http://example.com") is True
        assert is_valid_url("https://example.com") is True
        assert is_valid_url("http://example.com/path") is True
        assert is_valid_url("https://example.com/path?query=value") is True
        assert is_valid_url("https://sub.example.com:8080/path") is True
        assert is_valid_url("http://192.168.1.1") is True

        # Invalid URLs
        assert is_valid_url("example.com") is False
        assert is_valid_url("ftp://example.com") is False  # Not in our regex
        assert is_valid_url("http://") is False
        assert is_valid_url("http://.com") is False
        assert is_valid_url("") is False

    def test_is_valid_md5(self):
        """Test MD5 validation."""
        # Valid MD5 hash
        assert is_valid_md5("d41d8cd98f00b204e9800998ecf8427e") is True
        assert is_valid_md5("D41D8CD98F00B204E9800998ECF8427E") is True

        # Invalid MD5 hash
        assert is_valid_md5("d41d8cd98f00b204e9800998ecf8427") is False  # Too short
        assert is_valid_md5("d41d8cd98f00b204e9800998ecf8427ef") is False  # Too long
        assert is_valid_md5("d41d8cd98f00b204e9800998ecf8427z") is False  # Invalid char
        assert is_valid_md5("") is False

    def test_is_valid_sha1(self):
        """Test SHA1 validation."""
        # Valid SHA1 hash
        assert is_valid_sha1("da39a3ee5e6b4b0d3255bfef95601890afd80709") is True
        assert is_valid_sha1("DA39A3EE5E6B4B0D3255BFEF95601890AFD80709") is True

        # Invalid SHA1 hash
        assert is_valid_sha1("da39a3ee5e6b4b0d3255bfef95601890afd8070") is False  # Too short
        assert is_valid_sha1("da39a3ee5e6b4b0d3255bfef95601890afd807099") is False  # Too long
        assert is_valid_sha1("da39a3ee5e6b4b0d3255bfef95601890afd8070z") is False  # Invalid char
        assert is_valid_sha1("") is False

    def test_is_valid_sha256(self):
        """Test SHA256 validation."""
        # Valid SHA256 hash
        valid_sha256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        assert is_valid_sha256(valid_sha256) is True
        assert is_valid_sha256(valid_sha256.upper()) is True

        # Invalid SHA256 hash
        assert is_valid_sha256(valid_sha256[:-1]) is False  # Too short
        assert is_valid_sha256(valid_sha256 + "a") is False  # Too long
        assert is_valid_sha256(valid_sha256[:-1] + "z") is False  # Invalid char
        assert is_valid_sha256("") is False


class TestIOCDetection:
    """Test IOC detection functions."""

    def test_detect_ioc_type(self):
        """Test IOC type detection."""
        # IPv4
        ioc_type, error = detect_ioc_type("192.168.1.1")
        assert ioc_type == "ipv4"
        assert error is None

        # IPv6
        ioc_type, error = detect_ioc_type("2001:db8:85a3::8a2e:370:7334")
        assert ioc_type == "ipv6"
        assert error is None

        # Domain
        ioc_type, error = detect_ioc_type("example.com")
        assert ioc_type == "domain"
        assert error is None

        # URL
        ioc_type, error = detect_ioc_type("https://example.com/path")
        assert ioc_type == "url"
        assert error is None

        # MD5
        ioc_type, error = detect_ioc_type("d41d8cd98f00b204e9800998ecf8427e")
        assert ioc_type == "hash_md5"
        assert error is None

        # SHA1
        ioc_type, error = detect_ioc_type("da39a3ee5e6b4b0d3255bfef95601890afd80709")
        assert ioc_type == "hash_sha1"
        assert error is None

        # SHA256
        sha256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        ioc_type, error = detect_ioc_type(sha256)
        assert ioc_type == "hash_sha256"
        assert error is None

        # Invalid
        ioc_type, error = detect_ioc_type("invalid")
        assert ioc_type is None
        assert error is not None

        # Empty
        ioc_type, error = detect_ioc_type("")
        assert ioc_type is None
        assert error is not None


class TestIOCCanonicalization:
    """Test IOC canonicalization functions."""

    def test_canonicalize_ip(self):
        """Test IP canonicalization."""
        assert canonicalize_ip("192.168.1.1") == "192.168.1.1"
        assert canonicalize_ip("2001:db8:85a3::8a2e:370:7334") == "2001:db8:85a3::8a2e:370:7334"

    def test_canonicalize_domain(self):
        """Test domain canonicalization."""
        assert canonicalize_domain("EXAMPLE.com") == "example.com"
        assert canonicalize_domain("example.com.") == "example.com"
        assert canonicalize_domain("Sub.Example.Com") == "sub.example.com"

    def test_canonicalize_url(self):
        """Test URL canonicalization."""
        assert canonicalize_url("HTTP://EXAMPLE.COM") == "http://example.com"
        assert canonicalize_url("https://example.com/PATH") == "https://example.com/PATH"
        assert canonicalize_url("http://example.com/path?query=value#fragment") == "http://example.com/path?query=value"

    def test_canonicalize_hash(self):
        """Test hash canonicalization."""
        assert canonicalize_hash("D41D8CD98F00B204E9800998ECF8427E") == "d41d8cd98f00b204e9800998ecf8427e"
        assert canonicalize_hash("d41d8cd98f00b204e9800998ecf8427e") == "d41d8cd98f00b204e9800998ecf8427e"

    def test_canonicalize_ioc(self):
        """Test IOC canonicalization."""
        assert canonicalize_ioc("192.168.1.1", "ipv4") == "192.168.1.1"
        assert canonicalize_ioc("EXAMPLE.COM", "domain") == "example.com"
        assert canonicalize_ioc("HTTP://EXAMPLE.COM", "url") == "http://example.com"
        assert canonicalize_ioc("D41D8CD98F00B204E9800998ECF8427E", "hash_md5") == "d41d8cd98f00b204e9800998ecf8427e"

        with pytest.raises(ValueError):
            canonicalize_ioc("example.com", "invalid_type")

