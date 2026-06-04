import sys, subprocess, json
from pathlib import Path
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach()); sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
NARR = Path(__file__).resolve().parent / "assets" / "narration"
SUBTITLES = [
    "質譜把一支酒拆成上百種代謝物指紋",
    "GC-MS 把樣本變成「樣本 × 代謝物」矩陣",
    "每支酒是 108 維的一點，看不出來",
    "log 壓縮範圍，autoscale 讓代謝物公平",
    "PC1＝最大分散方向，PC2 與它垂直",
    "X ≈ T·Pᵀ：分數看樣本，負荷量看代謝物",
    "前 2–3 個成分就夠用來看見結構",
    "PCA 自動抓出唯一的 2001 舊年份批次",
    "PCA 不看品種，酒卻依品種自動分群",
    "糖、有機酸、胺基酸是分群的推手",
    "PCA 非監督：探索分群找異常，不做鑑別",
    "指紋 → 前處理 → PCA → 分數 / 負荷量 / 異常",
    "PCA：把上百種代謝物，壓縮成看得懂的方向",
    "下一支：PLS-DA，從指紋鑑別品種",
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
