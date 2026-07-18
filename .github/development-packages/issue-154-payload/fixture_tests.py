PAYLOAD = r'''
const missingDoc = new FakeDocument();
missingDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/9901' }, navigator: context.pageWindow.navigator, innerWidth: 1280, innerHeight: 720 };
const missingCandidate = makeMissionCandidateWithoutSource(missingDoc);
candidates = [missingCandidate];
api.scan();
flushAnimationFrames();
let missingRecord = Array.from(api.records.values())[0];
assert(missingRecord.panel.innerHTML.includes('Loading mission requirements'), 'source-less mission initially shows a bounded loading state');
missingRecord.startedAt = Date.now() - 2000;
api.scan();
flushAnimationFrames();
missingRecord = Array.from(api.records.values())[0];
assert(missingRecord.panel.innerHTML.includes('Unable to pull mission requirements'), 'source-less mission shows an explicit failure state');
assert(missingRecord.panel.innerHTML.includes('Report Mission'), 'failure state exposes Report Mission');

const unsafeSource = new FakeElement('div', missingDoc);
unsafeSource.id = 'missing_text';
unsafeSource.textContent = 'token=secret https://discord.com/api/webhooks/1/abc 55.9533,-3.1883';
unsafeSource.innerText = unsafeSource.textContent;
missingCandidate.root.appendChild(unsafeSource);
missingRecord.candidate.source = unsafeSource;
const reportUrl = api.reportUrl(missingRecord, 'token=secret');
assert(reportUrl.startsWith('https://github.com/Conroy1988/missionchief-toolkit-assets/issues/new?'), 'report uses the GitHub issue composer');
assert(reportUrl.includes('Mission+Info+Missing'), 'report requests the Mission Info Missing label');
assert(reportUrl.length <= 7600, 'report URL remains bounded');
const reportBody = new URL(reportUrl).searchParams.get('body');
assert(!reportBody.includes('secret'), 'report sanitises token values');
assert(!reportBody.includes('discord.com/api/webhooks'), 'report sanitises webhook URLs');
assert(!reportBody.includes('55.9533'), 'report sanitises coordinates');

api.scan();
flushAnimationFrames();
const recovered = Array.from(api.records.values())[0];
assert.strictEqual(recovered.source, unsafeSource, 'a later native source replaces the fallback anchor');
unsafeSource.textContent = '2 Police cars';
unsafeSource.innerText = unsafeSource.textContent;
recovered.startedAt = Date.now() - 2000;
api.scan();
flushAnimationFrames();
assert(Array.from(api.records.values())[0].panel.innerHTML.includes('Police Car'), 'fallback upgrades automatically to the normal matrix');
assert.strictEqual(missingDoc.querySelectorAll('#mc-map-command-toolkit-mission-requirements').length, 1, 'fallback recovery retains one panel');
api.clear();

const emptyDoc = new FakeDocument();
emptyDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/9902' } };
const emptyCandidate = makeMissionCandidate(emptyDoc, '');
candidates = [emptyCandidate];
api.scan();
flushAnimationFrames();
let emptyRecord = api.records.get(emptyCandidate.source);
emptyRecord.startedAt = Date.now() - 2000;
api.scan();
flushAnimationFrames();
assert(emptyRecord.panel.innerHTML.includes('No outstanding requirements reported by MissionChief'), 'empty native source is explicit rather than silently removed');
api.clear();

const unparseableDoc = new FakeDocument();
unparseableDoc.defaultView = { MutationObserver: FakeMutationObserver, location: { pathname: '/missions/9903' } };
const unparseableCandidate = makeMissionCandidate(unparseableDoc, 'Requirement information is currently unavailable');
candidates = [unparseableCandidate];
api.scan();
flushAnimationFrames();
const unparseableRecord = api.records.get(unparseableCandidate.source);
assert(unparseableRecord.panel.innerHTML.includes('Unable to pull mission requirements'), 'unparseable native text shows the failure state');
assert(unparseableRecord.panel.innerHTML.includes('Report Mission'), 'unparseable native text can be reported');
api.clear();

'''
