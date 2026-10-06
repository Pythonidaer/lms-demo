"""Build authored curriculum into the static LMS. No network or dependencies."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
modules = []

def source(path, title=None):
    base = 'https://www.typescriptlang.org'
    if path.startswith('https:'):
        return {'title': title or path, 'url': path}
    return {'title': title or path.rsplit('/', 1)[-1].replace('.html', '').replace('-', ' ').title(), 'url': base + path}

def M(slug, title, sources):
    module = {'id': 'ts-sec-' + slug, 'type': 'section', 'title': f'{len(modules)+1:02} {title}', 'children': [], 'sources': [source(*s) if isinstance(s, tuple) else source(s) for s in sources]}
    modules.append(module)
    return module

def L(m, slug, title, goal, explanation, code, practice, solution, takeaway, language='ts'):
    lid = 'ts-lesson-' + slug
    def s(kind, title, body):
        return {'id': lid + '-' + kind, 'title': title, 'body': body}
    lesson = {'id': lid, 'type': 'slides', 'title': title, 'minutes': 15, 'objectives': [goal], 'sources': m['sources'], 'slides': [
        s('concept', title, 'YOUR GOAL\n' + goal + '\n\n' + explanation),
        s('example', 'Read the code', f'```{language}\n{code.strip()}\n```\n\nPredict what the compiler checks and what happens when the code runs. These are separate questions.'),
        s('practice', 'Try it yourself', practice + '\n\nUse your editor or the TypeScript Playground. Try before opening the next slide. Practice is self-assessed; this LMS does not execute or grade code.'),
        s('solution', 'Compare your solution', f'```{language}\n{solution.strip()}\n```\n\nCompare behavior and types, rather than matching every character. Explain your choices aloud or in lesson notes.'),
        s('takeaway', 'Keep this in mind', takeaway + '\n\nBefore completing: make your example work, deliberately introduce a mistake, and explain the compiler response. Use the lesson sources below for deeper reading.')
    ]}
    m['children'].append(lesson)
    return lesson

def Q(m, prompt, correct, wrong1, wrong2, explanation):
    if not m['children'] or m['children'][-1]['type'] != 'quiz':
        name = re.sub(r'^\d{2} ', '', m['title'])
        m['children'].append({'id': m['id']+'-quiz', 'type': 'quiz', 'title': name, 'skill': name, 'questions': [], 'sources': m['sources']})
    quiz = m['children'][-1]
    index = len(quiz['questions'])
    options = [correct, wrong1, wrong2]
    shift = (len(modules) + index) % 3
    options = options[shift:] + options[:shift]
    quiz['questions'].append({'id': quiz['id'] + f'-q{index+1}', 'prompt': prompt, 'options': options, 'answer': options.index(correct), 'explanation': explanation})

m=M('orientation','Start and understand the runtime',[
('/docs/handbook/2/basic-types.html','TypeScript: The Basics'),('/docs/handbook/typescript-tooling-in-5-minutes.html','TypeScript tooling'),
('https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Introduction','MDN: Introduction')])
L(m,'pipeline','Type checking versus execution','Describe the path from TypeScript source to running JavaScript.',
'TypeScript checks whether your code uses values consistently. JavaScript still controls runtime behavior. Most type syntax is erased. An annotation cannot validate a server response or turn text into a number. Some features, such as enums, do emit JavaScript.',
'const minutes: number = 12;\nconsole.log(minutes + 1);\n// JavaScript output has no : number annotation.',
'Create a variable minutes with a number annotation. Assign text on purpose and inspect the error. Then convert the text with Number() and inspect the emitted JavaScript.',
'const input = "12";\nconst minutes: number = Number(input);\nif (!Number.isFinite(minutes)) throw new Error("Invalid minutes");\nconsole.log(minutes + 1);',
'A compiler check and a runtime validation solve different problems. Passing the compiler does not prove your program is correct.')
L(m,'setup','Create a strict practice project','Run the compiler with a reproducible project configuration.',
'Install TypeScript as a project development dependency and use its local compiler. A tsconfig.json defines the project. strict enables a family of checks. noEmit checks without writing JavaScript; an emitter or bundler is a separate choice. Pin and record your compiler version when comparing results.',
'npm init -y\nnpm install --save-dev typescript\nnpx tsc --init\nnpx tsc --noEmit\nnpx tsc --version',
'Create src/practice.ts. Enable strict, noEmit and an appropriate target in tsconfig.json. Run npx tsc -p tsconfig.json, then inspect the resolved config with --showConfig.',
'{\n  "compilerOptions": {\n    "target": "ES2022",\n    "strict": true,\n    "noEmit": true\n  },\n  "include": ["src/**/*.ts"]\n}',
'Commands belong in a terminal, not a .ts file. Passing explicit filenames to tsc bypasses the project config; use -p for project checks. Course snippets generally assume strict checking and ES2022 with DOM declarations.',language='text')
Q(m,'Does const value = payload as Lesson validate an API response?','No; assertions are erased','Yes; it checks every field','Yes; it converts JSON into a class','An assertion changes the checker’s view. Validate untrusted data with runtime checks.')
Q(m,'Which command explicitly checks the project config?','npx tsc -p tsconfig.json --noEmit','npx tsc practice.ts always loads tsconfig.json','node practice.ts always checks all types','-p selects a config. Explicit input filenames do not load its compiler options.')
Q(m,'What does strict primarily provide?','A family of stronger static checks','Automatic runtime input validation','A proof that there are no bugs','Strictness catches additional type mistakes, but cannot replace testing or input validation.')

m=M('javascript','JavaScript foundations for TypeScript',[
('https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Grammar_and_types','MDN: Grammar and types'),
('https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Functions','MDN: Functions'),
('https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Closures','MDN: Closures'),
('/docs/handbook/variable-declarations.html','TypeScript: Variable declarations')])
L(m,'scope','Scope, const, and closures','Predict which values a function can access.',
'let and const are block-scoped. const prevents rebinding; it does not freeze an object. A closure retains access to its lexical environment. TypeScript does not change these JavaScript rules. Prefer explicit inputs over hidden mutable state when practical.',
'function makeCounter() {\n  let count = 0;\n  return () => ++count;\n}\nconst next = makeCounter();\nconsole.log(next(), next()); // 1, 2',
'Create two counters. Predict whether they share a count. Then create a const object and update one property. Explain why that is allowed.',
'function makeCounter() {\n  let count = 0;\n  return () => ++count;\n}\nconst a = makeCounter();\nconst b = makeCounter();\nconsole.log(a(), a(), b()); // 1, 2, 1\nconst course = { title: "TypeScript" };\ncourse.title = "TypeScript skills";',
'Each invocation creates its own lexical environment. const, readonly, and Object.freeze address different kinds of change.')
L(m,'coercion','Equality, optional chaining, and defaults','Preserve legitimate zero and empty-string values.',
'Strict equality avoids implicit coercion. Optional chaining stops a property access when the receiver is null or undefined. Nullish coalescing uses a default only for null or undefined. Logical OR also replaces false, zero and empty text.',
'const zero = 0;\nconsole.log(zero || 10); // 10\nconsole.log(zero ?? 10); // 0\nconst user: { name?: string } = {};\nconsole.log(user.name?.toUpperCase() ?? "Guest");',
'Write a label function accepting { title?: string; minutes?: number }. Default absent minutes to 10 but preserve 0. Default absent title to Untitled but preserve empty text.',
'function label(value: { title?: string; minutes?: number }) {\n  const title = value.title ?? "Untitled";\n  const minutes = value.minutes ?? 10;\n  return `${title}: ${minutes} min`;\n}\nconsole.log(label({ title: "", minutes: 0 }));',
'Optional chaining does not validate an arbitrary value. A truthiness check can accidentally discard meaningful empty strings or zero.')
Q(m,'What does const prevent for an object binding?','Reassigning the binding','Every mutation inside the object','All changes through aliases','const protects the variable binding. Object properties may still change.')
Q(m,'What is 0 ?? 20?','0','20','undefined','?? uses the fallback only for null or undefined.')
Q(m,'Do two separate calls to makeCounter share the local count?','No, each call creates its own environment','Always','Only when strict is enabled','Closure behavior comes from JavaScript lexical environments, independent of type checking.')

m=M('everyday','Everyday types and inference',[
('/docs/handbook/2/everyday-types.html','Everyday Types'),('/docs/handbook/type-inference.html','Type Inference')])
L(m,'primitives','Annotate boundaries and trust inference','Use primitive and collection types without unnecessary annotations.',
'Use lowercase string, number and boolean for primitive values. TypeScript infers many local types from initializers. Annotate public function boundaries and ambiguous empty collections. A numeric-looking string is still text; number includes non-integer values and NaN.',
'let title = "Arrays"; // string\nconst published: boolean = true;\nconst minutes: number[] = [10, 12];\nfunction total(items: number[]): number {\n  return items.reduce((sum, value) => sum + value, 0);\n}',
'Write average(items: number[]): number | undefined. Return undefined for an empty array. Do not use any or the boxed Number type.',
'function average(items: number[]): number | undefined {\n  if (items.length === 0) return undefined;\n  return items.reduce((sum, n) => sum + n, 0) / items.length;\n}\nconsole.log(average([10, 20]));',
'An annotation describes allowed values; it does not coerce them. Hover inferred values before adding redundant annotations.')
L(m,'literals','Literal unions, as const, and satisfies','Check a configuration while retaining useful inference.',
'Literal types describe exact values. let often widens a literal to its broader primitive type. as const preserves literal information and gives object properties and arrays readonly types. satisfies checks compatibility while retaining the expression’s resulting type; contextual typing can still influence inference.',
'type Mode = "read" | "practice";\nconst config = {\n  mode: "read",\n  minutes: 10\n} satisfies { mode: Mode; minutes: number };\nconst steps = ["read", "practice"] as const;\ntype Step = typeof steps[number];',
'Define ThemeName as light | dark. Create an object containing those keys with string values using satisfies Record<ThemeName, string>. Call a string method on the dark value.',
'type ThemeName = "light" | "dark";\nconst themes = { light: "#ffffff", dark: "#111111" } satisfies Record<ThemeName, string>;\nconsole.log(themes.dark.toUpperCase());',
'as const does not freeze values at runtime. satisfies is a compatibility check, not a general runtime validator or a cast.')
Q(m,'Which type should normally describe primitive text?','string','String','any','Lowercase string describes primitive text. String is a boxed-object type.')
Q(m,'What is the purpose of satisfies?','Check compatibility while retaining the expression’s resulting type','Validate a server response at runtime','Always convert a value into the target type','satisfies provides a static compatibility check; it emits no runtime validation.')
Q(m,'What does as const guarantee at runtime?','No runtime freezing','Deep freezing','A validation exception on mutation','Const assertions only influence types. Runtime immutability needs separate behavior.')

m=M('objects','Model objects and collections',[
('/docs/handbook/2/objects.html','Object Types'),('/docs/handbook/2/everyday-types.html','Aliases and interfaces'),
('https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Working_with_objects','MDN: Objects'),
('https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Keyed_collections','MDN: Keyed collections')])
L(m,'shapes','Interfaces, aliases, and optional properties','Choose a reusable object shape and handle missing fields.',
'An interface names an object contract and can be extended or merged. A type alias can also name unions, tuples and other expressions. TypeScript normally checks structure rather than where a value was declared. Optional properties may be absent; reading one usually includes undefined under strictNullChecks.',
'interface Lesson {\n  readonly id: string;\n  title: string;\n  minutes?: number;\n}\ntype PublishedLesson = Lesson & { published: true };\nfunction duration(lesson: Lesson) {\n  return lesson.minutes ?? 0;\n}',
'Create a Lesson with optional summary. Write describe() that returns uppercase summary or No summary. Add an interface VideoLesson extending Lesson with url.',
'interface Lesson { id: string; summary?: string }\ninterface VideoLesson extends Lesson { url: string }\nfunction describe(lesson: Lesson): string {\n  return lesson.summary?.toUpperCase() ?? "No summary";\n}\nconst video: VideoLesson = { id: "intro", url: "intro.mp4" };',
'Fresh object literals receive excess-property checks. Do not bypass a misspelled property with an assertion. readonly is shallow and does not prevent mutation through other references.')
L(m,'collections','Arrays, tuples, records, maps, and sets','Choose a collection by its actual data model.',
'Arrays describe variable-length sequences. Tuples describe known positions and lengths. Record maps a key type to a value type; arbitrary string keys can still be missing at runtime. Map supports keys beyond strings; Set stores unique values. readonly arrays prevent mutation through that reference.',
'type Coordinate = readonly [x: number, y: number];\nconst point: Coordinate = [10, 20];\nconst scores: Record<"read" | "practice", number> = { read: 80, practice: 90 };\nconst names = new Map<string, string>([["a", "Arrays"]]);\nconst completed = new Set<string>(["a", "a"]);\nconsole.log(names.get("missing")); // undefined',
'Write totalMinutes accepting readonly number[]. Create a Map from lesson IDs to minutes and handle a missing entry. Explain why Record<string, number> alone does not prove any key exists.',
'function totalMinutes(values: readonly number[]): number {\n  return values.reduce((sum, n) => sum + n, 0);\n}\nconst minutes = new Map<string, number>([["intro", 10]]);\nconst missing = minutes.get("advanced") ?? 0;\nconsole.log(totalMinutes([missing, 10]));',
'A tuple is a type-level shape; it is still an array at runtime. noUncheckedIndexedAccess adds missing-value checks for unchecked indexing.')
Q(m,'Reading summary?: string with strictNullChecks gives which type?','string | undefined','Always string','Always null','An optional property might be missing, so reading it can produce undefined.')
Q(m,'Does readonly on a property deeply freeze its object?','No; it restricts assignment through that type','Yes, recursively','Only in production builds','readonly is a static and shallow restriction, not a runtime freeze.')
Q(m,'What does Map.get return for an absent key?','undefined','A default value of the declared value type','Always an exception','The return type includes undefined because a key may be absent.')

m=M('narrowing','Narrow uncertain values safely',[
('/docs/handbook/2/narrowing.html','Narrowing'),
('https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Control_flow_and_error_handling','MDN: Control flow')])
L(m,'guards','Union types and control-flow analysis','Use runtime evidence to narrow a union.',
'A union means a value can be any listed member. Before using a member-specific operation, establish which member you have. typeof, equality, in, instanceof, assignments and early returns can all narrow. typeof null is object, so object checks also need a null check.',
'function label(value: string | number | null): string {\n  if (value === null) return "Missing";\n  if (typeof value === "string") return value.toUpperCase();\n  return value.toFixed(0);\n}',
'Write normalize(value: string | string[] | null): string[]. Use a null check and Array.isArray. Preserve an empty string instead of treating it as missing.',
'function normalize(value: string | string[] | null): string[] {\n  if (value === null) return [];\n  if (Array.isArray(value)) return value;\n  return [value];\n}',
'typeof returns limited JavaScript categories. Truthiness is useful only when dropping every falsy value is intentional.')
L(m,'predicates','unknown, predicates, and assertion functions','Check external input before treating it as domain data.',
'unknown accepts any incoming value but requires evidence before use. A predicate returns value is Type. An assertion function returns asserts value is Type and throws when its condition fails. The compiler trusts declared predicates: your implementation must actually check the contract.',
'type Lesson = { id: string; minutes: number };\nfunction isLesson(value: unknown): value is Lesson {\n  return typeof value === "object" && value !== null\n    && "id" in value && typeof value.id === "string"\n    && "minutes" in value && typeof value.minutes === "number"\n    && Number.isFinite(value.minutes);\n}',
'Write assertText(value: unknown): asserts value is string. Throw an Error for non-text input. Use it before calling toUpperCase. Then explain what a dishonest predicate could break.',
'function assertText(value: unknown): asserts value is string {\n  if (typeof value !== "string") throw new Error("Expected text");\n}\nconst input: unknown = "TypeScript";\nassertText(input);\nconsole.log(input.toUpperCase());',
'any allows unchecked operations; unknown requires narrowing. A predicate validates only what its body checks, not every business rule automatically.')
Q(m,'Why use unknown at an untrusted boundary?','It requires narrowing before specific operations','It validates JSON automatically','It disables checks like any','unknown keeps later uses checked until evidence establishes a usable type.')
Q(m,'Why is typeof value === "object" insufficient to reject null?','typeof null is "object"','null is always an array','TypeScript rewrites typeof','JavaScript’s typeof null result requires an explicit null check.')
Q(m,'Can a declared type predicate lie?','Yes; its runtime implementation still needs correct checks','No, the compiler proves every property check','Only with strict disabled','The compiler trusts the predicate signature. Test validators with malformed values.')

m=M('states','Represent states and handle every case',[
('/docs/handbook/2/narrowing.html#discriminated-unions','Discriminated unions'),
('/docs/handbook/2/narrowing.html#exhaustiveness-checking','Exhaustiveness')])
L(m,'discriminants','Discriminated unions','Make invalid combinations harder to represent.',
'Use a shared literal field to identify each state. A loaded state can require data while an error state requires a message. This is stronger than one object with several unrelated optional fields. Checking the discriminant narrows the associated fields.',
'type LoadState =\n  | { status: "loading" }\n  | { status: "loaded"; title: string }\n  | { status: "error"; message: string };\nfunction text(state: LoadState) {\n  if (state.status === "loaded") return state.title;\n  if (state.status === "error") return state.message;\n  return "Loading";\n}',
'Model a payment as pending, paid with receiptId, or failed with reason. Write a label function. Try to construct a paid state without a receipt ID and inspect the error.',
'type Payment =\n  | { kind: "pending" }\n  | { kind: "paid"; receiptId: string }\n  | { kind: "failed"; reason: string };\nfunction label(payment: Payment): string {\n  switch (payment.kind) {\n    case "pending": return "Pending";\n    case "paid": return payment.receiptId;\n    case "failed": return payment.reason;\n  }\n}',
'Domain modeling catches impossible field combinations before UI code. Choose a discriminant that describes the state, not incidental implementation details.')
L(m,'exhaustive','never and exhaustive switches','Make a newly added union member trigger a useful compiler error.',
'never represents no possible value. After every union member is handled, the remaining value can be assigned to never. If you later add a member, that assignment fails until you handle it. This is a maintenance tool, not an automatic runtime proof for unvalidated input.',
'function assertNever(value: never): never {\n  throw new Error(`Unexpected state: ${String(value)}`);\n}\ntype Action = { kind: "start" } | { kind: "stop" };\nfunction label(action: Action): string {\n  switch (action.kind) {\n    case "start": return "Started";\n    case "stop": return "Stopped";\n    default: return assertNever(action);\n  }\n}',
'Add a pause action. Observe the assertNever error, then add the missing case. Explain how never differs from void.',
'type Action = { kind: "start" } | { kind: "stop" } | { kind: "pause" };\nfunction assertNever(value: never): never { throw new Error(String(value)); }\nfunction label(action: Action): string {\n  switch (action.kind) {\n    case "start": return "Started";\n    case "stop": return "Stopped";\n    case "pause": return "Paused";\n    default: return assertNever(action);\n  }\n}',
'void describes an ignored or absent useful return result. never describes a function that cannot return normally, or a value that cannot exist.')
Q(m,'Which model best ties loaded data to its state?','A discriminated union requiring data on loaded','An object with all fields optional','A string and an unrelated global data variable','A discriminated union makes the relationship explicit and supports narrowing.')
Q(m,'What does assigning the remaining switch value to never check?','All union members have been handled','The API is always online','All values were validated at runtime','An unhandled member remains assignable to its own type, not never, producing an error.')
Q(m,'Which return type describes a function that always throws?','never','unknown','string','It cannot return normally, so never expresses its return behavior.')

m=M('functions','Design function contracts',[
('/docs/handbook/2/functions.html','More on Functions'),
('https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Functions','MDN: Functions')])
L(m,'callbacks','Parameters, callbacks, rest, and void','Describe callable behavior without making promises your implementation breaks.',
'A function type describes parameters and a result. Optional parameters may be omitted by the caller. For callback contracts, a parameter should only be optional if the invoking code may omit it. Callbacks can ignore extra supplied arguments without making those parameters optional.',
'function visit(items: string[], callback: (item: string, index: number) => void) {\n  items.forEach(callback);\n}\nvisit(["types"], item => console.log(item));\nfunction sum(...values: number[]): number {\n  return values.reduce((a, b) => a + b, 0);\n}',
'Write repeat(count, callback), where callback always receives the iteration index. Show a callback that ignores the index and one that uses it. Do not write index?: number.',
'function repeat(count: number, callback: (index: number) => void): void {\n  for (let index = 0; index < count; index++) callback(index);\n}\nrepeat(2, () => console.log("Again"));\nrepeat(2, index => console.log(index.toFixed()));',
'A contextual () => void callback may return a value that the caller ignores. A function explicitly declared with : void cannot return an unrelated value.')
L(m,'overloads','Overloads, call signatures, and this','Choose a union or overload based on the input/output relationship.',
'Prefer a union parameter when all alternatives return the same type. Use overloads to describe meaningfully different call shapes or return types. The implementation signature must support them but is not itself a public overload. A this parameter documents the receiver without becoming a runtime argument.',
'function duplicate(value: string): string;\nfunction duplicate(value: number): number;\nfunction duplicate(value: string | number): string | number {\n  return typeof value === "string" ? value + value : value * 2;\n}\ntype Formatter = { (value: number): string; label: string };',
'Implement length(value: string | readonly unknown[]): number using a union rather than overloads. Then write a function with this: { title: string } and call it with .call().',
'function length(value: string | readonly unknown[]): number {\n  return value.length;\n}\nfunction heading(this: { title: string }): string {\n  return this.title.toUpperCase();\n}\nconsole.log(heading.call({ title: "Functions" }));',
'Overloads describe allowed calls; they do not run separate implementations. Preserve JavaScript receiver behavior when passing methods as callbacks.')
Q(m,'If an invoker always supplies an index, how should its callback parameter be typed?','index: number','index?: number','index: any','Optional means the invoker may omit it, not that a callback must use it.')
Q(m,'Can callers use an overload implementation signature that is not a declared overload?','No','Always','Only if it has optional parameters','Only the overload signatures describe the public call surface.')
Q(m,'Which is usually clearer for equal return behavior across input types?','A union parameter','Many redundant overloads','An any parameter','Use overloads when distinct call shapes or return relationships warrant them.')

m=M('generics','Build reusable generic APIs',[
('/docs/handbook/2/generics.html','Generics'),('/docs/handbook/2/functions.html#generic-functions','Generic functions')])
L(m,'generic-relations','Generics preserve relationships','Keep input and output types related without using any.',
'A type parameter captures a caller’s type and reuses it. It is useful when it connects multiple positions, such as array elements and a return value. The body must work for every allowed type. Unnecessary parameters make inference and reading harder.',
'function first<T>(items: readonly T[]): T | undefined {\n  return items[0];\n}\nconst title = first(["Types", "Objects"]); // string | undefined\ntype Page<T> = { items: T[]; total: number };\nconst page: Page<number> = { items: [1, 2], total: 2 };',
'Write mapValues<T, U>(items: readonly T[], convert: (item: T) => U): U[]. Call it to convert numbers into strings. Verify the inferred output.',
'function mapValues<T, U>(items: readonly T[], convert: (item: T) => U): U[] {\n  return items.map(convert);\n}\nconst labels = mapValues([1, 2], n => `${n} min`);\nconsole.log(labels);',
'Generics preserve information, but do not conjure runtime knowledge of T. Empty collections still need correct missing-value behavior.')
L(m,'constraints','Constraints, defaults, and key relationships','State the minimum capabilities a generic operation needs.',
'extends in a type parameter constrains allowed types. keyof can connect a key to the object it belongs to. Generic defaults provide a fallback type argument. Constraints let the implementation use promised members; they do not permit returning an arbitrary value as T.',
'function get<T, K extends keyof T>(object: T, key: K): T[K] {\n  return object[key];\n}\nconst minutes = get({ title: "Types", minutes: 10 }, "minutes");\ntype Result<T = string> = { value: T };',
'Write withLength<T extends { length: number }>(value: T): T. Log its length and return the same value. Try a string, array, and number. The number should fail.',
'function withLength<T extends { length: number }>(value: T): T {\n  console.log(value.length);\n  return value;\n}\nwithLength("Types");\nwithLength([1, 2]);\n// @ts-expect-error numbers do not have length\nwithLength(3);',
'A constrained T may include more properties than the constraint. Return the actual input when promising T; an object containing only the constraint can lose those properties.')
Q(m,'What does first<T>(items: T[]): T | undefined preserve?','The input element type and possible absence','A guaranteed first element','Only string values','T connects the input elements and output. undefined covers an empty array.')
Q(m,'What does K extends keyof T ensure?','K is a permitted key of T','All values of T are strings','The key exists on every unknown runtime object','The constraint connects the key argument to the declared object type.')
Q(m,'Can a function constrained to T extends { length: number } return any fresh { length: number } as T?','No; T may require additional properties','Yes, constraints erase additional fields','Only if strict is enabled','The constraint is a minimum capability, not the entire caller-specific type.')

m=M('operators','Derive types from existing information',[
('/docs/handbook/2/keyof-types.html','keyof'),('/docs/handbook/2/typeof-types.html','typeof'),('/docs/handbook/2/indexed-access-types.html','Indexed access types')])
L(m,'keyof-typeof','keyof and type-position typeof','Avoid repeating property and configuration types.',
'keyof produces permitted keys of a type. Type-position typeof gets the type of a variable or property. Runtime typeof returns a category string. These uses share spelling but do different jobs. A string index signature can make keyof include string and number.',
'const settings = { title: "TypeScript", minutes: 10 };\ntype Settings = typeof settings;\ntype SettingKey = keyof Settings; // "title" | "minutes"\nfunction read(key: SettingKey) { return settings[key]; }\nconsole.log(typeof settings); // "object" at runtime',
'Create a const object containing three feature flags. Derive its type with typeof, then derive its key union with keyof. Write an accessor that rejects an unknown flag.',
'const flags = { notes: true, exports: true, quizzes: false };\ntype Flag = keyof typeof flags;\nfunction enabled(flag: Flag): boolean { return flags[flag]; }\n// @ts-expect-error unknown flag\nenabled("payments");',
'keyof is not Object.keys(). It works on a static type and emits no list of runtime keys.')
L(m,'indexed','Indexed access and function extraction','Reuse property, element, parameter, and return types.',
'T["field"] looks up a property type. T[number] gets an array element type. ReturnType and Parameters derive information from function types. Use typeof fn when starting from a function value. This reduces drift when the source definition changes.',
'type Lesson = { id: string; minutes: number };\ntype Minutes = Lesson["minutes"];\nconst lessons = [{ id: "intro", minutes: 10 }];\ntype Item = typeof lessons[number];\nfunction makeLesson(id: string) { return { id, minutes: 10 }; }\ntype Created = ReturnType<typeof makeLesson>;',
'Write a buildUser(name: string, active: boolean) function. Derive its argument tuple and return object type using utility types. Do not manually repeat the types.',
'function buildUser(name: string, active: boolean) { return { name, active }; }\ntype Arguments = Parameters<typeof buildUser>;\ntype User = ReturnType<typeof buildUser>;\nconst args: Arguments = ["Johnny", true];\nconst user: User = buildUser(...args);',
'Types and values occupy different positions. Use typeof to bridge from a named value to its type, and avoid assuming a type expression executes a function.')
Q(m,'What is keyof { title: string; minutes: number }?','"title" | "minutes"','string | number values','An array of two strings','keyof produces a union of property keys, not a runtime array.')
Q(m,'How do you get the return type of a function value named build?','ReturnType<typeof build>','ReturnType<build>','typeof build() in a type alias','typeof build provides the function type to ReturnType.')
Q(m,'What does string[][number] represent?','string','number','The array length','Indexing an array type with number extracts its element type.')

m=M('transformations','Transform types with intent',[
('/docs/handbook/2/mapped-types.html','Mapped Types'),('/docs/handbook/2/conditional-types.html','Conditional Types'),('/docs/handbook/2/template-literal-types.html','Template Literal Types')])
L(m,'mapped','Mapped types, modifiers, and renamed keys','Derive a consistent object shape from another shape.',
'A mapped type iterates a union of keys. T[K] connects each key to its original value type. readonly and ? can be added or removed. An as clause remaps or filters keys. Prefer a readable built-in utility unless a custom transformation adds meaning.',
'type Flags<T> = { [K in keyof T]: boolean };\ntype Mutable<T> = { -readonly [K in keyof T]: T[K] };\ntype Complete<T> = { [K in keyof T]-?: T[K] };\ntype Getters<T> = {\n  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K]\n};',
'Given type Lesson = { title: string; minutes: number }, derive OptionalLesson with a mapped type. Then derive getter names getTitle and getMinutes without spelling them manually.',
'type Lesson = { title: string; minutes: number };\ntype OptionalLesson = { [K in keyof Lesson]?: Lesson[K] };\ntype Getters<T> = {\n  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K]\n};\nconst getters: Getters<Lesson> = { getTitle: () => "Types", getMinutes: () => 10 };',
'Mapped types transform descriptions, not runtime objects. Code must still implement any generated methods or fields.')
L(m,'conditional','Conditional types, infer, and string patterns','Recognize advanced type transformations and their limits.',
'T extends U ? X : Y selects a type based on assignability. infer captures a matched piece. A conditional with a naked type parameter distributes over unions; wrapping it in a tuple can prevent distribution. Template literal types compose string patterns and can create large unions.',
'type ElementOf<T> = T extends readonly (infer U)[] ? U : T;\ntype ToArray<T> = T extends unknown ? T[] : never;\ntype Together<T> = [T] extends [unknown] ? T[] : never;\ntype EventName = `${"lesson" | "quiz"}Completed`;\ntype Separate = ToArray<string | number>; // string[] | number[]\ntype Combined = Together<string | number>; // (string | number)[]',
'Create Unwrap<T> that extracts a Promise payload and otherwise returns T. Derive a completion event name from title | minutes using a template literal. Explain the distributive behavior of Unwrap on a union.',
'type Unwrap<T> = T extends Promise<infer U> ? U : T;\ntype A = Unwrap<Promise<string>>;\ntype B = Unwrap<Promise<string> | number>; // string | number\ntype Field = "title" | "minutes";\ntype Changed = `${Field}Changed`;',
'Advanced type computation can become harder to maintain than an explicit type. Keep recursive and string-union transformations bounded. Unwrap here is shallow; Awaited handles recursive promise-like unwrapping.')
Q(m,'Does a mapped type create runtime object properties?','No, it creates a type description','Yes, on import','Only with noEmit disabled','Runtime objects still need an implementation.')
Q(m,'What does infer do inside a conditional type?','Captures a type from a matching shape','Reads a runtime JSON value','Disables union distribution','infer introduces a type variable for a matched part of the tested type.')
Q(m,'What does ToArray<T> = T extends unknown ? T[] : never produce for string | number?','string[] | number[]','Only string[]','Always never','The naked type parameter causes the conditional to distribute over each union member.')

m=M('utilities','Use the standard utility types',[
('/docs/handbook/utility-types.html','Utility Types')])
L(m,'object-utilities','Transform object contracts','Use built-in helpers for projections and update shapes.',
'Partial makes properties optional. Required makes them required. Readonly restricts top-level writes. Pick selects keys; Omit removes keys. Record assigns a value type to keys. These are shallow static transformations: an optional update object still needs business-rule checks.',
'type Lesson = { id: string; title: string; minutes: number };\ntype Update = Partial<Pick<Lesson, "title" | "minutes">>;\ntype Preview = Omit<Lesson, "minutes">;\ntype Snapshot = Readonly<Lesson>;\nconst patch: Update = { title: "New title" };',
'Create User with id, email and passwordHash. Derive PublicUser without passwordHash. Create a settings patch that permits only email, never id. Explain why this does not sanitize an arbitrary runtime object.',
'type User = { id: string; email: string; passwordHash: string };\ntype PublicUser = Omit<User, "passwordHash">;\ntype UserPatch = Partial<Pick<User, "email">>;\nfunction publicUser(user: User): PublicUser {\n  return { id: user.id, email: user.email };\n}',
'Omit changes the type, not the runtime contents. Explicitly construct public outputs when fields must actually be removed.')
L(m,'union-utilities','Extract unions, signatures, and promise results','Read utility types used in library APIs.',
'Exclude removes union members; Extract keeps matching members. NonNullable removes null and undefined. Awaited models recursive promise-like unwrapping. Parameters, ReturnType, ConstructorParameters and InstanceType extract callable or constructable information. ThisParameterType, OmitThisParameter and ThisType describe receiver relationships. NoInfer limits inference from a chosen position.',
'type State = "draft" | "published" | "archived";\ntype Visible = Exclude<State, "archived">;\ntype Published = Extract<State, "published" | "missing">;\ntype Text = NonNullable<string | null | undefined>;\ntype Payload = Awaited<Promise<Promise<number>>>;\nfunction choose<T>(items: T[], fallback: NoInfer<T>): T {\n  return items[0] ?? fallback;\n}',
'Use Exclude to remove error from idle | loading | ready | error. Derive the instance and constructor-argument types of a class with a string constructor. Explain when NoInfer could prevent an unintended wider union.',
'type State = "idle" | "loading" | "ready" | "error";\ntype NormalState = Exclude<State, "error">;\nclass Lesson { constructor(public title: string) {} }\ntype Input = ConstructorParameters<typeof Lesson>;\ntype Output = InstanceType<typeof Lesson>;\nconst input: Input = ["Types"];\nconst lesson: Output = new Lesson(...input);',
'NoInfer is available in TypeScript 5.4+. ThisType is a contextual marker, not runtime binding. Utility types help you express relationships, but do not perform runtime transformations.')
Q(m,'Does assigning an object to Omit<User, "secret"> remove secret at runtime?','No; explicitly construct a sanitized object','Yes, automatically','Only with strict enabled','Type erasure does not delete fields. A projection function must actually remove them.')
Q(m,'Which utility removes null and undefined from a type?','NonNullable<T>','Required<T>','Partial<T>','NonNullable filters nullish union members. Required changes property optionality.')
Q(m,'What does NoInfer<T> influence?','Inference from that type position','Runtime input validation','Whether properties are readonly','NoInfer blocks that position from contributing inference candidates; it still checks compatibility.')

m=M('classes','Classes, compatibility, and composition',[
('/docs/handbook/2/classes.html','Classes'),('/docs/handbook/type-compatibility.html','Type Compatibility'),('/docs/handbook/mixins.html','Mixins'),
('https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Using_classes','MDN: Classes')])
L(m,'class-contracts','Initialization, inheritance, and privacy','Separate class runtime behavior from type-level restrictions.',
'Constructors initialize fields; strictPropertyInitialization checks required fields. implements checks that a class satisfies a contract but does not create members. extends establishes runtime inheritance. TypeScript private is mainly a type-checking restriction; JavaScript #private provides runtime privacy. readonly does not freeze nested values.',
'interface Named { title: string }\nclass Lesson implements Named {\n  #views = 0;\n  constructor(public readonly id: string, public title: string) {}\n  view(): number { return ++this.#views; }\n}\nconst lesson = new Lesson("a", "Types");\nconsole.log(lesson.view());',
'Create abstract class Content with abstract summary(): string. Implement TextContent with a constructor parameter property. Show why implements alone would not supply summary.',
'abstract class Content { abstract summary(): string; }\nclass TextContent extends Content {\n  constructor(public text: string) { super(); }\n  summary(): string { return this.text.slice(0, 40); }\n}\nconsole.log(new TextContent("Learn TypeScript").summary());',
'A definite-assignment assertion (!) suppresses an initialization check; it does not initialize the field. Check JavaScript this binding when passing instance methods.')
L(m,'compatibility','Structural typing, variance, and mixins','Understand why assignments succeed or fail.',
'Most compatibility is structural: required members matter more than declaration names. Private and protected class members add origin constraints. Function parameter checking under strictFunctionTypes protects against overly narrow callbacks, with a method-syntax exception. Generics that produce T and consume T have different compatibility directions. Compose capabilities when inheritance does not fit.',
'type Animal = { name: string };\ntype Dog = Animal & { bark(): void };\ntype Producer<T> = { make(): T };\ntype Consumer<T> = { consume: (value: T) => void };\nconst dogMaker: Producer<Dog> = { make: () => ({ name: "Ada", bark() {} }) };\nconst animalMaker: Producer<Animal> = dogMaker;\nconst consumeAnimal: Consumer<Animal> = { consume: a => console.log(a.name) };\nconst consumeDog: Consumer<Dog> = consumeAnimal;',
'Create two separately named interfaces with identical fields and assign one to the other. Then explain why a callback accepting only Dog cannot safely handle every Animal.',
'interface A { id: string }\ninterface B { id: string }\nconst b: B = { id: "lesson" };\nconst a: A = b;\ntype Animal = { name: string };\ntype Dog = Animal & { bark(): void };\nconst dogsOnly = (dog: Dog) => dog.bark();\n// @ts-expect-error some Animals cannot bark\nconst animals: (animal: Animal) => void = dogsOnly;',
'Variance annotations in/out are advanced tools, not a way to override structural compatibility. Mixins use class-expression factories with constructor constraints; simple function composition is often easier to maintain.')
Q(m,'Does implements create the interface’s methods?','No, the class must implement them','Yes, with empty bodies','Only when methods are public','implements is a compatibility check, not code generation.')
Q(m,'Which offers JavaScript runtime privacy?','#field','TypeScript private alone','readonly field','#private fields have runtime access restrictions; TypeScript private is primarily static.')
Q(m,'Can a handler requiring Dog safely substitute for a handler accepting every Animal?','No; some Animals cannot bark','Yes, because Dog has more properties','Always under strictFunctionTypes','The caller may pass an Animal that is not a Dog, so the narrower callback is unsafe.')

m=M('modules','Modules and runtime-aware resolution',[
('/docs/handbook/2/modules.html','Modules'),('/docs/handbook/modules/theory.html','Module theory'),('/docs/handbook/modules/reference.html','Module reference'),
('/docs/handbook/modules/guides/choosing-compiler-options.html','Choosing module options'),
('https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules','MDN: Modules')])
L(m,'module-boundaries','ES modules, type imports, and CommonJS','Distinguish runtime imports from type-only dependencies.',
'A file with module syntax normally has its own scope. export {} can make a file a module without exporting a value. import type is erased and cannot be used as a runtime value. ESM and CommonJS use different loading and interop rules. package.json type and file extensions influence Node module format.',
'// model.ts\nexport type Lesson = { id: string; title: string };\nexport const version = 1;\n\n// usage.ts (separate file)\n// import { version, type Lesson } from "./model.js";\n// const lesson: Lesson = { id: "a", title: "Modules" };',
'Split a Lesson type and a formatter into two files. Import only the type where no runtime value is needed. Inspect the output to confirm that the type import disappears.',
'// model.ts\nexport type Lesson = { title: string };\n\n// formatter.ts (separate file)\n// import type { Lesson } from "./model.js";\n// export function format(lesson: Lesson) { return lesson.title; }',
'Module specifiers must work in the actual host. A path the checker understands is not automatically a path the runtime understands. Multi-file examples are labeled and need separate files.')
L(m,'resolution','Choose module settings for the host','Diagnose a module that type-checks but fails to load.',
'TypeScript imitates a host’s resolution to find code and declarations. For Node ESM, use a compatible Node module mode and valid emitted import specifiers. For bundler-managed apps, bundler resolution with preserve or an appropriate ES module output may fit. paths does not rewrite emitted imports. package exports, imports and type conditions affect package resolution.',
'{\n  "compilerOptions": {\n    "module": "NodeNext",\n    "moduleResolution": "NodeNext",\n    "target": "ES2022",\n    "strict": true,\n    "outDir": "dist"\n  }\n}',
'Compare a Node ESM project and a bundler app. Identify which tool executes or bundles the output. Explain why adding paths: { "@/*": ["src/*"] } alone cannot teach Node to load @/lesson.',
'Node ESM: use a matching Node module mode, package.json "type": "module", and runtime-valid relative import extensions.\n\nBundler app: use moduleResolution "bundler" with module "preserve" or the documented ES module mode supported by the tool. Configure aliases in the bundler as well.\n\nDebug with: npx tsc -p tsconfig.json --traceResolution',
'Use the host-specific guide before copying tsconfig options. esModuleInterop affects some emit and checking behavior; it does not make every runtime interop pattern equivalent.',language='text')
Q(m,'Does paths rewrite JavaScript import specifiers?','No','Always','Only when aliases start with @','paths informs resolution for checking. Configure the runtime or bundler separately.')
Q(m,'What happens to import type in JavaScript output?','It is erased','It becomes require()','It validates the imported object','A type-only import has no runtime value import.')
Q(m,'What should drive module and moduleResolution choices?','The actual runtime or bundler host','The shortest config','Whether the project uses interfaces','The checker and output must agree with how the host loads modules.')

m=M('configuration','Compiler options and scalable projects',[
('/docs/handbook/tsconfig-json.html','tsconfig.json'),('/docs/handbook/compiler-options.html','Compiler CLI'),
('/docs/handbook/project-references.html','Project References'),('/docs/handbook/configuring-watch.html','Watch configuration'),('/tsconfig/','TSConfig Reference')])
L(m,'strict-config','Strictness, targets, libraries, and emit','Read compiler configuration as a set of concrete decisions.',
'target controls output syntax and default library choices; lib controls available API declarations. Neither adds a runtime polyfill. strict is a family of checks; noUncheckedIndexedAccess and exactOptionalPropertyTypes are separate useful choices. noEmit, noEmitOnError, declaration, sourceMap, rootDir and outDir affect output. include/exclude select root files, but imports can bring excluded files into a program.',
'{\n  "compilerOptions": {\n    "target": "ES2022",\n    "lib": ["ES2022", "DOM"],\n    "strict": true,\n    "noUncheckedIndexedAccess": true,\n    "exactOptionalPropertyTypes": true,\n    "noEmit": true\n  },\n  "include": ["src/**/*.ts"]\n}',
'Turn on noUncheckedIndexedAccess and inspect an array index. With exactOptionalPropertyTypes enabled, compare an absent optional property with a present property set to undefined. Explain what lib does not install.',
'type Settings = { title?: string };\nconst missing: Settings = {};\n// Under exactOptionalPropertyTypes this needs title?: string | undefined:\n// const present: Settings = { title: undefined };\nconst items: string[] = [];\nconst first: string | undefined = items[0];\nconsole.log(first ?? "No item");',
'Passing compilation does not guarantee platform APIs exist. Treat skipLibCheck as a tradeoff, not a way to fix mismatched declarations. Avoid suppressions before understanding the diagnostic.',language='text')
L(m,'build-workflow','Build tools, watch mode, and project references','Keep transpilation, type checking, and multi-project builds coordinated.',
'Babel and many fast bundlers can remove types without checking them. Run tsc separately in CI. Watch mode repeats checks on changes. Incremental builds reuse work. Project references split larger systems into composite projects; build mode orders dependencies and uses declaration outputs. They are useful when boundaries justify the extra configuration.',
'npx tsc -p tsconfig.json --noEmit\nnpx tsc -p tsconfig.json --watch\nnpx tsc -b\nnpx tsc -b --clean',
'Design two packages, domain and app. App references domain. Write a solution config and state what composite and declaration outputs provide. Also name the command CI should run if a bundler emits the app.',
'// solution tsconfig.json\n{ "files": [], "references": [{ "path": "./domain" }, { "path": "./app" }] }\n\n// app tsconfig.json references domain; referenced projects enable composite.\n// Build dependency projects: npx tsc -b\n// For a bundler app, also run an appropriate separate type-check script in CI.',
'Watch settings tune how changes are detected, not the type system. MSBuild, Gulp and framework-specific recipes are optional integration references, not prerequisites for every learner.',language='text')
Q(m,'Does lib: ["ES2022", "DOM"] install those APIs into a runtime?','No; it supplies declarations','Yes, it polyfills them','Only with target ES2022','lib controls static API knowledge. Actual runtime support is separate.')
Q(m,'Does strict include noUncheckedIndexedAccess?','No, configure it separately','Yes, always','Only for readonly arrays','Some additional safety flags are not part of the strict family.')
Q(m,'What should accompany a transpile-only bundler?','A separate type-check command','Nothing; removing types proves correctness','Only source maps','Run tsc or a suitable checker separately so build success does not hide type errors.')

m=M('declarations','Consume and publish declaration files',[
('/docs/handbook/2/type-declarations.html','Type Declarations'),('/docs/handbook/declaration-files/introduction.html','Writing declarations'),
('/docs/handbook/declaration-files/by-example.html','Declarations by example'),('/docs/handbook/declaration-files/library-structures.html','Library structures'),
('/docs/handbook/declaration-files/publishing.html','Publishing declarations'),('/docs/handbook/declaration-files/do-s-and-don-ts.html','Declaration guidelines')])
L(m,'consume-types','Find and describe library types','Explain what a declaration file promises and what it cannot supply.',
'A .d.ts file describes an existing implementation; it does not implement one. Types may be built in, bundled with a package, installed through @types, or authored locally. declare describes a value expected at runtime. A blanket declare module can hide mistakes by turning a module into any.',
'// Example declarations for an existing runtime library:\nexport interface Lesson { id: string; title: string }\nexport declare function findLesson(id: string): Lesson | undefined;\nexport declare class Catalog {\n  constructor(initial: Lesson[]);\n  find(id: string): Lesson | undefined;\n}',
'Describe an existing library function formatMinutes(number): string in a .d.ts file. Explain what else must exist for importing it to work at runtime. Check whether your actual library already bundles types before installing @types.',
'// index.d.ts; pairs with an actual runtime index.js implementation\nexport declare function formatMinutes(minutes: number): string;\n\n// Declarations tell the checker the signature.\n// The package still needs JavaScript that exports formatMinutes.',
'A declaration mismatch can make incorrect code compile. Validate declarations against actual behavior, including missing values, overloads and callback invocation rules.')
L(m,'publish-types','Generate, package, and test declarations','Keep a library’s JavaScript and public type surface aligned.',
'Generate declarations from implementation when possible. Set package metadata so consumers can find them; modern exports may need type conditions alongside runtime paths. Dependencies exposed by public declarations must be available to consumers. Global, module, callable, class and plugin libraries need matching declaration structures. Declaration merging and augmentation extend existing contracts, not runtime behavior.',
'{\n  "compilerOptions": {\n    "strict": true,\n    "declaration": true,\n    "declarationMap": true,\n    "outDir": "dist"\n  }\n}\n\n// package.json can point "types" at "./dist/index.d.ts".',
'Write an interface twice with compatible additional members to see declaration merging. Then describe a publishing checklist: runtime entry, type entry, dependent types, and a consumer compile test.',
'interface CourseOptions { title: string }\ninterface CourseOptions { sequential?: boolean }\nconst options: CourseOptions = { title: "Types", sequential: true };\n\n// Consumer checklist: resolve package entry and types; import a public API;\n// verify valid calls compile and invalid calls fail; run runtime smoke tests.',
'Module augmentation names an existing module and must obey merging rules. It cannot create working runtime members by itself. Use declaration templates matching how the library is actually loaded.',language='text')
Q(m,'What does a .d.ts file provide?','Type information without a JavaScript implementation','A complete runtime implementation','A runtime schema validator','Declarations describe existing values and APIs. They do not emit the implementation.')
Q(m,'Should public declaration dependencies be available to consumers?','Yes','No, devDependencies always suffice','Only during the author’s build','If exported types reference another package, consumers need its declarations to resolve.')
Q(m,'Does declaration merging add runtime methods?','No','Yes, as empty functions','Only for interfaces','Merging combines static declarations, while runtime behavior needs actual code.')

m=M('migration','Adopt TypeScript in JavaScript projects',[
('/docs/handbook/intro-to-js-ts.html','TypeScript in JavaScript'),('/docs/handbook/jsdoc-supported-types.html','JSDoc Reference'),
('/docs/handbook/type-checking-javascript-files.html','Checking JavaScript'),('/docs/handbook/migrating-from-javascript.html','Migration'),
('/docs/handbook/declaration-files/dts-from-js.html','Declarations from JavaScript')])
L(m,'jsdoc','Check JavaScript using JSDoc','Add useful checking before renaming every file.',
'allowJs includes JavaScript in a project. checkJs or @ts-check enables diagnostics for it. JSDoc can describe parameters, results, object shapes, imports and generic relationships. JavaScript inference has some different rules from .ts files; review the JS checking reference instead of assuming identical behavior.',
'// @ts-check\n/**\n * @param {number} minutes\n * @returns {string}\n */\nfunction label(minutes) { return `${minutes} min`; }\nconsole.log(label(10));',
'Create a .js file with @ts-check. Define a Lesson typedef containing title and minutes. Annotate a function taking that Lesson. Introduce an invalid argument and confirm a diagnostic.',
'// @ts-check\n/** @typedef {{ title: string, minutes: number }} Lesson */\n/** @param {Lesson} lesson */\nfunction summary(lesson) { return `${lesson.title}: ${lesson.minutes}`; }\nsummary({ title: "Types", minutes: 10 });',
'JSDoc offers @template, @satisfies, imported types and many other tags. Use the supported-tag reference; not every documentation tag changes checking.',language='js')
L(m,'incremental-migration','Migrate boundaries and manage escape hatches','Improve checking without hiding every diagnostic.',
'Migrate in small slices. Start with shared domain types and external-data boundaries, then strengthen checks. Use unknown and runtime validation for uncertainty. @ts-expect-error is useful for intentional negative tests because it reports when the expected error disappears; @ts-ignore does not. Avoid large any regions and blanket @ts-nocheck.',
'function minutesLabel(minutes: number): string { return `${minutes} min`; }\n// Intentional negative type test; do not run this as application behavior.\n// @ts-expect-error minutes must be numeric\nminutesLabel("10");',
'Choose one JavaScript module and identify its inputs, outputs and dependencies. Write a migration plan that includes baseline runtime tests, checkJs, conversion to .ts, and strict checking. Fix mismatches rather than casting every error away.',
'1. Record current behavior with meaningful tests.\n2. Enable checking for the selected JS module and annotate its boundaries.\n3. Validate external data and replace accidental any.\n4. Rename the selected module to .ts and correct import/build configuration.\n5. Run strict type checking and runtime tests; inspect changes before expanding.',
'Generating .d.ts files from JS can help library consumers without converting implementation files. A migration should preserve behavior while improving the contracts you can verify.',language='text')
Q(m,'Which setting enables diagnostics in included JavaScript files?','checkJs','allowJs alone always checks every error','declarationMap','allowJs includes files; checkJs enables checking. @ts-check can opt in per file.')
Q(m,'Why use @ts-expect-error for an intentional negative type test?','It reports when the expected error disappears','It validates runtime behavior','It suppresses the entire file','An unused expect-error directive is itself a diagnostic, which helps maintain negative tests.')
Q(m,'What is a useful early migration boundary?','Untrusted inputs and shared domain contracts','Every file annotated any','All diagnostics disabled','Boundary contracts limit the spread of uncertainty and give incremental migration practical value.')

m=M('async-dom','Async data and browser applications',[
('https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Using_promises','MDN: Promises'),
('/docs/handbook/dom-manipulation.html','DOM Manipulation'),('/docs/handbook/2/narrowing.html','Runtime guards'),
('https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/Network_requests','MDN: Fetching data')])
L(m,'async-validation','Promises, errors, and validated API data','Handle both network failures and invalid payloads.',
'An async function returns a Promise. Promise<T> describes the success value, not a typed rejection channel. Fetch can resolve for HTTP errors, so check response.ok. Treat parsed JSON as unknown and validate its fields. Catch variables under strict checking are unknown and need narrowing.',
'type Lesson = { title: string };\nfunction isLesson(value: unknown): value is Lesson {\n  return typeof value === "object" && value !== null\n    && "title" in value && typeof value.title === "string";\n}\nasync function loadLesson(url: string): Promise<Lesson> {\n  const response = await fetch(url);\n  if (!response.ok) throw new Error(`HTTP ${response.status}`);\n  const data: unknown = await response.json();\n  if (!isLesson(data)) throw new Error("Invalid lesson");\n  return data;\n}',
'Wrap a load call in try/catch. Produce a readable error message without assuming the thrown value is an Error. Identify how you would test HTTP failure and a successful response with invalid JSON shape.',
'async function run(): Promise<void> {\n  try {\n    const response = await fetch("/lesson.json");\n    if (!response.ok) throw new Error(`HTTP ${response.status}`);\n    const data: unknown = await response.json();\n    console.log(data); // validate before domain use\n  } catch (error: unknown) {\n    const message = error instanceof Error ? error.message : "Unknown failure";\n    console.error(message);\n  }\n}',
'A return annotation Promise<Lesson> does not validate response.json(). Test malformed fields, missing fields, null, HTTP errors and rejected network requests.')
L(m,'dom-events','DOM nullability, element types, and events','Use browser elements without unsafe assumptions.',
'A DOM query may return null and may select an unexpected element type. Narrow with instanceof when markup could differ. Event target is a general EventTarget, not necessarily an input. Typed querySelector overloads can help known tags, but a generic annotation alone does not verify the actual element.',
'const field = document.querySelector("#title");\nif (field instanceof HTMLInputElement) {\n  field.addEventListener("input", () => {\n    console.log(field.value);\n  });\n}\nconst button = document.createElement("button");\nbutton.textContent = "Save";',
'Query #minutes. Verify it is an HTMLInputElement, read valueAsNumber, and reject NaN. Explain why document.getElementById("minutes")! is not enough evidence.',
'const input = document.getElementById("minutes");\nif (input instanceof HTMLInputElement) {\n  const minutes = input.valueAsNumber;\n  if (Number.isFinite(minutes)) console.log(minutes);\n  else console.error("Enter a number");\n}',
'Non-null assertions do not check elements at runtime. Use textContent for text rather than injecting untrusted markup. DOM lib declarations do not make document exist in Node.')
Q(m,'Does fetch reject automatically for every HTTP 404 response?','No; inspect response.ok or status','Yes','Only with a Promise annotation','HTTP error responses can resolve normally; network failures are a separate failure path.')
Q(m,'Does Promise<Lesson> validate parsed JSON?','No','Yes, recursively','Only if Lesson is an interface','The annotation is static. Parsed external input needs runtime validation.')
Q(m,'What is a robust check before accessing an uncertain element’s value?','element instanceof HTMLInputElement','element! alone','element as HTMLInputElement always validates it','instanceof establishes runtime element identity and narrows its type.')

m=M('specialized','Specialized language and integration features',[
('/docs/handbook/enums.html','Enums'),('/docs/handbook/symbols.html','Symbols'),('/docs/handbook/iterators-and-generators.html','Iterators'),
('/docs/handbook/jsx.html','JSX'),('/docs/handbook/react.html','React integration'),('/docs/handbook/namespaces.html','Namespaces'),
('/docs/handbook/namespaces-and-modules.html','Namespaces and Modules'),('/docs/handbook/triple-slash-directives.html','Triple-slash directives')])
L(m,'enum-iterables','Enums, symbols, and generators','Recognize features that have runtime behavior as well as types.',
'Enums generally emit an object; numeric enums can include reverse mappings. Literal unions and const objects are alternatives. unique symbol can identify a particular symbol type. Iterables expose Symbol.iterator; for...of reads values while for...in reads enumerable property keys. A generator yields values lazily.',
'enum Status { Draft = "draft", Published = "published" }\nconst key: unique symbol = Symbol("lesson");\nfunction* ids(): Generator<string, void, unknown> {\n  yield "intro";\n  yield "arrays";\n}\nfor (const id of ids()) console.log(id);',
'Replace an enum with an as const object and derive its value union. Write a generator yielding 1 through 3. Explain why a typed array is different from an array with a TypeScript element annotation.',
'const Status = { Draft: "draft", Published: "published" } as const;\ntype StatusValue = typeof Status[keyof typeof Status];\nfunction* count(): Generator<number, void, unknown> {\n  for (let n = 1; n <= 3; n++) yield n;\n}\nconsole.log([...count()]);',
'const enum in published declarations has consumer pitfalls. Typed arrays such as Uint8Array are runtime binary-data structures; number[] is a general JavaScript array type.')
L(m,'jsx-legacy','JSX, namespaces, and ambient integrations','Locate the correct integration reference without mixing models.',
'JSX is optional syntax whose meaning depends on a factory or runtime. .tsx files and the jsx compiler option configure transformation; intrinsic elements and component signatures control checking. In TSX, use as assertions rather than angle-bracket assertions. Namespaces and triple-slash directives appear in legacy or ambient integrations; modern module-based applications normally use imports and exports.',
'// A component contract independent of a particular JSX runtime:\ntype LessonCardProps = { title: string; completed: boolean };\nfunction cardLabel(props: LessonCardProps): string {\n  return `${props.title}: ${props.completed ? "Complete" : "Ready"}`;\n}\n// In a React .tsx project, a component can accept this props shape.\n// Install/configure that project’s React runtime and type declarations.',
'Create a props type for title and an onComplete callback. Explain which parts come from TypeScript and which need the UI library’s runtime. Identify a legacy namespace or triple-slash directive in a dependency and read its matching reference.',
'type LessonProps = { title: string; onComplete: (id: string) => void };\nfunction complete(props: LessonProps, id: string): void {\n  props.onComplete(id);\n}\n\n// Ambient dependency reference example in a declaration file:\n// /// <reference types="node" />\n// This requests declarations, not a runtime import.',
'TypeScript does not include a React runtime. A namespace is not an ES module import. Match declaration structure and JSX options to the actual integration rather than copying framework-specific recipes blindly.')
Q(m,'Which generally emits JavaScript behavior rather than being fully erased?','An enum declaration','A type alias','An interface','Enums typically emit a runtime object. Interfaces and aliases are erased.')
Q(m,'What does for...of iterate?','Values produced by an iterable','Only object property names','Only array indexes as strings','for...of uses the iterable protocol; for...in enumerates property keys.')
Q(m,'Does TypeScript alone provide React’s runtime?','No','Yes, through JSX types','Only in .tsx files','TypeScript can check and transform JSX, but the UI runtime is a separate dependency.')

m=M('advanced-runtime','Decorators, disposal, and advanced runtime topics',[
('/docs/handbook/release-notes/typescript-5-0.html#decorators','Standard decorators'),('/docs/handbook/decorators.html','Legacy decorators'),
('/docs/handbook/variable-declarations.html#using-declarations','Resource disposal'),
('https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Resource_management','MDN: Resource management'),
('https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Meta_programming','MDN: Meta-programming'),
('https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Memory_management','MDN: Memory management')])
L(m,'decorator-models','Standard and legacy decorators','Identify the decorator model a project actually uses.',
'Modern TypeScript supports a standard decorator model with target/context arguments and initializer hooks. Older experimentalDecorators APIs use different signatures and rules. Standard decorators do not support legacy parameter decorators or emitDecoratorMetadata in the same way. A decorator can alter runtime behavior; it is not just a type annotation.',
'function logged<This, Args extends unknown[], Return>(\n  original: (this: This, ...args: Args) => Return,\n  context: ClassMethodDecoratorContext<This, (this: This, ...args: Args) => Return>\n) {\n  return function (this: This, ...args: Args): Return {\n    console.log(String(context.name));\n    return original.apply(this, args);\n  };\n}\nclass Catalog {\n  @logged\n  title(): string { return "TypeScript"; }\n}',
'Read the project’s compiler settings before using a decorator example. Explain why a legacy (target, key, descriptor) method decorator cannot simply be dropped into the standard decorator model. Predict the log for new Catalog().title().',
'Standard method decorators receive the original method and a context object.\nA replacement must preserve the receiver, argument and return relationships.\nCalling new Catalog().title() logs "title" before returning "TypeScript".\n\nLegacy examples require the legacy compiler model. Do not enable flags just to silence an incompatible example.',
'Decorators can affect initialization and composition order. Use them when a library or repeated runtime behavior warrants them, and test the resulting behavior.',language='text')
L(m,'resource-lifecycle','Resource management and platform behavior','Explain disposal and recognize what types cannot manage for you.',
'using disposes a resource on scope exit through Symbol.dispose. await using awaits asynchronous disposal through Symbol.asyncDispose. The await in await using applies to disposal; awaiting acquisition is a separate expression. Runtime support or polyfills and matching declarations are still needed. Garbage collection is not a substitute for closing external resources.',
'// Illustrative modern-runtime example; requires disposable API support.\nclass Resource {\n  [Symbol.dispose](): void { console.log("Closed"); }\n}\n{\n  using resource = new Resource();\n  console.log("Working");\n}\n// "Working", then "Closed"',
'Explain the difference between await using resource = acquire() and await using resource = await acquireAsync(). Then describe a try/finally fallback for closing a resource. Identify where Proxy/Reflect or memory-management knowledge might matter in debugging.',
'const resource = { close() { console.log("Closed"); } };\ntry {\n  console.log("Working");\n} finally {\n  resource.close();\n}\n// await using awaits disposal; a separate await awaits asynchronous acquisition.',
'TypeScript cannot prevent retained references or guarantee external resources close. Treat decorators, disposal and metaprogramming as targeted advanced skills, with actual runtime tests.',language='text')
Q(m,'Are standard and legacy decorator signatures interchangeable?','No','Always','Only for methods','They use different APIs and semantics. Match examples to the project’s decorator model.')
Q(m,'What does await using specifically await?','Asynchronous disposal','Acquisition automatically in every expression','Garbage collection','Awaiting acquisition may require a separate await on the initializer expression.')
Q(m,'Does adding declarations for Symbol.dispose supply missing runtime support?','No','Yes','Only with strict enabled','Declarations inform the checker. Runtime features or polyfills must exist separately.')

m=M('capstone','Build and verify a typed learning catalog',[
('/docs/handbook/2/narrowing.html','Boundary validation'),('/docs/handbook/2/generics.html','Generic API relationships'),
('/docs/handbook/2/objects.html','Domain shapes'),('/docs/handbook/2/modules.html','Module boundaries')])
L(m,'capstone-model','Capstone: design the domain and validate input','Create a typed catalog that rejects malformed data.',
'Build a small catalog with Lesson { id, title, minutes }, a validator accepting unknown, and a result union separating success from failure. Requirements: reject missing or blank IDs/titles and non-finite or negative minutes; handle null; do not trust a type assertion at the boundary. The examples folder contains a complete reference implementation.',
'type Lesson = { id: string; title: string; minutes: number };\ntype Result<T> = { ok: true; value: T } | { ok: false; error: string };\nfunction parseText(input: unknown): Result<string> {\n  return typeof input === "string" && input.trim() !== ""\n    ? { ok: true, value: input }\n    : { ok: false, error: "Expected non-empty text" };\n}',
'Implement isLesson(value: unknown): value is Lesson using real checks. Try valid data, null, missing title, NaN, negative minutes and a blank ID. Keep validation separate from display logic.',
'type Lesson = { id: string; title: string; minutes: number };\nfunction isLesson(value: unknown): value is Lesson {\n  return typeof value === "object" && value !== null\n    && "id" in value && typeof value.id === "string" && value.id.trim() !== ""\n    && "title" in value && typeof value.title === "string" && value.title.trim() !== ""\n    && "minutes" in value && typeof value.minutes === "number"\n    && Number.isFinite(value.minutes) && value.minutes >= 0;\n}',
'Define acceptance criteria before implementation. Duplicate IDs are a catalog-level rule, not an individual Lesson rule; check them when parsing the collection.')
L(m,'capstone-queries','Capstone: typed queries and verification','Combine generics, immutability, and meaningful tests.',
'Add a generic getProperty, a totalMinutes query, an immutable title update and a parser that rejects duplicate IDs. Verify both static contracts and runtime outcomes. Do not mark practical mastery just because slides are complete. The quiz checks concepts; the project rubric checks application.',
'type Lesson = { id: string; title: string; minutes: number };\nfunction getProperty<T, K extends keyof T>(value: T, key: K): T[K] {\n  return value[key];\n}\nfunction totalMinutes(lessons: readonly Lesson[]): number {\n  return lessons.reduce((sum, lesson) => sum + lesson.minutes, 0);\n}',
'Build the project in examples/catalog.ts or write your own. Meet the rubric in examples/README.md: validation, duplicate rejection, typed lookup, immutable updates, exhaustive result handling, type tests and runtime tests.',
'type Lesson = { id: string; title: string; minutes: number };\nfunction rename(lessons: readonly Lesson[], id: string, title: string): Lesson[] {\n  if (!title.trim()) throw new Error("Title is required");\n  return lessons.map(lesson => lesson.id === id ? { ...lesson, title } : lesson);\n}\nconst original = [{ id: "a", title: "Types", minutes: 10 }];\nconst updated = rename(original, "a", "Everyday types");\nconsole.log(original[0]?.title, updated[0]?.title);',
'Run npx tsc --noEmit and actual runtime tests. A typed return contract and an exhaustive switch protect maintenance; edge-case tests verify the behavior your users experience.')
Q(m,'Where should duplicate lesson IDs be rejected?','When validating the catalog collection','Only by the string type','By an as Lesson[] assertion','Uniqueness is a collection-level invariant that needs runtime logic.')
Q(m,'Which test targets real boundary behavior?','Rejecting null, blank IDs, invalid minutes and duplicate IDs','Only checking that a function exists','Only using as Lesson[] on sample JSON','Malformed inputs exercise the validator and business rules rather than mirroring the implementation.')
Q(m,'Does reading every slide establish practical mastery?','No; apply the skills and meet the project rubric','Yes, automatically','Only after refreshing','Completion tracks learning activity. Demonstrated skill requires solving and verifying practical tasks.')

previous=json.loads((ROOT/'course.json').read_text())
course={'schemaVersion':1,'id':'ts-skills-complete-v1','title':'TypeScript',
    'description':'A skills-based path through TypeScript foundations, advanced types, runtime boundaries, tooling and library integration. MDN provides JavaScript foundations; the official TypeScript documentation supplies TypeScript-specific material. Original examples and self-assessed exercises accompany each lesson.',
    'sections':modules,
    'finalQuiz':{'id':'ts-final-skills','type':'quiz','title':'Final assessment · Apply your TypeScript judgment','skill':'Integrated TypeScript judgment','questions':[]},
    'settings':{**previous['settings'],'passScore':80,'allowRetakes':True,'sequential':True,'requireLessons':True,'unlockAll':True,'showLessonDetails':False}}
# Final assessment uses fresh applied scenarios from across the course.
final_items = [
    ("An API sends minutes as text. What makes it a validated number?", "Convert and check the runtime value", "Use as number", "Add a number return annotation", "Annotations are erased; conversion and validation are runtime work."),
    ("A duration of zero is valid, but missing durations default to 10. Which expression fits?", "duration ?? 10", "duration || 10", "Boolean(duration)", "Nullish coalescing preserves zero while handling absent values."),
    ("You want a settings object checked without replacing its useful inferred shape. What fits?", "satisfies", "JSON.parse alone", "A non-null assertion", "satisfies checks a static contract while retaining the resulting expression type."),
    ("A list lookup may not find an item. What should the return contract express?", "Lesson | undefined", "Always Lesson", "never", "Model possible absence instead of claiming that a lookup always succeeds."),
    ("An object has an id field but its value is a number. Is an in check alone enough to prove id: string?", "No, also check the property's value type", "Yes, in validates values", "Yes, with strict", "Property presence and property value type are separate checks."),
    ("A success response requires data and failure requires a message. Which model prevents unrelated optional-field combinations?", "A discriminated union", "All fields optional", "any", "The discriminator ties each state to its required payload."),
    ("Your iterator always passes an index but callbacks may ignore it. Which contract fits?", "(item: string, index: number) => void", "(item: string, index?: number) => void", "Function", "Ignoring a supplied parameter does not mean the invoker may omit it."),
    ("You need a getter preserving the selected property's result type. What fits?", "get<T, K extends keyof T>(value: T, key: K): T[K]", "get(value: any, key: string): any", "get(value: object, key: number): string", "Generic constraints connect the object, its permitted keys and its result type."),
    ("A function build changes its result fields. How can a dependent type avoid manual duplication?", "ReturnType<typeof build>", "Copy the old shape", "typeof build() as a type expression", "The utility derives the result from the function's type without executing it."),
    ("You need a boolean flag for every existing property. Which feature derives that shape?", "A mapped type over keyof T", "A runtime typeof string", "An interface with no fields", "Mapped types can systematically derive properties from existing keys."),
    ("A public output must actually exclude a secret field. What is required?", "Construct an output containing only public fields", "Annotate the original object Omit<User, 'secret'>", "Use a type assertion", "Erased types do not sanitize runtime objects."),
    ("A method uses this but is passed unbound as a callback. Can its types alone preserve its receiver?", "No; bind it, wrap it, or use suitable arrow-function behavior", "Yes, with implements", "Yes, with readonly", "Receiver binding is JavaScript runtime behavior and needs an appropriate implementation."),
    ("An alias resolves in the editor but fails in Node output. What should you inspect?", "Runtime resolution and alias configuration, not only paths", "Only interface names", "Only font settings", "TypeScript paths does not rewrite emitted imports or configure the host loader."),
    ("A bundler succeeds while tsc reports an error. What does that suggest?", "The bundler may be transpiling without type checking", "The error is necessarily false", "The browser will validate the types", "Separate emission and type checking so successful bundling does not hide diagnostics."),
    ("A .d.ts declares an export absent from the actual package. What can happen?", "Code type-checks but fails at runtime", "TypeScript creates the missing export", "The declaration is automatically ignored", "Declarations can be inaccurate; consumer compile and runtime tests are both useful."),
    ("You want useful checking in a JavaScript file before converting it. Which option fits?", "@ts-check with supported JSDoc annotations", "A blanket @ts-nocheck", "Casting every value to any", "Opt-in JS checking and documented boundary types provide an incremental migration path."),
    ("A fetch resolves with HTTP 500 and malformed data. What should the loader check?", "HTTP status and payload shape", "Only its Promise return annotation", "Only that fetch resolved", "HTTP success and valid payload structure are different conditions."),
    ("A library example uses namespace declarations. Does that automatically mean it is an ESM runtime module?", "No, check the library's actual loading and declaration structure", "Yes, all namespaces are imports", "Yes, with JSX enabled", "Namespaces, ambient declarations and ES modules describe different integration patterns."),
    ("An async resource must be acquired and then disposed asynchronously. Which expression shows both waits?", "await using resource = await acquireAsync()", "using resource = acquireAsync() always does both", "await using resource = acquireAsync() automatically awaits acquisition", "The declaration awaits disposal; the initializer's separate await awaits acquisition."),
    ("Your capstone passes type checks. What else establishes correct malformed-input behavior?", "Runtime tests for invalid fields, null and duplicate IDs", "More type assertions", "Only reading the solution", "Static contracts cannot replace execution tests of validation and business rules.")
]
for i, (prompt, correct, wrong1, wrong2, explanation) in enumerate(final_items):
    options=[correct,wrong1,wrong2]
    shift=i % 3
    options=options[shift:]+options[:shift]
    course['finalQuiz']['questions'].append({'id':f'ts-final-scenario-{i+1}', 'prompt':prompt, 'options':options, 'answer':options.index(correct), 'explanation':explanation})
for m in modules:
    lesson_count=sum(n['type']=='slides' for n in m['children'])
    m['studyGuide']={'title':m['title']+' · Completion study guide','summary':f'Review the {lesson_count} skills below, then use the exercises to check what you can do without the examples.','takeaways':[n['slides'][-1]['body'].split('\n\nBefore completing:')[0] for n in m['children'] if n['type']=='slides']}
(ROOT/'course.json').write_text(json.dumps(course,ensure_ascii=False,indent=2)+'\n')
index=(ROOT/'index.html').read_text()
embedded=json.dumps(course,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
index=re.sub(r'(<script id="lms-course-data" type="application/json">).*?(</script>)',lambda match:match[1]+embedded+match[2],index,flags=re.S)
index=re.sub(r'<title>.*?</title>','<title>TypeScript</title>',index)
(ROOT/'index.html').write_text(index)
print(f'{len(modules)} modules, {sum(len(m["children"])-1 for m in modules)} slide lessons, {sum(len(n.get("slides",[])) for m in modules for n in m["children"])} slides, {sum(len(m["children"][-1]["questions"]) for m in modules)} section questions, {len(course["finalQuiz"]["questions"])} final questions')
