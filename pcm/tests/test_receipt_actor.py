from __future__ import annotations

import unittest

from continuity.cli import ContinuityError, authenticated_actor


class ReceiptActorTests(unittest.TestCase):
    def test_accepts_a_login(self) -> None:
        self.assertEqual(authenticated_actor("  Pukujan\n"), "Pukujan")

    def test_rejects_a_missing_login(self) -> None:
        with self.assertRaises(ContinuityError):
            authenticated_actor("  ")
        with self.assertRaises(ContinuityError):
            authenticated_actor("not a login")


if __name__ == "__main__":
    unittest.main()
