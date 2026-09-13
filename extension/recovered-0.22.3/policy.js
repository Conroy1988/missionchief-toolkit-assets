// The page bridge is untrusted. No credentials or cross-origin writes are exposed.
export function gameOrigin(value) {
  try {
    const u = new URL(value);
    return u.protocol === 'https:' && (u.hostname === 'missionchief.co.uk' || u.hostname.endsWith('.missionchief.co.uk')) && !u.port ? u.origin : null;
  } catch { return null; }
}
export function safeKey(key) {
  return typeof key === 'string' && key.length < 160 && /^(mc_map_command_toolkit_|mcms_)/.test(key)
    && !/discord|webhook|credential|secret|token|identity|finance|financial/i.test(key);
}
export function readUrl(value) {
  const u = new URL(value);
  if (u.protocol !== 'https:' || u.username || u.password || u.port || u.hash) throw Error('URL is not permitted.');
  const raw = u.hostname === 'raw.githubusercontent.com' && (
    /^\/Conroy1988\/missionchief-toolkit-assets\/main\/financial-intelligence\/(v1\/classification-rules|v2\/audit-policy)\.json$/.test(u.pathname)
    || u.pathname === '/Conroy1988/missionchief-toolkit-assets/release-state/status/update-manifest.json');
  const guide = u.hostname === 'tkb-gaming.scot' && /^\/games\/missionchief\/guides\/api\/v2\/(capabilities|units|personnel)\.json$/.test(u.pathname);
  const icon = u.hostname === 'leitstellenspiel.s3.amazonaws.com' && /\.(png|jpe?g|gif|webp)$/i.test(u.pathname);
  if (!raw && !guide && !icon) throw Error('This external request is outside the local pilot.');
  return u.href;
}
