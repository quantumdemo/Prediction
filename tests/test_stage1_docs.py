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

        required_sections = [
            "SECTION 1: MASTER CONTROL SPECIFICATION",
            "SECTION 2: FORMAL PLATFORM REQUIREMENTS DOCUMENT",
            "SECTION 3: SYSTEM BOUNDARIES",
            "SECTION 4: DATA CONTRACT PRINCIPLES",
            "SECTION 5: ML GOVERNANCE",
            "SECTION 6: PREDICTION LIFECYCLE",
            "SECTION 7: NO-BET GOVERNANCE",
            "SECTION 8: MARKET GOVERNANCE",
            "SECTION 9: DATA SOURCE GOVERNANCE",
            "SECTION 10: REQUIREMENTS TRACEABILITY MATRIX",
            "SECTION 11: STAGE DEPENDENCY MAP",
            "SECTION 12: OPEN TECHNICAL QUESTIONS REGISTER",
            "SECTION 13: PROJECT RISK REGISTER"
        ]
        for section in required_sections:
            self.assertIn(section, content, f"Missing section '{section}' in MASTER_SPECIFICATION.md")

    def test_requirement_ids(self):
        with open(self.master_spec_path, "r", encoding="utf-8") as f:
            content = f.read()

        req_prefixes = [
            "REQ-FUNC-",
            "REQ-DATA-",
            "REQ-ML-",
            "REQ-WEB-",
            "REQ-EVID-",
            "REQ-MKT-",
            "REQ-RISK-",
            "REQ-REP-",
            "REQ-SEC-",
            "REQ-TEST-",
            "REQ-DEP-",
            "REQ-MON-",
            "REQ-VER-"
        ]
        for prefix in req_prefixes:
            self.assertIn(prefix, content, f"Missing requirement prefix '{prefix}' in MASTER_SPECIFICATION.md")

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
