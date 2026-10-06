import { getProperty, findLesson, type Lesson } from '../examples/catalog.js';
const lesson: Lesson = { id: 'a', title: 'Types', minutes: 0 };
const minutes: number = getProperty(lesson, 'minutes');
// @ts-expect-error nonexistent key must be rejected
getProperty(lesson, 'minuts');
// @ts-expect-error lookup can be missing
const found: Lesson = findLesson([], 'a');
// @ts-expect-error readonly contract rejects mutation
lesson.title = 'Changed';
void minutes;
