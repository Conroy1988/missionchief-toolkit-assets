(() => {
  const CHANNEL = 'mcms-extension-pilot-v1';
  window.addEventListener('message', async event => {
    if (event.source !== window || event.origin !== location.origin || event.data?.channel !== CHANNEL || event.data?.direction !== 'request') return;
    const payload = event.data.payload;
    if (!payload || !['request', 'abort', 'save', 'engine'].includes(payload.op)) return;
    let response;
    try { response = await chrome.runtime.sendMessage(payload); }
    catch { response = {ok: false, error: 'Extension connection lost. Reload this tab.'}; }
    window.postMessage({channel: CHANNEL, direction: 'response', id: payload.id, response}, location.origin);
  });
  chrome.runtime.sendMessage({op: 'start', id: 'startup'}).then(result => {
    document.documentElement.dataset.mcmsExtensionState = result.ok ? result.value.state : 'error';
    if (!result.ok) console.warn('Toolkit pilot:', result.error);
  }).catch(() => {});
})();
