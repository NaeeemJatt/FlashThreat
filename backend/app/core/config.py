from typing import Dict, List, Optional, Set

from pydantic import AnyHttpUrl, Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )

    # Application settings
    APP_ENV: str = "dev"  # one of: dev, test, prod
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "FlashThreat"

    # Security
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database
    POSTGRES_DSN: PostgresDsn

    # Redis
    REDIS_URL: str

    # Provider API keys
    VT_API_KEY: str
    ABUSEIPDB_API_KEY: str
    OTX_API_KEY: str
    SHODAN_API_KEY: str

    # Cache TTLs
    CACHE_TTL_IP_SEC: int = 3600  # 1 hour
    CACHE_TTL_DOMAIN_SEC: int = 10800  # 3 hours
    CACHE_TTL_URL_SEC: int = 10800  # 3 hours
    CACHE_TTL_HASH_SEC: int = 604800  # 7 days

    # Provider timeouts
    PROVIDER_TIMEOUT_SEC: int = 8
    PROVIDER_CONNECT_TIMEOUT_SEC: int = 2

    # Circuit breaker
    CIRCUIT_BREAKER_FAILS: int = 3
    CIRCUIT_BREAKER_COOLDOWN_SEC: int = 60

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)


class ProviderConfig:
    """Configuration for a provider API."""

    base_url: str
    paths: Dict[str, str]


class ProvidersConfig:
    """Configuration for all provider APIs."""

    virustotal = ProviderConfig()
    virustotal.base_url = "https://www.virustotal.com/api/v3"
    virustotal.paths = {
        "ipv4": "/ip_addresses/{ioc}",
        "ipv6": "/ip_addresses/{ioc}",
        "domain": "/domains/{ioc}",
        "url": "/urls/{ioc}",
        "hash_md5": "/files/{ioc}",
        "hash_sha1": "/files/{ioc}",
        "hash_sha256": "/files/{ioc}",
    }

    abuseipdb = ProviderConfig()
    abuseipdb.base_url = "https://api.abuseipdb.com/api/v2"
    abuseipdb.paths = {
        "ipv4": "/check",  # with querystring ipAddress={ioc}
    }


    otx = ProviderConfig()
    otx.base_url = "https://otx.alienvault.com/api/v1"
    otx.paths = {
        "ipv4": "/indicators/IPv4/{ioc}/general",
        "ipv6": "/indicators/IPv6/{ioc}/general",
        "domain": "/indicators/domain/{ioc}/general",
        "url": "/indicators/url/{ioc}/general",
        "hash_md5": "/indicators/file/{ioc}/general",
        "hash_sha1": "/indicators/file/{ioc}/general",
        "hash_sha256": "/indicators/file/{ioc}/general",
    }


settings = Settings()
providers_config = ProvidersConfig()

