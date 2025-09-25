from typing import Any, Dict, List, Optional


class ScoringService:
    """Service for calculating verdict and score from provider results."""
    
    def __init__(self):
        # Default weights for each provider
        self.provider_weights = {
            "virustotal": 0.5,  # Increased from 0.4
            "otx": 0.3,        # Increased from 0.25
            "abuseipdb": 0.2   # Kept same
        }
        
        # Verdict thresholds
        self.verdict_thresholds = {
            "malicious": 80,  # 80-100
            "suspicious": 50,  # 50-79
            "unknown": 20,    # 20-49
            "clean": 0        # 0-19
        }
    
    def calculate_summary(self, provider_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate summary verdict and score from provider results.
        
        Args:
            provider_results: List of normalized provider results
            
        Returns:
            Summary dict with verdict, score, explanation, first_seen, last_seen
        """
        # Initialize summary
        summary = {
            "verdict": "unknown",
            "score": 0,
            "explanation": "",
            "first_seen": None,
            "last_seen": None
        }
        
        # Calculate weighted score
        total_weight = 0
        weighted_score = 0
        provider_scores = {}
        
        for result in provider_results:
            provider = result.get("provider")
            status = result.get("status")
            
            # Skip providers with errors
            if status != "ok":
                continue
            
            # Get provider weight
            weight = self.provider_weights.get(provider, 0.1)
            
            # Get reputation score
            reputation = result.get("reputation")
            if reputation is not None:
                # Cap contribution from any single provider at 80
                capped_reputation = min(reputation, 80)
                provider_scores[provider] = capped_reputation
                weighted_score += capped_reputation * weight
                total_weight += weight
            
            # Update first/last seen if available
            for evidence in result.get("evidence", []):
                attributes = evidence.get("attributes", {})
                if "first_seen" in attributes and attributes["first_seen"]:
                    if summary["first_seen"] is None or attributes["first_seen"] < summary["first_seen"]:
                        summary["first_seen"] = attributes["first_seen"]
                if "last_seen" in attributes and attributes["last_seen"]:
                    if summary["last_seen"] is None or attributes["last_seen"] > summary["last_seen"]:
                        summary["last_seen"] = attributes["last_seen"]
        
        # Calculate final score
        final_score = 0
        if total_weight > 0:
            final_score = int(weighted_score / total_weight)
        
        summary["score"] = final_score
        
        # Determine verdict based on score
        if final_score >= self.verdict_thresholds["malicious"]:
            summary["verdict"] = "malicious"
        elif final_score >= self.verdict_thresholds["suspicious"]:
            summary["verdict"] = "suspicious"
        elif final_score >= self.verdict_thresholds["unknown"]:
            summary["verdict"] = "unknown"
        else:
            summary["verdict"] = "clean"
        
        # Generate explanation
        explanation_parts = []
        
        # Add key drivers to explanation
        sorted_providers = sorted(
            provider_scores.items(), key=lambda x: x[1], reverse=True
        )
        
        if sorted_providers:
            top_provider, top_score = sorted_providers[0]
            if top_score > 50:
                explanation_parts.append(f"high {top_provider} score ({top_score})")
            
            # Add second provider if available and significant
            if len(sorted_providers) > 1:
                second_provider, second_score = sorted_providers[1]
                if second_score > 30:
                    explanation_parts.append(f"{second_provider} score ({second_score})")
        
        # Add evidence-based explanations
        malware_evidence = False
        network_evidence = False
        reputation_evidence = False
        
        for result in provider_results:
            for evidence in result.get("evidence", []):
                category = evidence.get("category")
                severity = evidence.get("severity")
                
                if category == "malware" and severity in ("critical", "high"):
                    malware_evidence = True
                elif category == "network" and severity in ("critical", "high"):
                    network_evidence = True
                elif category == "reputation" and severity in ("critical", "high"):
                    reputation_evidence = True
        
        if malware_evidence:
            explanation_parts.append("malware detections")
        if reputation_evidence:
            explanation_parts.append("poor reputation")
        if network_evidence:
            explanation_parts.append("suspicious network indicators")
        
        # If no specific explanations, use generic ones based on verdict
        if not explanation_parts:
            if summary["verdict"] == "malicious":
                explanation_parts = ["multiple malicious indicators"]
            elif summary["verdict"] == "suspicious":
                explanation_parts = ["some suspicious indicators"]
            elif summary["verdict"] == "clean":
                explanation_parts = ["no malicious indicators"]
            else:
                explanation_parts = ["insufficient data"]
        
        # Combine explanation parts
        summary["explanation"] = "Based on " + ", ".join(explanation_parts)
        
        return summary

