import os
import unittest

class TestStage1Docs(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.master_spec_path = os.path.join(self.root_dir, "docs", "MASTER_SPECIFICATION.md")
        self.constitution_path = os.path.join(self.root_dir, "docs", "ENGINEERING_CONSTITUTION.md")
        self.readme_path = os.path.join(self.root_dir, "README.md")

    def test_files_exist(self):
        self.assertTrue(os.path.exists(self.master_spec_path), "MASTER_SPECIFICATION.md must exist")
        self.assertTrue(os.path.exists(self.constitution_path), "ENGINEERING_CONSTITUTION.md must exist")
        self.assertTrue(os.path.exists(self.readme_path), "README.md must exist")

    def test_master_spec_sections(self):
        with open(self.master_spec_path, "r", encoding="utf-8") as f:
            content = f.read()

        required_keywords = [
            "SINGLE SOURCE OF TRUTH",
            "1. CORE PRODUCT",
            "2. FUNDAMENTAL ARCHITECTURE",
            "3. REAL DATA ONLY",
            "4. FOOTBALL ENTITY SYSTEM",
            "5. FIXTURE VERIFICATION",
            "6. HISTORICAL DATA",
            "7. CURRENT MATCH RESEARCH",
            "8. DATA VALIDATION",
            "9. FEATURE ENGINEERING",
            "10. FORECASTING ENGINE",
            "11. TIME-AWARE VALIDATION",
            "12. PROBABILITY CALIBRATION",
            "13. MARKET SYSTEM",
            "14. SPECIALIST MARKETS",
            "15. RISK, CONFIDENCE AND NO BET",
            "16. AUDITABILITY",
            "17. WEBSITE",
            "18. VERCEL",
            "19. SECURITY",
            "20. VERSIONING",
            "21. TESTING",
            "22. DATA AND RESEARCH RULE",
            "23. DEVELOPMENT STAGES",
            "24. STAGE CONTROL",
            "25. COMPLETION STANDARD",
            "26. NO INVENTION RULE",
            "27. STANDARD STAGE HANDOFF REPORT",
            "28. COMMUNICATION RULE",
            "29. MASTER PRINCIPLE"
        ]
        for keyword in required_keywords:
            self.assertIn(keyword, content, f"Missing required keyword/section '{keyword}' in MASTER_SPECIFICATION.md")

    def test_constitution_articles(self):
        with open(self.constitution_path, "r", encoding="utf-8") as f:
            content = f.read()

        required_articles = [
            "ARTICLE I — REAL DATA & ZERO-FABRICATION PRINCIPLE",
            "ARTICLE II — TIME-AWARE VALIDATION & LEAKAGE PREVENTION",
            "ARTICLE III — ENTITY CANONICALIZATION & FEATURE SEPARATION",
            "ARTICLE IV — ABSTENTION, RISK & NO-BET AS FIRST-CLASS OUTPUT",
            "ARTICLE V — AUDITABILITY & PROVENANCE",
            "ARTICLE VI — STAGE-GATED DEVELOPMENT & EXECUTION CONTROL"
        ]
        for article in required_articles:
            self.assertIn(article, content, f"Missing article '{article}' in ENGINEERING_CONSTITUTION.md")

    def test_readme_stage_and_architecture(self):
        with open(self.readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("STAGE 1 — Master Specification & Engineering Constitution", content)
        self.assertIn("System Architecture", content)
        self.assertIn("Development Stages", content)

if __name__ == "__main__":
    unittest.main()
