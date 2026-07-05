from html import escape
from typing import Iterable, Mapping, Sequence

import streamlit as st

PHONE_MAX_WIDTH = 720
TABLET_MAX_WIDTH = 1024
TOUCH_TARGET_PX = 44


RESPONSIVE_CSS = f"""
<style>
:root {{
  --v5-border: #d7dde6;
  --v5-muted: #526070;
  --v5-surface: #ffffff;
  --v5-soft: #f6f8fb;
  --v5-text: #18202a;
}}

.block-container {{
  max-width: 1180px;
  padding-top: 1rem;
  padding-bottom: 2rem;
}}

h1, h2, h3 {{
  letter-spacing: 0;
}}

div[data-baseweb="tab-list"] {{
  overflow-x: auto;
  gap: 0.25rem;
  scrollbar-width: thin;
}}

div[data-baseweb="tab"] {{
  min-height: {TOUCH_TARGET_PX}px;
  white-space: nowrap;
}}

div[role="radiogroup"] {{
  align-items: stretch;
  flex-wrap: wrap;
  gap: 0.35rem;
}}

.stButton button,
.stDownloadButton button,
button[kind="primary"],
button[kind="secondary"] {{
  min-height: {TOUCH_TARGET_PX}px;
}}

.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stSelectbox div[data-baseweb="select"],
.stTextArea textarea {{
  min-height: {TOUCH_TARGET_PX}px;
}}

.v5-records {{
  width: 100%;
  overflow-x: auto;
  margin: 0.25rem 0 1rem;
}}

.v5-table {{
  width: 100%;
  border-collapse: collapse;
  table-layout: auto;
  color: var(--v5-text);
  font-size: 0.92rem;
}}

.v5-table th,
.v5-table td {{
  border-bottom: 1px solid var(--v5-border);
  padding: 0.56rem 0.62rem;
  text-align: left;
  vertical-align: top;
  overflow-wrap: anywhere;
}}

.v5-table th {{
  background: var(--v5-soft);
  color: #273241;
  font-weight: 650;
}}

@media (max-width: {PHONE_MAX_WIDTH}px) {{
  .block-container {{
    padding: 0.75rem 0.75rem 1.25rem;
  }}

  h1 {{
    font-size: 1.45rem;
    line-height: 1.25;
  }}

  h2 {{
    font-size: 1.18rem;
  }}

  h3 {{
    font-size: 1.02rem;
  }}

  [data-testid="column"] {{
    width: 100% !important;
    flex: 1 1 100% !important;
    min-width: 100% !important;
  }}

  .v5-records {{
    overflow: visible;
  }}

  .v5-table,
  .v5-table tbody,
  .v5-table tr,
  .v5-table td {{
    display: block;
    width: 100%;
  }}

  .v5-table thead {{
    display: none;
  }}

  .v5-table tr {{
    background: var(--v5-surface);
    border: 1px solid var(--v5-border);
    border-radius: 8px;
    margin: 0 0 0.7rem;
    padding: 0.35rem;
  }}

  .v5-table td {{
    border-bottom: 0;
    display: grid;
    grid-template-columns: minmax(6.5rem, 42%) 1fr;
    gap: 0.55rem;
    padding: 0.46rem 0.4rem;
  }}

  .v5-table td::before {{
    color: var(--v5-muted);
    content: attr(data-label);
    font-weight: 650;
  }}
}}

@media (min-width: {PHONE_MAX_WIDTH + 1}px) and (max-width: {TABLET_MAX_WIDTH}px) {{
  .block-container {{
    max-width: 940px;
    padding-left: 1rem;
    padding-right: 1rem;
  }}

  .v5-table {{
    font-size: 0.9rem;
  }}
}}
</style>
"""


def inject_responsive_styles() -> None:
    st.markdown(RESPONSIVE_CSS, unsafe_allow_html=True)


def records_table_html(rows: Sequence[Mapping], columns: Iterable[str] | None = None) -> str:
    if not rows:
        return ""
    selected_columns = list(columns or rows[0].keys())
    header = "".join(f"<th>{escape(str(col))}</th>" for col in selected_columns)
    body_rows = []
    for row in rows:
        cells = []
        for col in selected_columns:
            value = row.get(col, "")
            label = escape(str(col))
            cells.append(f'<td data-label="{label}">{escape(str(value))}</td>')
        body_rows.append(f"<tr>{''.join(cells)}</tr>")
    return (
        '<div class="v5-records" role="region" aria-label="数据列表">'
        '<table class="v5-table">'
        f"<thead><tr>{header}</tr></thead>"
        f"<tbody>{''.join(body_rows)}</tbody>"
        "</table></div>"
    )


def render_records(rows: Sequence[Mapping], columns: Iterable[str] | None = None, empty_message: str = "暂无数据。") -> None:
    if not rows:
        st.info(empty_message)
        return
    st.markdown(records_table_html(rows, columns), unsafe_allow_html=True)

