import tempfile
import unittest
from pathlib import Path

from scripts.validate_content_system import check


ROOT = Path(__file__).resolve().parents[1]


class ContentSystemValidationTests(unittest.TestCase):
    def test_repository_contract_is_valid(self):
        self.assertEqual(check(ROOT), [])

    def test_missing_module_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            for source in (ROOT / "system-version.json", ROOT / "CHATGPT_SETUP.md"):
                destination = target / source.name
                destination.write_bytes(source.read_bytes())
            errors = check(target)
            self.assertTrue(any("missing module" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
