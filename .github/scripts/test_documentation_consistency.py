#!/usr/bin/env python3
import json
from pathlib import Path
import check_documentation_drift as drift_audit
ROOT=Path(__file__).resolve().parents[2]
def main():
 manifest=json.loads((ROOT/'dist/release-manifest.json').read_text());dashboard=json.loads((ROOT/'status/release-dashboard.json').read_text());readme=(ROOT/'README.md').read_text();help_text=(ROOT/'help/index.html').read_text();hero=(ROOT/'docs/media/readme-hero.svg').read_text();site=json.loads((ROOT/'docs/site-data.json').read_text())
 assert str(manifest['version']) and str(dashboard['latestRelease']['version'])
 assert all('The One We Knew Before' in text for text in [readme,help_text])
 forbidden=['Operational Window Suite','Enhanced Operational Requirements','Extended Call Window','Extended Call List','Enhanced Transport Requests']
 assert not any(item in text for item in forbidden for text in [readme,help_text,hero])
 names=[f['name'] for c in site['featureCategories'] for f in c.get('features',[])];assert all(item in names for item in ['Mission Age map timers','Mission Value','Patient Transport Sweep','Resource Gap','Vehicle Code Status','Alliance Credits','Financial intelligence','Economy Mode','Desktop, Tablet and iOS Mobile Mode'])
 report=drift_audit.audit(ROOT,allow_release_candidate=True);assert report['status']=='passed',report['failures'];print('Documentation consistency passed for stable and candidate release states.')
if __name__=='__main__': raise SystemExit(main())
