"""ElevenLabs-style CSS layer (S22): typography, chrome, spacing, rounding.

Injected ONCE from ``app.py`` (never from page modules) so the 312-test suite
- which AppTests page files directly - is structurally unaffected. ALL colors
come from ``.streamlit/config.toml`` (``[theme.light]`` / ``[theme.dark]``
achromatic palettes; the browser's Light/Dark/System setting selects which
one Streamlit applies), so this layer is deliberately mode-agnostic: shapes,
radii, spacing, and typography only. Cosmetic only - the global sidebar
disclaimer and every caption/label stay exactly as they were, and the
settings menu stays visible so visitors can switch theme modes.
"""

from __future__ import annotations

import streamlit as st

_CSS = """
<style>
/* ---------- typography: Inter-first system stack, tighter headings ---- */
html, body, [class*="st-"] {
    font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI",
        system-ui, Roboto, "Helvetica Neue", Arial, sans-serif;
}
h1, h2, h3, h4, h5, h6 {
    letter-spacing: -0.02em;
    font-weight: 600;
}
[data-testid="stCaptionContainer"] {
    letter-spacing: 0.01em;
}

/* ---------- chrome: hide the footer, keep the settings menu ------------ */
footer {visibility: hidden;}
[data-testid="stHeader"] {background: transparent;}

/* ---------- buttons: pill shape, subtle press/hover feedback ----------- */
.stButton > button, .stDownloadButton > button {
    border-radius: 999px;
    font-weight: 500;
    letter-spacing: -0.01em;
    transition: opacity 120ms ease, transform 120ms ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    opacity: 0.85;
}
.stButton > button:active, .stDownloadButton > button:active {
    transform: scale(0.985);
}

/* ---------- cards / containers: soft rounding -------------------------- */
[data-testid="stExpander"] details,
[data-testid="stMetric"],
[data-testid="stAlert"],
[data-testid="stAudio"],
[data-testid="stDataFrame"] {
    border-radius: 14px;
}

/* ---------- sidebar: hairline divider (neutral, works in both modes) --- */
[data-testid="stSidebar"] {
    border-right: 1px solid rgba(128, 128, 128, 0.22);
}

/* ---------- breathing room: generous but bounded ------------------------ */
.block-container {
    padding-top: 2.2rem;
    max-width: 1200px;
}
</style>
"""


def apply_theme() -> None:
    """Inject the cosmetic CSS layer. Call once from app.py after
    ``st.set_page_config``. Never hides or alters disclaimers, labels, or
    widget keys - the frozen claims boundary is untouched."""
    st.markdown(_CSS, unsafe_allow_html=True)
