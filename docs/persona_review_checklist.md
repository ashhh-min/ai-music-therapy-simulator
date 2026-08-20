# Persona Review Checklist

Unit: S11 (2026-08-20). Implementation: `src/ai_music_therapy/persona_service.py`,
UI review workflow in `src/ai_music_therapy/ui/personas.py`.

Every AI-drafted persona must pass this human review before it can be saved.
The automated lint (`lint_persona`) is a safety net, not the review: a human
makes the final accept/reject/revise decision.

## Automated gates (enforced in code)

| Gate | Kind | Behavior |
|---|---|---|
| Schema | blocking | Must validate as `Persona` (Pydantic, `extra="forbid"`, age 4-18, `synthetic` locked `True`, non-empty lists, `P-` id prefix). Invalid drafts never leave the drafting function. |
| Stereotype wording | blocking (hard) | Text scanned for functioning-level labels and deficit/tragedy framing ("high-functioning", "low-functioning", "suffers from", "burden", ...). Accept is refused until the wording is revised. |
| Synthetic wording | blocking (hard) | `profile_summary` must state the profile is synthetic. |
| Near-duplicate | confirm (soft) | Structural match (same support profile + communication modes + triggers) with an approved persona requires an explicit confirmation checkbox. |
| No-overwrite | blocking | A draft whose `persona_id` already exists is refused - approved personas can never be overwritten by a draft. |

## Human reviewer checklist (per draft)

1. **Fictional?** The profile must not resemble a real child - no real names,
   ages tied to identity, real histories, or real settings.
2. **Visibly synthetic?** The summary says so; the UI labels the draft
   "NOT saved" until accepted.
3. **Respectful language?** Identity-first/neutral phrasing as appropriate;
   no functioning labels; strengths present, not deficit-only framing.
4. **Multidimensional support?** Communication, sensory, routine, and social
   dimensions described - not one global severity label.
5. **Representativeness?** The profile must not be presented as typical of
   autistic people generally.
6. **Diversity value?** Does the draft add meaningful variation to the
   approved set, or is it a near-duplicate?
7. **Decision.** Accept (saves a new record only), Revise (edit and re-lint),
   or Reject (draft discarded; nothing saved).

## Provenance of drafts

Drafts are ephemeral: `PersonaDraft` carries source ("ai"), creation time, and
lint flags, and is deliberately **not** persisted - the database stores only
approved personas. AI drafting uses the same AI boundary as S10 (Responses API,
`store=False`, strict validation; see `docs/ai_boundary.md`).

## Limitations

- The stereotype lint is a fixed keyword list; it cannot catch subtler
  stereotyping - that is exactly why the human gate exists.
- Near-duplicate detection is structural (support/modes/triggers equality),
  not semantic; a differently-worded but conceptually identical profile passes.
- Hand-written personas bypass the drafting UI (schema still enforces
  structure and `synthetic=True`); reviewers should apply the same checklist.
