# Logged-in UX audit

Audited 2026-10-30 against the running demo (`student1@lms.local` / `student123`, `instructor@lms.local` / `teach123`, `admin@lms.local` / `admin123`). Screenshots of each main page at 1440×900 and 390×844 were taken before the rebuild. Decisions below are what the rebuild did. Nothing in this list was deleted: every cut is one click deeper, or merged into a plainer label.

## What was wrong

The same destinations showed up three times: a top bar (account, sections, sign out, role switch), a left tree with nested disclosures, and in-page tabs or chip bars. Student home repeated Course Chapters, Hands-On Labs, and Practice under the continue card. Instructor home put the full roster and a per-class button stack behind tabs. Admin home was four stat cards plus a “go to” wall, and every admin page repeated Overview / Users & Sections / Exports / More tools.

## Shell (all three roles)

| Item | Where it was | Decision |
| --- | --- | --- |
| Brand | Top bar | Keep |
| Search (Cmd-K) | Top bar | Keep. Escape hatch for anything moved deeper |
| Account, search and settings toggler | Top bar | Cut. Replaced by one avatar menu |
| Name and role chip | Top bar | Merged into the avatar menu |
| Sections dropdown (`#secSwitch`) | Top bar | Cut. Classes is the switcher |
| Admin mode / Instructor mode | Top bar | Moved into the avatar menu |
| Account link | Top bar and sidebar foot | Merged into the avatar menu |
| Sign out | Top bar and sidebar foot | Merged into the avatar menu |
| Dark mode | Top bar | Moved into the avatar menu |
| Teaching timer bar | Second row under the top bar | Moved into the avatar menu. Start, stop, class, and break reminder are unchanged |
| Sidebar trees (Learn, Practice, Help, Teach, Inbox, Reports, System, Classes, and the per-class “More tools” nest) | Left rail | Cut as a tree. Replaced by 6 flat items per role |
| Sidebar foot (Account, Sign out) | Left rail | Merged into the avatar menu |
| Mobile tab “Menu” | Bottom bar (5th item) | Cut. Four tabs only. Items that do not fit are in the avatar menu on small screens |
| Lab / lesson menu button | Top bar, forced visible on those routes | Keep. Those pages hide the rail; the button still opens it |
| Logged-in marketing footer (specs, ROI, consult, pilot) | Footer | Cut from the app. Those pages stay on the public site and, for ROI, under Admin → Reports |
| Lesson reader right rail and mobile sheet | Lesson page | Keep. Not part of this nav |

### New top-level nav

Student (sidebar): Home, Course Chapters, Hands-On Labs, Practice, Grades, Eye Tracking. Mobile tabs: Home, Course, Labs, Practice.

Instructor: Home, Classes, Grades, Practice, Reports, Help Desk Queue. Mobile tabs: Home, Classes, Grades, Reports.

Admin: Home, People, Courses, Reports, Settings, Help Desk Queue. Mobile tabs: Home, People, Courses, Settings.

Avatar menu (every role): name, Account, Help (messages, contact, and the role’s queue when it is not already a tab), Dark mode, Sign out. Admins also get the mode switch. The teaching timer sits here for instructors.

## Student

Home answered “what do I do next?” only after a tab wall.

| Item | Decision |
| --- | --- |
| Continue card and its one button | Keep |
| Path progress on that card | Keep |
| Course pills (one per enrolled course) | Keep |
| Daily Review line under the continue card | Merged into a Daily Review card |
| Course Chapters tab and the chapter list with an Open button per chapter | Cut from home. The list is the Course Chapters page |
| Hands-On Labs tab, eight labs, “All labs”, “Every lab (114)” | Cut from home. Next lab is one card. The full list is Hands-On Labs |
| Practice Exams tab (Practice Exams, Speed-Drill, Skill Mastery) | Cut from home. One Practice card. The exams are the Practice page |
| Per-class links inside the old Practice disclosure (Windows CLI, GUI, switch, router, convening, A-school, pilot, C-school) | Cut from the sidebar. Search and the labs catalog still open them |
| Ask instructor, curriculum tickets, search, eye-tracking policy | Help Desk Queue, Messages, and Contact live in the avatar Help menu. Search stays in the top bar |
| Course page button row (All labs, Practice Exams, Speed-Drill, My grades, Course tools drawer) | Cut. One Continue button. Skip What You Know, My plan, What helps you learn, Syllabus, and Practice are text links |

## Instructor

Home answered “who needs help?” only on the first of three tabs, then a roster and a button stack.

| Item | Decision |
| --- | --- |
| Students Needing Help list | Keep on home |
| Class pass rate | Keep, inside one Class progress summary |
| Today’s briefing links | Merged into the needs-help list when a briefing has work |
| Students & Grades tab, filter, roster table, Export CSV | Moved to Students (one click from home) |
| Labs & Assignments tab (Assignments / Labs / Practice Exams per class) | Cut from home. Open the class |
| Sidebar class tree (gradebook, eye tracking, labs, results, tutor, outcomes, mastery, briefing, explanations, syllabus, course stats) repeated per class | Cut from the sidebar. The class page links Eye Tracking, Skill Mastery, Today’s briefing, Skills scores, Syllabus, LMS connection, and the pilot run sheet. Gradebook is the one primary button |
| Class page header buttons and “More tools & setup” drawer | Cut. Same destinations, as links, not a drawer |
| Sections hub button row (Setup, Roster, Clone) | Merged. Setup and Roster are links. Clone stays the one button |

## Admin

| Item | Decision |
| --- | --- |
| Four stat cards (seats, instructors, Exam Readiness, lab savings) | Merged. Home keeps seats and people counts, plus the course list. Exam Readiness and savings are on Reports |
| “Go to” cards (Users & Sections, Exports, More tools) | Cut. Those are People, Settings, and Reports |
| Chip bar on every admin page | Cut |
| Users / Sections sub-chips | Cut. People is users. Courses is classes |
| More tools list (curriculum, ROI, outcomes, LTI, privacy, tickets, teaching time, analytics, health) | Split. Reports holds outcomes, results, savings, teaching time, test analytics, and the score hub. Settings holds exports (cmi5, xAPI, SCORM), branding, integrations, privacy, FERPA, audit, security, health, backup, demo guide, and platform architecture. Course contents is linked from Courses |
| Help Desk Queue | Own nav item. Was “Tickets” / “Curriculum tickets” |
| Setup checklist | New on home, and hidden once every item is done |
| Old `#admin-class` bookmarks | Keep. Home still forwards them |

## Counts

| | Cut from the surface | Merged | Relocated one click deeper |
| --- | ---: | ---: | ---: |
| Shared chrome | 8 (sections menu, top account, top sign-out, role chip, top mode switch, sidebar foot pair, mobile Menu, marketing footer) | 3 (account, sign-out, and dark mode into one avatar menu) | 2 (teaching timer, mode switch) |
| Student | 3 home tabs and the chapter / lab / exam lists on home; the Practice disclosure (8 track links); the course-page button row and tools drawer | 1 (Daily Review line into a card) | 8 (chapters, labs catalog, practice exams, speed drill, skill mastery, tickets, messages, policy) |
| Instructor | 2 home tabs, the per-class 3-button row, the class-page 5-button row and tools drawer, the per-class sidebar nest | 2 (briefing into the help list; Setup/Roster into links) | 4 (full roster, gradebook detail, reports, class tools) |
| Admin | 4-up stat wall, 3 hub cards, the chip bar, the Users/Sections chips | 2 (seats and courses into two home regions) | 16 tool pages now under Reports or Settings |

No route was removed. Cmd-K still searches lessons, labs, and commands.
