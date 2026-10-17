/* Site-wide UI behaviour (pass 6): back buttons, inline form validation, submit feedback.
   Progressive enhancement only: every form still works without this file. */
(function () {
  'use strict';

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
    if (form.hasAttribute('data-no-enhance') || form.__ciwt) return;
    form.__ciwt = true;
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

  function init() { document.querySelectorAll('form[method=post], form[method=POST], form.needs-validation').forEach(enhance); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
