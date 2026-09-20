"""
Stage 18 Risk, Confidence & NO-BET Engine Implementation

Evaluates Stage 17 market reports and Stage 16 forecast containers to compute
deterministic confidence scores, risk flags, and decision statuses (ELIGIBLE, LOW_CONFIDENCE,
HIGH_RISK, INSUFFICIENT_EVIDENCE, BLOCKED) without bookmaker odds or value edge calculations.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from services.ml.app.markets.schemas import MappedMarket, MappedMarketReport
from services.ml.app.pipeline.schemas import CurrentMatchForecastContainer
from services.ml.app.research.schemas import ResearchState
from services.ml.app.risk.schemas import (
    ConfidenceLevel,
    DecisionStatus,
    MarketDecision,
    RiskEngineReport,
    RiskFlag,
)

logger = logging.getLogger("football_ml.risk.engine")


class RiskEngine:
    """
    Deterministic Risk, Confidence & NO-BET Decision Engine.
    """

    def evaluate_fixture_risk_and_confidence(
        self,
        market_report: MappedMarketReport,
        forecast_container: CurrentMatchForecastContainer,
    ) -> RiskEngineReport:
        logger.info(f"Evaluating risk and confidence for fixture {market_report.fixture_id} across {len(market_report.mapped_markets)} markets...")

        decisions: Dict[str, MarketDecision] = {}
        eligible_count = 0
        no_bet_count = 0
        blocked_count = 0

        for mkt_id, mkt in market_report.mapped_markets.items():
            decision = self.evaluate_market_decision(mkt, forecast_container)
            decisions[mkt_id] = decision

            if decision.decision_status == DecisionStatus.ELIGIBLE:
                eligible_count += 1
            elif decision.decision_status in (DecisionStatus.LOW_CONFIDENCE, DecisionStatus.HIGH_RISK, DecisionStatus.INSUFFICIENT_EVIDENCE):
                no_bet_count += 1
            elif decision.decision_status == DecisionStatus.BLOCKED:
                blocked_count += 1

        report = RiskEngineReport(
            report_id=f"RISK_REP_{market_report.fixture_id}_{uuid.uuid4().hex[:6]}",
            fixture_id=market_report.fixture_id,
            source_container_id=forecast_container.container_id,
            source_market_report_id=market_report.report_id,
            eligible_markets_count=eligible_count,
            no_bet_markets_count=no_bet_count,
            blocked_markets_count=blocked_count,
            market_decisions=decisions,
            created_at_utc=datetime.now(timezone.utc).isoformat(),
            risk_engine_version="STAGE18_RISK_ENGINE_v1.0.0",
        )

        logger.info(f"Risk evaluation complete for {market_report.fixture_id}: Eligible={eligible_count}, NO-BET={no_bet_count}, Blocked={blocked_count}.")
        return report

    def evaluate_market_decision(
        self,
        market: MappedMarket,
        forecast_container: CurrentMatchForecastContainer,
    ) -> MarketDecision:
        risk_flags: List[RiskFlag] = []
        reasons: List[str] = []

        # Provenance summary
        prov_summary = {
            "source_container_id": forecast_container.container_id,
            "source_fixture_id": forecast_container.fixture.fixture_id,
            "model_name": forecast_container.model_name,
            "model_version": forecast_container.model_version,
            "calibration_method": forecast_container.calibration_method,
            "container_status": forecast_container.validation_status,
            "container_blocked_reason": forecast_container.blocked_reason,
            "market_supported": market.is_supported,
            "market_unsupported_reason": market.unsupported_reason,
        }

        # 1. Blocked Forecast Container Check
        if forecast_container.validation_status != "READY":
            risk_flags.append(RiskFlag.RISK_BLOCKED_FORECAST_CONTAINER)
            reasons.append(f"Forecast container blocked ({forecast_container.blocked_reason or 'NOT_READY'})")
            if "UNVERIFIED_FIXTURE" in str(forecast_container.blocked_reason):
                risk_flags.append(RiskFlag.RISK_UNVERIFIED_FIXTURE)

            return MarketDecision(
                market_id=market.market_id,
                market_name=market.market_name,
                decision_status=DecisionStatus.BLOCKED,
                confidence_score=0.0,
                confidence_level=ConfidenceLevel.LOW,
                risk_flags=risk_flags,
                decision_reasons=reasons,
                provenance_summary=prov_summary,
            )

        # 2. Unsupported Market Check
        if not market.is_supported or not market.outcomes:
            risk_flags.append(RiskFlag.RISK_UNSUPPORTED_MARKET)
            reasons.append(f"Market unsupported: {market.unsupported_reason or 'NO_OUTCOMES'}")

            return MarketDecision(
                market_id=market.market_id,
                market_name=market.market_name,
                decision_status=DecisionStatus.BLOCKED,
                confidence_score=0.0,
                confidence_level=ConfidenceLevel.LOW,
                risk_flags=risk_flags,
                decision_reasons=reasons,
                provenance_summary=prov_summary,
            )

        # 3. Find Top Probability Outcome
        top_outcome = max(market.outcomes, key=lambda o: o.probability)
        top_prob = top_outcome.probability

        # 4. Evaluate Feature & Evidence Quality Signals
        base_confidence = 0.70 if forecast_container.calibration_method == "platt_sigmoid" else 0.50

        # Check missing key features
        missing_feats = [
            fid for fid, val in forecast_container.updated_feature_vector.items() if val is None
        ]
        if missing_feats:
            risk_flags.append(RiskFlag.RISK_MISSING_KEY_FEATURE)
            reasons.append(f"Feature vector has {len(missing_feats)} missing values")
            base_confidence -= min(0.30, 0.05 * len(missing_feats))

        # Check evidence conflicts and stale evidence
        for prov in forecast_container.feature_provenance:
            if prov.evidence_state == ResearchState.CONFLICTING:
                if RiskFlag.RISK_UNRESOLVED_EVIDENCE_CONFLICT not in risk_flags:
                    risk_flags.append(RiskFlag.RISK_UNRESOLVED_EVIDENCE_CONFLICT)
                    reasons.append("Unresolved evidence conflict present in source features")
                    base_confidence -= 0.35
            elif prov.evidence_state == ResearchState.UNCERTAIN:
                if RiskFlag.RISK_STALE_EVIDENCE not in risk_flags:
                    risk_flags.append(RiskFlag.RISK_STALE_EVIDENCE)
                    reasons.append("Stale or uncertain research evidence used in features")
                    base_confidence -= 0.15

        # Check Probability Margin
        is_multiclass = market.market_type == "MULTI_CLASS"
        threshold = 0.38 if is_multiclass else 0.52
        if top_prob < threshold:
            risk_flags.append(RiskFlag.RISK_LOW_TOP_PROBABILITY)
            reasons.append(f"Top probability {top_prob:.3f} is below market threshold {threshold}")
            base_confidence -= 0.15
        else:
            base_confidence += 0.20 * top_prob

        # Clamp confidence score [0.0, 1.0]
        confidence_score = max(0.0, min(1.0, float(base_confidence)))

        # Assign Confidence Level
        if confidence_score >= 0.70:
            confidence_level = ConfidenceLevel.HIGH
        elif confidence_score >= 0.50:
            confidence_level = ConfidenceLevel.MEDIUM
        else:
            confidence_level = ConfidenceLevel.LOW

        # 5. Deterministic Decision Status Rules
        if RiskFlag.RISK_UNRESOLVED_EVIDENCE_CONFLICT in risk_flags or len(missing_feats) > 10:
            decision_status = DecisionStatus.INSUFFICIENT_EVIDENCE
            reasons.append("NO-BET: Insufficient or conflicting evidence")
        elif RiskFlag.RISK_LOW_TOP_PROBABILITY in risk_flags or confidence_level == ConfidenceLevel.LOW:
            decision_status = DecisionStatus.LOW_CONFIDENCE
            reasons.append("NO-BET: Probability confidence below required threshold")
        elif len(risk_flags) >= 2:
            decision_status = DecisionStatus.HIGH_RISK
            reasons.append("NO-BET: Multiple risk conditions detected")
        else:
            decision_status = DecisionStatus.ELIGIBLE
            reasons.append("ELIGIBLE: Sufficient confidence and acceptable risk profile")

        return MarketDecision(
            market_id=market.market_id,
            market_name=market.market_name,
            decision_status=decision_status,
            confidence_score=round(confidence_score, 4),
            confidence_level=confidence_level,
            top_outcome_id=top_outcome.outcome_id,
            top_outcome_name=top_outcome.outcome_name,
            top_probability=top_prob,
            risk_flags=risk_flags,
            decision_reasons=reasons,
            provenance_summary=prov_summary,
        )
