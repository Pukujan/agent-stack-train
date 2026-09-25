from __future__ import annotations

import ast
import dataclasses
import unittest
from pathlib import Path

from continuity.receipt_admission import (
    PCM67_WIN32_DELETE_EXTRA_V1,
    AdmissionContext,
    AdmissionVerdict,
    CandidateProfile,
    EmptyProductionQualificationProvider,
    EvidenceKind,
    EvidenceRecord,
    EvidenceStatus,
    Gate,
    LegacyWriterState,
    StoreProvenance,
    evaluate_admission,
    production_admission,
)

POLICY_REVISION = "policy-r7"
WRITER_REVISION = "writer-r4"

GATE_QUALIFYING_KINDS: dict[Gate, EvidenceKind] = {
    Gate.D1: EvidenceKind.REVIEWED_RUNTIME_REPORT,
    Gate.D2: EvidenceKind.REVIEWED_DURABILITY_MATRIX,
    Gate.P: EvidenceKind.REVIEWED_CUSTODY_RECORDS,
    Gate.Q: EvidenceKind.REVIEWED_ROUTE_COVERAGE,
}

INSUFFICIENT_ALONE_KINDS = (
    EvidenceKind.VERSION_STRING,
    EvidenceKind.PRAGMA_READBACK,
    EvidenceKind.STORE_UUID,
    EvidenceKind.LOCAL_PATH,
    EvidenceKind.LOCAL_FLAG,
    EvidenceKind.ARTIFACT_HASH,
    EvidenceKind.OPERATOR_ATTESTATION,
)

STATUS_DENY_CODES = {
    EvidenceStatus.STALE: "STALE_EVIDENCE",
    EvidenceStatus.UNKNOWN: "UNKNOWN_EVIDENCE",
    EvidenceStatus.CONFLICTING: "CONFLICTING_EVIDENCE",
    EvidenceStatus.UNSUPPORTED: "UNSUPPORTED_EVIDENCE",
    EvidenceStatus.FAILED: "FAILED_EVIDENCE",
    EvidenceStatus.INVALIDATED: "INVALIDATED_EVIDENCE",
}


def make_profile(**overrides: object) -> CandidateProfile:
    values: dict[str, object] = {
        "profile_id": PCM67_WIN32_DELETE_EXTRA_V1,
        "python_version": "3.12.10",
        "sqlite_version": "3.49.1",
        "os_name": "Windows",
        "os_build": "26200",
        "vfs": "win32wink",
        "filesystem": "NTFS",
        "journal_mode": "DELETE",
        "synchronous": "EXTRA",
        "store_provenance": StoreProvenance.ORIGINAL,
        "legacy_writers": LegacyWriterState.QUIESCENT,
    }
    values.update(overrides)
    return CandidateProfile(**values)  # type: ignore[arg-type]


def make_context(**overrides: object) -> AdmissionContext:
    values: dict[str, object] = {
        "profile_id": PCM67_WIN32_DELETE_EXTRA_V1,
        "policy_revision": POLICY_REVISION,
        "writer_revision": WRITER_REVISION,
    }
    values.update(overrides)
    return AdmissionContext(**values)  # type: ignore[arg-type]


def make_record(
    gate: Gate,
    kind: EvidenceKind,
    bound_profile: CandidateProfile,
    *,
    status: EvidenceStatus = EvidenceStatus.CURRENT,
    reviewed: bool = True,
    policy_revision: str = POLICY_REVISION,
    writer_revision: str = WRITER_REVISION,
) -> EvidenceRecord:
    return EvidenceRecord(
        gate=gate,
        kind=kind,
        status=status,
        reviewed=reviewed,
        bound_profile=bound_profile,
        policy_revision=policy_revision,
        writer_revision=writer_revision,
    )


def full_clean_evidence(profile: CandidateProfile) -> tuple[EvidenceRecord, ...]:
    return tuple(
        make_record(gate, GATE_QUALIFYING_KINDS[gate], bound_profile=profile)
        for gate in Gate
    )


class TableProvider:
    """Test-only qualification fixture; never wired into production code."""

    def __init__(self, records_by_profile: dict[str, tuple[EvidenceRecord, ...]] | None = None) -> None:
        self._records = records_by_profile or {}

    def qualifications(self, profile_id: str) -> tuple[EvidenceRecord, ...]:
        return self._records.get(profile_id, ())


def provider_replacing(
    profile: CandidateProfile,
    gate: Gate,
    records: tuple[EvidenceRecord, ...],
) -> TableProvider:
    others = tuple(
        make_record(other, GATE_QUALIFYING_KINDS[other], bound_profile=profile)
        for other in Gate
        if other is not gate
    )
    return TableProvider({profile.profile_id: others + records})


PCM67_PROFILE = make_profile()
MATCHING_CONTEXT = make_context()


class ReceiptAdmissionTests(unittest.TestCase):
    def test_hypothetical_pass_through_the_test_only_fixture(self) -> None:
        provider = TableProvider({PCM67_WIN32_DELETE_EXTRA_V1: full_clean_evidence(PCM67_PROFILE)})
        verdict = evaluate_admission(PCM67_PROFILE, MATCHING_CONTEXT, provider)
        self.assertTrue(verdict.admitted)
        self.assertEqual(verdict.reasons, ())
        self.assertEqual(verdict.checked_profile_id, PCM67_WIN32_DELETE_EXTRA_V1)

    def test_production_always_denies_the_exact_pcm67_candidate_tuple(self) -> None:
        expected = ("MISSING_GATE:D1", "MISSING_GATE:D2", "MISSING_GATE:P", "MISSING_GATE:Q")
        with self.subTest(entry="production_admission"):
            verdict = production_admission(PCM67_PROFILE, MATCHING_CONTEXT)
            self.assertFalse(verdict.admitted)
            self.assertEqual(verdict.reasons, expected)
            self.assertEqual(verdict.checked_profile_id, PCM67_WIN32_DELETE_EXTRA_V1)
        with self.subTest(entry="empty_provider"):
            verdict = evaluate_admission(
                PCM67_PROFILE, MATCHING_CONTEXT, EmptyProductionQualificationProvider()
            )
            self.assertFalse(verdict.admitted)
            self.assertEqual(verdict.reasons, expected)

    def test_a_single_gate_never_admits_the_other_gates_still_deny(self) -> None:
        for gate in Gate:
            with self.subTest(gate=gate.value):
                provider = TableProvider(
                    {PCM67_WIN32_DELETE_EXTRA_V1: (make_record(gate, GATE_QUALIFYING_KINDS[gate], PCM67_PROFILE),)}
                )
                verdict = evaluate_admission(PCM67_PROFILE, MATCHING_CONTEXT, provider)
                self.assertFalse(verdict.admitted)
                expected_missing = tuple(
                    f"MISSING_GATE:{other.value}" for other in Gate if other is not gate
                )
                self.assertEqual(verdict.reasons, expected_missing)

    def test_each_missing_gate_denies(self) -> None:
        for missing in Gate:
            with self.subTest(missing=missing.value):
                records = tuple(
                    make_record(gate, GATE_QUALIFYING_KINDS[gate], PCM67_PROFILE)
                    for gate in Gate
                    if gate is not missing
                )
                provider = TableProvider({PCM67_WIN32_DELETE_EXTRA_V1: records})
                verdict = evaluate_admission(PCM67_PROFILE, MATCHING_CONTEXT, provider)
                self.assertFalse(verdict.admitted)
                self.assertIn(f"MISSING_GATE:{missing.value}", verdict.reasons)

    def test_each_non_current_status_denies_its_gate(self) -> None:
        for gate in Gate:
            for status, code in STATUS_DENY_CODES.items():
                with self.subTest(gate=gate.value, status=status.value):
                    provider = provider_replacing(
                        PCM67_PROFILE,
                        gate,
                        (make_record(gate, GATE_QUALIFYING_KINDS[gate], PCM67_PROFILE, status=status),),
                    )
                    verdict = evaluate_admission(PCM67_PROFILE, MATCHING_CONTEXT, provider)
                    self.assertFalse(verdict.admitted)
                    self.assertIn(f"{code}:{gate.value}", verdict.reasons)

    def test_unreviewed_evidence_denies_its_gate(self) -> None:
        for gate in Gate:
            with self.subTest(gate=gate.value):
                provider = provider_replacing(
                    PCM67_PROFILE,
                    gate,
                    (make_record(gate, GATE_QUALIFYING_KINDS[gate], PCM67_PROFILE, reviewed=False),),
                )
                verdict = evaluate_admission(PCM67_PROFILE, MATCHING_CONTEXT, provider)
                self.assertFalse(verdict.admitted)
                self.assertIn(f"UNREVIEWED_EVIDENCE:{gate.value}", verdict.reasons)

    def test_each_insufficient_alone_kind_cannot_satisfy_a_gate_by_itself(self) -> None:
        for gate in Gate:
            for kind in INSUFFICIENT_ALONE_KINDS:
                with self.subTest(gate=gate.value, kind=kind.value):
                    provider = provider_replacing(
                        PCM67_PROFILE, gate, (make_record(gate, kind, PCM67_PROFILE),)
                    )
                    verdict = evaluate_admission(PCM67_PROFILE, MATCHING_CONTEXT, provider)
                    self.assertFalse(verdict.admitted)
                    self.assertIn(f"INSUFFICIENT_EVIDENCE:{gate.value}", verdict.reasons)

    def test_sufficient_evidence_alongside_insufficient_alone_evidence_still_admits(self) -> None:
        for kind in INSUFFICIENT_ALONE_KINDS:
            for gate in Gate:
                with self.subTest(gate=gate.value, kind=kind.value):
                    provider = provider_replacing(
                        PCM67_PROFILE,
                        gate,
                        (
                            make_record(gate, kind, PCM67_PROFILE),
                            make_record(gate, GATE_QUALIFYING_KINDS[gate], PCM67_PROFILE),
                        ),
                    )
                    verdict = evaluate_admission(PCM67_PROFILE, MATCHING_CONTEXT, provider)
                    self.assertTrue(verdict.admitted)
                    self.assertEqual(verdict.reasons, ())

    def test_is_sufficient_alone_flag_matches_the_owner_decision_table(self) -> None:
        for kind in INSUFFICIENT_ALONE_KINDS:
            with self.subTest(kind=kind.value):
                self.assertFalse(kind.is_sufficient_alone)
        for kind in GATE_QUALIFYING_KINDS.values():
            with self.subTest(kind=kind.value):
                self.assertTrue(kind.is_sufficient_alone)

    def test_qualifies_for_matches_the_owner_gate_binding(self) -> None:
        for gate, expected_kind in GATE_QUALIFYING_KINDS.items():
            for kind in EvidenceKind:
                with self.subTest(gate=gate.value, kind=kind.value):
                    self.assertEqual(kind.qualifies_for(gate), kind is expected_kind)
        for gate in Gate:
            for kind in EvidenceKind:
                if kind.qualifies_for(gate):
                    with self.subTest(implication=kind.value):
                        self.assertTrue(kind.is_sufficient_alone)

    def test_a_reviewed_kind_bound_to_another_gate_denies_the_gate(self) -> None:
        for gate in Gate:
            for other_gate, other_kind in GATE_QUALIFYING_KINDS.items():
                if other_gate is gate:
                    continue
                with self.subTest(gate=gate.value, kind=other_kind.value):
                    provider = provider_replacing(
                        PCM67_PROFILE, gate, (make_record(gate, other_kind, PCM67_PROFILE),)
                    )
                    verdict = evaluate_admission(PCM67_PROFILE, MATCHING_CONTEXT, provider)
                    self.assertFalse(verdict.admitted)
                    self.assertEqual(verdict.reasons, (f"KIND_GATE_MISMATCH:{gate.value}",))

    def test_mixed_insufficient_and_wrong_gate_reviewed_evidence_emits_both_codes(self) -> None:
        for gate in Gate:
            wrong_gate = next(other for other in Gate if other is not gate)
            with self.subTest(gate=gate.value):
                provider = provider_replacing(
                    PCM67_PROFILE,
                    gate,
                    (
                        make_record(gate, EvidenceKind.VERSION_STRING, PCM67_PROFILE),
                        make_record(gate, GATE_QUALIFYING_KINDS[wrong_gate], PCM67_PROFILE),
                    ),
                )
                verdict = evaluate_admission(PCM67_PROFILE, MATCHING_CONTEXT, provider)
                self.assertFalse(verdict.admitted)
                self.assertEqual(
                    verdict.reasons,
                    (f"INSUFFICIENT_EVIDENCE:{gate.value}", f"KIND_GATE_MISMATCH:{gate.value}"),
                )

    def test_clean_own_gate_evidence_still_admits_after_kind_binding(self) -> None:
        provider = TableProvider({PCM67_WIN32_DELETE_EXTRA_V1: full_clean_evidence(PCM67_PROFILE)})
        verdict = evaluate_admission(PCM67_PROFILE, MATCHING_CONTEXT, provider)
        self.assertTrue(verdict.admitted)
        self.assertEqual(verdict.reasons, ())

    def test_binding_drift_denies(self) -> None:
        drifted_profile = make_profile(sqlite_version="3.48.0")
        with self.subTest(kind="profile_binding"):
            provider = provider_replacing(
                PCM67_PROFILE,
                Gate.D1,
                (make_record(Gate.D1, EvidenceKind.REVIEWED_RUNTIME_REPORT, drifted_profile),),
            )
            verdict = evaluate_admission(PCM67_PROFILE, MATCHING_CONTEXT, provider)
            self.assertFalse(verdict.admitted)
            self.assertIn("PROFILE_BINDING_DRIFT", verdict.reasons)
        with self.subTest(kind="policy_revision"):
            provider = provider_replacing(
                PCM67_PROFILE,
                Gate.D2,
                (
                    make_record(
                        Gate.D2,
                        EvidenceKind.REVIEWED_DURABILITY_MATRIX,
                        PCM67_PROFILE,
                        policy_revision="policy-r6",
                    ),
                ),
            )
            verdict = evaluate_admission(PCM67_PROFILE, MATCHING_CONTEXT, provider)
            self.assertFalse(verdict.admitted)
            self.assertIn("POLICY_REVISION_DRIFT", verdict.reasons)
        with self.subTest(kind="writer_revision"):
            provider = provider_replacing(
                PCM67_PROFILE,
                Gate.P,
                (
                    make_record(
                        Gate.P,
                        EvidenceKind.REVIEWED_CUSTODY_RECORDS,
                        PCM67_PROFILE,
                        writer_revision="writer-r3",
                    ),
                ),
            )
            verdict = evaluate_admission(PCM67_PROFILE, MATCHING_CONTEXT, provider)
            self.assertFalse(verdict.admitted)
            self.assertIn("WRITER_REVISION_DRIFT", verdict.reasons)

    def test_every_non_original_provenance_denies(self) -> None:
        for provenance in (
            StoreProvenance.COPIED,
            StoreProvenance.RESTORED,
            StoreProvenance.REIMAGED,
            StoreProvenance.DESTROYED,
            StoreProvenance.UNKNOWN,
        ):
            with self.subTest(provenance=provenance.value):
                profile = make_profile(store_provenance=provenance)
                provider = TableProvider({profile.profile_id: full_clean_evidence(profile)})
                verdict = evaluate_admission(profile, MATCHING_CONTEXT, provider)
                self.assertFalse(verdict.admitted)
                self.assertIn("STORE_NOT_ORIGINAL", verdict.reasons)

    def test_every_non_quiescent_legacy_writer_state_denies(self) -> None:
        for state in (
            LegacyWriterState.UNCERTAIN,
            LegacyWriterState.UNKNOWN,
            LegacyWriterState.ACTIVE,
        ):
            with self.subTest(state=state.value):
                profile = make_profile(legacy_writers=state)
                provider = TableProvider({profile.profile_id: full_clean_evidence(profile)})
                verdict = evaluate_admission(profile, MATCHING_CONTEXT, provider)
                self.assertFalse(verdict.admitted)
                self.assertIn("LEGACY_WRITERS_UNCERTAIN", verdict.reasons)

    def test_unknown_profile_id_denies(self) -> None:
        profile = make_profile(profile_id="PCM67-WIN32-DELETE-EXTRA-v2")
        context = make_context(profile_id=profile.profile_id)
        verdict = evaluate_admission(profile, context, TableProvider())
        self.assertFalse(verdict.admitted)
        self.assertIn("UNKNOWN_PROFILE", verdict.reasons)

    def test_context_profile_mismatch_denies(self) -> None:
        context = make_context(profile_id="SOME-OTHER-PROFILE-v1")
        provider = TableProvider({PCM67_WIN32_DELETE_EXTRA_V1: full_clean_evidence(PCM67_PROFILE)})
        verdict = evaluate_admission(PCM67_PROFILE, context, provider)
        self.assertFalse(verdict.admitted)
        self.assertEqual(verdict.reasons, ("CONTEXT_PROFILE_MISMATCH",))

    def test_reasons_accumulate_all_deny_codes_sorted_and_deduplicated(self) -> None:
        profile = make_profile(
            store_provenance=StoreProvenance.RESTORED,
            legacy_writers=LegacyWriterState.ACTIVE,
        )
        records = (
            make_record(Gate.D1, EvidenceKind.REVIEWED_RUNTIME_REPORT, profile, status=EvidenceStatus.STALE),
            make_record(Gate.D1, EvidenceKind.ARTIFACT_HASH, profile, status=EvidenceStatus.STALE),
            make_record(Gate.D2, EvidenceKind.REVIEWED_DURABILITY_MATRIX, profile),
            make_record(Gate.D2, EvidenceKind.STORE_UUID, profile),
            make_record(Gate.P, EvidenceKind.REVIEWED_CUSTODY_RECORDS, profile),
        )
        provider = TableProvider({profile.profile_id: records})
        verdict = evaluate_admission(profile, MATCHING_CONTEXT, provider)
        self.assertFalse(verdict.admitted)
        self.assertEqual(
            verdict.reasons,
            (
                "LEGACY_WRITERS_UNCERTAIN",
                "MISSING_GATE:Q",
                "STALE_EVIDENCE:D1",
                "STORE_NOT_ORIGINAL",
            ),
        )

    def test_evaluation_is_deterministic(self) -> None:
        provider = TableProvider({PCM67_WIN32_DELETE_EXTRA_V1: full_clean_evidence(PCM67_PROFILE)})
        first = evaluate_admission(PCM67_PROFILE, MATCHING_CONTEXT, provider)
        second = evaluate_admission(PCM67_PROFILE, MATCHING_CONTEXT, provider)
        self.assertEqual(first, second)

    def test_verdict_shape_carries_only_a_verdict_and_reasons_no_capability(self) -> None:
        field_names = {field.name for field in dataclasses.fields(AdmissionVerdict)}
        self.assertEqual(field_names, {"admitted", "reasons", "checked_profile_id"})
        self.assertTrue(AdmissionVerdict.__dataclass_params__.frozen)

    def test_module_imports_only_pure_stdlib_dependencies(self) -> None:
        source = Path(__file__).resolve().parents[1] / "src" / "continuity" / "receipt_admission.py"
        tree = ast.parse(source.read_text(encoding="utf-8"))
        allowed = {"__future__", "dataclasses", "enum", "typing"}
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.add((node.module or "").split(".")[0])
        self.assertEqual(imported, imported & allowed)


if __name__ == "__main__":
    unittest.main()
