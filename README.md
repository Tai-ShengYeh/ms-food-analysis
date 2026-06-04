# 質譜 × 食品分析教學包（MS × Food Analysis Teaching Kit）

用一份**公開的白酒 GC-MS 代謝體資料**，教兩個化學計量學核心方法：
**PCA**（非監督探索）與 **PLS-DA**（監督式品種鑑別）。三層遞進：先看影片建直覺 → 看 Python 學「怎麼算」 → 用 Orange 親手拉一遍。

| 交付物 | 路徑 |
|------|------|
| 教學網頁（互動課程頁） | `index.html` → `teaching.html` |
| Python 分析 + 圖表 | `python/`（`ms_utils.py` `01_explore.py` `02_pca.py` `03_plsda.py`、圖在 `python/figures/`） |
| Orange 工作流程 + 圖解指南 | `orange/wine_ms_workflow.ows`、`orange/ORANGE_GUIDE.md` |
| 教學影片① PCA（~5.3 分） | `videos/pca/final.mp4` |
| 教學影片② PLS-DA（~4.8 分） | `videos/plsda/final.mp4` |
| 影片腳本 / 視覺規範 | `videos/pca/SCRIPT.md`、`videos/plsda/SCRIPT.md`、`videos/DESIGN.md` |

## 資料來源

**NIH Metabolomics Workbench — Study ST000006「White Wine Study」**（Fiehn lab）。
GC-TOF 質譜，**101 支白酒 × 108 種代謝物**（峰高），7 個葡萄品種。公開資料（CC0）。
原始資料表快取於 `data/_wine_mw_raw.txt`；清理後輸出 `data/wine_gcms.csv` 與 `data/wine_orange.tab`。

> REST 取得：`https://www.metabolomicsworkbench.org/rest/study/analysis_id/AN000020/datatable`

## 重現分析

```bash
pip install numpy pandas scipy scikit-learn matplotlib pyreadr
cd python
python 01_explore.py     # 清理資料 + 指紋 / 前處理圖
python 02_pca.py         # 陡坡 / 分數（含 Hotelling T² 異常）/ 負荷量
python 03_plsda.py       # 監督分數 / 選 LV / 混淆矩陣 / VIP
```

## 重現影片（純 CSS/JS + Playwright + FFmpeg 管線）

```powershell
# 一次性：在 %TEMP% 安裝 Playwright（避開雲端同步 / 中文路徑）
$WorkDir="$env:TEMP\cvs-render"; ni -ItemType Directory -Force $WorkDir | Out-Null
pushd $WorkDir; npm init -y | Out-Null; npm install playwright; npx playwright install chromium; popd

# 每支影片：旁白 → 量時長 → 渲染
cd videos\pca         # 或 videos\plsda
python generate_narration.py
python get_durations.py            # 把 PAGES / PAGES_TIMINGS 貼回 index.html / render.py（已內建）
$env:NODE_PATH="$env:TEMP\cvs-render\node_modules"; python render.py   # -> final.mp4
```

## 關鍵結果

- **PCA**（log+autoscale）：Hotelling T² 自動抓出 5 支異常 = 資料中唯一的 2001 舊年份批次；
  清理後白酒依**葡萄品種自動分群**（Chardonnay / Sauvignon Blanc / Viognier…）。
- **PLS-DA**（Chardonnay 36 vs Sauvignon Blanc 24）：5 折交叉驗證 **100% 準確率**（1 個 LV 已 97%），
  混淆矩陣 36/0/0/24；VIP 榜首 **酒石酸、脯胺酸、肌醇**——真實酒化學。

## 製作

分析與圖表以 Python（scikit-learn）產生；教學影片以 **claude-code-video-kit**（純 CSS/JS + Playwright + FFmpeg）製作。
字體：源石黑體 GenSekiGothic2TW。配色：teal `#0E7C7B` + coral `#E36414`。
