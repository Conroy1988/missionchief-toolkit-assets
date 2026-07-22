#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2]
S=R/'src/MissionChief_Map_Command_Toolkit.user.js'; F=R/'.github/fixtures/settings-ui-contract.json'; T=R/'.github/scripts/test_settings_ui_contract.py'; H=R/'.github/fixtures/main-style-source-headroom.json'
OLD='4.20.29'; NEW='4.20.30'
def x(t,a,b,n):
 c=t.count(a)
 if c!=1: raise RuntimeError(f'{n}: {c}')
 return t.replace(a,b,1)
s=S.read_text()
s=x(s,f'// @version      {OLD}',f'// @version      {NEW}','meta'); s=x(s,f"version: '{OLD}'",f"version: '{NEW}'",'runtime')
for n,a in [('lock state',"""        if (feature === 'missionLockAudio') {
            state.missionLockAudio = !state.missionLockAudio;
            if (state.missionLockAudio) unlockPayoutAudio(true);
        }
"""),('payout state',"""        if (feature === 'payoutFlash') state.payoutFlash.enabled = !state.payoutFlash.enabled;
        if (feature === 'payoutSound') {
            state.payoutFlash.soundEnabled = !state.payoutFlash.soundEnabled;
            if (state.payoutFlash.soundEnabled) unlockPayoutAudio();
            else disposePayoutMediaAudio();
        }
"""),('lock toast',"        if (feature === 'missionLockAudio') showToast(state.missionLockAudio ? 'Mission tracking audio on' : 'Mission tracking audio off');\n"),('sound toast',"        if (feature === 'payoutSound') showToast(state.payoutFlash.soundEnabled ? 'Theme audio on · hosted MP3 cues load only when played' : 'Theme audio off');\n"),('flash toast',"        if (feature === 'payoutFlash') showToast(state.payoutFlash.enabled ? 'Emergency payout flash on' : 'Emergency payout flash off');\n")]: s=x(s,a,'',n)
s=x(s,"""    function toggleFeature(feature) {
        handleMapVisibilityToggle(feature);
        handleMissionWindowToggle(feature);
""","""    function handlePayoutAudioToggle(feature) {
        if (feature === 'missionLockAudio') { state.missionLockAudio = !state.missionLockAudio; if (state.missionLockAudio) unlockPayoutAudio(true); }
        else if (feature === 'payoutFlash') state.payoutFlash.enabled = !state.payoutFlash.enabled;
        else if (feature === 'payoutSound') { state.payoutFlash.soundEnabled = !state.payoutFlash.soundEnabled; if (state.payoutFlash.soundEnabled) unlockPayoutAudio(); else disposePayoutMediaAudio(); }
        else return false;
        return true;
    }
    function applyPayoutAudioToggleEffects(feature) {
        if (feature === 'missionLockAudio') showToast(state.missionLockAudio ? 'Mission tracking audio on' : 'Mission tracking audio off');
        else if (feature === 'payoutSound') showToast(state.payoutFlash.soundEnabled ? 'Theme audio on · hosted MP3 cues load only when played' : 'Theme audio off');
        else if (feature === 'payoutFlash') showToast(state.payoutFlash.enabled ? 'Emergency payout flash on' : 'Emergency payout flash off');
    }
    function toggleFeature(feature) {
        handleMapVisibilityToggle(feature);
        handleMissionWindowToggle(feature);
        handlePayoutAudioToggle(feature);
""",'helper')
s=x(s,"""        reconcileFeatureRefreshes({ includeSnapshots: missionSnapshotsNeeded(), positionPanel: false });
        applyMissionWindowToggleEffects(feature);
""","""        reconcileFeatureRefreshes({ includeSnapshots: missionSnapshotsNeeded(), positionPanel: false });
        applyMissionWindowToggleEffects(feature);
        applyPayoutAudioToggleEffects(feature);
""",'effect call')
S.write_text(s)
for p in [R/'MissionChief_Map_Command_Toolkit.user.js',R/'MissionChief_Map_Command_Toolkit.txt']: p.write_text(s)
f=json.loads(F.read_text()); routes=['missionLockAudio','payoutFlash','payoutSound']; f['extractedPayoutAudioToggleRoutes']=routes; f['extractedPayoutAudioEffectRoutes']=routes; f['extractedPayoutAudioToggleStatePaths']={'missionLockAudio':'missionLockAudio','payoutFlash':'payoutFlash.enabled','payoutSound':'payoutFlash.soundEnabled'}; F.write_text(json.dumps(f,indent=2,ensure_ascii=False)+'\n')
t=T.read_text()
t=x(t,'    "applyMissionWindowToggleEffects",\n    "toggleFeature",','    "applyMissionWindowToggleEffects",\n    "handlePayoutAudioToggle",\n    "applyPayoutAudioToggleEffects",\n    "toggleFeature",','fn list')
t=x(t,'    apply_mission_window_effects = extract_function(source, masked, "applyMissionWindowToggleEffects")\n    toggle_feature = extract_function(source, masked, "toggleFeature")','    apply_mission_window_effects = extract_function(source, masked, "applyMissionWindowToggleEffects")\n    handle_payout_audio_toggle = extract_function(source, masked, "handlePayoutAudioToggle")\n    apply_payout_audio_effects = extract_function(source, masked, "applyPayoutAudioToggleEffects")\n    toggle_feature = extract_function(source, masked, "toggleFeature")','extractors')
t=x(t,"""    mission_window_effect_routes = values(r'feature\\s*===\\s*[\"\\']([^\"\\']+)[\"\\']', apply_mission_window_effects)
    toggle_routes = sorted(set(direct_toggle_routes + extracted_toggle_routes + mission_window_toggle_routes))
""","""    mission_window_effect_routes = values(r'feature\\s*===\\s*[\"\\']([^\"\\']+)[\"\\']', apply_mission_window_effects)
    payout_audio_toggle_routes = values(r'feature\\s*===\\s*[\"\\']([^\"\\']+)[\"\\']', handle_payout_audio_toggle)
    payout_audio_effect_routes = values(r'feature\\s*===\\s*[\"\\']([^\"\\']+)[\"\\']', apply_payout_audio_effects)
    toggle_routes = sorted(set(direct_toggle_routes + extracted_toggle_routes + mission_window_toggle_routes + payout_audio_toggle_routes))
""",'routes')
t=x(t,'    assert "applyMissionWindowToggleEffects(feature)" in toggle_feature, "Main toggle router must delegate to the extracted mission-window effect family"\n    assert setting_families == sorted(fixtures["settingFamilies"]), "Setting-family routing changed"','    assert "applyMissionWindowToggleEffects(feature)" in toggle_feature, "Main toggle router must delegate to the extracted mission-window effect family"\n    assert payout_audio_toggle_routes == sorted(fixtures["extractedPayoutAudioToggleRoutes"]), "Extracted payout/audio toggle routing changed"\n    assert payout_audio_effect_routes == sorted(fixtures["extractedPayoutAudioEffectRoutes"]), "Extracted payout/audio effect routing changed"\n    assert not set(direct_toggle_routes).intersection(payout_audio_toggle_routes), "Extracted payout/audio toggles remain duplicated"\n    assert "handlePayoutAudioToggle(feature)" in toggle_feature\n    assert "applyPayoutAudioToggleEffects(feature)" in toggle_feature\n    assert setting_families == sorted(fixtures["settingFamilies"]), "Setting-family routing changed"','asserts')
test=r'''

function testExtractedPayoutAudioToggleContracts() {{
    for (const [feature, path] of Object.entries(fixtures.extractedPayoutAudioToggleStatePaths)) {{
        resetEnvironment(); const before = pathValue(state, path);
        assert.equal(handlePayoutAudioToggle(feature), true); assert.notEqual(pathValue(state, path), before);
        assert.equal(localStorage.getItem(SCRIPT.storageState), null); assert.equal(wasCalled("updateUI"), false);
    }}
    resetEnvironment(); const before = JSON.stringify(state);
    assert.equal(handlePayoutAudioToggle("unknown-payout-audio"), false); assert.equal(JSON.stringify(state), before);
    resetEnvironment(); state.missionLockAudio = false; handlePayoutAudioToggle("missionLockAudio"); assert.deepEqual(callFor("unlockPayoutAudio").args, [true]);
    resetEnvironment(); state.payoutFlash.soundEnabled = true; handlePayoutAudioToggle("payoutSound"); assert.equal(wasCalled("disposePayoutMediaAudio"), true);
    for (const [feature, message] of [["missionLockAudio","Mission tracking audio on"],["payoutSound","Theme audio off"],["payoutFlash","Emergency payout flash on"]]) {{
        resetEnvironment(); applyPayoutAudioToggleEffects(feature); assert.equal(callFor("showToast").args[0], message);
    }}
    resetEnvironment(); applyPayoutAudioToggleEffects("coverage"); assert.equal(calls.length, 0);
}}
'''
t=x(t,'\nasync function testToggleContracts() {{\n',test+'\nasync function testToggleContracts() {{\n','direct tests')
order=r'''

    for (const [feature, prepare, immediate] of [
        ["missionLockAudio", () => {{ state.missionLockAudio = false; }}, "unlockPayoutAudio"],
        ["payoutSound", () => {{ state.payoutFlash.soundEnabled = false; }}, "unlockPayoutAudio"],
        ["payoutFlash", () => {{ state.payoutFlash.enabled = false; }}, null],
    ]) {{
        resetEnvironment(); prepare(); toggleFeature(feature);
        const update = calls.findIndex(call => call.name === "updateUI");
        const reconcile = calls.findIndex(call => call.name === "reconcileFeatureRefreshes");
        const toast = calls.findIndex(call => call.name === "showToast");
        assert.ok(update >= 0 && update < reconcile && reconcile < toast);
        if (immediate) assert.ok(calls.findIndex(call => call.name === immediate) < update);
    }}
'''
t=x(t,'    resetEnvironment();\n    toggleFeature("criticalView");',order+'\n    resetEnvironment();\n    toggleFeature("criticalView");','order tests')
t=x(t,'    testExtractedMissionWindowToggleContracts();\n    await testToggleContracts();','    testExtractedMissionWindowToggleContracts();\n    testExtractedPayoutAudioToggleContracts();\n    await testToggleContracts();','test call')
t=x(t,'extracted mission-window toggle parity, extracted financial route parity,','extracted mission-window toggle parity, extracted payout/audio toggle parity, extracted financial route parity,','summary'); T.write_text(t)
c=(R/'CHANGELOG.md').read_text(); entry=f'''## [{NEW}] - 2026-07-22

### Internal reliability
- Extracted Mission Tracking Audio, Emergency Payout Flash and Theme Audio state and notification routing from `toggleFeature()` into dedicated payout/audio helpers.
- Preserved immediate audio unlock/disposal and post-reconciliation notification ordering with direct and delegated contracts.

### Compatibility
- No payout presentation, hosted audio source, threshold, duration, volume, device layout, theme or public asset changed.

'''; (R/'CHANGELOG.md').write_text(x(c,'## [Unreleased]\n\n','## [Unreleased]\n\n'+entry,'changelog'))
h=(R/'help/index.html').read_text();
if OLD not in h: raise RuntimeError('help version missing')
(R/'help/index.html').write_text(h.replace(OLD,NEW))
q=json.loads(H.read_text()); lines=len(s.splitlines()); q['candidateVersion']=NEW; q['candidateSourceLines']=lines; q['recoveredSourceLines']=q['originalSourceLines']-lines; q['candidateSourceSha256']=hashlib.sha256(s.encode()).hexdigest(); q['invariant']='The reviewed compact stylesheet retains at least 500 recovered source lines while payout/audio routing remains fixture-backed and managed runtime budgets remain unchanged.'; H.write_text(json.dumps(q,indent=2)+'\n')
subprocess.check_call([sys.executable,str(T)],cwd=R)
print(f'Prepared {NEW}; source lines={lines}; recovered={q["recoveredSourceLines"]}')
