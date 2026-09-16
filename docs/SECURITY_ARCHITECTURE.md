# SECURITY ARCHITECTURE
## FOOTBALL AI INTELLIGENCE & MACHINE-LEARNING PLATFORM

### 1. SECRETS MANAGEMENT & ENVIRONMENT SEPARATION

#### 1.1 Strict Server-Client Boundary
- Server secrets (`DATABASE_URL`, `API_FOOTBALL_KEY`, `MODAL_TOKEN`, `JWT_SECRET`) MUST NEVER be prefixed with `NEXT_PUBLIC_` or exposed to client-side JS bundles.
- Vercel Environment Variables are configured separately for `Development`, `Preview`, and `Production` environments.

#### 1.2 Database Access Control
- Web API services connect via connection-pooled low-privilege roles (read/write access to business tables only; schema alteration prohibited).
- DB Migrations execute via dedicated CI/CD execution service roles.

---

### 2. THREAT MITIGATION IN WEB RESEARCH

#### 2.1 Server-Side Request Forgery (SSRF) Defense
- All HTTP requests initiated by the Web Research Engine execute through an isolated HTTP proxy.
- Private IP ranges (`10.0.0.0/8`, `127.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.169.254`) and non-HTTP protocols (`file://`, `gopher://`) are strictly blocked at DNS resolution time.

#### 2.2 Indirect Prompt Injection Mitigation
- Web pages fetched during research are treated as **untrusted raw text**.
- Raw text is stripped of embedded instructions or HTML comment injections prior to LLM analysis.
- LLMs execute extraction strictly via deterministic Pydantic schema validation. Extracted strings are NEVER passed to system instructions or SQL execution strings.

---

### 3. API SECURITY & INPUT VALIDATION

- All client-facing API endpoints validate incoming JSON payloads using Pydantic / Zod schemas.
- Administrative, re-indexing, and model training trigger routes require JWT / Bearer Token authorization with Role-Based Access Control (RBAC).
- Rate limiting is enforced at the Vercel Edge layer (e.g., 60 requests/minute per IP).
