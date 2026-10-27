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

    // 1. Keep <aside class="novak-visual-blueprint"> open and visible at the top of the lesson
    var blueprint = lessonBody.querySelector('aside.novak-visual-blueprint');
    if (blueprint && !blueprint.hasAttribute('data-ux-enhanced')) {
      blueprint.setAttribute('data-ux-enhanced', '1');
      var specWrap = blueprint.querySelector('.novak-spec-table-wrap');
      var header = blueprint.querySelector('.novak-visual-header');
      if (specWrap && header) {
        var toggleSpecBtn = document.createElement('button');
        toggleSpecBtn.type = 'button';
        toggleSpecBtn.className = 'btn btn-sm btn-outline-navy ms-auto';
        toggleSpecBtn.setAttribute('aria-expanded', 'true');
        toggleSpecBtn.textContent = 'Compact Spec Table';
        toggleSpecBtn.addEventListener('click', function () {
          var hidden = specWrap.classList.toggle('d-none');
          toggleSpecBtn.setAttribute('aria-expanded', hidden ? 'false' : 'true');
          toggleSpecBtn.textContent = hidden ? 'Expand 5-Row Spec Table' : 'Compact Spec Table';
        });
        header.appendChild(toggleSpecBtn);
      }
    }

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

      // Keep inline visual figures & boot deep dive visible on their corresponding steps (or always visible in Full mode)
      var inlineFigs = Array.prototype.slice.call(lessonBody.querySelectorAll('figure.novak-inline-visual'));
      inlineFigs.forEach(function (fig, fIdx) {
        var targetStep = Math.min(totalSteps - 1, fIdx);
        fig.classList.toggle('d-none', focusMode && activeIdx !== targetStep && activeIdx !== 0);
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

    function renderDropdown(data) {
      var results = (data && data.results) || [];
      if (!results.length) {
        dropdown.innerHTML = '<div class="p-2 small text-muted">No instant matches for “' + esc(data.query) + '”. Press Enter for full search.</div>';
        dropdown.classList.remove('d-none');
        return;
      }
      var html = [];
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
