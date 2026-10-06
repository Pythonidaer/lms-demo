# Capstone: typed learning catalog

Try implementing this yourself before reading `catalog.ts`.

Acceptance criteria:

- Validate `unknown`; reject null, non-arrays, missing or blank IDs/titles, non-finite and negative minutes, and duplicate IDs.
- Accept an empty catalog and zero-minute lessons.
- Return a discriminated success/error result. Handle both branches exhaustively.
- Construct public outputs explicitly rather than trusting assertions or retaining extra fields.
- Preserve generic property/result relationships and return `undefined` for an absent lookup.
- Rename without mutating the original input; reject blank replacement titles.
- Verify invalid property names fail static checking and malformed inputs fail at runtime.

Run the project checks from the repository root:

```sh
npm ci
npm test
```

The LMS tracks self-confirmed practice completion and multiple-choice results. It does not execute submitted code, authenticate learners, or certify mastery.
