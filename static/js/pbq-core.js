/* Performance-based item helpers (pass 11): choose-N, ordering and matching answers.
 * Pure functions, shared by static/js/assessment.js in the browser and tests/js/pbq-core.test.js in node.
 * Answers are plain arrays of option text; the server grades them (curriculum_v2/cert/practice.py). */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.CIWTPBQ = factory();
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  function isTyped(q) { return !!(q && q.type && q.type !== 'single'); }

  /** Starting answer for a typed question (ordering starts from the shuffled presentation order). */
  function initial(q) {
    if (q.type === 'multi') return [];
    if (q.type === 'order') return (q.options || []).slice();
    if (q.type === 'match') return (q.prompts || []).map(function () { return ''; });
    return null;
  }

  /** True when the answer is complete enough to count as answered. Ordering needs an explicit confirm or move,
   * tracked by the caller as `touched`. */
  function isAnswered(q, a, touched) {
    if (a == null) return false;
    if (!isTyped(q)) return a !== '';
    if (!Array.isArray(a)) return false;
    if (q.type === 'multi') return a.length === (q.choose || a.length) && a.length > 0;
    if (q.type === 'order') return !!touched && a.length === (q.options || []).length;
    if (q.type === 'match') return a.length === (q.prompts || []).length && a.every(function (v) { return v !== '' && v != null; });
    return false;
  }

  /** Toggle an option in a choose-N answer; refuses to go past N (returns the unchanged array). */
  function toggle(a, opt, choose) {
    var out = (a || []).slice(), i = out.indexOf(opt);
    if (i >= 0) { out.splice(i, 1); return out; }
    if (choose && out.length >= choose) return out;
    out.push(opt);
    return out;
  }

  /** Move item i up (dir = -1) or down (dir = +1); returns a new array and the new index. */
  function move(a, i, dir) {
    var out = (a || []).slice(), j = i + dir;
    if (i < 0 || i >= out.length || j < 0 || j >= out.length) return { list: out, index: i };
    var t = out[i]; out[i] = out[j]; out[j] = t;
    return { list: out, index: j };
  }

  /** Set the choice for prompt row r in a matching answer. */
  function setMatch(a, r, value, n) {
    var out = (a && a.length ? a.slice() : new Array(n).fill(''));
    out[r] = value || '';
    return out;
  }

  /** Value for the hidden form field: option text for single answers, JSON for typed answers. */
  function serialize(q, a) {
    if (!isTyped(q)) return a == null ? '' : String(a);
    return JSON.stringify(a || []);
  }

  return { isTyped: isTyped, initial: initial, isAnswered: isAnswered, toggle: toggle, move: move, setMatch: setMatch, serialize: serialize };
}));
