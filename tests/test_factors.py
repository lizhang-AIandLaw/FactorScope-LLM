import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import factors  # noqa: E402


class FactorRegistryTests(unittest.TestCase):
    def test_complete_catalog_is_default(self):
        self.assertEqual(len(factors.ACTIVE), 26)
        self.assertEqual(factors.ACTIVE_NAME, "27")
        self.assertNotIn("F9", factors.ACTIVE)

    def test_entailment_helpers_are_consistent(self):
        for source in factors.ACTIVE:
            for target in factors.entailed_by(source):
                self.assertIn(source, factors.entailers_of(target))


if __name__ == "__main__":
    unittest.main()
