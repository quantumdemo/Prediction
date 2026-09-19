# STAGE 15 — EVIDENCE VALIDATION AND PROVENANCE REPORT

**Dataset Version**: `STAGE9_FEATURE_DATASET_v1.0.0`
**Feature Version**: `STAGE9_FEATURE_DATASET_v1.0.0`
**Code Identifier**: `STAGE15_EVIDENCE_VALIDATION_v1.0.0`
**Status**: COMPLETE

---

## 1. Executive Summary

Stage 15 implements the platform's Evidence Validation Engine. Built directly on top of the approved Stage 14 Current-Match Web Research Engine, Stage 15 performs deterministic verification, freshness evaluation, deduplication, entity association checks, source domain credibility auditing, and contradiction flagging for all collected current-match evidence items.

Every validated item preserves full source provenance (Source Name, URL, UTC Retrieval Timestamp, UTC Publication Timestamp, Claim, Entity Associations, Original Research State, Adjusted Research State, Validation Outcome, and Validation Reasons). Validation results are classified deterministically into four outcomes (`ACCEPTED`, `DOWNGRADED`, `REJECTED`, `FLAGGED_CONFLICT`). Uncertain, stale, conflicting, or missing evidence is NEVER silently converted into verified data. Rejections and validation report results are completely auditable and reproducible via deterministic SHA256 audit trail hashes.

---

## 2. Validation Architecture & Deterministic Decision Rules

```
[Stage 14 Research Report]
           │
           ▼
[1. URL & Protocol Check] ──(Rejects non-HTTP/HTTPS URLs -> REJECTED)
           │
           ▼
[2. Source Allowlist Audit] ──(Allowlisted -> ACCEPTED; Unallowlisted -> DOWNGRADED)
           │
           ▼
[3. Claim Completeness Check] ──(Empty or whitespace -> REJECTED)
           │
           ▼
[4. Freshness Evaluator] ──(Retrieval > 7 days or Publication > 14 days -> STALE / DOWNGRADED)
           │
           ▼
[5. Entity Association Check] ──(Wrong entity/fixture context -> REJECTED)
           │
           ▼
[6. Deduplication Engine] ──(MD5 claim hash duplicate -> REJECTED)
           │
           ▼
[7. Contradiction Flagging] ──(Opposing claims -> FLAGGED_CONFLICT / CONFLICTING)
           │
           ▼
[Auditable Evidence Validation Report] ──► SHA256 Audit Trail Hash
```

### 2.1 Deterministic Outcome Decision Rules

| Validation Outcome | Condition / Reason Code | State Action | Downstream Action |
| :--- | :--- | :--- | :--- |
| **`ACCEPTED`** | Valid URL, allowlisted source domain, fresh timestamp, valid entity association, unique claim. | Retains `VERIFIED` or `LIKELY`. | Eligible for Stage 16 feature updating. |
| **`DOWNGRADED`** | Unallowlisted source domain OR stale timestamp (> 7 days). | Downgraded to `LIKELY` or `UNCERTAIN`. | Eligible with lower confidence weight. |
| **`FLAGGED_CONFLICT`** | Contradictory claims detected for same entity/category across sources. | Adjusted to `CONFLICTING`. | Triggers Stage 18 Risk / NO-BET conflict flags. |
| **`REJECTED`** | Invalid URL schema, missing timestamp, empty claim, wrong entity association, or duplicate claim. | Set to `UNAVAILABLE`. | Filtered out from feature update pipelines. |

---

## 3. Provenance & Auditability Contracts

Every `ValidatedEvidenceItem` retains immutable provenance attributes:
- `validation_id`: Immutable UUID key.
- `fact_id`: Parent research item ID.
- `fixture_id`: Target match canonical ID.
- `category`: Fact category (`INJURIES`, `SUSPENSIONS`, `EXPECTED_LINEUPS`, etc.).
- `claim`: Extracted text claim.
- `source_name` & `source_url`: Full source attribution URL.
- `retrieval_timestamp_utc`: Exact UTC timestamp when evidence was fetched.
- `original_research_state` & `adjusted_research_state`: Complete state transition trail.
- `validation_outcome` & `validation_reasons`: Deterministic decision outcome and reason codes.
- `validation_timestamp_utc`: UTC timestamp when validation rule was evaluated.

Every `EvidenceValidationReport` computes a deterministic SHA256 `audit_trail_hash` over the sorted JSON representation of all evaluated items, ensuring 100% auditable and reproducible validation results.

---

## 4. Testing & Verification

Unit test suite (`services/ml/tests/test_stage15_evidence_validation.py`) verifies:
- Acceptance of valid primary source evidence.
- Downgrading of unallowlisted sources and stale timestamps (> 7 days).
- Rejection of invalid URL schemas (e.g. `ftp://`), missing timestamps, and empty claims.
- Rejection of duplicate evidence via MD5 claim hashing.
- Flagging of conflicting evidence and adjustment to `ResearchState.CONFLICTING`.
- Rejection of wrong entity / wrong fixture evidence associations.
- Retention of full source provenance attributes.
- Deterministic SHA256 audit trail hash generation.
- Absolute rejection of fabricated or artificially upgraded missing data.

---

## 5. Stage Boundary & Limitations

1. **No Feature Updates**: Current evidence merging into numerical feature vectors belongs to Stage 16.
2. **No Market Mapping or Odds**: Market catalogue mapping and bookmaker odds belong to Stage 17.
3. **No Value / Kelly / NO-BET Logic**: Risk evaluation, abstention thresholds, and NO-BET decisions belong to Stage 18.
