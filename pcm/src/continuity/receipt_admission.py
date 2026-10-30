"""Internal, disabled receipt admission evaluator (PCM-0026 TASK-09).

Implements the four-gate receipt admission decision (D1, D2, P, Q) described
in issue #67 owner decision OWNER-17. Production always denies: the only
production provider returns no qualification evidence for any profile.

This module is pure standard library (``dataclasses``, ``enum``, ``typing``
only). It performs no I/O, reads no clock, uses no randomness, and touches no
store, transport, CLI, or credential surface. Every result is a verdict with
reason codes only; it is never a send token or capability of any kind.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

PCM67_WIN32_DELETE_EXTRA_V1 = "PCM67-WIN32-DELETE-EXTRA-v1"

#: The only profile identifier this evaluator recognizes. This identifies a
#: candidate, not an approved stack; the production qualification set is empty.
KNOWN_QUALIFICATION_PROFILE_IDS: frozenset[str] = frozenset({PCM67_WIN32_DELETE_EXTRA_V1})


class Gate(StrEnum):
    """The four admission gates; every one is required for admission."""

    D1 = "D1"
    D2 = "D2"
    P = "P"
    Q = "Q"


class EvidenceKind(StrEnum):
    """Kinds of admission evidence.

    The insufficient-alone kinds (including operator attestation, per its
    explicit trust limit) can never satisfy a gate by themselves; version
    strings, PRAGMA readback, UUIDs, paths, local flags, and artifact hashes
    identify a candidate at best and never establish qualification.
    """

    VERSION_STRING = "VERSION_STRING"
    PRAGMA_READBACK = "PRAGMA_READBACK"
    STORE_UUID = "STORE_UUID"
    LOCAL_PATH = "LOCAL_PATH"
    LOCAL_FLAG = "LOCAL_FLAG"
    ARTIFACT_HASH = "ARTIFACT_HASH"
    OPERATOR_ATTESTATION = "OPERATOR_ATTESTATION"
    REVIEWED_RUNTIME_REPORT = "REVIEWED_RUNTIME_REPORT"
    REVIEWED_DURABILITY_MATRIX = "REVIEWED_DURABILITY_MATRIX"
    REVIEWED_CUSTODY_RECORDS = "REVIEWED_CUSTODY_RECORDS"
    REVIEWED_ROUTE_COVERAGE = "REVIEWED_ROUTE_COVERAGE"

    def qualifies_for(self, gate: Gate) -> bool:
        """True only for the one gate the owner decision table binds this kind to.

        A reviewed kind satisfies exactly its own gate; every kind that is not
        sufficient alone qualifies for no gate. Qualification implies
        ``is_sufficient_alone``.
        """
        return _QUALIFYING_GATE_BY_KIND.get(self) is gate

    @property
    def is_sufficient_alone(self) -> bool:
        """True only for reviewed evidence kinds that may satisfy a gate alone."""
        return self in _SUFFICIENT_ALONE_KINDS


_SUFFICIENT_ALONE_KINDS: frozenset[EvidenceKind] = frozenset(
    {
        EvidenceKind.REVIEWED_RUNTIME_REPORT,
        EvidenceKind.REVIEWED_DURABILITY_MATRIX,
        EvidenceKind.REVIEWED_CUSTODY_RECORDS,
        EvidenceKind.REVIEWED_ROUTE_COVERAGE,
    }
)

#: Owner decision table (issue #67): each reviewed kind is bound to exactly one
#: gate, and only that gate; insufficient-alone kinds qualify for none.
_QUALIFYING_GATE_BY_KIND: dict[EvidenceKind, Gate] = {
    EvidenceKind.REVIEWED_RUNTIME_REPORT: Gate.D1,
    EvidenceKind.REVIEWED_DURABILITY_MATRIX: Gate.D2,
    EvidenceKind.REVIEWED_CUSTODY_RECORDS: Gate.P,
    EvidenceKind.REVIEWED_ROUTE_COVERAGE: Gate.Q,
}


class EvidenceStatus(StrEnum):
    """Lifecycle status of an evidence record; only CURRENT can count."""

    CURRENT = "CURRENT"
    STALE = "STALE"
    UNKNOWN = "UNKNOWN"
    CONFLICTING = "CONFLICTING"
    UNSUPPORTED = "UNSUPPORTED"
    FAILED = "FAILED"
    INVALIDATED = "INVALIDATED"


class StoreProvenance(StrEnum):
    """Custody provenance of the installation store under evaluation."""

    ORIGINAL = "ORIGINAL"
    COPIED = "COPIED"
    RESTORED = "RESTORED"
    REIMAGED = "REIMAGED"
    DESTROYED = "DESTROYED"
    UNKNOWN = "UNKNOWN"


class LegacyWriterState(StrEnum):
    """Observed quiescence of legacy writers at the deployed writer revision."""

    QUIESCENT = "QUIESCENT"
    UNCERTAIN = "UNCERTAIN"
    UNKNOWN = "UNKNOWN"
    ACTIVE = "ACTIVE"


@dataclass(frozen=True)
class CandidateProfile:
    """Exact runtime/binary/VFS/adapter/OS/filesystem/storage candidate tuple."""

    profile_id: str
    python_version: str
    sqlite_version: str
    os_name: str
    os_build: str
    vfs: str
    filesystem: str
    journal_mode: str
    synchronous: str
    store_provenance: StoreProvenance
    legacy_writers: LegacyWriterState


@dataclass(frozen=True)
class AdmissionContext:
    """Revision context the admission decision is bound to."""

    profile_id: str
    policy_revision: str
    writer_revision: str


@dataclass(frozen=True)
class EvidenceRecord:
    """One reviewed evidence item bound to a profile and revision pair."""

    gate: Gate
    kind: EvidenceKind
    status: EvidenceStatus
    reviewed: bool
    bound_profile: CandidateProfile
    policy_revision: str
    writer_revision: str


@dataclass(frozen=True)
class AdmissionVerdict:
    """A verdict and reason codes only; never a send token or capability."""

    admitted: bool
    reasons: tuple[str, ...]
    checked_profile_id: str


class QualificationProvider(Protocol):
    """Supplies evidence records for a profile identifier."""

    def qualifications(self, profile_id: str) -> tuple[EvidenceRecord, ...]: ...


class EmptyProductionQualificationProvider:
    """Production provider: the qualification set is empty, so admission denies."""

    def qualifications(self, profile_id: str) -> tuple[EvidenceRecord, ...]:
        return ()


def _evaluate_gate(
    gate: Gate,
    records: tuple[EvidenceRecord, ...],
    profile: CandidateProfile,
    context: AdmissionContext,
) -> list[str]:
    """Return deny reason codes for one gate, in the fixed priority order."""
    if not records:
        return [f"MISSING_GATE:{gate.value}"]
    denied: list[str] = []
    for record in records:
        if record.status is not EvidenceStatus.CURRENT:
            denied.append(f"{record.status.value.upper()}_EVIDENCE:{gate.value}")
    if denied:
        return denied
    if any(not record.reviewed for record in records):
        return [f"UNREVIEWED_EVIDENCE:{gate.value}"]
    for record in records:
        if record.bound_profile != profile:
            denied.append("PROFILE_BINDING_DRIFT")
        if record.policy_revision != context.policy_revision:
            denied.append("POLICY_REVISION_DRIFT")
        if record.writer_revision != context.writer_revision:
            denied.append("WRITER_REVISION_DRIFT")
    if denied:
        return denied
    if any(record.kind.qualifies_for(gate) for record in records):
        return []
    kind_codes: list[str] = []
    if any(not record.kind.is_sufficient_alone for record in records):
        kind_codes.append(f"INSUFFICIENT_EVIDENCE:{gate.value}")
    if any(record.kind.is_sufficient_alone for record in records):
        kind_codes.append(f"KIND_GATE_MISMATCH:{gate.value}")
    return sorted(kind_codes)


def evaluate_admission(
    profile: CandidateProfile,
    context: AdmissionContext,
    provider: QualificationProvider,
) -> AdmissionVerdict:
    """Decide admission deterministically; any doubt denies.

    Checks run in a fixed order: context match (short-circuits), known profile
    identifier, store provenance, legacy writer quiescence, then each gate in
    D1, D2, P, Q order. Deny returns every accumulated reason code, sorted
    without duplicates; a PASS verdict carries no reasons.
    """
    if profile.profile_id != context.profile_id:
        return AdmissionVerdict(
            admitted=False,
            reasons=("CONTEXT_PROFILE_MISMATCH",),
            checked_profile_id=profile.profile_id,
        )
    reasons: list[str] = []
    if profile.profile_id not in KNOWN_QUALIFICATION_PROFILE_IDS:
        reasons.append("UNKNOWN_PROFILE")
    if profile.store_provenance is not StoreProvenance.ORIGINAL:
        reasons.append("STORE_NOT_ORIGINAL")
    if profile.legacy_writers is not LegacyWriterState.QUIESCENT:
        reasons.append("LEGACY_WRITERS_UNCERTAIN")
    records = provider.qualifications(profile.profile_id)
    for gate in Gate:
        gate_records = tuple(record for record in records if record.gate is gate)
        reasons.extend(_evaluate_gate(gate, gate_records, profile, context))
    return AdmissionVerdict(
        admitted=not reasons,
        reasons=tuple(sorted(set(reasons))),
        checked_profile_id=profile.profile_id,
    )


def production_admission(profile: CandidateProfile, context: AdmissionContext) -> AdmissionVerdict:
    """Production entry point: always denies via the empty qualification set."""
    return evaluate_admission(profile, context, EmptyProductionQualificationProvider())
