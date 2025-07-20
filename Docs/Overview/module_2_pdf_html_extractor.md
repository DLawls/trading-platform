# 📄 Module 2: PDF/HTML Data Extractor

## Purpose

Extract and structure data from unstructured or semi-structured documents relevant to financial markets.

This module supports ingestion from:

- Regulatory filings (e.g. ASX announcements, 10-K/10-Q)
- Broker research PDFs
- Financial news and analysis articles
- Government policy documents (e.g. budgets, regulations)

---

## Inputs

- **PDF Files** from ASX, EDGAR, broker portals
- **HTML Pages** from financial news or research portals
- **Raw text** (optional, if preprocessed elsewhere)

---

## Outputs

Structured data ready for downstream modules:

- Parsed tables (e.g. income statements, risk tables)
- Named Entity Recognition (companies, tickers, events)
- Paragraphs for NLP summarization or sentiment scoring
- Cleaned text for embedding generation or storage

---

## Functional Components

### 1. 🧾 PDF Extraction

- Use `pdfplumber`, `PyMuPDF`, or `pdfminer.six`
- Extract:
  - Full text
  - Tables (attempt structure retention)
  - Metadata (dates, tickers, title pages)

### 2. 🌐 HTML Extraction

- Use `BeautifulSoup`, `newspaper3k`, or `trafilatura`
- Extract:
  - Article content (remove ads, navbars)
  - Titles, timestamps
  - Author and source

### 3. 🧹 Cleaning & Normalization

- Normalize whitespace, encoding, broken tokens
- Remove boilerplate (e.g. "Page 3 of 5")
- Redact irrelevant sections if needed (legal disclaimers)

### 4. 🧠 Entity Extraction (Optional)

- Run `spaCy` or `flair` NER pipelines
- Identify company names, tickers, event types, dates
- Output as JSON records

### 5. 🧰 Optional Pre-NLP Staging

- Store extracted output to `.json`, `.txt`, or `.parquet`
- Tag by source, date, and doc type
- Save to shared volume or database for use by:
  - NLP summarizer
  - News/event signal generator
  - Embedding store

---

## Integration Points

✅ **Feeds Into:**

- NLP Summarizer (Module 4)
- News/Event Signal Generator (Module 3)
- Embedding Store (Module 5)

---

## Monetization Options

- Offer as an API service to parse financial documents
- Browser plugin or CLI tool for analysts and researchers
- Internal pipeline for institutional clients (compliance, research desks)

---

## Example Output Schema (JSON)

```json
{
  "source": "asx",
  "title": "Quarterly Activities Report",
  "ticker": "BHP",
  "date": "2025-04-15",
  "content": "... full cleaned text ...",
  "tables": [
    {
      "title": "Cash Flow Summary",
      "rows": [...]
    }
  ],
  "entities": {
    "companies": ["BHP Group"],
    "events": ["dividend announcement"],
    "dates": ["2025-04-15"]
  }
}
```

---

## Folder Structure

```
src/pdf_extractor_02/
├── extract_pdf.py
├── extract_html.py
├── clean_text.py
├── entity_recognition.py
├── run_pipeline.py
├── sample_outputs/
└── configs/
```

---

## Development Stack

- Python
- Libraries: `pdfplumber`, `trafilatura`, `spaCy`, `BeautifulSoup`, `pandas`, `json`

---

## Next Steps

-

