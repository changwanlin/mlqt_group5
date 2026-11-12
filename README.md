# 第五組：台灣半導體相關股票 波動率預測與動態資產配置（ML4T 期中）

一次完整走完 ML4T 流程：setup → 資料 → 標籤特徵 → 篩選 → 模型驗證 → 回測成本風險 → 封存測試 → 結果。

## 重現步驟（從專案根目錄執行）

```bash
pip install -r requirements.txt
python src/01_download.py        # 下載 FinMind 原始資料（免費版有次數限制，程式會自動等待重試）
python src/01b_listing.py        # 證交所上市日期與產業別、手動分割事件（0050 2025-06-18 一拆四）
python src/02_build_dataset.py   # 清理、自行還原權值、資料品質報告
python src/03_features_labels.py # 15 項特徵（10/20/40 日）與開盤到開盤 5 日波動標籤
python src/04_triage.py          # 特徵五道關卡（只用 2016-11～2021 訓練期）
python src/05_validate.py        # 三個驗證年度 walk-forward、參數選擇、成對比較、SHAP 穩定度
python src/06_backtest_validation.py  # 驗證期回測、變體、成本掃描
python src/07_holdout.py         # 封存測試：只能執行一次（outputs/HOLDOUT_USED.txt 存在時會拒絕執行）
python src/08_report.py          # 總表、六張圖、風險、預測區間、DSR
python src/09_excel.py           # 表格彙整成 Excel
```

重現時請先刪除 `run_log.csv` 與 `outputs/HOLDOUT_USED.txt`。所有隨機種子固定為 42；
數字若與報告不同，最可能的原因是 FinMind 資料下載日期不同（`data/raw/manifest.json` 記錄本次下載時間 2026-11-12 UTC）。

## 檔案
- `setup.yaml`：交易設定 v1（決策、成交、標籤、切分、成本、配置、風險）
- `run_log.csv`：研究帳本（每次執行的 git 版本、資料快照、設定、評估區間、指標、決策）
- `outputs/tables/`：所有表格；`outputs/figures/`：所有圖
- `outputs/MLQT_group5_results.xlsx`：表格彙整

## 實作時的決定（簡報未寫明、在此揭露）
1. 資料來源 FinMind（TWSE/TPEx 日成交）；FinMind 免費版沒有還原價，自行以除權息與減資參考價回溯調整。
2. 5222、6770、8028 只使用證交所上市日之後的資料（之前為興櫃，無漲跌幅限制）。
3. 訓練樣本使用所有交易日（標籤重疊，以 purge 處理）；評估只用每 5 日的決策日（時間上不重疊）。
4. Ridge alpha 依老師要求擴為 0.01～10000（含簡報的 0.1/1/10）；LightGBM 使用 MAE 損失、簡報的 8 組參數，未用 early stopping。
5. 股利處理：持有期間以還原價評價（等同股利再投入同一股票，最多 5 日），成交用原始開盤價、整張。
6. 主策略事先指定為「驗證 MAE 最低的模型（LightGBM）＋股票等權」，在看回測結果之前決定。
7. 本金採簡報第 11 頁的 3 億元；備註中的 100 萬元列為變體（整張限制下多數股票買不到）。
