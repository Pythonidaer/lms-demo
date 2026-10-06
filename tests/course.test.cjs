const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const os = require('node:os');
const ts = require('typescript');
const course = JSON.parse(fs.readFileSync('course.json', 'utf8'));
const context = vm.createContext({ URL, crypto: require('node:crypto').webcrypto });
vm.runInContext(fs.readFileSync('lms-runtime.js', 'utf8') + '\nthis.LMS = LMS;', context);
const LMS = context.LMS;

test('Course and offline HTML agree; every authored section is complete and sourced', () => {
  const embedded = fs.readFileSync('index.html', 'utf8').match(/<script id="lms-course-data" type="application\/json">([\s\S]*?)<\/script>/)[1];
  assert.deepEqual(JSON.parse(embedded), course);
  const validated = LMS.validate(course);
  assert.equal(LMS.ready(validated).length, 0);
  assert.equal(course.sections.length, 20);
  assert.equal(LMS.flatten(validated.sections).length, 60);
  for (const section of validated.sections) {
    assert.equal(section.children.filter(n => n.type === 'slides').length, 2);
    assert.equal(section.children.at(-1).type, 'quiz');
    assert.equal(section.children.at(-1).questions.length, 3);
    assert.equal(section.studyGuide.takeaways.length, 2);
    for (const lesson of section.children) {
      assert.ok(lesson.sources.length > 0);
      if (lesson.type === 'slides') {
        assert.equal(lesson.slides.length, 5);
        assert.ok(lesson.objectives[0]);
        assert.ok(lesson.slides[2].body.includes('self-assessed'));
      }
    }
  }
  assert.equal(validated.finalQuiz.questions.length, 20);
});

test('Rendered examples stay escaped and unsafe source URLs are discarded', () => {
  const output = LMS.prose('Hello <img src=x onerror=alert(1)>\n```ts\nconst text = "<script>";\n```');
  assert.ok(!output.includes('<img'));
  assert.ok(output.includes('&lt;script&gt;'));
  assert.ok(output.includes('<pre'));
  const malicious = structuredClone(course);
  malicious.sections[0].children[0].sources = [{ title: 'Unsafe', url: 'javascript:alert(1)' }];
  assert.equal(LMS.validate(malicious).sections[0].children[0].sources.length, 0);
});

test('Study guides retain worked examples, notes, source links and attribution', () => {
  const section = LMS.validate(course).sections[0];
  const markdown = LMS.studyGuide(section, { [section.children[0].id]: { notes: 'My note about erasure.' } });
  for (const text of ['## Key takeaways', 'Try it yourself', 'Compare your solution', 'My note about erasure.', 'https://www.typescriptlang.org', 'CC BY-SA 2.5']) assert.ok(markdown.includes(text));
});

test('All runnable TypeScript lesson snippets type-check independently in strict mode', () => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'lms-snippets-'));
  const files = [];
  for (const lesson of course.sections.flatMap(s => s.children)) {
    for (const slide of lesson.slides || []) {
      const block = slide.body.match(/```ts\n([\s\S]*?)```/);
      if (!block) continue;
      const file = path.join(temp, slide.id + '.ts');
      fs.writeFileSync(file, 'export {};\n' + block[1]);
      files.push(file);
    }
  }
  try {
    const program = ts.createProgram(files, { strict: true, noEmit: true, target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ESNext, lib: ['lib.es2022.d.ts', 'lib.dom.d.ts'] });
    const diagnostics = ts.getPreEmitDiagnostics(program);
    assert.equal(diagnostics.length, 0, ts.formatDiagnosticsWithColorAndContext(diagnostics, { getCurrentDirectory: () => process.cwd(), getCanonicalFileName: f => f, getNewLine: () => '\n' }));
    assert.ok(files.length >= 55);
  } finally { fs.rmSync(temp, { recursive: true, force: true }); }
});
