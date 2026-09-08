const checkbox = document.getElementById('enabled');
const status = document.getElementById('status');
const button = document.getElementById('reload');
const labels = {'userscript-active': 'Userscript detected. Disable it in Tampermonkey, then reload.', started: 'Pilot running in this tab.', 'already-started': 'Pilot running in this tab.', off: 'Pilot is off in this tab.'};
async function initialise() {
  checkbox.checked = Boolean((await chrome.storage.local.get('enabled')).enabled);
  const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
  const url = new URL(tab?.url || 'https://invalid.example');
  const supported = url.protocol === 'https:' && (url.hostname === 'missionchief.co.uk' || url.hostname.endsWith('.missionchief.co.uk'));
  if (!supported) { status.textContent = 'Open MissionChief UK to test the pilot.'; button.disabled = true; return; }
  const [result] = await chrome.scripting.executeScript({target: {tabId: tab.id}, func: () => ({state: document.documentElement.dataset.mcmsExtensionState, error: document.documentElement.dataset.mcmsExtensionStorageError})});
  status.textContent = result?.result?.error || labels[result?.result?.state] || 'Apply your choice and reload the game tab.';
  button.onclick = async () => {
    button.disabled = true;
    try { await chrome.storage.local.set({enabled: checkbox.checked}); await chrome.tabs.reload(tab.id); window.close(); }
    catch (error) { status.textContent = error.message; button.disabled = false; }
  };
}
initialise().catch(error => { status.textContent = error.message; });
