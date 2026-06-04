# Orange Data Mining 實作指南 — 質譜食品分析（PCA + 品種鑑別）

> 給課堂用的「不寫程式」版本。學生用拖拉式 widget，重現 Python 影片裡的 PCA 與 PLS-DA 結果。
> 資料：`../data/wine_orange.tab`（101 支白酒 × 108 個 GC-MS 代謝物 + variety / variety_group）。
> 一鍵開檔：`wine_ms_workflow.ows`（已含 8 個 widget、7 條連線）。
> Orange 版本：3.36+（PCA、Logistic Regression、Confusion Matrix 皆為內建）。

---

## Part 0 ｜ 安裝 Orange

1. 到 <https://orangedatamining.com/download> 下載安裝（Windows / macOS 皆可，含 Python）。
2. 開啟 Orange，看到空白 canvas、左側 widget 工具列即安裝成功。
3. 本指南用到的 widget 都是內建：**Data ▸ File / Select Rows**、**Unsupervised ▸ PCA**、
   **Visualize ▸ Scatter Plot**、**Model ▸ Logistic Regression**、**Evaluate ▸ Test and Score / Confusion Matrix**。

---

## Part 1 ｜ 認識資料

`wine_orange.tab` 欄位（已標好角色，直接可用）：

| 欄位 | 數量 | 角色 (role) | 說明 |
|------|------|------------|------|
| `sample_id` | 1 | **meta** | 樣本編號（不參與分析） |
| `label` | 1 | **meta** | 完整標籤（品種, 產地, 年份） |
| 108 個代謝物名 | 108 | **feature** | GC-MS 峰高 → PCA / 分類的輸入 |
| `variety` | 1 | meta | 7 個品種（PCA 上色用） |
| `variety_group` | 1 | **target (class)** | 品種群（Fume Blanc 併入 Sauvignon Blanc）→ 分類目標 |

> 資料來源：NIH Metabolomics Workbench 研究 **ST000006 White Wine Study**（GC-TOF MS，公開 CC0）。

---

## Part 2 ｜ 開啟現成工作流程

`File ▸ Open` 選 `wine_ms_workflow.ows`。會看到兩條分支：

```
                 ┌──────────────┐
         ┌──────▶│  Data Table  │   檢視原始峰高
         │       └──────────────┘
         │       ┌──────┐  Transformed Data   ┌──────────────────────┐
         │  ┌───▶│ PCA  │────────────────────▶│ Scatter Plot 分數圖   │  ← PCA 分支（探索）
 ┌───────┴──┐│   └──────┘                      └──────────────────────┘
 │  File    ├┤
 │wine_     ││   ┌────────────┐ Matching  ┌───────────────┐ Eval  ┌─────────────────┐
 │orange.tab│└──▶│ Select Rows│──────────▶│ Test and Score│──────▶│ Confusion Matrix│
 └──────────┘    └────────────┘   Data    └───────────────┘  Res  └─────────────────┘
                                              ▲ Learner
                                        ┌─────┴──────────────┐
                                        │ Logistic Regression│   ← 分類分支（監督）
                                        └────────────────────┘
```

**第一步永遠是設定 File widget**：雙擊 `File` → 右下 `Browse` 選 `../data/wine_orange.tab` → 按 `Apply`。
（`.tab` 檔已標好角色：`variety_group` = target、`sample_id`/`label`/`variety` = meta、其餘 108 個維持 feature。）

> 中文路徑載入失敗時，把 `wine_orange.tab` 複製到純英文路徑再 Browse。

---

## Part 3 ｜ PCA 分支（對應第一支影片）

**目標**：把 108 個代謝物壓成 2–3 個主成分，看酒是否依品種自動排列、並找出異常。

| # | 動作 | Widget 設定 | 應觀察到 |
|---|------|------------|---------|
| 1 | 拉 **File** | 載入 `wine_orange.tab` | 101 instances、108 features |
| 2 | 接 **Data Table** | （File→Data Table） | 看到原始 GC-MS 峰高表格 |
| 3 | 接 **PCA** | 視窗內勾 **Normalize variables**（= autoscale），看變異解釋曲線 | 約 10 個成分才到 80%；PC1 ≈ 22% |
| 4 | 接 **Scatter Plot** | PCA 的 **Transformed Data** → Scatter Plot | 下一步上色 |
| 5 | 設定 Scatter Plot | Axis x = **PC1**、y = **PC2**、**Color = variety** | Chardonnay 一邊、Sauvignon Blanc / Viognier 另一邊；左側幾個離群點 |

**教學提問**：
- PCA 有沒有用到品種標籤？（沒有，它是非監督；卻仍依品種聚集 → 結構自己浮現）
- 左邊那幾個離群點是誰？把滑鼠移上去看 `label` → 多半是 **2001 年的 Sauvignon Blanc**（唯一舊年份，呼應影片的 Hotelling T² 異常偵測）。
- 把 Color 改成 `variety_group` 或某個代謝物，觀察梯度。

> 影片的 Python 版多做了 log 轉換；Orange 只勾 Normalize（autoscale），座標數值會略有不同，
> 但「少數成分看見品種結構、PCA 自動抓出 2001 異常批次」的結論一致。
> 想更貼近 Python，可在 File 與 PCA 之間插一個 **Preprocess** widget。

---

## Part 4 ｜ 分類分支（對應第二支影片的 PLS-DA）

**目標**：用代謝指紋建立一個能分辨 **Chardonnay vs Sauvignon Blanc** 的分類器，並誠實驗證。

> **關於 PLS-DA**：影片用的 PLS-DA = 在 0/1 類別標籤上做 PLS 回歸。Orange 內建的 **PLS** widget
> 只做數值回歸，因此這裡改用 **Logistic Regression**——同樣是「監督式線性鑑別」，能直接輸出
> 混淆矩陣與準確率，教學概念與 PLS-DA 完全相通（都在找一條最能分開兩類的方向）。

| # | 動作 | Widget 設定 | 應觀察到 |
|---|------|------------|---------|
| 1 | 接 **Select Rows** | 條件：`variety_group` **is one of** `Chardonnay`, `Sauvignon Blanc` | Matching Data ≈ **60 列**（36 + 24） |
| 2 | 接 **Logistic Regression** | （Model 類別）預設即可；Regularization 可留預設 | 產生 Learner |
| 3 | 接 **Test and Score** | Select Rows 的 **Matching Data** → Test&Score 的 **Data**；Logistic 的 **Learner** → Test&Score。選 **Cross validation, 5 folds** | **CA（準確率）≈ 0.97–1.00**（對應影片混淆矩陣） |
| 4 | 接 **Confusion Matrix** | Test&Score 的 **Evaluation Results** → Confusion Matrix | 對角線幾乎全中：Chardonnay / Sauvignon Blanc 互不混淆 |

**重現影片的「過度擬合」教學（選做）**：
- 換上 **PLS** 或調整不同模型複雜度（或在 Logistic 調 Regularization C），看 Test&Score 的 CA：
  太簡單欠擬合、夠用就好；本題兩品種差異大，1–2 個方向就近乎完美，**加更多複雜度沒有幫助**。
- 教學結論：用交叉驗證挑「夠用」的複雜度，不是越複雜越好（呼應影片 fig ms07）。

**看是哪些代謝物在分類**（呼應影片 VIP，fig ms09）：
- 接 **Rank**（Data 類別）到 Select Rows 的 Matching Data，依 information gain / ANOVA 排序，
  排前面的常是 **酒石酸 tartaric acid、脯胺酸 proline、肌醇 inositol** 等——和影片的 VIP 榜一致。

---

## Part 5 ｜ 和 Python / 影片對照

| 概念 | 影片 / Python 圖 | Orange widget |
|------|-----------------|---------------|
| 代謝指紋（原始） | ms01 | File → Data Table |
| 主成分數量 | ms03 scree | PCA 視窗內的變異曲線 |
| 分數圖（依品種上色） | ms04 | PCA → Scatter Plot（Color=variety） |
| 異常偵測（2001 批次） | ms04_full | Scatter Plot 左側離群點（hover 看 label） |
| 監督式分數 / 分類 | ms06 / ms08 | Logistic Regression + Test&Score + Confusion Matrix |
| 選複雜度 / 過度擬合 | ms07 | 調模型 + Test&Score 的 CA |
| 哪些代謝物在分類 | ms09 VIP | Rank widget（information gain / ANOVA） |

學生先看影片建立直覺、看 Python 看「怎麼算」、最後用 Orange 親手「拉一遍」，三層遞進。

---

## Part 6 ｜ 疑難排解

| 現象 | 原因 / 修法 |
|------|------------|
| Logistic / Test&Score 灰掉沒反應 | File 沒把 `variety_group` 設成 target；或 Select Rows 沒接上 Data |
| Select Rows 選不到品種 | 條件值要逐一加：`variety_group` is one of → 勾 Chardonnay、Sauvignon Blanc |
| 開 .ows 後 File 紅框 | File 還沒指定檔案：雙擊 File 重新 Browse 到 `wine_orange.tab` |
| Scatter Plot 沒有 PC1/PC2 選項 | 確認連的是 PCA 的 **Transformed Data**（不是原始 Data） |
| Confusion Matrix 空白 | 確認 Test&Score 跑完且選了 Cross validation；連的是 **Evaluation Results** |
| CA 和 Python 略不同 | 隨機折數 / 模型不同所致，量級一致即可（兩品種都接近 100%） |
| 中文路徑載入失敗 | 把 `wine_orange.tab` 複製到純英文路徑再 Browse |
