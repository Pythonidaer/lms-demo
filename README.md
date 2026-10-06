# TypeScript skills course

Live site: https://pythonidaer.github.io/lms-demo/

20 sections · 40 lessons · 200 slides · 20 section quizzes (60 questions) · 20-question final assessment.

A skills-based course for learners who can already read basic JavaScript. It covers runtime foundations, everyday types, objects, narrowing, state modeling, functions, generics, type operators, advanced transformations, utility types, classes, modules, compiler configuration, declarations, migration, async/browser code, specialized features, decorators/disposal, and a catalog capstone.

Run `python3 -m http.server 8000` in this folder and open http://localhost:8000. The deployed course needs no install, build step, backend, AI service, or external fonts. Lessons and quizzes work from the bundled files; source links need connectivity. The embedded JSON also permits opening `index.html` directly, subject to browser storage/download policies.

Each lesson has a goal, explanation, example, practice task, worked solution and takeaway. Read all five slides before marking a lesson complete. Lessons and quizzes are freely accessible by default, matching Design Lab. Turn off “Unlock all lessons and quizzes” in learner settings for sequential progression. Pass the section quiz with 80% and complete its lessons to unlock the Markdown study-guide download. The guide includes takeaways, examples, exercises, solutions, learner notes and source links. Retakes are allowed. With sequential progression enabled, the final quiz unlocks after all 60 lesson/quiz items are complete.

## Editing and validation

The authored content lives in `scripts/build-course.py`. Run `python3 scripts/build-course.py` to regenerate both `course.json` and the embedded JSON in `index.html`. Keep IDs stable; changed lesson content invalidates completion for that lesson. The new course ID keeps starter-course progress separate.

```sh
npm ci
npm test
```

Development checks use pinned TypeScript 5.9.3. They compile runnable lesson examples independently under strict checking, compile the capstone including negative type tests, test malformed catalog input, verify export contents, and check that embedded and standalone course data match. Newer documentation is inventoried separately; the course does not claim to teach every compiler-version change.

Optional UI checks need Playwright (`npm install --no-save playwright`, then `npx playwright install chromium`) and a running local server:

```sh
npm run test:browser
```

These checks traverse the full course, exercise failed quizzes and retakes, download a guide, complete the final assessment, verify persistence and invalidation, and inspect layout at 390/768/1440px.

## Sources and scope

MDN documents the JavaScript foundation; the official TypeScript documentation supplies TypeScript-specific material. This course adapts concepts into original explanations and examples rather than copying website pages. See `docs/SOURCES.md` and `docs/source-inventory.json` for attribution, pinned source commits, and explicit coverage statuses. The inventory includes 1,639 documentation paths; it does **not** mean every document was read in full or turned into a lesson. Historical, superseded and specialized reference pages remain reference material.

This is a complete core skills path, not an exhaustive reproduction of MDN, every TSConfig option, every integration recipe, or every historical release note. Raw documentation ingestion and a RAG assistant are future work, not features supplied here.

Reports and learner settings are browser-local. No authentication, server, cloud dashboard, SCORM/xAPI integration or verified grading is included. Correct answers are in the client. Clearing browser data clears progress. Quiz attempts are not exam-secure.

Coding exercises are self-assessed; use the capstone rubric and tests to verify practical work. Completion is not certification. Source attribution is retained in downloadable guides; see `docs/ATTRIBUTION.md`.

## Design Lab visual and report update

The shared learner UI follows Design Lab commit `274cb3a`: compact flat outline rows, lighter navigation icons, completion checks, persistent section collapse, optional lesson metadata, and dedicated learner settings. The TypeScript code formatting, sources, notes and completion-gated study-guide exports remain intact.

Reports fill the learner column, with a compact interactive pie beside skill grade bars on desktop and stacked charts on mobile. Each section quiz maps to its section skill; the final quiz maps to integrated TypeScript judgment. Average quiz grade uses the best score of each submitted quiz, including failed scores. Skill grades average submitted quizzes in their group. Unattempted quizzes do not affect averages; skills at the course passing score count as learned. These are quiz-based indicators, not verification of practical coding mastery.

Unattempted skill bars are hidden until selected. Reports initially show actual learner results, including an honest empty state. The optional, clearly labeled sample report and its CSV never modify progress. Report tables and CSVs list quizzes, skills, attempts and best scores, without time columns. Presentation-only skill label changes preserve existing quiz completion and scores.
