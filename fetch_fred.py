import json, os, sys, time, urllib.request
from datetime import date, datetime, timedelta, timezone

KEY = os.environ.get('FRED_API_KEY', '').strip()
if not KEY:
    sys.exit('缺少 FRED_API_KEY')

SERIES = {
    'SP500':'d','NASDAQCOM':'d','DTWEXBGS':'d','DCOILBRENTEU':'d','VIXCLS':'d',
    'DGS3MO':'d','DGS2':'d','DGS10':'d','DGS30':'d','T10Y2Y':'d','T10Y3M':'d','DFII10':'d','T10YIE':'d',
    'DFEDTARU':'d','DFEDTARL':'d','EFFR':'d','BAMLH0A0HYM2':'d','BAMLC0A0CM':'d',
    'WALCL':'w','ICSA':'w','NFCI':'w','MORTGAGE30US':'w',
    'CPIAUCSL':'m','CPILFESL':'m','PCEPILFE':'m','PPIFIS':'m','UNRATE':'m','PAYEMS':'m',
    'INDPRO':'m','RSAFS':'m','UMCSENT':'m','M2SL':'m',
    'A191RL1Q225SBEA':'q',
}
BACK = {'d':800,'w':1150,'m':2650,'q':2650}

def get(url):
    for i in range(3):
        try:
            return json.loads(urllib.request.urlopen(url, timeout=20).read())
        except Exception as e:
            print('  retry', i + 1, e, flush=True); time.sleep(2 * (i + 1))
    return None

out = {}
for sid, f in SERIES.items():
    start = (date.today() - timedelta(days=BACK[f])).isoformat()
    j = get(f'https://api.stlouisfed.org/fred/series/observations?series_id={sid}'
            f'&api_key={KEY}&file_type=json&observation_start={start}')
    rows = []
    for o in (j or {}).get('observations', []):
        try: rows.append([o['date'], float(o['value'])])
        except ValueError: pass
    if rows: out[sid] = rows
    print(sid, len(rows), flush=True)
    time.sleep(0.3)

os.makedirs('data', exist_ok=True)
path = 'data/fred.json'
old = {}
if os.path.exists(path):
    try: old = json.load(open(path)).get('series', {})
    except Exception: pass
with open(path, 'w') as fh:
    json.dump({'updated': datetime.now(timezone.utc).isoformat(timespec='seconds'),
               'series': {**old, **out}}, fh, separators=(',', ':'))
print('done', len(out), 'series', flush=True)
