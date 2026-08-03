import streamlit as st

st.title("Methods, Evidence Boundary, and Limitations")
st.markdown(
    """
## What the system can demonstrate

- A reproducible software workflow for structured persona, music, and response records.
- How prompt constraints and persona parameters change model-generated outputs.
- How to design a controlled synthetic trial matrix and visualize results.
- How to document uncertainty, provenance, and failure modes.

## What it cannot demonstrate

- A real autistic child's likely response.
- The effectiveness of music therapy or any specific song.
- Diagnosis, prognosis, treatment, or safety for an individual.
- Causal relationships between music parameters and clinical outcomes.

## Evidence hierarchy

1. Peer-reviewed systematic reviews and authoritative health sources.
2. The student's preregistered software experiment and test logs.
3. Model-generated synthetic outputs, labeled as such.
4. Interpretive discussion that never exceeds the evidence above.
"""
)
