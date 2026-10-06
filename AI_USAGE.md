# AI Usage

## Tool Used

* **Claude (Anthropic)** was used during development for debugging, troubleshooting, code review, and resolving implementation issues.

## How AI Was Used

AI assistance was used selectively during development for:

* Debugging Python errors
* Reviewing parts of the scraping implementation
* Troubleshooting pagination and scraping issues
* Reviewing data cleaning and validation logic
* Checking test failures and improving test coverage
* Understanding and resolving implementation issues
* Reviewing project documentation

The project was implemented, tested, and reviewed manually. AI was not used as a replacement for understanding or verifying the implementation.

## Representative Prompts

Examples of prompts used during development:

1. "Help me debug this Python error and explain why it is occurring."
2. "Review this scraping logic and identify any issues."
3. "Help me understand why this test is failing."
4. "Review the data cleaning and validation logic for possible edge cases."

## Changes After AI Review

AI suggestions were reviewed before being applied. Changes were made manually where necessary based on the actual project requirements, test results, and live scraper behavior.

Examples included:

* Simplifying overly complicated code.
* Fixing implementation issues identified during testing.
* Adjusting scraping behavior after checking the actual website structure.
* Improving logging and error reporting.
* Reviewing duplicate-detection behavior against the actual scraped data.

## Problems Found During Review

Some AI-generated suggestions required modification or correction after testing.

The implementation was always verified against the assignment requirements and actual test/live-run results before being accepted.

## Testing and Verification

The project was tested using:

```text
python -m pytest
```

Result:

```text
20 passed
```

A complete live run was also performed:

* Books to Scrape: 1,000 records
* Quotes to Scrape: 100 records
* Raw records: 1,100
* Final records: 1,099
* Reconciliation: True

The final implementation was verified for:

* Pagination
* Data cleaning
* Data validation
* Duplicate detection
* Error handling
* CSV generation
* JSON summary generation
* Logging
* Record-count reconciliation
