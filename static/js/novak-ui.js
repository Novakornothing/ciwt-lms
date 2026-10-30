/* Site-wide UI behaviour (pass 6): back buttons, inline form validation, submit feedback.
   Progressive enhancement only: every form still works without this file. */
(function () {
  'use strict';

  // form[data-confirm]: one confirm() for destructive actions (text comes from an escaped attribute, never inline JS)
  document.addEventListener('submit', function (e) {
    var f = e.target;
    if (f && f.matches && f.matches('form[data-confirm]') && !window.confirm(f.getAttribute('data-confirm'))) {
      e.preventDefault(); e.stopImmediatePropagation();
    }
  }, true);

  // [data-history-back]: go back if there is somewhere to go, else home
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-history-back]');
    if (!b) return;
    e.preventDefault();
    if (history.length > 1 && document.referrer && document.referrer.indexOf(location.origin) === 0) history.back();
    else location.href = '/';
  });

  // ---- inline validation: native constraint checks, shown next to the field instead of browser bubbles
  function feedbackFor(el) {
    var id = (el.id || el.name || 'f') + '-err';
    var fb = el.form && el.form.querySelector('[data-auto-feedback="' + id + '"]');
    if (!fb) {
      fb = document.createElement('div');
      fb.className = 'invalid-feedback'; fb.setAttribute('data-auto-feedback', id); fb.id = id.replace(/[^\w-]/g, '_');
      var anchor = el.closest('.input-group') || el;
      anchor.parentNode.insertBefore(fb, anchor.nextSibling);
      var d = el.getAttribute('aria-describedby');
      el.setAttribute('aria-describedby', (d ? d + ' ' : '') + fb.id);
    }
    return fb;
  }
  function message(el) {
    var v = el.validity, label = (el.labels && el.labels[0] && el.labels[0].textContent.trim()) || el.getAttribute('aria-label') || 'This field';
    label = label.replace(/\s*\*$/, '').replace(/\s*\(optional\)$/i, '');
    if (v.valueMissing) return (el.tagName === 'SELECT' ? 'Choose ' : 'Enter ') + label.charAt(0).toLowerCase() + label.slice(1) + '.';
    if (v.typeMismatch && el.type === 'email') return 'Enter an email address like name@example.com.';
    if (v.tooShort) return 'Use at least ' + el.minLength + ' characters.';
    if (v.tooLong) return 'Use at most ' + el.maxLength + ' characters.';
    if (v.rangeUnderflow) return 'Use ' + el.min + ' or more.';
    if (v.rangeOverflow) return 'Use ' + el.max + ' or less.';
    if (v.patternMismatch) return el.getAttribute('data-pattern-msg') || el.title || 'Check the format.';
    return el.validationMessage;
  }
  function check(el) {
    if (!el.willValidate) return true;
    var ok = el.checkValidity();
    el.classList.toggle('is-invalid', !ok);
    el.setAttribute('aria-invalid', ok ? 'false' : 'true');
    if (!ok) feedbackFor(el).textContent = message(el);
    else { var fb = el.form && el.form.querySelector('[data-auto-feedback="' + (el.id || el.name || 'f') + '-err"]'); if (fb) fb.textContent = ''; }
    return ok;
  }
  function enhance(form) {
    if (form.hasAttribute('data-no-enhance') || form.__novak) return;
    form.__novak = true;
    form.setAttribute('novalidate', '');
    form.addEventListener('submit', function (e) {
      var bad = null;
      Array.prototype.forEach.call(form.elements, function (el) { if (!check(el) && !bad) bad = el; });
      if (bad) {
        e.preventDefault(); e.stopImmediatePropagation();
        bad.focus();
        return;
      }
      busy(form, e.submitter, e);
    }, true);
    form.addEventListener('input', function (e) { if (e.target.classList && e.target.classList.contains('is-invalid')) check(e.target); });
    form.addEventListener('change', function (e) { if (e.target.classList && e.target.classList.contains('is-invalid')) check(e.target); });
  }

  // ---- submit feedback: one click = one submission; the button shows progress
  function busy(form, btn, ev) {
    btn = btn || form.querySelector('button[type=submit], button:not([type]), input[type=submit]');
    if (!btn || form.hasAttribute('data-no-busy') || form.target === '_blank') return;
    if (/\.csv|export|download/i.test(form.action || '')) return;      // downloads never navigate away
    setTimeout(function () {    // after other submit handlers (confirm() etc.) and after the browser read the submitter
      if (ev && ev.defaultPrevented) return;
      form.setAttribute('aria-busy', 'true');
      btn.disabled = true; btn.classList.add('is-busy');
      if (btn.tagName === 'BUTTON' && !btn.querySelector('.spinner-border')) btn.insertAdjacentHTML('afterbegin', '<span class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>');
    }, 0);
  }
  window.addEventListener('pageshow', function () {                   // back/forward cache: re-enable
    document.querySelectorAll('.is-busy').forEach(function (b) { b.disabled = false; b.classList.remove('is-busy'); var s = b.querySelector('.spinner-border'); if (s) s.remove(); });
    document.querySelectorAll('form[aria-busy]').forEach(function (f) { f.removeAttribute('aria-busy'); });
  });

  // Sideways-scrolling chip/tab rows: bring the current item into view; drop the edge fade once scrolled to the end
  function initScrollers() {
    document.querySelectorAll('.chip-scroll').forEach(function (row) {
      var cur = row.querySelector('[aria-current="page"], [aria-current="true"]');
      if (cur && row.scrollWidth > row.clientWidth) {
        row.scrollLeft = Math.max(0, cur.offsetLeft - (row.clientWidth - cur.offsetWidth) / 2);
      }
      var edge = function () { row.classList.toggle('at-end', row.scrollLeft + row.clientWidth >= row.scrollWidth - 2); };
      edge(); row.addEventListener('scroll', edge, { passive: true });
    });
  }

  function init() {
    document.querySelectorAll('form[method=post], form[method=POST], form.needs-validation').forEach(enhance);
    initScrollers();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

/* =====================================================================
   Novak LMS™ Curriculum UX (Progress Bar, Step-by-Step Focus Mode,
   Blueprint Progressive Disclosure) & Instant Smart Search Autocomplete
   ===================================================================== */
(function () {
  'use strict';

  function initCurriculumUX() {
    var lessonBody = document.getElementById('lessonBody');
    var progressBar = document.getElementById('novakLessonProgressBar');
    var workspace = document.getElementById('novakLessonWorkspace') || document.querySelector('.novak-lesson-workspace');
    if (!lessonBody || !progressBar) return;

    var progressFill = document.getElementById('lessonProgressFill');
    var currentSecNum = document.getElementById('currentSecNum');
    var stepDots = Array.prototype.slice.call(document.querySelectorAll('.novak-step-dot'));
    var focusToggleBtn = document.getElementById('toggle-focus-mode');
    var focusModeLabel = document.getElementById('focusModeLabel');
    var focusNavBar = document.getElementById('focusModeNavBar');
    var focusPrevBtn = document.getElementById('focusPrevSection');
    var focusNextBtn = document.getElementById('focusNextSection');
    var focusStepCounter = document.getElementById('focusStepCounter');

    // Collect section blocks (.novak-section-card or section.sublesson)
    function getSectionBlocks() {
      var cards = Array.prototype.slice.call(lessonBody.querySelectorAll('.novak-section-card'));
      if (cards.length) return cards;
      return Array.prototype.slice.call(lessonBody.querySelectorAll('section.sublesson'));
    }

    // Group sections into 4 Cohesive Concept Steps (by data-step-group, or chunked into 4 groups)
    function getStepGroups() {
      var blocks = getSectionBlocks();
      if (!blocks.length) return [];
      var groupsMap = {};
      var groupKeys = [];
      var hasExplicitGroups = blocks[0].hasAttribute('data-step-group');
      blocks.forEach(function (b, idx) {
        var g = hasExplicitGroups ? (parseInt(b.getAttribute('data-step-group'), 10) || 1) : (Math.min(4, Math.floor((idx * 4) / blocks.length) + 1));
        if (!groupsMap[g]) {
          groupsMap[g] = [];
          groupKeys.push(g);
        }
        groupsMap[g].push(b);
      });
      groupKeys.sort(function (a, b) { return a - b; });
      return groupKeys.map(function (k) { return groupsMap[k]; });
    }

    // 1. Streamline <aside class="novak-visual-blueprint"> & <article class="novak-boot-deep-dive">
    //    so the SVG diagram is visible while reference tables/watchouts sit in a clean collapsible drawer
    var blueprint = lessonBody.querySelector('aside.novak-visual-blueprint');
    if (blueprint && !blueprint.hasAttribute('data-ux-enhanced')) {
      blueprint.setAttribute('data-ux-enhanced', '1');
      if (!blueprint.querySelector('details.novak-spec-drawer')) {
        var specWrap = blueprint.querySelector('.novak-spec-table-wrap');
        var watchout = blueprint.querySelector('details.novak-field-watchout');
        if (specWrap) {
          var drawer = document.createElement('details');
          drawer.className = 'novak-spec-drawer';
          var sum = document.createElement('summary');
          sum.className = 'novak-spec-drawer-summary';
          sum.innerHTML = '<i class="bi bi-table me-1" aria-hidden="true"></i><strong>Technical Specification Table &amp; Field Watchout</strong> <span class="novak-spec-drawer-hint">Expand 5-row spec reference &amp; field watchout ▾</span>';
          var bodyDiv = document.createElement('div');
          bodyDiv.className = 'novak-spec-drawer-body pt-2';
          specWrap.parentNode.insertBefore(drawer, specWrap);
          bodyDiv.appendChild(specWrap);
          if (watchout) {
            watchout.setAttribute('open', '');
            bodyDiv.appendChild(watchout);
          }
          drawer.appendChild(sum);
          drawer.appendChild(bodyDiv);
        }
      }
    }

    Array.prototype.slice.call(lessonBody.querySelectorAll('article.novak-boot-deep-dive')).forEach(function (art) {
      if (art.hasAttribute('data-ux-enhanced')) return;
      art.setAttribute('data-ux-enhanced', '1');
      var bootFig = art.querySelector('figure.novak-boot-svg-figure');
      if (!bootFig) return;
      var rest = [];
      var sib = bootFig.nextElementSibling;
      while (sib) {
        rest.push(sib);
        sib = sib.nextElementSibling;
      }
      if (rest.length) {
        var bDrawer = document.createElement('details');
        bDrawer.className = 'novak-spec-drawer mt-2';
        var bSum = document.createElement('summary');
        bSum.className = 'novak-spec-drawer-summary';
        bSum.innerHTML = '<i class="bi bi-cpu me-1" aria-hidden="true"></i><strong>6-Stage Boot Pipeline Deep-Dive Table, Fault Codes &amp; WinRE/GRUB Recovery Commands</strong> <span class="novak-spec-drawer-hint">Click to expand full reference ▾</span>';
        var bBody = document.createElement('div');
        bBody.className = 'novak-spec-drawer-body pt-2';
        rest.forEach(function (el) { bBody.appendChild(el); });
        bDrawer.appendChild(bSum);
        bDrawer.appendChild(bBody);
        art.appendChild(bDrawer);
      }
    });

    // 2. Guided Step Flow (Default ON: 4 Cohesive Concept Steps per lesson, each showing 3-5 sub-sections + inline visuals + 1 Milestone Check)
    var activeIdx = 0;
    var focusMode = true;

    // If URL hash points to a specific section, open on the Concept Step containing that section
    var initGroups = getStepGroups();
    if (location.hash && initGroups.length) {
      var hashId = location.hash.slice(1);
      for (var gi = 0; gi < initGroups.length; gi++) {
        for (var bi = 0; bi < initGroups[gi].length; bi++) {
          var b = initGroups[gi][bi];
          var bSid = b.getAttribute('data-ladder-sid') || '';
          if (b.id === hashId || ('ladder-sec-' + bSid) === hashId || ('ladder-sub-' + bSid) === hashId) {
            activeIdx = gi;
            break;
          }
        }
      }
    }

    function updateFocusView() {
      var groups = getStepGroups();
      if (!groups.length) return;
      var totalSteps = groups.length;
      activeIdx = Math.max(0, Math.min(totalSteps - 1, activeIdx));
      if (workspace) workspace.classList.toggle('focus-mode-active', focusMode);
      lessonBody.classList.toggle('novak-focus-mode-active', focusMode);
      groups.forEach(function (grp, gIdx) {
        var hide = focusMode && gIdx !== activeIdx;
        grp.forEach(function (b) {
          b.classList.toggle('novak-step-hidden', hide);
        });
      });

      if (blueprint) {
        blueprint.classList.toggle('d-none', focusMode && activeIdx !== 0);
      }

      // Show inline visual figures on their corresponding steps (Step 2 -> fig 0, Step 3 -> fig 1, Step 4 -> fig 2)
      var inlineFigs = Array.prototype.slice.call(lessonBody.querySelectorAll('figure.novak-inline-visual'));
      inlineFigs.forEach(function (fig, fIdx) {
        var targetStep = Math.min(totalSteps - 1, fIdx + 1);
        fig.classList.toggle('d-none', focusMode && activeIdx !== targetStep);
      });

      var bootArticles = Array.prototype.slice.call(lessonBody.querySelectorAll('article.novak-boot-deep-dive'));
      bootArticles.forEach(function (art, aIdx) {
        var targetStep = Math.min(totalSteps - 1, aIdx + 1);
        art.classList.toggle('d-none', focusMode && activeIdx !== targetStep);
      });

      var labSec = document.getElementById('chapter-lab');
      var gateSec = document.getElementById('ladderGate');
      var quickSec = document.getElementById('mxQuick');
      var onLastStep = activeIdx >= totalSteps - 1;
      if (labSec) labSec.classList.toggle('d-none', focusMode && !onLastStep);
      if (gateSec) gateSec.classList.toggle('d-none', focusMode && !onLastStep);
      if (quickSec) quickSec.classList.toggle('d-none', focusMode && !onLastStep);

      stepDots.forEach(function (d, idx) {
        d.classList.toggle('is-active', idx === activeIdx);
      });
      if (currentSecNum) currentSecNum.textContent = String(activeIdx + 1);
      if (focusStepCounter) focusStepCounter.textContent = 'Step ' + (activeIdx + 1) + ' of ' + totalSteps;
      if (focusPrevBtn) focusPrevBtn.disabled = activeIdx <= 0;
      if (focusNextBtn) focusNextBtn.disabled = activeIdx >= totalSteps - 1;
      if (focusToggleBtn) {
        focusToggleBtn.classList.toggle('is-active', focusMode);
        focusToggleBtn.setAttribute('data-focus-mode', focusMode ? 'on' : 'off');
        focusToggleBtn.setAttribute('aria-pressed', focusMode ? 'true' : 'false');
      }
      if (focusModeLabel) {
        focusModeLabel.textContent = focusMode ? 'Show All Sections' : 'Guided Step View';
      }
      if (focusNavBar) {
        focusNavBar.classList.toggle('d-none', !focusMode || totalSteps <= 1);
      }
      if (focusMode && progressFill) {
        var pct = Math.round(((activeIdx + 1) / totalSteps) * 100);
        progressFill.style.width = pct + '%';
        progressFill.setAttribute('aria-valuenow', String(pct));
      }
      emitStep();
    }

    function emitStep() {
      var g = getStepGroups();
      document.dispatchEvent(new CustomEvent('novak:lesson-step', { detail: {
        idx: activeIdx, total: g.length, focus: focusMode,
        pct: progressFill ? parseInt(progressFill.style.width, 10) || 0 : 0 } }));
    }

    function onScrollProgress() {
      if (focusMode) return;
      var rect = lessonBody.getBoundingClientRect();
      var viewH = window.innerHeight || document.documentElement.clientHeight;
      var totalScroll = Math.max(1, lessonBody.offsetHeight - viewH * 0.5);
      var scrolled = Math.max(0, -rect.top + viewH * 0.25);
      var pct = Math.max(5, Math.min(100, Math.round((scrolled / totalScroll) * 100)));
      if (progressFill) {
        progressFill.style.width = pct + '%';
        progressFill.setAttribute('aria-valuenow', String(pct));
      }
      var groups = getStepGroups();
      if (groups.length) {
        var found = 0;
        for (var i = 0; i < groups.length; i++) {
          var firstCard = groups[i][0];
          if (firstCard) {
            var br = firstCard.getBoundingClientRect();
            if (br.top <= viewH * 0.45) found = i;
          }
        }
        activeIdx = found;
        if (currentSecNum) currentSecNum.textContent = String(activeIdx + 1);
        stepDots.forEach(function (d, idx) {
          d.classList.toggle('is-active', idx === activeIdx);
        });
      }
      emitStep();
    }

    window.addEventListener('scroll', onScrollProgress, { passive: true });
    updateFocusView();

    document.addEventListener('ladder:updated', function () {
      updateFocusView();
    });

    // 3. Guided Step Mode / Show All Sections Toggle
    if (focusToggleBtn) {
      focusToggleBtn.addEventListener('click', function () {
        focusMode = !focusMode;
        updateFocusView();
        if (!focusMode) onScrollProgress();
      });
    }

    if (focusPrevBtn) {
      focusPrevBtn.addEventListener('click', function () {
        if (activeIdx > 0) {
          activeIdx--;
          updateFocusView();
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }
      });
    }
    if (focusNextBtn) {
      focusNextBtn.addEventListener('click', function () {
        var groups = getStepGroups();
        if (activeIdx < groups.length - 1) {
          activeIdx++;
          updateFocusView();
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }
      });
    }

    // Intercept "Next section ↓" chip clicks inside Guided Step mode:
    // scroll to the next sub-card within the current step, or advance to the next step only after the step milestone card
    document.addEventListener('click', function (e) {
      var chip = e.target.closest && e.target.closest('[data-continue]');
      if (!chip || !focusMode) return;
      var card = chip.closest ? chip.closest('.novak-section-card') : null;
      var groups = getStepGroups();
      var curGrp = groups[activeIdx] || [];
      var posInGrp = card ? curGrp.indexOf(card) : -1;
      if (posInGrp >= 0 && posInGrp < curGrp.length - 1) {
        e.preventDefault();
        e.stopImmediatePropagation();
        var nextCard = curGrp[posInGrp + 1];
        if (nextCard && nextCard.scrollIntoView) {
          nextCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        return;
      }
      if (activeIdx < groups.length - 1) {
        e.preventDefault();
        e.stopImmediatePropagation();
        activeIdx++;
        updateFocusView();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    }, true);

    stepDots.forEach(function (dot) {
      dot.addEventListener('click', function (e) {
        var idx = parseInt(dot.getAttribute('data-section-jump'), 10);
        if (isNaN(idx)) return;
        activeIdx = idx;
        if (focusMode) {
          e.preventDefault();
          updateFocusView();
          window.scrollTo({ top: 0, behavior: 'smooth' });
        } else {
          stepDots.forEach(function (d, i) { d.classList.toggle('is-active', i === idx); });
          if (currentSecNum) currentSecNum.textContent = String(idx + 1);
        }
      });
    });

    // Phase 1: small API for the lesson rail / bottom sheet
    window.novakLessonNav = {
      groups: getStepGroups,
      isFocus: function () { return focusMode; },
      go: function (i) {
        activeIdx = i;
        if (focusMode) {
          updateFocusView();
          lessonBody.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
          var g = getStepGroups()[i];
          if (g && g[0]) g[0].scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      },
      toggleAll: function () { if (focusToggleBtn) focusToggleBtn.click(); },
      toLab: function () {
        var g = getStepGroups();
        if (focusMode && g.length) { activeIdx = g.length - 1; updateFocusView(); }
        var lab = document.getElementById('chapter-lab');
        if (lab) setTimeout(function () { lab.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, 30);
      },
      refresh: emitStep
    };

    // Swapping explanations changes section heights. Pin the section at the top of the viewport
    // (by its stable data-ladder-sid, since swapped boxes are replaced) and hold it there.
    var keeper = null;
    // Layout top, ignoring the swap animation's translateY so the reader is held where the box will settle.
    function layoutTop(el) {
      var top = el.getBoundingClientRect().top;
      var t = window.getComputedStyle(el).transform;
      if (t && t !== 'none') {
        var m = t.match(/matrix(3d)?\(([^)]+)\)/);
        if (m) { var v = m[2].split(','); top -= parseFloat(v[m[1] ? 13 : 5]) || 0; }
      }
      return top;
    }
    function readerAnchor() {
      var top = 0;
      var tl = document.querySelector('.lesson-topline');
      if (tl) top = Math.max(0, tl.getBoundingClientRect().bottom);
      var boxes = lessonBody.querySelectorAll('[data-ladder-sid]');
      for (var i = 0; i < boxes.length; i++) {
        var r = boxes[i].getBoundingClientRect();
        if (r.height && r.bottom > top + 1) return { sid: boxes[i].getAttribute('data-ladder-sid'), top: layoutTop(boxes[i]) };
      }
      return null;
    }
    function restoreAnchor() {
      if (!keeper) return;
      var el = lessonBody.querySelector('[data-ladder-sid="' + keeper.sid + '"]');
      if (!el) return;
      var d = layoutTop(el) - keeper.top;
      if (Math.abs(d) >= 0.5) window.scrollBy({ top: d, left: 0, behavior: 'instant' });
    }
    function keepReaderInPlace() {
      var a = readerAnchor();
      if (!a) return null;
      if (keeper && keeper.timer) clearTimeout(keeper.timer);
      keeper = a;
      keeper.pending = 0;
      // Hold the spot until every queued swap lands (slow networks) or the reader scrolls on their own.
      var stop = function () { if (keeper === a) keeper = null; window.removeEventListener('wheel', stop); window.removeEventListener('touchstart', stop); window.removeEventListener('keydown', stop); };
      a.stop = stop;
      window.addEventListener('wheel', stop, { passive: true });
      window.addEventListener('touchstart', stop, { passive: true });
      window.addEventListener('keydown', stop);
      keeper.timer = setTimeout(stop, 20000);
      if (window.ResizeObserver && !lessonBody._novakRO) {
        lessonBody._novakRO = new ResizeObserver(function () { restoreAnchor(); });
        lessonBody._novakRO.observe(lessonBody);
      }
    }
    document.addEventListener('ladder:updated', function () {
      restoreAnchor();
      requestAnimationFrame(restoreAnchor);
      setTimeout(restoreAnchor, 420);
      if (keeper && keeper.pending > 0) {
        keeper.pending -= 1;
        if (keeper.pending === 0) { var k = keeper; clearTimeout(k.timer); k.timer = setTimeout(k.stop, 1500); }
      }
    });

    // 4b. Step-Level Learning Style Switcher (#novakStepStyleBar)
    var stepStyleBar = document.getElementById('novakStepStyleBar');
    if (stepStyleBar) {
      var styleBtns = Array.prototype.slice.call(stepStyleBar.querySelectorAll('[data-step-rung]'));
      styleBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
          var rung = btn.getAttribute('data-step-rung') || 'R0';
          styleBtns.forEach(function (b) {
            var act = b === btn;
            b.classList.toggle('is-active', act);
            b.setAttribute('aria-pressed', act ? 'true' : 'false');
          });
          var groups = getStepGroups();
          var targetCards = (focusMode && groups[activeIdx]) ? groups[activeIdx] : getSectionBlocks();
          var anchor = keepReaderInPlace();
          // Swap the section in view first, then the ones below it, then the ones above.
          var order = targetCards.slice();
          var ai = -1;
          order.forEach(function (c, i) { if (ai < 0 && anchor && (c.getAttribute('data-ladder-sid') === anchor.sid || c.querySelector('[data-ladder-sid="' + anchor.sid + '"]'))) ai = i; });
          if (ai > 0) order = order.slice(ai).concat(order.slice(0, ai).reverse());
          var queued = 0;
          order.forEach(function (card) {
            var box = card.hasAttribute('data-ladder-sid') ? card : card.querySelector('[data-ladder-sid]');
            if (!box || box.getAttribute('data-shown') === rung) return;
            var pill = box.querySelector('.novak-rung-pill[data-rung-pick="' + rung + '"]');
            if (pill) {
              box.setAttribute('data-swap-quiet', '1');
              setTimeout(function () { pill.click(); }, queued * 45);
              queued += 1;
            }
          });
          if (keeper) keeper.pending = queued;
        });
      });
    }

    // 5. Windows Boot Process Streamlined Summary Mode button
    var bootBtn = document.getElementById('toggleBootConciseBtn');
    if (bootBtn) {
      bootBtn.addEventListener('click', function () {
        var concise = bootBtn.getAttribute('aria-pressed') !== 'true';
        bootBtn.setAttribute('aria-pressed', concise ? 'true' : 'false');
        bootBtn.textContent = concise ? 'Show Full Lesson Prose' : 'Streamlined Exam Summary Mode';
        lessonBody.querySelectorAll('section.sublesson.depth, .worked, .scenario-box').forEach(function (el) {
          el.classList.toggle('d-none', concise);
        });
      });
    }
  }

  // 5. Live Instant Smart Search Autocomplete Dropdown in Navbar
  function initInstantSearch() {
    var input = document.getElementById('curricSearch');
    var dropdown = document.getElementById('globalSearchDropdown');
    if (!input || !dropdown) return;
    var form = input.closest('form');
    var apiUrl = (form && form.getAttribute('data-api-search')) || '/api/search';
    var timer = null;
    var activeItemIdx = -1;

    function closeDropdown() {
      dropdown.classList.add('d-none');
      dropdown.innerHTML = '';
      activeItemIdx = -1;
    }

    function esc(s) {
      var d = document.createElement('div');
      d.textContent = s || '';
      return d.innerHTML;
    }

    function cardHtml(c) {
      if (!c) return '';
      var prac = (c.practice || []).map(function (p, i) {
        return '<a class="novak-search-item novak-cmd-practice" role="option" data-search-idx="c' + i + '" href="' + esc(p.url) + '"><span class="badge text-bg-secondary me-1">' + esc(p.kind) + '</span>' + esc(p.title) + '</a>';
      }).join('');
      return '<div class="novak-cmd-card" data-command-card="' + esc(c.key) + '">' +
        '<div class="d-flex justify-content-between align-items-baseline gap-2"><strong class="novak-cmd-name"><code>' + esc(c.command) + '</code></strong><span class="small text-muted">' + esc(c.platform) + '</span></div>' +
        '<div class="small mt-1">' + esc(c.what) + '</div>' +
        '<div class="novak-cmd-syntax"><code>' + esc(c.syntax) + '</code></div>' +
        '<div class="small text-muted">Example: <code>' + esc(c.example) + '</code></div>' +
        (prac ? '<div class="novak-search-cat mt-2">Practice it</div>' + prac : '') +
        '</div>';
    }

    function renderDropdown(data) {
      var results = (data && data.results) || [];
      var card = cardHtml(data && data.command_card);
      if (!results.length && card) {
        dropdown.innerHTML = card;
        dropdown.classList.remove('d-none');
        activeItemIdx = -1;
        return;
      }
      if (!results.length) {
        dropdown.innerHTML = '<div class="p-2 small text-muted">No instant matches for “' + esc(data.query) + '”. Press Enter for full search.</div>';
        dropdown.classList.remove('d-none');
        return;
      }
      var html = [];
      if (card) html.push(card);
      if (data.did_you_mean && data.did_you_mean.toLowerCase() !== (data.query || '').toLowerCase()) {
        html.push('<div class="novak-search-cat">Showing smart match: <strong>' + esc(data.did_you_mean) + '</strong></div>');
      }
      var topItems = results.slice(0, 8);
      topItems.forEach(function (r, idx) {
        html.push(
          '<a class="novak-search-item" role="option" data-search-idx="' + idx + '" href="' + esc(r.url) + '">' +
          '<div class="d-flex justify-content-between align-items-center gap-2">' +
          '<strong class="text-truncate">' + esc(r.title) + '</strong>' +
          '<span class="badge text-bg-secondary">' + esc(r.kind) + '</span>' +
          '</div>' +
          '<div class="small text-muted text-truncate">' + esc(r.course) + (r.chapter ? ' · ' + esc(r.chapter) : '') + '</div>' +
          '</a>'
        );
      });
      dropdown.innerHTML = html.join('');
      dropdown.classList.remove('d-none');
      activeItemIdx = -1;
    }

    document.addEventListener('keydown', function (e) {
      if ((e.metaKey || e.ctrlKey) && (e.key === 'k' || e.key === 'K')) {
        e.preventDefault();
        input.focus();
        input.select();
      }
    });

    input.addEventListener('input', function () {
      var q = (input.value || '').trim();
      if (timer) clearTimeout(timer);
      if (q.length < 2) {
        closeDropdown();
        return;
      }
      timer = setTimeout(function () {
        fetch(apiUrl + '?q=' + encodeURIComponent(q), { headers: { 'Accept': 'application/json' } })
          .then(function (r) { return r.ok ? r.json() : null; })
          .then(function (data) { if (data && data.ok) renderDropdown(data); })
          .catch(function () {});
      }, 160);
    });

    input.addEventListener('keydown', function (e) {
      if (dropdown.classList.contains('d-none')) return;
      var items = Array.prototype.slice.call(dropdown.querySelectorAll('.novak-search-item'));
      if (!items.length) return;
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        activeItemIdx = (activeItemIdx + 1) % items.length;
        items.forEach(function (el, i) { el.classList.toggle('is-active', i === activeItemIdx); });
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        activeItemIdx = (activeItemIdx - 1 + items.length) % items.length;
        items.forEach(function (el, i) { el.classList.toggle('is-active', i === activeItemIdx); });
      } else if (e.key === 'Enter' && activeItemIdx >= 0 && items[activeItemIdx]) {
        e.preventDefault();
        window.location.href = items[activeItemIdx].getAttribute('href');
      } else if (e.key === 'Escape') {
        closeDropdown();
      }
    });

    document.addEventListener('click', function (e) {
      if (!e.target.closest('.novak-search-form')) closeDropdown();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      initCurriculumUX();
      initInstantSearch();
    });
  } else {
    initCurriculumUX();
    initInstantSearch();
  }
})();

/* Phase 1: reader preferences (font size, line spacing, high contrast, dyslexia-friendly font). localStorage only. */
(function () {
  'use strict';
  var KEY = 'novak.readerPrefs.v1';
  var root = document.documentElement;
  function load() { try { return JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (e) { return {}; } }
  function save(p) { try { localStorage.setItem(KEY, JSON.stringify(p)); } catch (e) { /* private mode */ } }
  function apply(p) {
    var fs = Math.max(-2, Math.min(4, parseInt(p.fs || 0, 10) || 0));
    root.style.setProperty('--reader-scale', String(1 + fs * 0.1));
    root.classList.toggle('reader-fs-custom', fs !== 0);
    root.classList.toggle('reader-lh-relaxed', p.lh === 'relaxed');
    root.classList.toggle('reader-lh-loose', p.lh === 'loose');
    root.classList.toggle('reader-contrast', !!p.contrast);
    root.classList.toggle('reader-dys', !!p.dys);
  }
  var prefs = load();
  apply(prefs);
  function wire() {
    var box = document.getElementById('readerPrefs');
    if (!box) return;
    var lh = box.querySelector('[data-rp="lh"]'), hc = box.querySelector('[data-rp="contrast"]'), dy = box.querySelector('[data-rp="dys"]');
    function sync() { if (lh) lh.value = prefs.lh || 'normal'; if (hc) hc.checked = !!prefs.contrast; if (dy) dy.checked = !!prefs.dys; }
    sync();
    box.querySelectorAll('[data-rp="fs"]').forEach(function (b) {
      b.addEventListener('click', function () { prefs.fs = Math.max(-2, Math.min(4, (parseInt(prefs.fs || 0, 10) || 0) + parseInt(b.getAttribute('data-val'), 10))); save(prefs); apply(prefs); });
    });
    if (lh) lh.addEventListener('change', function () { prefs.lh = lh.value; save(prefs); apply(prefs); });
    if (hc) hc.addEventListener('change', function () { prefs.contrast = hc.checked; save(prefs); apply(prefs); });
    if (dy) dy.addEventListener('change', function () { prefs.dys = dy.checked; save(prefs); apply(prefs); });
    var rs = box.querySelector('[data-rp="reset"]');
    if (rs) rs.addEventListener('click', function () { prefs = {}; save(prefs); apply(prefs); sync(); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', wire); else wire();
})();

/* Phase 1: lesson rail (desktop, collapsible, remembered) and bottom sheet (tablet/mobile). */
(function () {
  var KEY = 'novak.lessonRail.v1';
  function init() {
    var rail = document.getElementById('lessonRail');
    if (!rail) return;
    var nav = window.novakLessonNav;
    var stepsOl = document.getElementById('lessonRailSteps');
    var stepNo = rail.querySelector('[data-rail-step]');
    var stepTot = rail.querySelector('[data-rail-total]');
    var fill = rail.querySelector('[data-rail-fill]');
    var topLine = document.querySelector('#lessonTopLine > span');
    var allBtn = document.getElementById('lessonRailAll');
    var toggle = document.getElementById('lessonRailToggle');
    var fab = document.getElementById('lessonSheetBtn');
    var scrim = document.getElementById('lessonSheetScrim');
    var closeBtn = document.getElementById('lessonSheetClose');
    var desk = window.matchMedia('(min-width: 1024px)');

    function setCollapsed(c, persist) {
      rail.classList.toggle('is-collapsed', c);
      document.body.classList.toggle('lesson-rail-collapsed', c);
      if (toggle) {
        toggle.setAttribute('aria-expanded', c ? 'false' : 'true');
        toggle.title = c ? 'Expand lesson menu' : 'Collapse lesson menu';
      }
      if (persist) { try { localStorage.setItem(KEY, c ? 'collapsed' : 'open'); } catch (e) { /* private mode */ } }
    }
    var saved = null;
    try { saved = localStorage.getItem(KEY); } catch (e) { /* private mode */ }
    setCollapsed(saved === 'collapsed', false);
    if (toggle) toggle.addEventListener('click', function () { setCollapsed(!rail.classList.contains('is-collapsed'), true); });

    function openSheet(open) {
      rail.classList.toggle('is-open', open);
      if (fab) fab.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (scrim) scrim.hidden = !open;
      document.body.classList.toggle('lesson-sheet-open', open);
      if (open) { var f = rail.querySelector('button, a'); if (f) f.focus({ preventScroll: true }); } else if (fab && !desk.matches) { fab.focus({ preventScroll: true }); }
    }
    if (fab) fab.addEventListener('click', function () { openSheet(!rail.classList.contains('is-open')); });
    if (scrim) scrim.addEventListener('click', function () { openSheet(false); });
    if (closeBtn) closeBtn.addEventListener('click', function () { openSheet(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && rail.classList.contains('is-open')) openSheet(false); });
    function closeIfSheet() { if (!desk.matches) openSheet(false); }

    // Short, clean step names: drop numbering ("1.", "1.1", "Step 2:"), trailing notes, filler words; cap at ~6 words
    var FILLER = /^(actually|really|just|basically|simply)$/i;
    function cleanStepName(raw) {
      var t = String(raw || '').replace(/\s+/g, ' ').trim();
      t = t.replace(/^(step|part|section|lesson|ch(apter)?)\s*\d+[a-z]?\s*[:.\-–—)]?\s*/i, '');
      t = t.replace(/^[\d.]+[a-z]?\s*[:.\-–—)]?\s*/i, '');
      t = t.split(/\s[—–-]\s|:\s|\s\(|;\s/)[0];
      t = t.replace(/[.,;:!?]+$/, '').trim();
      var words = t.split(' ').filter(function (w, i) { return !(i > 0 && FILLER.test(w)); });
      if (words.length > 6) words = words.slice(0, 5);
      t = words.join(' ').replace(/\s+(and|or|of|to|for|with|in|on|&)$/i, '');
      return t ? t.charAt(0).toUpperCase() + t.slice(1) : '';
    }

    // Steps list, built from the same step groups the guided view uses
    function buildSteps() {
      if (!stepsOl || !nav) return;
      var groups = nav.groups();
      stepsOl.innerHTML = '';
      groups.forEach(function (g, i) {
        var first = g[0];
        var head = cleanStepName(first && (first.getAttribute('data-heading') || (first.querySelector('h2, h3') || {}).textContent)) || ('Step ' + (i + 1));
        var li = document.createElement('li');
        var b = document.createElement('button');
        b.type = 'button';
        b.className = 'rail-stepbtn';
        b.setAttribute('data-rail-go', String(i));
        b.textContent = String(head).replace(/\s+/g, ' ').trim();
        b.addEventListener('click', function () { nav.go(i); closeIfSheet(); });
        li.appendChild(b);
        stepsOl.appendChild(li);
      });
    }
    function onStep(d) {
      if (stepNo) stepNo.textContent = String((d.idx || 0) + 1);
      if (stepTot && d.total) stepTot.textContent = String(d.total);
      var pct = d.focus ? Math.round(((d.idx + 1) / Math.max(1, d.total)) * 100) : d.pct;
      if (fill) fill.style.width = pct + '%';
      if (topLine) topLine.style.width = pct + '%';
      if (stepsOl) Array.prototype.forEach.call(stepsOl.querySelectorAll('[data-rail-go]'), function (b, i) {
        var on = i === d.idx;
        b.classList.toggle('is-active', on);
        if (on) b.setAttribute('aria-current', 'step'); else b.removeAttribute('aria-current');
      });
      if (allBtn) {
        allBtn.textContent = d.focus ? 'Show all steps on one page' : 'Back to one step at a time';
        allBtn.setAttribute('aria-pressed', d.focus ? 'false' : 'true');
      }
    }
    document.addEventListener('novak:lesson-step', function (e) { onStep(e.detail || {}); });
    if (allBtn && nav) allBtn.addEventListener('click', function () { nav.toggleAll(); });

    // Launch Lab: jump to the last step so the lab card is visible, then scroll to it
    Array.prototype.forEach.call(rail.querySelectorAll('#lessonRailLab, [data-rail-lab]'), function (a) {
      a.addEventListener('click', function (e) {
        if (!nav) return;
        e.preventDefault();
        openSheet(false);
        nav.toLab();
      });
    });

    // 5 Ways to Learn: drive the existing step switcher so behaviour stays identical
    var ways = Array.prototype.slice.call(rail.querySelectorAll('[data-rail-rung]'));
    function syncWays(rung) {
      ways.forEach(function (b) {
        var on = b.getAttribute('data-rail-rung') === rung;
        b.classList.toggle('is-active', on);
        b.setAttribute('aria-pressed', on ? 'true' : 'false');
      });
    }
    ways.forEach(function (b) {
      b.addEventListener('click', function () {
        var rung = b.getAttribute('data-rail-rung');
        var src = document.querySelector('#novakStepStyleBar [data-step-rung="' + rung + '"]');
        if (src) src.click();
        syncWays(rung);
        // On tablet/phone close the sheet so the reader sees the swap where they are
        if (!desk.matches) openSheet(false);
      });
    });
    Array.prototype.forEach.call(document.querySelectorAll('#novakStepStyleBar [data-step-rung]'), function (b) {
      b.addEventListener('click', function () { syncWays(b.getAttribute('data-step-rung')); });
    });

    // Tablet/mobile: tutor and Eye Tracking move into the sheet so only one small button floats
    var extra = document.getElementById('lessonRailExtra');
    var tutor = document.getElementById('tutor-open');
    if (extra && tutor) {
      var tb = document.createElement('button');
      tb.type = 'button';
      tb.className = 'btn btn-sm btn-outline-navy w-100 rail-sheet-only';
      tb.innerHTML = '<i class="bi bi-chat-square-text" aria-hidden="true"></i> Ask the tutor';
      tb.addEventListener('click', function () { openSheet(false); tutor.click(); });
      extra.appendChild(tb);
    }
    function addEye() {
      var pill = document.querySelector('#helixDock .helix-pill-btn, #helixDock button');
      if (!extra || !pill || extra.querySelector('[data-rail-eye]')) return !!pill;
      var eb = document.createElement('button');
      eb.type = 'button';
      eb.className = 'btn btn-sm btn-outline-navy w-100 rail-sheet-only';
      eb.setAttribute('data-rail-eye', '1');
      eb.innerHTML = '<i class="bi bi-eye" aria-hidden="true"></i> Eye Tracking';
      eb.addEventListener('click', function () { openSheet(false); pill.click(); });
      extra.appendChild(eb);
      return true;
    }
    if (!addEye()) { var tries = 0; var t = setInterval(function () { if (addEye() || ++tries > 20) clearInterval(t); }, 500); }

    buildSteps();
    if (nav) nav.refresh();
    document.addEventListener('ladder:updated', function () { buildSteps(); if (nav) nav.refresh(); });
    var onMq = function () { if (desk.matches) openSheet(false); };
    if (desk.addEventListener) desk.addEventListener('change', onMq);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function () { setTimeout(init, 0); });
  else setTimeout(init, 0);
})();
