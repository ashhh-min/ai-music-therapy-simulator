# AI Boundary

Unit: S10 (2026-08-20). Implementation: `src/ai_music_therapy/ai_client.py`.
Tests: `tests/test_ai_client.py` (all mocked - no live calls in automated tests).

## What the AI client is allowed to do

The optional AI engine generates **synthetic reaction hypotheses** for fictional
personas. It is a content generator for an educational software prototype. It is
not a diagnostic tool, a therapy recommender, or a source of clinical evidence.

## Hard boundary rules (enforced in code)

1. **No key, no problem.** Without `OPENAI_API_KEY` the client raises immediately
   (before any network access) and the application stays in deterministic mode,
   which needs no key. Default operation never requires a key.
2. **Validation before use.** Every AI response must parse as JSON and validate
   as `ReactionOutput` (Pydantic, `extra="forbid"`, strict ranges) before it can
   be used or persisted. Invalid output is rejected - never clamped, coerced into
   range, or partially saved.
3. **Storage disabled.** The request uses the OpenAI **Responses API** with
   `store=False`. Responses API state is not retained provider-side by request.
4. **System prompt boundary.** The system prompt forbids claims about real
   children, diagnosis, treatment prescription, and therapeutic effectiveness;
   requires respectful neurodiversity language; and requires treating the persona
   as fictional. The requested object is enumerated field-by-field so the model
   returns exactly the schema.
5. **Provenance.** Callers record `engine="openai"`, the configured model name,
   and the prompt version in every `TrialRecord` (`seed` stays `None` for AI
   output - it is not reproducible, and we do not pretend otherwise).

## Provider compatibility (observed 2026-08-20)

- The current `.env.local` targets a Volcano Ark endpoint
  (`OPENAI_BASE_URL=.../api/plan/v3`, `OPENAI_MODEL=ark-code-latest`).
  Observed: `POST /responses` returns 200 - this provider **does** support the
  Responses API, so `store=False` structured requests work directly.
- The earlier GLM setup from D014 (`open.bigmodel.cn/api/paas/v4/...`) exposed
  only `/chat/completions`; with that provider this client will fail. Use a
  Responses-API-compatible endpoint, or switch to deterministic mode.
- Live end-to-end verification (one real call, 2026-08-20): structured output
  validated, `start/middle/end` stages complete, `synthetic=True`. Evidence:
  `evidence/S10/check_outputs.txt`.

## Provider drift handling (sanitizer + retry)

OpenAI-compatible providers do not all enforce JSON schemas server-side.
Observed drift: extra top-level keys, a bare string where a list is expected,
time stages returned out of order. The client therefore:

1. requests JSON mode (`text={"format": {"type": "json_object"}}`);
2. sanitizes only semantically-neutral shape drift: unknown keys dropped
   (including per-stage), a bare string wrapped into a one-element list,
   `start/middle/end` reordered into canonical order;
3. validates with full strictness - out-of-range scores, wrong types, and
   missing required fields still raise;
4. on any parse/validation failure, retries **once** with the validation
   errors fed back to the model, then rejects with `RuntimeError`.

The sanitizer never "repairs" a value that would change meaning: a score of 12
is rejected, not clamped to 10 (guarded by test).

## Limitations (be able to state one)

- AI output is **not reproducible**: no seed, and the model may return different
  scores for identical inputs on different calls. Deterministic mode is the
  reproducibility guarantee; AI mode is for qualitative comparison only
  (see `docs/preregistration.md`).
- `store=False` is a request to the provider; it cannot be independently
  verified from the client. The project still sends no real person's data, so
  the privacy exposure is zero regardless.
- One retry means transient provider errors still surface as failures; there is
  no exponential backoff (acceptable for a single-user demo; revisit with the
  S18 pooling hardening).
- The sanitizer's drift list is based on observed behavior of one provider;
  another provider could invent new drift shapes that get rejected.
