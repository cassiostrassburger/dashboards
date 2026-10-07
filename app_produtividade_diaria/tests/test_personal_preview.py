"""The private snapshot must not publish unverified daily records as fact."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from app_produtividade_diaria.build_personal_preview import build


class PersonalPreviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name) / "data.json"
        self.output = Path(self.temp.name) / "index.html"
        self.data = {
            "monthly": [{"period": "2026-01"}, {"period": "2026-02"}],
            "dailyActivities": [],
            "relationships": [],
        }

    def save(self):
        self.source.write_text(json.dumps(self.data), encoding="utf-8")

    def test_confirmed_relation_requires_evidence_and_reference(self):
        self.data["relationships"] = [{
            "processA": "PROC-A", "processB": "PROC-B",
            "relationType": "Mesmo CAR", "confirmationState": "confirmed",
            "evidence": "", "evidenceReference": "",
        }]
        self.save()
        with self.assertRaisesRegex(ValueError, "evidência e referência"):
            build(self.source, self.output)
        self.assertFalse(self.output.exists())

    def test_daily_activity_needs_date_and_description(self):
        self.data["dailyActivities"] = [{
            "activityDate": "", "description": "",
            "processIds": [], "category": "analysis",
        }]
        self.save()
        with self.assertRaisesRegex(ValueError, "data e descrição"):
            build(self.source, self.output)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
