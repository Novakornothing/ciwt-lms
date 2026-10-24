# Accessibility — WCAG 2.1 AA conformance notes (instructor guide)

Status: **Pending SME review** (internal audit; not a third-party VPAT). Last audit: automated axe-core 4.x at
390 px and 1280 px, light and dark themes, on the student lesson, ladder, lab, quiz and all instructor/admin
school-ready pages (`tools/launch_shots.py --axe`): 0 violations. Manual keyboard and screen-reader spot checks
(NVDA + Firefox, VoiceOver + Safari) on the lesson → quick check → explanation swap → next lesson flow.

| Area | What students get | What you can do |
|---|---|---|
| Keyboard | Every control is reachable with Tab; visible focus ring; skip link to main content; no keyboard traps (VM terminal releases focus with Esc then Tab). | Nothing to configure. |
| Landmarks & headings | `header`, `nav`, `main`, `footer` landmarks; one `h1` per page; sections use `h2`. | Keep headings in authored content in order. |
| Explanation swaps (ladder) | When a quick check is missed, the section is replaced in place and announced through an `aria-live="polite"` region; focus moves to the new explanation heading. The comprehension-gate banner is also a polite live region. | Turn the gate off or exempt a student (accommodation) on the Explanations page. |
| Contrast | Text and controls meet 4.5:1 (3:1 for large text and UI) in both light and dark themes. | — |
| Reduced motion | `prefers-reduced-motion` disables transitions and animated scrolling. | — |
| Text-to-speech | Lessons are plain HTML, so screen readers and browser read-aloud work; figures have text descriptions. | — |
| Captions | Videos (if added) must carry captions; the platform does not autoplay media. | Upload captioned video only. |
| Helix (webcam attention) | Strictly opt-in with consent; declining never affects grades or access. Non-visual alternative: the same optional review offers are available from the lesson menu without a camera. | Turn Helix off for the class in Attention settings. |
| VM labs | The terminal is a text surface readable by screen readers (`role="log"`, live output); every lab has typed commands only, no drag-and-drop required; lab hints are text. | Extend time (no lab is timed). |
| Forms | Every input has a visible label; errors are announced and linked to their field. | — |
| Zoom/reflow | Content reflows at 320 px / 400 % zoom with no horizontal scrolling (tables become stacked cards). | — |

Known limitations: third-party LMS frames (LTI launches) inherit the LMS's accessibility; diagram images in older
chapters rely on their text descriptions. Report a barrier: contact your instructor or the site administrator;
fixes are prioritised ahead of new features.
