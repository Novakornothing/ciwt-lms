# Novak LMS™ WebAssembly Toolchain, VM Emulation Layer & Open-Source License Audit

**Commercial Monetization & OEM Whitelabel Clearance Status:** **VERIFIED BUSINESS-SAFE (MIT / Apache 2.0 / BSD-2-Clause / BSD-3-Clause)**

All core Novak LMS™ intellectual property — including the 5-Path Adaptive Explanation Ladder Engine (`R0`–`R4`), Per-Objective Bayesian Knowledge Tracing (`mastery/`), Helix™ 30 Hz Browser-Local Gaze Telemetry & `OneEuro1D` / Ridge Calibration Engine (`static/js/helix/`), Interactive Ubuntu 24.04 GNOME 46 + Bash Split-View Workbenches (`labs_linux_gui.py`), Windows 11 GUI & Cisco IOS CLI Simulators (`interactive_labs.py`), 3-Tab Split-Pane PBQ Workbenches (`pbq-workbench.js`), SCORM 1.2/2004 & ADL xAPI Bridge (`scorm_xapi.py`), and all 860,000+ words of instructional curriculum — is **100% proprietary to Novak Learning** and free of any viral copyleft (GPL/AGPL) linkage.

---

## 1. WebAssembly Runtimes & Virtual Machine Emulation Layers

| Component / Artifact | Version | License | Commercial & Whitelabel Clearance |
|---|---|---|---|
| **v86 x86 WebAssembly Emulator** (`libv86.js`, `v86.wasm`) | `0.5.471` (`copy/v86`) | **BSD-2-Clause** | **100% Permissive.** Allows commercial monetization, proprietary modification, and OEM whitelabeling without disclosing Novak LMS™ proprietary source code. |
| **MediaPipe Tasks Vision / FaceLandmarker WASM** (`vision_wasm_internal.wasm`, `vision_bundle.mjs`, `face_landmarker.task`) | `1.1.1` (`@mediapipe/tasks-vision`) | **Apache-2.0** | **100% Permissive + Patent Grant.** Allows commercial distribution and whitelabeling with zero copyleft disclosure requirements. |
| **Helix™ Gaze Engine, `OneEuro1D` Filter & Clean-Room Fallback Shim** (`static/js/helix/*.js`, `static/vendor/webgazer.js`) | `2.0` | **Proprietary / MIT** | **100% Novak Learning IP / MIT.** Zero GPLv3 code exists in the JavaScript runtime. |
| **Interactive Ubuntu GNOME 46 GUI + Bash Workbenches, Win11 GUI & Cisco IOS CLI Engines** | `Wave 6` | **Proprietary (Novak Learning)** | **100% Proprietary.** Pure Python/JS state machines with zero external emulator dependencies. |

### Guest VM Disk Image Isolation Boundary (`novak-linux.bin` / `ciwt-linux.bin`)
For the 24 in-browser Linux VM labs, the **BSD-2-Clause `v86.wasm` hardware emulator** boots an unmodified guest disk image (`novak-linux.bin`, containing Linux kernel 6.8.12 and Alpine Linux v3.20 userland) as an isolated virtual block/RAM disk over an emulated x86 hardware boundary, communicating exclusively via standard serial console (`ttyS0`) character streams.
- **GPLv2 Section 2 "Mere Aggregation" Separation:** Under GPLv2 Section 2, an unmodified guest operating system image executed inside a BSD-2-Clause hardware emulator over a clean hardware virtualization boundary constitutes separate data ("mere aggregation") and does **not** form a derivative work of the host web application, WebAssembly emulator, or proprietary LMS backend.
- **Upstream Source Pointer:** Complete reproducible build recipes and upstream source URLs (kernel.org and Alpine Linux aports) are published in `static/vendor/v86/SOURCES.txt` and `tools/vm_image/build.sh`.
- **100% BSD/MIT/Proprietary Whitelabel Option:** Enterprise OEM whitelabel deployments may optionally disable the guest VM binary and run 100% on Novak LMS™'s proprietary Ubuntu GNOME GUI + Bash Split-View Workbenches (`labs_linux_gui.py`) and Linux Shell state engine (`labs_linux.py`) with zero GPL guest binaries distributed.

---

## 2. Frontend UI & Typography Libraries

| Component | Version | License | Commercial Clearance |
|---|---|---|---|
| **Bootstrap CSS & JS** (`static/vendor/bootstrap/5.3.3/`) | `5.3.3` | **MIT License** | Permissive commercial & whitelabel safe |
| **Bootstrap Icons** (`static/vendor/bootstrap-icons/1.11.3/`) | `1.11.3` | **MIT License** | Permissive commercial & whitelabel safe |
| **IBM Plex Sans, IBM Plex Mono & Orbitron Fonts** | `v1` | **SIL Open Font License 1.1** | Permissive commercial webfont bundling |

---

## 3. Python Server-Side Dependencies (`requirements.txt`)

| Package | License | Commercial Clearance |
|---|---|---|
| `Flask`, `Werkzeug`, `Jinja2`, `Click`, `Flask-SQLAlchemy`, `Flask-WTF` | **BSD-3-Clause** | Permissive commercial & whitelabel safe |
| `SQLAlchemy`, `Flask-Login`, `Flask-Compress`, `Gunicorn`, `PyJWT`, `python-docx` | **MIT License** | Permissive commercial & whitelabel safe |
| `cryptography` | **Apache-2.0 / BSD-3-Clause** | Permissive commercial & whitelabel safe |
| `ReportLab` | **BSD-3-Clause** | Permissive commercial & whitelabel safe |
| `lxml` | **BSD-3-Clause** | Permissive commercial & whitelabel safe |

## 4. Word list

| Component | Version | License | Notes |
|---|---|---|---|
| **SCOWL** (Spell Checker Oriented Word Lists), Kevin Atkinson, files `curriculum_sec/words/en_US.txt`, `curriculum_sec/words/security_allowlist.txt`, notice `curriculum_sec/words/SCOWL_COPYRIGHT.txt` | scowl-5 | **Permissive grant** | The collective work is copyright 2000-2011 by Kevin Atkinson. Permission to use, copy, modify, distribute, and sell the word lists, the associated scripts, their output, and the documentation for any purpose is granted without fee, provided the copyright notice appears in all copies and both the copyright notice and the permission notice appear in supporting documentation. It is provided as is. Component lists (including public-domain Moby Words II and Brian Kelk's UK English wordlist) keep the notices in `SCOWL_COPYRIGHT.txt`. |

The Windows simulation, the Cisco IOS-style console, and the network view in `static/js/sims/lab-stages.js` are original code in this repository. They do not add another third-party runtime. v86 remains BSD-2-Clause, listed above.
