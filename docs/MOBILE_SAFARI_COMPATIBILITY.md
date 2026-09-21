# Mobile Safari compatibility

On 21 September 2026, an external iPhone test showed repeated `TypeError: Importing a module script failed` messages for the dashboard's metrics and charts. The server and Python application were healthy; the failure occurred in dynamically loaded browser-side JavaScript modules. Render had installed Streamlit 1.64.0 because the dependency range allowed any version below 2.0.

Streamlit's maintainers documented a mobile Safari compatibility boundary after Streamlit 1.46.0 introduced a frontend dependency that uses JavaScript regular-expression lookbehind. Safari added lookbehind support in version 16.4, so older iPhones can render the Streamlit shell and text while failing on lazy-loaded widgets. The repository now pins Streamlit 1.45.1, the final release before 1.46.0, and constrains pandas below 3.0 for that Streamlit version.

The pinned dependency set was installed in a clean virtual environment. Six unit tests passed, Python compilation passed, and `pip check` reported no broken requirements. A privacy-safe Streamlit 1.45.1 preview returned a healthy status and rendered the title, all four tabs, four KPI cards, the Plotly conversion chart, reconciliation note, and data-limitations section without a frontend error.

Evidence: Streamlit community report `https://discuss.streamlit.io/t/streamlit-update-mobile-browser-issues/115909`; Streamlit browser support policy `https://docs.streamlit.io/knowledge-base/using-streamlit/supported-browsers`.
The compatibility preview's Risk Overview tab rendered all four KPI cards, the fraud-rate bar chart and event-mix donut. The Top 5 tab rendered the priority table, stacked component chart, five case expanders, challenger table and CSV download. These tests cover the widget categories that failed in the external iPhone screenshot.
