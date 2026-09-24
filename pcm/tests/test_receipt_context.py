from __future__ import annotations

import unittest

from continuity.cli import receipt_parent_url, receipt_test_line


class ReceiptContextTests(unittest.TestCase):
    def test_parent_url_uses_the_repository_and_issue(self) -> None:
        self.assertEqual(
            receipt_parent_url("Pukujan/project-continuity-modules", "53"),
            "https://github.com/Pukujan/project-continuity-modules/issues/53",
        )
        self.assertEqual(receipt_parent_url("Pukujan/project-continuity-modules", None), "not supplied")

    def test_test_line_uses_supplied_evidence(self) -> None:
        self.assertEqual(receipt_test_line(["pytest -q", "  "]), "pytest -q")
        self.assertEqual(receipt_test_line([]), "not supplied")


if __name__ == "__main__":
    unittest.main()
