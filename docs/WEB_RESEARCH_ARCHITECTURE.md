# WEB RESEARCH ARCHITECTURE
## FOOTBALL AI INTELLIGENCE & MACHINE-LEARNING PLATFORM

### 1. OBJECTIVE & ARCHITECTURAL ISOLATION

The Current-Match Web Research Engine gathers real-time current evidence (team news, press conference quotes, injury updates, suspension notices, and expected lineups) for upcoming verified fixtures.

#### STRICT ISOLATION PRINCIPLE
- Web research outputs **DO NOT** generate numerical win/loss probabilities.
- Numerical probabilities MUST originate strictly from trained statistical/ML models.
- The LLM's role in web research is limited to:
  1. Extracting structured facts from unstructured news/press releases.
  2. Resolving player and team name aliases.
  3. Classifying evidence state (`VERIFIED`, `LIKELY`, `UNCERTAIN`, `CONFLICTING`).
  4. Detecting contradictions between multiple news sources.

---

### 2. PIPELINE ARCHITECTURE

```
[VERIFIED UPCOMING FIXTURE]
             │
             ▼
[1. SEARCH & FETCH WORKER] ──(Controlled Domain Allowlist)
             │
             ▼
 [2. HTML / TEXT CLEANER] ──(Sanitizer & Prompt Injection Guard)
             │
             ▼
[3. STRUCTURED FACT PARSER] ──(LLM JSON Extraction)
             │
             ▼
[4. ALIAS & ENTITY LINKER] ──(Map Player/Team to Canonical UUID)
             │
             ▼
[5. EVIDENCE CLASSIFIER] ──(Classify: VERIFIED / UNCERTAIN / CONFLICTING)
             │
             ▼
 [6. PROVENANCE DB LOGGER] ──► Stores Evidence Item (URL, Timestamp, Fact, State)
```

---

### 3. SECURITY & SAFETY CONTROLS

#### 3.1 Server-Side Request Forgery (SSRF) Safeguards
- All outbound web requests MUST use an HTTP client configured with a domain allowlist and private IP range blocklists (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.1`).
- Redirects to local/internal network interfaces are strictly blocked.

#### 3.2 Prompt Injection Safeguards
- Scraped HTML content MUST be stripped of script tags, comments, and hidden styling before passing to LLMs.
- LLM extraction prompts use strict system prompt delimiters and Pydantic schema enforcing:
  ```python
  class ExtractedPlayerFact(BaseModel):
      player_canonical_name: str
      fact_type: Literal["INJURY", "SUSPENSION", "LINEUP_CONFIRMED", "TACTICAL_NOTE"]
      status_severity: Literal["OUT", "DOUBTFUL", "AVAILABLE"]
      source_confidence: Literal["VERIFIED", "LIKELY", "UNCERTAIN", "CONFLICTING"]
  ```
