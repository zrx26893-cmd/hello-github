"""每小时由 GitHub Actions 运行：从 FRED 抓取宏观序列，写入 data/fred.json"""
import csv, io, json, os, time, urllib.request
from datetime import date, datetime, timedelta, timezone

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
            req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0 macro-dashboard'})
            return urllib.request.urlopen(req, timeout=40).read().decode('utf-8')
        except Exception as e:
            print('retry', url, e); time.sleep(4 * (i + 1))
    return None

out = {}
for sid, f in SERIES.items():
    cosd = (date.today() - timedelta(days=BACK[f])).isoformat()
    txt = get(f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}&cosd={cosd}')
    if not txt: continue
    rows = []
    for r in list(csv.reader(io.StringIO(txt)))[1:]:
        try: rows.append([r[0], float(r[1])])
        except (ValueError, IndexError): pass
    if rows: out[sid] = rows
    print(sid, len(rows))

os.makedirs('data', exist_ok=True)
path = 'data/fred.json'
old = {}
if os.path.exists(path):
    try: old = json.load(open(path)).get('series', {})
    except Exception: pass
merged = {**old, **out}  # 某个序列失败时保留上次数据
with open(path, 'w') as fh:
    json.dump({'updated': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'series': merged}, fh, separators=(',', ':'))
