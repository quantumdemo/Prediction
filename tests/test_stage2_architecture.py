import os
import unittest

class TestStage2ArchitectureDocs(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.docs_dir = os.path.join(self.root_dir, "docs")

    def test_required_stage2_files_exist(self):
        required_files = [
            "ARCHITECTURE_OVERVIEW.md",
            "INFRASTRUCTURE_ARCHITECTURE.md",
            "TECHNOLOGY_RESEARCH.md",
            "FOOTBALL_DATA_SOURCES.md",
            "WEB_RESEARCH_ARCHITECTURE.md",
            "DATA_ARCHITECTURE.md",
            "ML_ARCHITECTURE.md",
            "SECURITY_ARCHITECTURE.md",
            "DEPLOYMENT_ARCHITECTURE.md",
            "FAILURE_AND_RECOVERY_ARCHITECTURE.md",
            "TECHNOLOGY_RISK_REGISTER.md",
            "ADR_DECISIONS.md"
        ]
        for filename in required_files:
            filepath = os.path.join(self.docs_dir, filename)
            self.assertTrue(os.path.exists(filepath), f"Stage 2 document {filename} must exist in docs/")

    def test_adr_decisions_structure(self):
        filepath = os.path.join(self.docs_dir, "ADR_DECISIONS.md")
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        required_adrs = [
            "ADR-001: FRONTEND & WEB LAYER ARCHITECTURE",
            "ADR-002: BACKEND & API ARCHITECTURE",
            "ADR-003: DATABASE SELECTION",
            "ADR-004: MACHINE LEARNING FORECASTING ENGINE",
            "ADR-005: ASYNCHRONOUS WORKER & BACKGROUND JOB ARCHITECTURE",
            "ADR-006: OBJECT & ARTIFACT STORAGE",
            "ADR-007: DEPLOYMENT INFRASTRUCTURE",
            "ADR-008: SYSTEM MONITORING & OBSERVABILITY",
            "ADR-009: FOOTBALL DATA SOURCE INTEGRATION STRATEGY"
        ]
        for adr in required_adrs:
            self.assertIn(adr, content, f"Missing required ADR '{adr}' in ADR_DECISIONS.md")

    def test_infrastructure_vercel_separation(self):
        filepath = os.path.join(self.docs_dir, "INFRASTRUCTURE_ARCHITECTURE.md")
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("Vercel Responsibilities", content)
        self.assertIn("Non-Vercel Infrastructure Responsibilities", content)
        self.assertIn("PostgreSQL", content)
        self.assertIn("Async Python Workers", content)

    def test_football_data_sources_verified(self):
        filepath = os.path.join(self.docs_dir, "FOOTBALL_DATA_SOURCES.md")
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("Football-Data.co.uk", content)
        self.assertIn("API-Football", content)
        self.assertIn("VERIFIED", content)
        self.assertIn("Licensing", content)

    def test_ml_leakage_and_calibration(self):
        filepath = os.path.join(self.docs_dir, "ML_ARCHITECTURE.md")
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("ZERO FUTURE-DATA LEAKAGE", content)
        self.assertIn("PROBABILITY CALIBRATION", content)
        self.assertIn("Platt Scaling", content)
        self.assertIn("Isotonic Regression", content)

    def test_no_bet_and_failure_recovery(self):
        filepath = os.path.join(self.docs_dir, "FAILURE_AND_RECOVERY_ARCHITECTURE.md")
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("NO-BET FALLBACK MATRIX", content)
        self.assertIn("NO BET", content)

if __name__ == "__main__":
    unittest.main()
