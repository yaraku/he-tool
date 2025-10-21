Proposed by: **ChatGPT (gpt-5-codex)**

Proposed on: **2025-10-21**

# Overview

This RFC proposes a comprehensive modernization of the Human Evaluation Tool frontend. The work spans four pillars: (1) upgrading the React/Vite stack and its dependencies to current LTS releases, (2) migrating the codebase to TypeScript with strict typings, (3) producing exhaustive product and technical documentation for the UI under `docs/frontend/` (with Mermaid diagrams) and an updated `frontend/README.md`, and (4) establishing a complete automated testing strategy with near-100% coverage using modern TypeScript/React testing tooling. The goal is to give the frontend parity with the recently overhauled backend in reliability, observability, and maintainability.

# Background

* **Technology drift:** The frontend still targets the 2023 stack (React 18.2, Vite 4, TanStack Query 4, etc.). Several direct and transitive dependencies are now two or more release trains behind, leaving us without security patches and access to current React Router and React Query APIs.
* **Lack of typings:** All components/hooks are JavaScript (`.jsx`/`.js`) with implicit `any`s. This makes regressions during refactors hard to catch and prevents editors/CI from providing actionable feedback.
* **Sparse documentation:** Aside from a high-level README, there is no narrative documentation that explains routing, state management, annotation workflows, results rendering (the MQM viewer), or how the React Query cache is structured. This makes onboarding new contributors difficult.
* **Testing gap:** There are no automated tests. Critical UI paths such as annotation marking, authentication redirects, and evaluation dashboards are unguarded. Service wrappers around `fetch` have no contract tests, so backend schema changes would go unnoticed until runtime failures.

# The What

1. **TypeScript adoption & project layout refinements**
   * Introduce a strict `tsconfig.json`, convert `vite.config.js` to `vite.config.ts`, and migrate `src/**/*.jsx`/`.js` files to `.tsx`/`.ts` with explicit interfaces/types (including API payload models and React Query hook generics).
   * Add ambient type definitions for global MQM viewer helpers (`mqmCreateViewer`, `mqmSetData`) and any other globals exposed by third-party scripts.
   * Create utility modules (e.g., `src/utils/marking.ts`) to extract pure logic currently embedded in UI components (selection validation, CSS class mapping) so they can be unit-tested independently.
   * Update linting/formatting configs to cover TypeScript (`@typescript-eslint/eslint-plugin`, `eslint-config-prettier`) and ensure Tailwind class sorting still works.

2. **Dependency and tooling upgrades**
   * Upgrade to the latest stable versions (checked at implementation time) of React, React DOM, TypeScript, Vite, React Router, TanStack Query 5, Tailwind CSS 4+, Bootstrap 5.3+, React Hot Toast, ESLint 9 (or latest 8.x LTS if 9 remains beta), Prettier, Sass, and PostCSS ecosystem packages.
   * Adopt Node.js 22 LTS (documented in `.nvmrc`/`package.json` `engines`) and ensure npm lockfile is regenerated.
   * Adjust source code for breaking changes (e.g., TanStack Query 5’s `QueryClient` defaults, `useMutation` return signatures, React Router API updates if any).

3. **Documentation deliverables**
   * Create a dedicated `docs/frontend/` directory containing:
     * `architecture.md` – high-level module overview with a Mermaid component diagram depicting routing (`App` → `ProtectedRoute` → feature pages) and how shared layout/components interact.
     * `data-flow.md` – sequence diagram(s) showing annotation fetching, marking creation/update/delete flows (user action → hook → service → backend → React Query cache update) and evaluation results hydration.
     * `state-management.md` – explanation of React Query cache keys, mutation lifecycle, and client state (Mermaid state diagram tying hooks and query keys).
     * `testing.md` – outlines the testing strategy, tooling, and a coverage matrix mapping modules to test types (unit/integration/contract) plus instructions to run coverage reports.
     * `ui-guide.md` – documents major UI components, accessibility considerations, Tailwind/Bootstrap interplay, and custom styling conventions.
     * `contributing.md` (frontend-specific) – describes development workflow, coding conventions, and how documentation/tests should be updated for new features.
   * Refresh `frontend/README.md` to align with the new stack, include setup steps, highlight documentation entry points, and cross-link diagrams.

4. **Testing strategy & coverage targets**
   * Introduce Vitest as the primary test runner (`vitest`, `@vitest/coverage-c8`) with jsdom environment, React Testing Library (`@testing-library/react`, `@testing-library/user-event`), and jest-dom matchers for assertions.
   * Use MSW (`msw`, `msw/node`) to mock backend endpoints consistently across service and component tests. Provide reusable handlers reflecting API contracts.
   * Establish coverage thresholds at 100% lines/branches/functions/statements for `src/`, with explicit exclusions for:
     * Third-party assets (`public/viewer.js`, compiled CSS/SCSS, `src/assets/**`).
     * Auto-generated enum data (e.g., `LanguageSelector` options) once validated via snapshot/spot checks.
   * Planned test suites:
     * **Routing & auth** – `App`, `ProtectedRoute`, `NavigationBar` using MemoryRouter and mocked `useAuth`/`useLogout` hooks to verify redirects and UI states.
     * **Annotation workflow** – `AnnotatePage`, `AnnotateInstance`, `Marking`, `MarkingItem`, `MarkingPopup`, and the associated hooks. Extracted pure utilities (selection validation, severity class mapping, overlap detection) will receive focused unit tests; interactive behavior will be covered with integration tests simulating user selections via Testing Library + `document.getSelection` mocks.
     * **Evaluation dashboard** – `EvaluationsPage`, `EvaluationDetailPage`, `ResultsPage` (with stubs for `mqmCreateViewer`/`mqmSetData`) ensuring toggles, checkbox mutations, and viewer integration behave correctly.
     * **Authentication forms** – `LoginForm`, `RegisterForm` to validate form validation logic, submission flows, and disabled states while asserting mutation side effects on the React Query cache.
     * **Service modules** – `api*.ts`, `utils.ts` tested with MSW to assert success and error branches, headers (CSRF token handling), and error messages; `clamp` and shuffle helpers covered via deterministic tests (seeded RNG ensures reproducibility).
     * **Supporting components** – `ClickOutsideListener`, selectors, spinners (snapshot/test IDs), `LanguageSelector` (ensuring default selection & total option count) to close coverage gaps.
   * Add `npm run test`, `npm run test:watch`, `npm run coverage` scripts and wire coverage output to CI (mirroring backend approach).

5. **Build & distribution adjustments**
   * Ensure Vite build outputs continue to land in `../public` but verify TypeScript/Vite 5 configuration handles path aliases, CSS/SCSS pipelines, and Tailwind JIT.
   * Document bundling of `public/viewer.js` (third-party MQM viewer) and consider wrapping it in an ES module shim with types to simplify imports.

# The How

1. **Baseline and preparation**
   * Audit current dependency versions vs. npm latest and gather release notes for breaking changes.
   * Introduce tooling prerequisites (`.nvmrc`, EditorConfig updates if needed).

2. **TypeScript migration**
   * Add TypeScript dependencies and configuration.
   * Incrementally rename files to `.tsx`/`.ts`, starting with services/utilities, then hooks, then components/pages. Introduce shared type definitions for API models (`frontend/src/types/api.ts`) and React Query data shapes.
   * Resolve type errors, create helper functions to reduce inline `any`s, and define module augmentation for `mqm` globals.

3. **Dependency upgrades**
   * Update package.json dependency ranges, regenerate lockfile, and adapt code to new APIs (TanStack Query 5, React Router updates, etc.).
   * Adjust Babel/TypeScript config as required by Vite 5, React 18.3+/19, or ESLint 9.

4. **Testing infrastructure**
   * Add Vitest config (`vitest.config.ts`), MSW setup (`src/test/server.ts`), and Testing Library utilities (`src/test/utils.tsx`).
   * Write tests module-by-module, prioritizing high-risk flows first (annotation interactions, authentication) and backfilling supporting components until coverage thresholds are met.
   * Ensure coverage reports exclude intended files via `coverage.include`/`coverage.exclude`.

5. **Documentation production**
   * Draft the new documents listed above, embedding Mermaid diagrams (`flowchart`, `sequence`, `stateDiagram`).
   * Update `frontend/README.md` with new sections: prerequisites, scripts, architecture summary, testing/coverage instructions, and documentation index.

6. **Verification**
   * Run `npm run lint`, `npm run test`, `npm run coverage`, `npm run build`, and `npm run preview` to validate the upgraded stack.
   * Manual QA of key flows (auth, annotation, evaluation management, results viewer) in dev and preview builds.

# The Why

* **Reliability:** Strict typing and full coverage drastically lower the risk of regressions, especially when backend contracts evolve.
* **Maintainability:** Updated docs, modularized utilities, and modernized dependencies help future contributors navigate and extend the UI quickly.
* **Security & compliance:** Staying on supported versions of React, Vite, Tailwind, and Node ensures we receive security patches and remain compliant with corporate security baselines.
* **Developer experience:** TypeScript tooling, MSW-powered tests, and clear docs shorten feedback loops and reduce onboarding friction.

# The Benefits

* Predictable builds and consistent local environments due to Node LTS alignment and refreshed tooling.
* Higher confidence in releases through comprehensive automated tests and coverage enforcement.
* Easier onboarding thanks to rich, diagram-backed documentation describing data flow and state management.
* Safer refactors enabled by TypeScript typings and extracted pure utilities.
* Reduced runtime errors from outdated dependencies or API mismatches.

# The Concerns

* **Migration complexity:** Converting the entire codebase to TypeScript and upgrading TanStack Query/React Router may surface subtle runtime changes that need careful QA.
* **MQM viewer integration:** The third-party `viewer.js` script relies on globals; wrapping it in TypeScript without altering its behavior requires cautious shimming and may limit testability.
* **Annotation selection testing:** Simulating `window.getSelection()` across browsers/test environments is non-trivial. We will need reliable mocks to avoid flakiness.
* **Time investment:** Achieving 100% coverage—including interactive annotation flows—will require significant effort to design meaningful tests and refactor code for testability.

# Additional notes, links

* Prior backend overhaul RFC (`docs/rfcs/0001-backend-quality-overhaul.md`) will be used as a stylistic/process reference to keep parity across the codebase.
* Candidate tooling references for execution phase:
  * TanStack Query v5 migration guide
  * React Router latest changelog
  * Vite 5 migration guide
  * MSW + Vitest integration examples
* We will preserve GPL headers and existing code comments during migrations to respect licensing requirements.
