/* Node check: every widget type rejects its initial state and accepts a solved state. */
var assert = require('assert');
var S = require('./novak-sims.js');

assert.ok(S.TYPES.length >= 23, 'widget type count');
S.TYPES.forEach(function (type) {
  var spec = S.sample(type);
  assert.strictEqual(spec.type, type);
  assert.ok(spec.instruction && spec.instruction.split(/\s+/).length <= 25, type + ' instruction');
  var bad = S.evaluate(spec, S.initial(spec));
  var good = S.evaluate(spec, S.solved(spec));
  assert.strictEqual(bad.ok, false, type + ' initial should fail: ' + bad.message);
  assert.strictEqual(good.ok, true, type + ' solved should pass: ' + good.message);
});

var sub = S.subnetFacts('10.0.0.50', 28);
assert.strictEqual(sub.network, '10.0.0.48');
assert.strictEqual(sub.broadcast, '10.0.0.63');
assert.strictEqual(sub.hosts, 14);

var raid = S.raidInfo('5', 4, 2);
assert.strictEqual(raid.usable, 6);
assert.strictEqual(raid.fault, 1);
assert.strictEqual(S.bitsToOctal([1, 1, 1, 1, 0, 1, 1, 0, 0]), '754');
assert.notStrictEqual(S.teachHash('backup-report'), S.teachHash('backup-reporu'));

var sortSpec = {
  type: 'troubleshoot',
  instruction: 'Sort each item into the matching group, then check.',
  params: {
    mode: 'sort',
    buckets: ['Keep', 'Replace'],
    items: [
      { id: 'i0', text: 'Known-good cable', bucket: 'Keep' },
      { id: 'i1', text: 'Swollen capacitor', bucket: 'Replace' },
      { id: 'i2', text: 'Current driver', bucket: 'Keep' },
      { id: 'i3', text: 'Burned connector', bucket: 'Replace' }
    ]
  },
  goal: { items: { i0: 'Keep', i1: 'Replace', i2: 'Keep', i3: 'Replace' } }
};
assert.strictEqual(S.evaluate(sortSpec, S.initial(sortSpec)).ok, false);
assert.strictEqual(S.evaluate(sortSpec, S.solved(sortSpec)).ok, true);

var dns = S.sample('dora');
dns.params.mode = 'dns';
assert.strictEqual(S.evaluate(dns, S.solved(dns)).ok, true);

console.log('ok ' + S.TYPES.length + ' widget types');
