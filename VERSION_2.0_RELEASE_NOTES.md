QuXAT Healthcare Quality Grid — Version 2.0 Release Notes

Date: 2025-10-02

Summary
- JCI made a mandatory hospital accreditation within the QuXAT scoring model.
- UI now explicitly displays JCI as mandatory in the Mandatory Requirements section.
- Equivalency added: U.S. Joint Commission (TJC) recognized as a JCI-equivalent for hospital accreditation.
- Penalty surfaced in UI using the scoring breakdown’s category penalty (default 10 points) when JCI/TJC is missing.
- Verified live in local app; visual warnings and penalty details render reliably.

Key Changes
- streamlit_app.py: Enabled JCI mandatory card with detection for “JCI”, “JOINT COMMISSION INTERNATIONAL”, and non-international “JOINT COMMISSION” as equivalency.
- Mandatory penalties and compliance summaries now align with JCI visibility.

Deployment
- Version metadata updated to 2.0.0.
- Prepared for GitHub backup and Streamlit Cloud deployment via CI.

Notes
- CAP mandatory logic retained; ISO mandatory banner continues to display separately.
- If your organization’s certification naming is unconventional, normalization may be needed.