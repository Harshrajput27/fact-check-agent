# Fact-Check Agent

Upload a text-based PDF to extract a small set of factual claims, search the
live web, and receive a sourced fact-check report with a CSV download.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Free Gemini setup

1. Create a Google AI Studio API key at <https://aistudio.google.com/api-keys>.
2. Enter it in the app's **Google AI Studio API key** field.
3. Upload a PDF and run the fact-check.

The app uses `gemini-3.5-flash-lite` on Google's free tier, subject to availability
and rate limits. It sends one model request per PDF, limits extraction to 10
claims by default, and uses free DuckDuckGo search. Free-tier usage has Google's
own data terms; avoid uploading confidential documents.

To configure the key locally instead of entering it in the UI, add this to
`.streamlit/secrets.toml`:

```toml
GOOGLE_API_KEY = "your-key"
```

## Limits

- Scanned/image-only PDFs are not supported (OCR is not included).
- A maximum of 10 claims are checked by default.
- Search results may be incomplete; review sources and low-confidence verdicts.
- Google AI Studio free-tier availability and quotas can change.
