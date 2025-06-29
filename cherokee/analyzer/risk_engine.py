class RiskEngine:
    def score(self, token_details: dict):
        # Simplified scoring based on available data
        risk_score = 0.5  # Placeholder constant
        if not token_details:
            risk_score = 1.0
        risk_level = self._to_level(risk_score)
        return risk_score, risk_level

    def _to_level(self, score: float) -> str:
        if score < 0.3:
            return 'Low'
        if score < 0.6:
            return 'Medium'
        if score < 0.9:
            return 'High'
        return 'Critical'
