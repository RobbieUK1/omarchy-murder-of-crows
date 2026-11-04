const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const context = vm.createContext({});
vm.runInContext(fs.readFileSync(path.join(__dirname, '../scripts/Randomize.js'), 'utf8'), context);
const files = ['a', 'b', 'c', 'd'];
let previous = {};
for (let trial = 0; trial < 1000; trial++) {
  const names = trial % 2 ? ['DP-1', 'HDMI-A-1'] : ['HDMI-A-1', 'DP-1', 'DP-2', 'eDP-1'];
  const chosen = context.assign(names, files, previous);
  assert.equal(Object.keys(chosen).length, names.length);
  assert.equal(new Set(Object.values(chosen)).size, names.length);
  for (const name of names) {
    assert.ok(files.includes(chosen[name]));
    assert.notEqual(chosen[name], previous[name]);
  }
  previous = chosen;
}
assert.equal(Object.keys(context.assign(['DP-1'], [], {})).length, 0);
assert.equal(context.assign(['DP-1'], ['only'], {'DP-1': 'only'})['DP-1'], 'only');
const many = context.assign(['a', 'b', 'c', 'd', 'e'], ['one', 'two'], {});
assert.equal(Object.keys(many).length, 5);
assert.equal(new Set(Object.values(many)).size, 2);
assert.equal(Object.keys(context.assign([], files, {})).length, 0);
console.log('PASS: 1,000 reshuffles, no repeats or duplicates, hotplug, empty/single/short image pools');
