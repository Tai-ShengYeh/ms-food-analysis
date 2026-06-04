import sys, subprocess, json
from pathlib import Path
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach()); sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
NARR = Path(__file__).resolve().parent / "assets" / "narration"
SUBTITLES = [
    "PLS-DA：讓模型學會鑑別品種",
    "PCA 不看答案，PLS-DA 衝著答案去",
    "PLS-DA 把軸轉去對齊類別分界",
    "找潛在變量 LV，最大化與類別共變異",
    "LV1 乾淨地左右分開兩個品種",
    "交叉驗證：訓練與測試分開才誠實",
    "1 個 LV 已 97%，夠用就好別過擬合",
    "對角線全中，兩品種完美區分",
    "酒石酸、脯胺酸…都是真實酒化學",
    "產地、品種、摻偽——都靠 PLS-DA",
    "先用 PCA 探索，再用 PLS-DA 鑑別",
    "PLS-DA：讓質譜指紋說出這是什麼",
    "接下來：用 Orange 親手做一次",
]
N = len(SUBTITLES)
def dur(p):
    r = subprocess.run(["ffprobe","-v","quiet","-print_format","json","-show_format",str(p)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return float(json.loads(r.stdout.decode('utf-8'))["format"]["duration"])
def main():
    PAGES_JS, timings, total = [], [], 0
    for i in range(1, N+1):
        p = NARR / f"page-{i:02d}.mp3"
        if not p.exists(): print(f"missing {p.name}"); return
        d = dur(p); pd = int(round(d + 3.0)); total += pd; timings.append(pd)
        PAGES_JS.append(f'  {{ i: {i}, dur: {pd}, sub: "{SUBTITLES[i-1]}" }}')
        print(f"page-{i:02d}: {d:.2f}s -> {pd}s")
    print("\nconst PAGES = [\n" + ",\n".join(PAGES_JS) + "\n];")
    print("\nPAGES_TIMINGS = [" + ", ".join(f'{{"i": {i+1}, "dur": {d}}}' for i,d in enumerate(timings)) + "]")
    print(f"\nTOTAL = {total}s | record ms = {total*1000+800}")
if __name__ == "__main__": main()
