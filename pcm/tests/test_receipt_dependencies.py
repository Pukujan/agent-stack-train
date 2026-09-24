from __future__ import annotations

import unittest

from continuity.cli import receipt_dependency_line


class ReceiptDependencyTests(unittest.TestCase):
    def test_dependencies_are_joined_and_not_invented(self) -> None:
        self.assertEqual(receipt_dependency_line(["#53", " #66 "]), "#53, #66")
        self.assertEqual(receipt_dependency_line([]), "not supplied")


if __name__ == "__main__":
    unittest.main()
