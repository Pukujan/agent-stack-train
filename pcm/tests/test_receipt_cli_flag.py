from __future__ import annotations

import unittest

from continuity.cli import ContinuityError, build_parser, page_is_complete, require_receipt_pair


class ReceiptCliFlagTests(unittest.TestCase):
    def test_checkpoint_defaults_omit_the_receipt_flags(self) -> None:
        args = build_parser().parse_args(["checkpoint", "PCM-0026", "--agent", "staff", "--next", "continue"])
        self.assertIsNone(args.receipt_repo)
        self.assertIsNone(args.receipt_issue)

    def test_one_receipt_flag_is_rejected(self) -> None:
        with self.assertRaises(ContinuityError):
            require_receipt_pair("Pukujan/project-continuity-modules", None)
        with self.assertRaises(ContinuityError):
            require_receipt_pair(None, "67")

    def test_full_page_is_not_proof_of_absence(self) -> None:
        self.assertFalse(page_is_complete(100, 100))
        self.assertTrue(page_is_complete(3, 100))


if __name__ == "__main__":
    unittest.main()
