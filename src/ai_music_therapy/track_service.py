"""Staged workflow for uploaded tracks (S19).

State machine shared with the UI:

    proposed -> under_review -> trial_confirmed -> approved | rejected

The persistence boundary is the whole point (student requirement and D028):
nothing is written to the database before explicit approval, rejection
persists nothing, and an approved entry is write-once (the repository has no
update path and refuses duplicate track ids). Review-stage confirmation
trials run in memory only and are never saved.

The raw audio file never reaches disk or database anywhere in this pipeline:
a proposal carries the in-memory extraction profile plus the source-file
sha256, and only those survive approval.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import UTC, datetime

from .models import AudioExtraction, MusicParameters, TrackEntry

PROPOSED = "proposed"
UNDER_REVIEW = "under_review"
TRIAL_CONFIRMED = "trial_confirmed"
APPROVED = "approved"
REJECTED = "rejected"

#: Valid forward transitions; approval is terminal (write-once entry).
TRANSITIONS: dict[str, tuple[str, ...]] = {
    PROPOSED: (UNDER_REVIEW,),
    UNDER_REVIEW: (TRIAL_CONFIRMED, APPROVED, REJECTED),
    TRIAL_CONFIRMED: (APPROVED, REJECTED, UNDER_REVIEW),
    APPROVED: (),
    REJECTED: (),
}


def advance(proposal: TrackProposal, to: str) -> str:
    """Move a proposal between workflow states, refusing invalid jumps.

    Approval/rejection can only happen from review or trial-confirmed; a
    proposal cannot skip review, and terminal states cannot move.
    """
    state = proposal.state
    if state not in TRANSITIONS:
        raise ValueError(f"Unknown workflow state: {state}")
    if to not in TRANSITIONS[state]:
        raise ValueError(f"Invalid workflow transition: {state} -> {to}")
    proposal.state = to
    return to


def file_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass
class TrackProposal:
    """An uploaded track under consideration. Ephemeral by design.

    Holds the in-memory extraction and source attribution only; the audio
    bytes themselves are discarded after extraction, so even the proposal
    cannot leak the file.
    """

    extraction: AudioExtraction
    source_file_name: str
    source_file_sha256: str
    state: str = PROPOSED
    created_at: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )


def finalize_track(
    proposal: TrackProposal,
    track_id: str,
    display_name: str,
    music: MusicParameters,
    overridden_fields: list[str],
    notes: str = "",
) -> TrackEntry:
    """Build the write-once TrackEntry at approval time.

    Pure: raises on invalid ids/shapes via the TrackEntry schema, and refuses
    to finalize a proposal that was rejected (approval must come from an
    active review state). Persisting the result is the caller's explicit act.
    """
    if proposal.state not in (UNDER_REVIEW, TRIAL_CONFIRMED):
        raise ValueError(
            f"Cannot approve a track in state '{proposal.state}'; a proposal "
            "must be under review first"
        )
    advance(proposal, APPROVED)
    return TrackEntry(
        track_id=track_id,
        display_name=display_name,
        source_file_name=proposal.source_file_name,
        source_file_sha256=proposal.source_file_sha256,
        music=music,
        extraction=proposal.extraction,
        overridden_fields=sorted(overridden_fields),
        notes=notes,
    )


def reject(proposal: TrackProposal) -> None:
    """Reject a proposal; nothing may be persisted afterwards."""
    if proposal.state not in (PROPOSED, UNDER_REVIEW, TRIAL_CONFIRMED):
        raise ValueError(f"Cannot reject a track in state '{proposal.state}'")
    advance(proposal, REJECTED)
