# 第五組：台灣半導體股票 波動率預測與動態資產配置

**目前版本：V7**（依小組《研究計畫書 V7》執行，2026-11-23）。
Model 1 預測 15 檔半導體股未來 5 個交易日的波動率；Model 2 依預測分配資金與現金比例，並用回測驗證。

---

## 零、只想看結果

不用執行任何程式，直接打開這些檔案：

| 想看什麼 | 打開哪個檔案 | 怎麼開 |
|---|---|---|
| **互動式儀表板**（回測、預測、驗證） | `outputs/v7/dashboard/dashboard.html` | 在 Finder（Mac）或檔案總管（Windows）雙擊，用瀏覽器開啟 |
| 回測總表 | `outputs/v7/tables/model2/backtest_A_to_D.csv` | Excel 或 Numbers |
| 每週每檔的預測波動率 | `outputs/v7/tables/volatility_predictions_weekly.csv` | Excel 或 Numbers |
| 結果圖 | `outputs/v7/figures/v7_fig1 ～ fig11.png` | 預覽程式（Mac）或相片（Windows） |

---

## 一、取得專案與在哪裡執行

**取得專案**：把整個 `mlqt_group5` 資料夾複製到自己的電腦，例如壓縮成 zip 傳給組員。
要包含 `data/raw/`（原始資料），對方才不必重新下載。`.venv` 是 Mac 專用的，Windows 用不到，可以不附。

所有指令都在「指令視窗」裡、**專案資料夾（專案根目錄）**中執行。不要先切到 `src` 再執行，程式會找不到 `setup.yaml`。

### Mac

1. 打開「終端機」：按 `⌘ + 空白鍵`，輸入「終端機」或「Terminal」，按 Enter。
2. 進入專案資料夾（每次打開終端機都要做一次）：

```bash
cd ~/Desktop/mlqt_group5      # 進入桌面上的專案資料夾（放在別處就改成那個位置）
pwd                           # 確認位置：應顯示 /Users/<你的帳號>/Desktop/mlqt_group5
ls                            # 應看得到 README.md、run_v7.sh、src、data、outputs
```

### Windows

1. 打開「PowerShell」：按 `Windows 鍵`，輸入「PowerShell」，按 Enter。
   （也可以在檔案總管打開 `mlqt_group5` 資料夾，在網址列輸入 `powershell` 後按 Enter，會直接開在這個資料夾。）
2. 進入專案資料夾：

```powershell
cd $HOME\Desktop\mlqt_group5  # 進入桌面上的專案資料夾（放在別處就改成那個位置）
pwd                           # 確認位置：應顯示 C:\Users\<你的帳號>\Desktop\mlqt_group5
dir                           # 應看得到 README.md、run_v7.ps1、run_v7.bat、src、data、outputs
```

> 如果桌面有同步到 OneDrive，路徑可能是 `$HOME\OneDrive\桌面\mlqt_group5`。

---

## 二、第一次使用：安裝 Python 與套件（只要做一次）

需要 **Python 3.13**（3.11 以上應該也可以，但我們只在 3.13 測試過）。

### Mac

專案裡已經有虛擬環境 `.venv`，但還缺 `arch` 和 `PyPortfolioOpt` 兩個套件：

```bash
.venv/bin/python --version                              # 確認：應顯示 Python 3.13.x
.venv/bin/python -m pip install -r requirements.txt     # 安裝／補齊所有套件（約 1–3 分鐘）
```

**為什麼不用 `pip install` 或 `source .venv/bin/activate`？**
這個 `.venv` 原本建在「下載」資料夾，後來搬到桌面，裡面的 `pip` 和 `activate` 還記著舊路徑：

- 直接打 `pip install` 會出現 `bad interpreter`。
- `source .venv/bin/activate` 會把舊的「下載」路徑加進搜尋路徑，之後打 `python` 會找不到（`command not found`），或用到沒有安裝套件的系統 Python（`ModuleNotFoundError`）。

所以 Mac 一律寫 `.venv/bin/python`，就不會受舊路徑影響。

想重建乾淨的虛擬環境（選用）：

```bash
python3 -m venv --clear .venv                           # 清空並在目前位置重建 .venv
.venv/bin/python -m pip install -r requirements.txt     # 重新安裝套件
```

### Windows

1. **安裝 Python**：到 <https://www.python.org/downloads/> 下載 Python 3.13 的 Windows installer。
   安裝畫面第一頁**一定要勾選「Add python.exe to PATH」**，再按 Install Now。
2. **確認安裝成功**（關掉再重開 PowerShell）：

```powershell
py -3.13 --version            # 應顯示 Python 3.13.x（py 是 Python 官方安裝程式附的啟動器）
```

3. **建立 Windows 專用的虛擬環境並安裝套件**。名稱用 `.venv-win`，避免和 Mac 的 `.venv` 混在一起：

```powershell
py -3.13 -m venv .venv-win                                   # 在專案資料夾建立虛擬環境
.venv-win\Scripts\python -m pip install --upgrade pip        # 更新 pip
.venv-win\Scripts\python -m pip install -r requirements.txt  # 安裝所有套件（約 2–5 分鐘）
```

4. **設定 UTF-8**（每次開新的 PowerShell 都要；用 `run_v7.ps1`／`run_v7.bat` 執行時會自動設定）：

```powershell
$env:PYTHONUTF8 = "1"         # 讓 Python 用 UTF-8 讀寫中文，避免 UnicodeEncodeError
```

---

## 三、執行程式

### 方法 A：一次全部執行（建議）

**Mac**

```bash
bash run_v7.sh              # 全部執行，約 8–12 分鐘
bash run_v7.sh --skip-pit   # 跳過最慢的 PIT 驗證，約 5 分鐘
bash run_v7.sh --download   # 先重新下載原始資料再全部執行（需要網路）
```

**Windows**（擇一）

```powershell
.\run_v7.bat                # 最簡單：也可以在檔案總管直接雙擊 run_v7.bat
.\run_v7.bat -SkipPit       # 跳過最慢的 PIT 驗證
powershell -ExecutionPolicy Bypass -File .\run_v7.ps1            # 直接執行 PowerShell 版
powershell -ExecutionPolicy Bypass -File .\run_v7.ps1 -SkipPit   # 跳過 PIT
powershell -ExecutionPolicy Bypass -File .\run_v7.ps1 -Download  # 先重新下載原始資料（需要網路）
```

> `-ExecutionPolicy Bypass` 是因為 Windows 預設不讓 PowerShell 執行沒有簽章的腳本；這個寫法只對這一次執行有效，不會改到系統設定。
> 兩個腳本都會自動使用 `.venv-win`；沒有的話就用系統的 `python`。

共同說明：

- 畫面會依序顯示 `=== 時間 執行 程式名`。
- 最後出現「全部完成」就是成功。
- 任何一步出錯會立刻停下，最後幾行就是錯誤訊息。
- 原始資料已經放在 `data/raw/`，平常**不需要**重新下載。

### 方法 B：一支一支執行

想只重跑某一步時用這種方式。順序不能顛倒，因為後面的程式會用到前面的結果。

**Mac** 的寫法如下。**Windows** 把每行開頭的 `.venv/bin/python` 換成 `.venv-win\Scripts\python`、把 `src/` 換成 `src\`，例如 `.venv-win\Scripts\python src\02_build_dataset.py`（記得先設定 `$env:PYTHONUTF8 = "1"`）。

```bash
.venv/bin/python src/02_build_dataset.py        # 1. 清理資料、還原權值
.venv/bin/python src/03_features_labels.py      # 2. 標籤（未來 5 日開盤到開盤波動）與第一批特徵
.venv/bin/python src/03b_features_v2.py         # 3. 第二批特徵
.venv/bin/python src/features_30.py             # 4. 其餘特徵
.venv/bin/python src/universe.py                # 5. 每週可交易名單與決策日
.venv/bin/python src/03d_garch_oo.py            # 6. 第 18 項特徵：開盤到開盤 GARCH
.venv/bin/python src/05_model1_v7.py            # 7. Model 1：選模、預測區間
.venv/bin/python src/07_model2_v7.py            # 8. Model 2：選設定、A–D 回測
.venv/bin/python src/11_figures_v7.py           # 9. 結果圖
.venv/bin/python src/12_correlation_checks.py   # 10. 相關性檢查
.venv/bin/python src/13_fixed_split_check.py    # 11. 與小組固定切分版比對
.venv/bin/python src/10_pit_check.py            # 12. 特徵 PIT 驗證（最慢）
.venv/bin/python src/14_export_predictions.py   # 13. 每週預測波動率整理成 CSV
.venv/bin/python src/15_build_dashboard.py      # 14. 互動式儀表板
```

| 步驟 | 程式 | 做什麼 | 約需時間 | 主要輸出 |
|---|---|---|---|---|
| 0 | `01_download.py`、`01b_listing.py` | 從 FinMind 下載行情、除權息、減資、上市日（2015-06 起） | 數十分鐘 | `data/raw/` |
| 1 | `02_build_dataset.py` | 清理、自行還原權值 | 數秒 | `data/processed/panel.parquet` |
| 2–4 | `03_features_labels.py`、`03b_features_v2.py`、`features_30.py` | 標籤與 18 項特徵 | 約 20 秒 | `data/processed/samples.parquet`、`features_*.parquet` |
| 5 | `universe.py` | 可交易名單（250 日均額 ≥ 3.5 億、有效日 ≥ 200）與每週決策日 | 數秒 | `data/processed/universe_v3.parquet` |
| 6 | `03d_garch_oo.py` | 開盤到開盤 GARCH(1,1)，每 63 日重估 | 約 15 秒 | `data/processed/features_garch_oo.parquet` |
| 7 | `05_model1_v7.py` | 117 個候選模型、三年 QLIKE 選模、2025–26 事後評估、90% 預測區間 | 約 2.5 分鐘 | `outputs/v7/tables/model1_*.csv` |
| 8 | `07_model2_v7.py`（數學在 `model2_v7.py`） | 窗口 → 目標波動率 → α，A–D 回測、Deflated Sharpe、敏感度 | 約 1 分鐘 | `outputs/v7/tables/model2/` |
| 9 | `11_figures_v7.py` | 9 張結果圖 | 數秒 | `outputs/v7/figures/` |
| 10 | `12_correlation_checks.py` | 特徵相關、相關矩陣數值檢查、權重穩定性 | 約 20 秒 | `outputs/v7/tables/correlation/` |
| 11 | `13_fixed_split_check.py` | 用小組固定切分（訓練到 2021、驗證 2022–23、測試 2024–26）重跑比對 | 約 10 秒 | `outputs/v7/tables/fixed_split/` |
| 12 | `10_pit_check.py` | 刪掉截止日之後的資料重跑，確認特徵沒有偷看未來 | 約 3–5 分鐘 | `outputs/v7/tables/pit/` |
| 13 | `14_export_predictions.py` | 每週每檔預測、90% 區間、HV20、GARCH、EWMA、實際值 | 數秒 | `outputs/v7/tables/volatility_predictions_weekly.csv` |
| 14 | `15_build_dashboard.py`（版面在 `dashboard_template.html`） | 互動式儀表板 | 數秒 | `outputs/v7/dashboard/dashboard.html` |

時間是在一般筆電上的估計，Windows 和 Mac 差不多。**只改了某一步時，要從那一步往後全部重跑。** 例如改了 Model 2 的程式，就從第 8 步跑到第 14 步（第 12 步 PIT 可省略）。

---

## 四、結果放在哪裡

```
outputs/v7/
├── dashboard/dashboard.html          互動式儀表板（雙擊開啟）
├── figures/                          結果圖 v7_fig1 ～ fig11
└── tables/
    ├── model1_*.csv                  Model 1：選模、各年 QLIKE、事後評估、預測區間
    ├── selected_configs.csv          選出的主模型
    ├── volatility_predictions_weekly.csv  每週每檔的預測波動率
    ├── model2/                       Model 2：窗口比較、目標波動率、α、回測、淨值、每週配置、交易、敏感度、DSR
    ├── pit/                          PIT 驗證
    ├── correlation/                  相關性檢查
    └── fixed_split/                  固定切分比對
```

V7 沒有寫明、本版自行決定的處理（例如缺資料、停牌、利率），列在 `src/07_model2_v7.py` 開頭。

---

## 五、常見錯誤

### Mac 與共通

| 看到的訊息 | 原因 | 解決方式 |
|---|---|---|
| `bad interpreter: /Users/.../Downloads/...` | `.venv` 搬過位置，`pip` 記著舊路徑 | 改用 `.venv/bin/python -m pip ...`（見第二節） |
| `ModuleNotFoundError: No module named 'arch'`（或 `pypfopt`） | 套件沒裝，或用到系統 Python | 執行 `.venv/bin/python -m pip install -r requirements.txt`，並用 `.venv/bin/python` 執行 |
| `FileNotFoundError: ... setup.yaml` | 不在專案根目錄 | 先 `cd ~/Desktop/mlqt_group5` |
| `FileNotFoundError: ... panel.parquet`（或其他 parquet） | 前面的步驟還沒跑 | 依第三節順序從前面補跑，或直接 `bash run_v7.sh` |
| `CERTIFICATE_VERIFY_FAILED`（下載或安裝時） | Mac 的 Python 找不到 SSL 憑證 | `.venv/bin/python -m pip install --upgrade certifi`，再執行 `export SSL_CERT_FILE=$(.venv/bin/python -m certifi)`，然後重試 |
| `command not found: python` | Mac 預設只有 `python3` | 用 `.venv/bin/python`，或把 `python` 改成 `python3` |
| 圖上的中文變成方框 | 找不到中文字型 | 不影響數字；Mac 會自動使用「蘋方-繁」，Windows 會使用「微軟正黑體」 |

### Windows

| 看到的訊息 | 原因 | 解決方式 |
|---|---|---|
| 輸入 `python` 卻打開 Microsoft Store | Windows 內建的假捷徑 | 改用 `py -3.13`；或到「設定 → 應用程式 → 進階應用程式設定 → 應用程式執行別名」關掉 python.exe 的兩個開關 |
| `'py' 不是內部或外部命令` | Python 沒裝好，或安裝時沒勾「Add python.exe to PATH」 | 重新執行 Python 安裝程式，選 Modify 或重新安裝並勾選 |
| `因為這個系統上已停用指令碼執行` | PowerShell 預設不執行腳本 | 用 `powershell -ExecutionPolicy Bypass -File .\run_v7.ps1`，或雙擊 `run_v7.bat` |
| `UnicodeEncodeError` 或中文變亂碼 | Windows 預設不是 UTF-8 | 先執行 `$env:PYTHONUTF8 = "1"` 再跑；用 `run_v7.ps1`／`run_v7.bat` 時會自動設定 |
| `ModuleNotFoundError` | 用到沒有安裝套件的 Python | 用 `.venv-win\Scripts\python` 執行，或重新做第二節的安裝 |
| 安裝套件時 `Microsoft Visual C++ 14.0 is required` | 少數套件需要編譯 | 確認用的是 64 位元的 Python 3.13（通常可直接下載現成套件，不需編譯）；仍不行再安裝「Microsoft C++ Build Tools」 |
| 路徑中有空白或中文出錯 | 少數工具不支援 | 把專案放在較短的英文路徑，例如 `C:\mlqt_group5` |

---

## 六、其他資料夾

| 資料夾或檔案 | 內容 |
|---|---|
| `setup.yaml` | 所有設定：股票、期間、特徵清單（`features.active: v7`）、成本 |
| `data/raw/` | FinMind 原始資料；`manifest.json` 記錄下載日期 |
| `data/processed/` | 處理後的資料與特徵 |
| `研究計畫書_V7.pdf` | 小組 V7 說明書 |
| `_backup_before_v7_2026-11-23/` | 換成 V7 前被覆蓋的舊檔備份 |
| `_v7_transfer/` | 傳檔用的壓縮檔，確認無誤後可自行刪除 |
| `run_v7.sh` | Mac／Linux 一鍵執行 |
| `run_v7.ps1`、`run_v7.bat` | Windows 一鍵執行（`.bat` 可直接雙擊） |
| `.venv`／`.venv-win` | Mac／Windows 各自的虛擬環境，不要互相複製使用 |
| `notebooks/`、`docs/` | 課程範本檢查與早期規格文件 |

---

# 舊版紀錄（v1–v3）

以下是 V7 之前的版本說明，保留作為研究紀錄。

## 舊版本（setup.yaml 的 `features.active`）

| 版本 | 特徵 | 驗證期 | 封存期 | 結果位置 |
|---|---|---|---|---|
| **v1** | 文件原始 15 項 | 已跑 | **已正式執行一次（唯一一次）** | `outputs/tables`、`outputs/figures`、`outputs/MLQT_group5_results.xlsx` |
| **v2** | 第二版 17 項（`notebooks/03b` 只用 2016-11～2020 篩選） | 已跑 | **不重跑**：封存期已用過，v2 若在封存期評估必須標註為事後評估 | `outputs/v2/` |
| **v3**（目前，理想策略） | 同 v2 的 17 項（大盤 HMM 未通過第 4 關，不加入）＋書面提案的完整交易規則 | **模型驗證已跑；回測程式已寫好、尚未執行** | 同上：只能做「事後評估」 | `outputs/v3/`、規格見 `docs/strategy_v3.md` |

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
python src/universe.py           # （v3）時點正確的可交易股票池（250 日均額 ≥ 3.5 億）與每週決策日
python src/05_validate_v3.py     # （v3）115 個候選模型、QLIKE 選模、兩種風險等級規則比較（不交易）
python src/06_backtest_v3.py     # （v3）驗證期回測——已寫好，尚未執行
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
10. v3 的選模規則原文是「QLIKE 差距 1% 內選較簡單者」，第一次執行時 Lasso 與 ElasticNet 同分，原文沒有定義跨家族誰較簡單；
    補寫為「先比超參數個數，再比懲罰強度／樹數」（`setup.yaml` 的 `v3.models.tie_break`）。這個補充只用到驗證期資訊。
11. v3 的模型用所有合格股票訓練（學「波動怎麼變」），只有交易、門檻與評估限制在可交易股票。
