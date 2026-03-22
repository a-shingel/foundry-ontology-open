# Human Services Eligibility Case Study

Government benefits eligibility domain (aligned with Cúram expertise):

- **Object Types**: Client, Case, Benefit, EligibilityDetermination, Evidence
- **Link Types**: Client→Cases, Case→Benefits, Case→Evidence
- **Action Types**: SubmitApplication, DetermineEligibility, ApproveBenefit, DenyBenefit
- **Validation**: ApproveBenefit requires evidence, income threshold
