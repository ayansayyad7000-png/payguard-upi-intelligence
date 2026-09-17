from dataclasses import dataclass


@dataclass(frozen=True)
class DefaultSettings:
    threshold: float = 2000.0
    mdr_rate: float = 0.40
    velocity_window_min: int = 10
    medium_risk_score: int = 35
    high_risk_score: int = 70


DEFAULTS = DefaultSettings()
APP_NAME = "PayGuard UPI Intelligence"
APP_TAGLINE = "Smart UPI payment analytics, MDR simulation and fraud-pattern intelligence"
