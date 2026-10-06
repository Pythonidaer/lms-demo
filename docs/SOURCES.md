# Source scope and coverage

Snapshot: 2026-10-06.

| Source | Pinned commit | Role |
| --- | --- | --- |
| [MDN content](https://github.com/mdn/content) | `5fd3b03e9ad1ee4e8bc64d4f6888570690a7fbc8` | JavaScript runtime foundations and browser data handling |
| [TypeScript Website](https://github.com/microsoft/TypeScript-Website) | `6556b08756b766fd41d0f887174cb0b042e5f72c` | TypeScript language, tooling and integration documentation |

MDN does not provide the comprehensive TypeScript language reference. The course therefore combines MDN foundations with the official TypeScript documentation. Content is reorganized and adapted into skills, not one lesson per page.

## Inventory

`source-inventory.json` inventories 297 English TypeScript documentation/TSConfig Markdown files and 1,342 English MDN JavaScript Guide/Reference paths and the selected network-requests learning page. The source catalog records links, source paths, available hashes/headings, related sections and coverage/review status. Unchecked-out MDN reference paths have no guessed public URL; their pinned GitHub source URL is retained.

| Status | Meaning |
| --- | --- |
| linked-source | Linked from a section; selected passages and topic outlines informed authoring |
| linked-feature-reference | A historical release note used for a particular modern feature |
| reference-only | Inventoried, optionally related to a subject area; no claim of full review or full lesson coverage |
| superseded-reference | Older Handbook material superseded by the current Handbook |
| historical-reference | Release history; not a required sequence of lessons |
| reference-navigation | TSConfig grouping/navigation content |

An inventory is **not a reviewed offline corpus or a RAG index**. No embeddings, model training, retrieval backend, document ingestion service or automatic source updater is included. Future RAG ingestion should retrieve the actual text at pinned commits, retain licensing/attribution, split at useful headings, preserve code context, and validate retrieval using real questions.

## Course mapping

| Sections | Main source areas |
| --- | --- |
| 01–02 | TypeScript Basics/tooling; MDN scope, functions, closures and operators |
| 03–04 | Everyday Types, inference, Object Types; MDN objects/collections |
| 05–06 | Narrowing, predicates, discriminated unions, never/exhaustiveness |
| 07–08 | More on Functions, Generics |
| 09–10 | keyof, typeof, indexed access, mapped/conditional/template literal types |
| 11–12 | Utility Types, Classes, compatibility, composition/mixins |
| 13–14 | Module theory/reference, host-specific configuration, TSConfig, build/watch/references |
| 15–16 | Declaration consumption/authoring/publishing, JSDoc, JavaScript checking/migration |
| 17–19 | MDN promises, DOM, specialized language/integration features, decorators and disposal |
| 20 | Applied validation, generics, domain modeling and verification |

Deep platform topics such as every RegExp construct, date/time API, internationalization operation, every built-in method, full framework tutorials and every TSConfig flag remain reference material. This course teaches the transferable TypeScript skills needed to understand those APIs; it does not claim line-by-line coverage of every website document.

## Technical baseline

Most runnable examples assume strict TypeScript checking, ES2022 and DOM declarations. The development compiler is pinned to 5.9.3. `NoInfer` requires TypeScript 5.4 or newer. Standard decorators use their modern model; legacy decorators are identified separately. Disposal examples require appropriate disposable declarations and runtime support. Multi-file examples are labeled; terminal/configuration/prose examples are not standalone `.ts` programs.

Source links may change after this snapshot. To rebuild the catalog against local upstream checkouts:

```sh
python3 scripts/inventory-sources.py /path/to/TypeScript-Website /path/to/mdn-content
```

Updating the catalog alone does not update lesson content. Review affected lessons and rerun checks before publishing a new course version.
