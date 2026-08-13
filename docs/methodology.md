# Methodology

This document outlines the analytical methodology used by the Sri Lanka IT Talent Intelligence platform.

## Zero Fake Data Principle
The platform strictly adheres to a "live-data" requirement. No statistics, percentages, or KPI values are hardcoded or simulated. If data is unavailable, the UI gracefully displays an empty state or loading indicator.

## Metrics Calculation (Future)
- **Talent-to-Opportunity Ratio**: Will be calculated by comparing registered graduate supply with active job demand.
- **Skill Demand Percentage**: Computed by counting the occurrences of canonical skills across all active `JobContract` records divided by the total number of active jobs.

## Classification
Job classification will rely on a multi-feature approach:
- Job Title Keywords
- Extracted Skills
- Description NLP
- Company Context
This replaces simplistic title-only mapping.
