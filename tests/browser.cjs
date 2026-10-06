/* Run against a local static server; optional Playwright dependency. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
let playwright;
try { playwright = require('playwright'); }
catch { playwright = require(path.join(process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES || '', 'playwright')); }
const course = JSON.parse(fs.readFileSync('course.json', 'utf8'));
const base = process.env.LMS_TEST_URL || 'http://127.0.0.1:8000';

(async () => {
  let launch = { headless: true };
  if (process.env.LMS_CHROMIUM_PACKAGE) {
    const { default: chromium } = await import(path.resolve(process.env.LMS_CHROMIUM_PACKAGE, 'build/index.js'));
    launch = { ...launch, executablePath: process.env.LMS_CHROMIUM_EXECUTABLE || await chromium.executablePath(), args: chromium.args };
  }
  const browser = await playwright.chromium.launch(launch);
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, acceptDownloads: true });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  const item = id => page.locator(`[data-lms="open"][data-id="${id}"]`);
  const next = page.locator('[data-lms="slide-next"]');
  const complete = page.locator('[data-lms="complete"]');
  const guide = page.locator('[data-lms="guide"]');
  await page.goto(base);
  assert.equal(await complete.isDisabled(), true);
  assert.equal(await guide.isDisabled(), true);
  assert.equal(await item(course.sections[0].children[1].id).isDisabled(), true);
  await page.locator('[data-lms-notes]').fill('Remember: types are erased.');
  for (let i = 0; i < 4; i++) await next.click();
  assert.equal(await complete.isEnabled(), true);
  await complete.click();
  await page.reload();
  assert.equal(await page.locator('[data-lms-notes]').inputValue(), 'Remember: types are erased.');
  assert.equal(await item(course.sections[0].children[1].id).isEnabled(), true);

  for (let sectionIndex = 0; sectionIndex < course.sections.length; sectionIndex++) {
    const section = course.sections[sectionIndex];
    const details = page.locator('details').filter({ has: page.locator(`[data-id="${section.children[0].id}"]`) }).first();
    if (!(await details.getAttribute('open') !== null)) await details.locator('summary').first().click();
    for (let lessonIndex = 0; lessonIndex < section.children.length; lessonIndex++) {
      const lesson = section.children[lessonIndex];
      await item(lesson.id).click();
      if (lesson.type === 'slides') {
        // Check full examples on desktop/tablet/mobile for unintended page overflow.
        await next.click();
        for (const width of [1440, 768, 390]) {
          await page.setViewportSize({ width, height: 1000 });
          assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), true, `Overflow: ${lesson.id} at ${width}`);
        }
        await page.setViewportSize({ width: 1440, height: 1000 });
        for (let i = 0; i < 3; i++) await next.click();
        await complete.click();
      } else {
        if (sectionIndex === 0) {
          for (const q of lesson.questions) await page.locator(`input[name="q-${q.id}"][value="${(q.answer+1)%q.options.length}"]`).check();
          await page.locator('#lms-quiz button[type="submit"]').click();
          assert.equal(await guide.isDisabled(), true);
          const nextDetails = page.locator('details').filter({ has: page.locator(`[data-id="${course.sections[1].children[0].id}"]`) }).first();
          await nextDetails.locator('summary').first().click();
          assert.equal(await item(course.sections[1].children[0].id).isDisabled(), true);
        }
        for (const q of lesson.questions) await page.locator(`input[name="q-${q.id}"][value="${q.answer}"]`).check();
        await page.locator('#lms-quiz button[type="submit"]').click();
        assert.equal(await guide.isEnabled(), true);
        if (sectionIndex === 0) {
          const downloadPromise = page.waitForEvent('download');
          await guide.click();
          const download = await downloadPromise;
          const filename = path.join('test-results', download.suggestedFilename());
          fs.mkdirSync('test-results', { recursive: true });
          await download.saveAs(filename);
          const text = fs.readFileSync(filename, 'utf8');
          assert.ok(text.includes('Remember: types are erased.'));
          assert.ok(text.includes('## Sources'));
          assert.ok(text.includes('Compare your solution'));
        }
      }
    }
  }
  await item(course.finalQuiz.id).click();
  for (const q of course.finalQuiz.questions) await page.locator(`input[name="q-${q.id}"][value="${q.answer}"]`).check();
  await page.locator('#lms-quiz button[type="submit"]').click();
  assert.ok((await page.locator('#lms-progress').getAttribute('value')) === '100');
  await page.reload();
  assert.equal(await page.locator('#lms-progress').getAttribute('value'), '100');
  await page.locator('[data-lms="view"][data-view="report"]').click();
  assert.ok((await page.locator('.lms-metrics').innerText()).includes('60/60'));

  // Changed content invalidates stored completion and relocks dependent lessons.
  // Change the incoming course, rather than editing storage while the old runtime is saving.
  await page.addInitScript(() => document.addEventListener('DOMContentLoaded', () => {
    const element = document.querySelector('#lms-course-data');
    const raw = JSON.parse(element.textContent);
    raw.sections[0].children[0].slides[0].body += '\nUpdated lesson content.';
    element.textContent = JSON.stringify(raw);
  }));
  await page.evaluate(() => { location.hash = 'learn'; });
  await page.reload();
  assert.equal(await item(course.sections[0].children[1].id).isDisabled(), true);
  const firstDetails = page.locator('details').filter({ has: item(course.sections[0].children[0].id) }).first();
  if (await firstDetails.getAttribute('open') === null) await firstDetails.locator('summary').first().click();
  await item(course.sections[0].children[0].id).click();
  assert.equal(await guide.isDisabled(), true);
  assert.equal(await complete.isDisabled(), true);

  await page.setViewportSize({ width: 390, height: 844 });
  await page.locator('[data-lms="outline"]').click();
  assert.equal(await page.locator('#lms-outline').isVisible(), true);
  assert.equal(await page.locator('[data-lms="outline"]').getAttribute('aria-expanded'), 'true');
  await page.locator('[data-lms="outline"]').click();
  await page.screenshot({ path: 'test-results/mobile.png', fullPage: true });
  await page.setViewportSize({ width: 1440, height: 1000 });
  await next.click();
  await page.screenshot({ path: 'test-results/desktop.png', fullPage: true });
  assert.deepEqual(errors, []);
  await browser.close();
  console.log('Browser checks passed: all 60 lessons, quiz failure/retake, final assessment, exports, persistence, stale progress, mobile outline, and 390/768/1440px overflow.');
})().catch(error => { console.error(error); process.exit(1); });
