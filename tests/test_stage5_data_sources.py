import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


class TestStage5DataSources(unittest.TestCase):
    def test_required_stage5_documentation_exists(self):
        required_docs = [
            "FOOTBALL_DATA_SOURCE_RESEARCH.md",
            "FOOTBALL_DATA_SOURCE_MATRIX.md",
            "DATA_SOURCE_HIERARCHY.md",
            "DATA_ACQUISITION_STRATEGY.md",
            "DATA_SOURCE_LICENSING.md",
            "DATA_ACQUISITION_RISK_REGISTER.md",
            "STAGE6_ACQUISITION_PLAN.md",
        ]
        for filename in required_docs:
            filepath = os.path.join(DOCS_DIR, filename)
            self.assertTrue(
                os.path.exists(filepath),
                f"Required Stage 5 documentation file '{filename}' must exist in docs/",
            )

    def test_source_matrix_fields_and_verification_states(self):
        matrix_path = os.path.join(DOCS_DIR, "FOOTBALL_DATA_SOURCE_MATRIX.md")
        with open(matrix_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check required providers
        self.assertIn("Football-Data.co.uk", content)
        self.assertIn("API-Football", content)
        self.assertIn("StatsBomb Open Data", content)
        self.assertIn("OpenFootball", content)

        # Check verification state presence
        self.assertIn("VERIFIED", content)

    def test_openfootball_classification(self):
        research_path = os.path.join(DOCS_DIR, "FOOTBALL_DATA_SOURCE_RESEARCH.md")
        with open(research_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("REFERENCE / ENTITY RESOLUTION SOURCE", content)
        self.assertIn("NOT a match statistics source", content)

    def test_stage6_plan_references_stage4_schema(self):
        plan_path = os.path.join(DOCS_DIR, "STAGE6_ACQUISITION_PLAN.md")
        with open(plan_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("sources", content)
        self.assertIn("raw_source_payloads", content)
        self.assertIn("provenance_records", content)
        self.assertIn("dataset_versions", content)


if __name__ == "__main__":
    unittest.main()
