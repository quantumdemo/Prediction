import os
import sys
import unittest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from services.ml.app.db.models import (  # noqa: E402
    ClubExternalIdModel,
    DatasetVersionModel,
    ProvenanceRecordModel,
    RawSourcePayloadModel,
)


class TestAcquisitionSchemaAlignment(unittest.TestCase):
    def test_acquisition_models_have_required_fields(self):
        # RawSourcePayloadModel
        self.assertTrue(hasattr(RawSourcePayloadModel, "source_id"))
        self.assertTrue(hasattr(RawSourcePayloadModel, "raw_payload_json"))
        self.assertTrue(hasattr(RawSourcePayloadModel, "retrieved_at_utc"))
        self.assertTrue(hasattr(RawSourcePayloadModel, "ingestion_run_id"))

        # ProvenanceRecordModel
        self.assertTrue(hasattr(ProvenanceRecordModel, "source_url"))
        self.assertTrue(hasattr(ProvenanceRecordModel, "validation_state"))

        # DatasetVersionModel
        self.assertTrue(hasattr(DatasetVersionModel, "cutoff_timestamp_utc"))

        # ClubExternalIdModel
        self.assertTrue(hasattr(ClubExternalIdModel, "external_id"))
        self.assertTrue(hasattr(ClubExternalIdModel, "source_id"))


if __name__ == "__main__":
    unittest.main()
