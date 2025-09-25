from typing import Dict, List

from app.core.ioc_utils import IOCType
from app.services.providers.abuseipdb import AbuseIPDBAdapter
from app.services.providers.base import ProviderAdapter
from app.services.providers.otx import OTXAdapter
from app.services.providers.virustotal import VirusTotalAdapter


class ProviderFactory:
    """Factory for creating provider adapters."""

    @staticmethod
    def create_all() -> Dict[str, ProviderAdapter]:
        """
        Create all provider adapters.
        
        Returns:
            Dictionary mapping provider names to adapter instances
        """
        return {
            "virustotal": VirusTotalAdapter(),
            "abuseipdb": AbuseIPDBAdapter(),
            "otx": OTXAdapter(),
        }
    
    @staticmethod
    def create_for_ioc_type(ioc_type: IOCType) -> Dict[str, ProviderAdapter]:
        """
        Create provider adapters that support the given IOC type.
        
        Args:
            ioc_type: The IOC type
            
        Returns:
            Dictionary mapping provider names to adapter instances
        """
        all_providers = ProviderFactory.create_all()
        return {
            name: provider
            for name, provider in all_providers.items()
            if ioc_type in provider.supports_types
        }
    
    @staticmethod
    def get_provider_order() -> List[str]:
        """
        Get the order in which providers should be displayed.
        
        Returns:
            List of provider names in display order
        """
        return ["virustotal", "abuseipdb", "otx"]

