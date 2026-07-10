# AUIB Financial Performance Portal v3.1.0 — Regression Test Report

**Automated interaction checks passed: 185**  
**Failed: 0**

Coverage:

- Initial application load
- Every navigation page
- Every College selection
- Every slider individually at minimum, maximum and restored baseline
- Every new-intake input at 0, 3,000 and restored baseline
- All sliders and inputs simultaneously at maximum
- All sliders and inputs simultaneously at minimum
- Every page under both extreme scenarios
- Every College under both extreme scenarios
- Repeated tuition changes in one session
- Repeated College switching in one session
- Reset to workbook baseline and value verification
- Internal teaching allocation reconciliation
- College Contribution recalculation
- University result bridge
- Local Streamlit server startup and HTTP 200 response
- Python syntax compilation

Visual consistency controls:

- App-wide primary interactive colour set to AUIB Navy `#17365D`
- Additional CSS fallback applies navy to every Streamlit slider handle and active track
- Crimson retained only for headings and section accents
- Deprecated Streamlit width arguments removed

No scenario preset buttons remain. They were removed because they created fragile widget-state interactions in earlier versions.
