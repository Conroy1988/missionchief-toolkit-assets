(() => {
  const result={executed:true,bridgeWorld:globalThis.__MCMS_COMPAT_BRIDGE__===true};
  document.documentElement.setAttribute('data-mcms-compat-result',JSON.stringify(result));
})();
