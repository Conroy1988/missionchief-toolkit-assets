import { promises as fs } from 'node:fs';
import path from 'node:path';

const root = path.resolve('financial-intelligence/benchmark-submissions');
const output = path.resolve('financial-intelligence/v1/benchmark-summary.json');
const metrics = ['incomePerActiveHour', 'averageMissionReward', 'operatingMarginPercent', 'allianceIncomePercent', 'capitalInvestmentRatioPercent', 'classificationConfidence'];
const bandLabels = {
  '<1m': 'Under 1M reserve',
  '1m-10m': '1M–10M reserve',
  '10m-50m': '10M–50M reserve',
  '50m-100m': '50M–100M reserve',
  '100m+': '100M+ reserve',
  all: 'All submitted players'
};

async function walk(directory) {
  const files = [];
  let entries = [];
  try { entries = await fs.readdir(directory, { withFileTypes: true }); } catch { return files; }
  for (const entry of entries) {
    const target = path.join(directory, entry.name);
    if (entry.isDirectory()) files.push(...await walk(target));
    else if (entry.isFile() && entry.name.endsWith('.json')) files.push(target);
  }
  return files;
}

function percentile(values, fraction) {
  if (!values.length) return null;
  const ordered = values.slice().sort((a, b) => a - b);
  const position = (ordered.length - 1) * fraction;
  const lower = Math.floor(position);
  const upper = Math.ceil(position);
  if (lower === upper) return ordered[lower];
  return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower);
}

function metricSummary(samples, metric) {
  const values = samples.map(sample => Number(sample[metric])).filter(Number.isFinite);
  if (!values.length) return null;
  const round = value => Math.round(value * 10) / 10;
  return {
    p25: round(percentile(values, 0.25)),
    median: round(percentile(values, 0.5)),
    p75: round(percentile(values, 0.75))
  };
}

function summariseBand(id, samples) {
  const summary = {};
  for (const metric of metrics) {
    const value = metricSummary(samples, metric);
    if (value) summary[metric] = value;
  }
  return { id, label: bandLabels[id] || id, sampleSize: samples.length, metrics: summary };
}

const files = await walk(root);
const cutoff = Date.now() - 90 * 86400000;
const samples = [];
for (const file of files) {
  try {
    const sample = JSON.parse(await fs.readFile(file, 'utf8'));
    if (Number(sample.schema) !== 1 || Number(sample.receivedAt || sample.submittedAt) < cutoff) continue;
    if (!Object.hasOwn(bandLabels, sample.balanceBand)) continue;
    samples.push(sample);
  } catch {}
}

const bands = [];
for (const id of ['<1m', '1m-10m', '10m-50m', '50m-100m', '100m+']) {
  const group = samples.filter(sample => sample.balanceBand === id);
  if (group.length) bands.push(summariseBand(id, group));
}
if (samples.length) bands.push(summariseBand('all', samples));

const payload = {
  schema: 1,
  version: new Date().toISOString().slice(0, 10).replaceAll('-', '.') + '.1',
  generatedAt: new Date().toISOString(),
  sampleSize: samples.length,
  minimumSampleSize: 20,
  windowDays: 90,
  bands,
  message: samples.length < 20
    ? `Benchmark collection has ${samples.length} recent sample${samples.length === 1 ? '' : 's'}; at least 20 are required before comparisons are shown.`
    : 'Benchmark comparisons use rolling 90-day medians from opt-in aggregate submissions.'
};
await fs.mkdir(path.dirname(output), { recursive: true });
await fs.writeFile(output, JSON.stringify(payload, null, 2) + '\n');
console.log(`Wrote ${output} from ${samples.length} samples.`);
