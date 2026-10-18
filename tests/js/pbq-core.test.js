// Run: node --test tests/js/
const test = require('node:test');
const assert = require('node:assert');
const P = require('../../static/js/pbq-core.js');

const multi = { type: 'multi', options: ['a', 'b', 'c', 'd', 'e'], choose: 2 };
const order = { type: 'order', options: ['s3', 's1', 's2', 's4'] };
const match = { type: 'match', prompts: ['p1', 'p2', 'p3'], options: ['x', 'y', 'z', 'decoy'] };

test('single-answer questions are not typed and serialize to the option text', () => {
  assert.strictEqual(P.isTyped({ options: ['a'] }), false);
  assert.strictEqual(P.serialize({}, 'Option A'), 'Option A');
  assert.strictEqual(P.isAnswered({}, 'Option A'), true);
  assert.strictEqual(P.isAnswered({}, null), false);
});

test('choose-N toggles and refuses to exceed N', () => {
  let a = P.initial(multi);
  a = P.toggle(a, 'a', 2); a = P.toggle(a, 'c', 2);
  assert.deepStrictEqual(P.toggle(a, 'e', 2), ['a', 'c']);
  assert.strictEqual(P.isAnswered(multi, a), true);
  a = P.toggle(a, 'a', 2);
  assert.deepStrictEqual(a, ['c']);
  assert.strictEqual(P.isAnswered(multi, a), false);
});

test('ordering moves swap neighbours and stay in bounds', () => {
  let a = P.initial(order);
  assert.deepStrictEqual(a, ['s3', 's1', 's2', 's4']);
  let r = P.move(a, 0, +1);
  assert.deepStrictEqual(r.list, ['s1', 's3', 's2', 's4']); assert.strictEqual(r.index, 1);
  r = P.move(r.list, 0, -1);
  assert.deepStrictEqual(r.list, ['s1', 's3', 's2', 's4']); assert.strictEqual(r.index, 0);
  r = P.move(r.list, 3, +1);
  assert.strictEqual(r.index, 3);
  assert.strictEqual(P.isAnswered(order, r.list, false), false, 'untouched order is not an answer');
  assert.strictEqual(P.isAnswered(order, r.list, true), true);
});

test('matching needs every row filled', () => {
  let a = P.initial(match);
  a = P.setMatch(a, 0, 'x', 3); a = P.setMatch(a, 2, 'z', 3);
  assert.strictEqual(P.isAnswered(match, a), false);
  a = P.setMatch(a, 1, 'y', 3);
  assert.strictEqual(P.isAnswered(match, a), true);
  assert.strictEqual(P.serialize(match, a), JSON.stringify(['x', 'y', 'z']));
});

test('serialize never includes anything but the learner’s own selections', () => {
  const s = P.serialize(multi, ['b', 'd']);
  assert.deepStrictEqual(JSON.parse(s), ['b', 'd']);
});
