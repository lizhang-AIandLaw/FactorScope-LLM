import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from inspect_dataset import audit_dataset, verify_manifest  # noqa: E402


class DatasetReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit_dataset(ROOT / "data")
        cls.manifest = json.loads((ROOT / "data" / "manifest.json").read_text())

    def test_frozen_dataset_matches_manifest(self):
        verify_manifest(self.report, self.manifest)

    def test_catalog_has_26_factors_and_no_f9(self):
        self.assertEqual(len(self.report["factor_ids"]), 26)
        self.assertNotIn("F9", self.report["factor_ids"])


if __name__ == "__main__":
    unittest.main()
