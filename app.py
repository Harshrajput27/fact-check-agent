import datetime
import os

import pandas as pd
import streamlit as st

from pipeline import ModelError, PDFError, run


MODEL = "gemini-3.5-flash-lite"

st.set_page_config(page_title="Fact-Check Agent", page_icon="🔎", layout="wide")
st.title("🔎 Fact-Check Agent")
st.caption(
    "Upload a PDF to extract key factual claims, search the live web, "
    "and check all claims in one model call."
)

with st.sidebar:
    st.header("Settings")
    try:
        saved_key = st.secrets.get("GOOGLE_API_KEY", "")
    except Exception:
        saved_key = ""
    entered_key = st.text_input(
        "Google AI Studio API key",
        type="password",
        key="google_api_key_input",
        help="Google AI Studio offers a free tier with usage limits.",
    )
    api_key = entered_key.strip() or saved_key.strip() or os.getenv("GOOGLE_API_KEY", "").strip()
    if api_key:
        st.caption(f"Gemini free-tier model: {MODEL}")
    max_claims = st.slider("Maximum claims", 3, 20, 10)
    st.info("One Gemini call per PDF. Web search and PDF extraction are free.")
    st.caption("Free-tier quotas apply. Google may use free-tier content to improve its products.")

uploaded = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded and st.button("Run fact-check", type="primary"):
    if not api_key:
        st.error("Enter a Google AI Studio API key in the sidebar.")
        st.stop()

    progress = st.progress(0.0, text="Reading PDF and checking claims...")
    try:
        rows = run(
            uploaded,
            {"GOOGLE_API_KEY": api_key, "GOOGLE_MODEL": MODEL},
            progress=lambda done, total: progress.progress(
                done / total,
                text=f"Preparing results: {done} of {total}",
            ),
            max_claims=max_claims,
        )
    except PDFError as exc:
        progress.empty()
        st.warning(str(exc))
        st.stop()
    except ModelError as exc:
        progress.empty()
        st.error(str(exc))
        st.stop()
    except Exception as exc:
        progress.empty()
        st.error("The fact-check could not be completed.")
        st.caption(f"{type(exc).__name__}: {exc}")
        st.stop()

    progress.empty()
    if not rows:
        st.info("No checkable numeric or date-based claims were found.")
        st.stop()

    st.session_state["rows"] = rows
    st.session_state["checked"] = datetime.date.today().isoformat()

rows = st.session_state.get("rows")
if rows:
    dataframe = pd.DataFrame(rows)
    counts = dataframe["verdict"].value_counts()
    st.subheader(
        f"{len(dataframe)} claims: "
        f"{counts.get('Verified', 0)} verified, "
        f"{counts.get('Inaccurate', 0)} inaccurate, "
        f"{counts.get('False', 0)} false"
    )
    st.caption(
        f"Checked on {st.session_state['checked']}. "
        "Review low-confidence findings against their linked sources."
    )
    display = dataframe.rename(columns={
        "page": "Page",
        "claim": "Claim",
        "verdict": "Verdict",
        "confidence": "Confidence",
        "correct_fact": "Correct fact",
        "reason": "Reason",
        "source": "Source",
    })
    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        column_config={"Source": st.column_config.LinkColumn("Source")},
    )
    st.download_button(
        "Download report (CSV)",
        display.to_csv(index=False),
        "factcheck_report.csv",
        "text/csv",
    )
