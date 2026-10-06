const test = require('node:test');
const assert = require('node:assert/strict');
const ts = require('typescript');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('examples/catalog.ts', 'utf8');
const output = ts.transpileModule(source, { compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.CommonJS } });
const context = vm.createContext({ exports: {} });
vm.runInContext(output.outputText, context);
const catalog = context.exports;
const valid = { id: 'a', title: 'Types', minutes: 0 };

test('Catalog validates malformed values, duplicates and zero-minute edge cases', () => {
  for (const value of [null, {}, [null], [{ ...valid, id: ' ' }], [{ ...valid, title: '' }], [{ ...valid, minutes: -1 }], [{ ...valid, minutes: NaN }], [{ ...valid, minutes: Infinity }], [{ id: 'a', minutes: 1 }], [valid, valid]]) assert.equal(catalog.parseCatalog(value).ok, false);
  assert.equal(catalog.parseCatalog([]).ok, true);
  assert.equal(catalog.parseCatalog([valid]).ok, true);
});

test('Catalog projects outputs, preserves input and handles missing lookups', () => {
  const raw = { ...valid, secret: 'remove' };
  const parsed = catalog.parseCatalog([raw]);
  assert.equal(parsed.ok, true);
  assert.equal('secret' in parsed.value[0], false);
  assert.notEqual(parsed.value[0], raw);
  const updated = catalog.rename(parsed.value, 'a', 'Everyday types');
  assert.equal(parsed.value[0].title, 'Types');
  assert.equal(updated[0].title, 'Everyday types');
  assert.equal(catalog.findLesson(updated, 'absent'), undefined);
  assert.equal(catalog.totalMinutes(updated), 0);
  assert.throws(() => catalog.rename(updated, 'a', ' '));
  assert.equal(catalog.describe(parsed), '1 lessons, 0 minutes');
});

test('Capstone contracts compile and deliberately invalid keys fail', () => {
  const program = ts.createProgram(['examples/catalog.ts', 'tests/catalog-types.ts'], { strict: true, noEmit: true, noUncheckedIndexedAccess: true, exactOptionalPropertyTypes: true, target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.NodeNext, moduleResolution: ts.ModuleResolutionKind.NodeNext });
  const errors = ts.getPreEmitDiagnostics(program);
  assert.equal(errors.length, 0, errors.map(d => ts.flattenDiagnosticMessageText(d.messageText, '\n')).join('\n'));
});
