# Claim Ledger

Maps every planned **background claim** the project makes to one or more real sources in `docs/evidence_table.csv`, and states how each claim is bounded. No claim here is a clinical efficacy, diagnostic, or treatment claim, and no citation or result is invented. Source IDs refer to `docs/evidence_table.csv`.

| Claim ID | Background claim | Source(s) | How the claim is bounded |
|---|---|---|---|
| C1 | Music therapy for autistic people has been studied systematically, but the evidence is uncertain across outcomes. | S2 (Cochrane, music therapy) | The simulator makes **no** therapeutic-effectiveness claim for its synthetic outputs; it describes synthetic hypotheses only. |
| C2 | Sound-based interventions are a distinct evidence base from music therapy. | S3 (Cochrane, sound-based interventions) | The project does not deliver or evaluate any sound-based intervention; music parameters are simulation inputs. |
| C3 | Autism is heterogeneous and support needs are multidimensional; a single functioning-level label is inadequate. | S1 (NIMH), S6 (ASAN) | The five personas are fictional and explicitly synthetic; they are not representative of the autistic population. |
| C4 | Use identity-first, respectful, non-deficit language. | S6 (ASAN), plus the project's ethics framing | This is a language choice, not a clinical or scientific claim. |
| C5 | The project adopts Respect for persons, Beneficence, Justice, and Transparency. | S4 (Belmont Report) | Adopted voluntarily; no human subjects are involved (synthetic personas only). |
| C6 | The project's AI-use posture follows transparency and accountability principles. | S5 (UNESCO AI ethics) | A posture statement, not a compliance certification. |
| C7 | The optional AI engine uses the OpenAI Responses API with Pydantic structured outputs and `store=False`. | S7 (OpenAI docs) | Technical basis only; the configured model id must be verified before AI mode is enabled. |
| C8 | The interface uses Streamlit's multipage architecture and secrets handling. | S8 (Streamlit docs) | Technical basis only; not a research finding. |

## Rules

- Every public background statement should trace to a row here; if a claim has no source, it must be removed or reframed as a project decision (not an evidence claim).
- Quantitative results (sample sizes, effect sizes, certainty ratings, deep-link URLs) that are not verified are recorded as "verify before public release" in `docs/evidence_table.csv`; they must not be stated as fact.
- This ledger is a student educational review aid, not a systematic review, and does not establish clinical effectiveness.
