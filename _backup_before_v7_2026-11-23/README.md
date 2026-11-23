# 第五組：台灣半導體相關股票 波動率預測與動態資產配置（ML4T 期中）

一次完整走完 ML4T 流程：setup → 資料 → 標籤特徵 → 篩選 → 模型驗證 → 回測成本風險 → 封存測試 → 結果。

## 兩個版本（setup.yaml 的 `features.active`）

| 版本 | 特徵 | 驗證期 | 封存期 | 結果位置 |
|---|---|---|---|---|
| **v1** | 文件原始 15 項 | 已跑 | **已正式執行一次（唯一一次）** | `outputs/tables`、`outputs/figures`、`outputs/MLQT_group5_results.xlsx` |
| **v2**（目前） | 第二版 17 項（`notebooks/03b` 只用 2016-11～2020 篩選） | 已跑 | **不重跑**：封存期已用過，v2 若在封存期評估必須標註為事後評估 | `outputs/v2/` |

v1 vs v2 驗證期比較：`outputs/v2/tables/v1_vs_v2_validation.xlsx`、`outputs/v2/figures/v1_vs_v2_validation.png`。

## 重現步驟（從專案根目錄執行）

```bash
pip install -r requirements.txt
python src/01_download.py        # 下載 FinMind 原始資料（免費版有次數限制，程式會自動等待重試）
python src/01b_listing.py        # 證交所上市日期與產業別、手動分割事件（0050 2025-06-18 一拆四）
python src/02_build_dataset.py   # 清理、自行還原權值、資料品質報告
python src/03_features_labels.py # v1 的 15 項特徵（10/20/40 日）與開盤到開盤 5 日波動標籤
python src/03b_features_v2.py    # v2 候選特徵 27 項（含每檔 GARCH 走勢前進估計、行事曆）
python src/04_triage.py          # v1 特徵五道關卡（只用 2016-11～2021 訓練期）
python src/05_validate.py        # 三個驗證年度 walk-forward、參數選擇、成對比較、SHAP（依 features.active 決定特徵組）
python src/06_backtest_validation.py  # 驗證期回測、變體、成本掃描
python src/06b_compare_versions.py    # （v2 時）v1 vs v2 比較
python src/07_holdout.py         # 封存測試：只能執行一次（outputs/HOLDOUT_USED.txt 存在時會拒絕執行；v1 已用過）
python src/08_report.py          # v1 總表、六張圖、風險、預測區間、DSR
python src/09_excel.py           # v1 表格彙整成 Excel
```

`notebooks/` 依課程範本（ETF case study 01–05）做資料與特徵檢查，見 `notebooks/README.md`。
所有隨機種子固定為 42；數字若與報告不同，最可能的原因是 FinMind 資料下載日期不同（`data/raw/manifest.json`）。

## 檔案
- `setup.yaml`：交易設定（v1 決策、成交、標籤、切分、成本、配置、風險；v2 只新增特徵清單與 GARCH 設定）
- `run_log.csv`：研究帳本（每次執行的 git 版本、資料快照、特徵組、評估區間、指標、決策）
- `run_log_before_fix.csv`：帳本修正前的原檔（見下方「修正紀錄」）

## 修正紀錄（2026-11-17）
1. **驗證期碰到封存期**：2024-12-25 決策日的 15 筆驗證樣本，標籤在 2025/1 才結束。已改為依「標籤結束日」切（`models.split`）。
   重算後 v1 選出的參數完全相同，因此 v1 的回測與封存結果不受影響。
2. **研究帳本欄位錯位**：早期 append 時欄位沒有對齊，回看期、回測、封存期紀錄的數值落在錯的欄位，第一次驗證期回測也被重複記錄。
   以 `src/tools_fix_run_log.py` 依各類紀錄的原始欄位順序重建（原檔保留為 `run_log_before_fix.csv`），`log_runs` 改為依欄名對齊。
3. **Deflated Sharpe 的試驗數**：原本誤把封存期紀錄算成試驗（N=69），改為只算封存測試執行之前的試驗（N=57）；DSR 幾乎不變。

## 實作時的決定（簡報未寫明、在此揭露）
1. 資料來源 FinMind（TWSE/TPEx 日成交）；FinMind 免費版沒有還原價，自行以除權息與減資參考價回溯調整。
2. 5222、6770、8028 只使用證交所上市日之後的資料（之前為興櫃，無漲跌幅限制）。
3. 訓練樣本使用所有交易日（標籤重疊，以 purge 處理）；評估只用每 5 日的決策日（時間上不重疊）。
4. Ridge alpha 依老師要求擴為 0.01～10000（含簡報的 0.1/1/10）；LightGBM 使用 MAE 損失、簡報的 8 組參數，未用 early stopping。
5. 股利處理：持有期間以還原價評價（等同股利再投入同一股票，最多 5 日），成交用原始開盤價、整張。
6. 主策略事先指定為「驗證 MAE 最低的模型（LightGBM）＋股票等權」，在看回測結果之前決定。
7. 本金採簡報第 11 頁的 3 億元；備註中的 100 萬元列為變體（整張限制下多數股票買不到）。
8. v2 的股票池規則與 v1 相同；v2 特徵的缺值（新股前 60 天、GARCH 暖身期）在 Ridge 用訓練期中位數補，LightGBM 直接處理缺值。
9. v2 有兩項特徵用到超過 20 日的歷史（60 日波動、GARCH），與文件「過去 20 個交易日」不同，需在報告說明。
