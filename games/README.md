# 配套互動題庫 — 質譜 × 食品分析（PCA / PLS-DA）

依課程內容自動生成的可匯入題庫，檔案在 [`game_imports/`](game_imports/)。
重新生成：`python gen_game_imports.py`（需 `pip install openpyxl`）。

| 檔案 | 平台 | 題數 | 匯入路徑 |
|------|------|------|---------|
| `kahoot_pca.xlsx` | Kahoot（PCA 場）| 10 | kahoot.com → 建立測驗 → 試算表匯入 |
| `kahoot_plsda.xlsx` | Kahoot（PLS-DA 場）| 10 | 同上 |
| `wordwall_match.csv` | Wordwall **Match** | 16 對 | wordwall.net → Match → Import |
| `wordwall_quiz.csv` | Wordwall **Quiz** | 12 | wordwall.net → Quiz → Import |
| `wordwall_sort_pca.csv` | Wordwall **Rank Order** | 1 排序 | wordwall.net → Rank Order → Import |
| `wordwall_sort_plsda.csv` | Wordwall **Rank Order** | 1 排序 | 同上 |
| `gimkit.csv` | Gimkit | 26 | gimkit.com → Create Kit → Import |

## 課堂使用建議
- **課前**：Kahoot PCA 前測喚起概念。
- **看完影片①後**：Wordwall Match 配對鞏固術語、`wordwall_sort_pca.csv` 排出 PCA 流程。
- **看完影片②後**：Kahoot PLS-DA 場 + `wordwall_sort_plsda.csv` 建模步驟。
- **回家練習**：Gimkit 快答（術語/數值）。

## 注意事項
- **Kahoot 免費方案**每場 ≤ 10 題，故拆成 PCA / PLS-DA 兩場。
- **Wordwall Rank Order**：一個排序活動 = 一個 CSV（多題合一會被合併成一條超長序列），故 PCA / PLS-DA 各自一檔。
- 所有 CSV 以 **UTF-8 with BOM** 輸出，Excel / Wordwall 匯入中文不亂碼。
- 正解欄（Kahoot）為數字 1–4，對應 Answer 1–4。
