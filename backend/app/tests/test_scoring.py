import pytest

from app.services.scoring import ScoringService


class TestScoringService:
    """Test scoring service."""

    def test_calculate_summary_malicious(self):
        """Test summary calculation for malicious verdict."""
        service = ScoringService()
        
        provider_results = [
            {
                "provider": "virustotal",
                "status": "ok",
                "reputation": 90,
                "malicious_count": 15,
                "evidence": [
                    {
                        "title": "Detections",
                        "category": "malware",
                        "severity": "critical",
                        "description": "Detected as malicious by 15 engines",
                        "attributes": {"detection_count": 15}
                    }
                ]
            },
            {
                "provider": "otx",
                "status": "ok",
                "reputation": 85,
                "evidence": [
                    {
                        "title": "Threat Intelligence",
                        "category": "threat_intel",
                        "severity": "high",
                        "description": "Found in 8 threat intelligence reports",
                        "attributes": {"pulse_count": 8}
                    }
                ]
            }
        ]
        
        summary = service.calculate_summary(provider_results)
        
        assert summary["verdict"] == "malicious"
        assert summary["score"] >= 80
        assert "high virustotal score" in summary["explanation"].lower()
        assert "otx score" in summary["explanation"].lower()

    def test_calculate_summary_suspicious(self):
        """Test summary calculation for suspicious verdict."""
        service = ScoringService()
        
        provider_results = [
            {
                "provider": "virustotal",
                "status": "ok",
                "reputation": 65,
                "malicious_count": 5,
                "evidence": [
                    {
                        "title": "Detections",
                        "category": "malware",
                        "severity": "medium",
                        "description": "Detected as malicious by 5 engines",
                        "attributes": {"detection_count": 5}
                    }
                ]
            },
            {
                "provider": "abuseipdb",
                "status": "ok",
                "reputation": 55,
                "confidence": 55,
                "evidence": [
                    {
                        "title": "Abuse Reports",
                        "category": "reputation",
                        "severity": "medium",
                        "description": "Reported 10 times by 5 users",
                        "attributes": {"total_reports": 10, "distinct_users": 5}
                    }
                ]
            }
        ]
        
        summary = service.calculate_summary(provider_results)
        
        assert summary["verdict"] == "suspicious"
        assert 50 <= summary["score"] < 80
        assert "virustotal score" in summary["explanation"].lower()

    def test_calculate_summary_clean(self):
        """Test summary calculation for clean verdict."""
        service = ScoringService()
        
        provider_results = [
            {
                "provider": "virustotal",
                "status": "ok",
                "reputation": 5,
                "malicious_count": 0,
                "evidence": []
            },
            {
                "provider": "abuseipdb",
                "status": "ok",
                "reputation": 10,
                "confidence": 10,
                "evidence": []
            }
        ]
        
        summary = service.calculate_summary(provider_results)
        
        assert summary["verdict"] == "clean"
        assert summary["score"] < 20
        assert "no malicious indicators" in summary["explanation"].lower()

    def test_calculate_summary_with_errors(self):
        """Test summary calculation with provider errors."""
        service = ScoringService()
        
        provider_results = [
            {
                "provider": "virustotal",
                "status": "error",
                "error": {"code": "timeout", "message": "Request timed out"}
            },
            {
                "provider": "otx",
                "status": "ok",
                "reputation": 85,
                "evidence": [
                    {
                        "title": "Threat Intelligence",
                        "category": "threat_intel",
                        "severity": "high",
                        "description": "Found in 8 threat intelligence reports",
                        "attributes": {"pulse_count": 8}
                    }
                ]
            }
        ]
        
        summary = service.calculate_summary(provider_results)
        
        # Should still calculate based on available data
        assert summary["verdict"] == "suspicious"
        assert summary["score"] > 0

    def test_calculate_summary_first_last_seen(self):
        """Test first/last seen extraction."""
        service = ScoringService()
        
        provider_results = [
            {
                "provider": "virustotal",
                "status": "ok",
                "reputation": 90,
                "evidence": [
                    {
                        "title": "First Submission",
                        "category": "timeline",
                        "severity": "info",
                        "description": "First seen 2023-01-15",
                        "attributes": {"first_seen": "2023-01-15T10:00:00Z"}
                    }
                ]
            },
            {
                "provider": "otx",
                "status": "ok",
                "reputation": 85,
                "evidence": [
                    {
                        "title": "Last Activity",
                        "category": "timeline",
                        "severity": "info",
                        "description": "Last seen 2023-03-20",
                        "attributes": {"last_seen": "2023-03-20T15:30:00Z"}
                    }
                ]
            }
        ]
        
        summary = service.calculate_summary(provider_results)
        
        assert summary["first_seen"] == "2023-01-15T10:00:00Z"
        assert summary["last_seen"] == "2023-03-20T15:30:00Z"

