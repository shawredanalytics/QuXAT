# JCI Validation Requirements

## Official JCI Sources
- Official JCI website: https://www.jointcommissioninternational.org/who-we-are/accredited-organizations/
- JCI accredited organizations finder: https://www.jointcommission.org/en/about-us/recognizing-excellence/find-accredited-international-organizations

## Current Issue
The system was automatically assigning JCI accreditation to organizations without proper validation from official JCI sources.

## Solution Implemented
1. Removed automatic JCI assignment logic in `enhance_certification_with_jci()` method
2. Removed fallback JCI check that assigned JCI without validation
3. System now only shows certifications from validated official sources

## Next Steps
- Verify JCI database contains only officially accredited organizations
- Update validation logic to use official certification agency websites
- Test system to ensure no simulated results are shown

## Note
Only organizations listed on the official JCI website should be considered JCI-accredited.