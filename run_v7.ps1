# run_v7.ps1 — Windows 版：依 V7 說明書的順序，一次執行全部程式（功能和 Mac 的 run_v7.sh 相同）
# 用法（在 PowerShell 裡、專案資料夾 mlqt_group5 中執行）：
#   powershell -ExecutionPolicy Bypass -File .\run_v7.ps1            # 全部執行（約 8–12 分鐘）
#   powershell -ExecutionPolicy Bypass -File .\run_v7.ps1 -SkipPit   # 跳過最慢的 PIT 驗證（約 5 分鐘）
#   powershell -ExecutionPolicy Bypass -File .\run_v7.ps1 -Download  # 先重新下載 FinMind 原始資料（需要網路）
# 也可以直接雙擊 run_v7.bat，或在命令提示字元輸入 run_v7.bat -SkipPit
param([switch]$SkipPit, [switch]$Download)                  # 兩個選項：跳過 PIT、重新下載
Set-Location $PSScriptRoot                                   # 切換到這個檔案所在的資料夾（專案根目錄）
$env:PYTHONUTF8 = "1"                                        # 讓 Python 一律用 UTF-8 讀寫，中文才不會出錯
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}  # 讓視窗正確顯示中文
$py = Join-Path $PSScriptRoot ".venv-win\Scripts\python.exe" # 優先使用 Windows 專用的虛擬環境
if (-not (Test-Path $py)) { $py = "python" }                 # 沒有虛擬環境時改用系統的 python
function Run([string]$name) {                                # 定義：印出時間與程式名，再執行；失敗就停下
    Write-Host ""
    Write-Host ("=== {0} 執行 {1}" -f (Get-Date -Format "HH:mm:ss"), $name)
    & $py ("src\" + $name + ".py")
    if ($LASTEXITCODE -ne 0) { Write-Host ("*** {0} 失敗，錯誤訊息在上面幾行" -f $name); exit $LASTEXITCODE }
}
if ($Download) { Run "01_download"; Run "01b_listing" }      # 重新下載原始資料（選用）
Run "02_build_dataset"                                       # 清理資料、還原權值
Run "03_features_labels"                                     # 標籤與第一批特徵
Run "03b_features_v2"                                        # 第二批特徵
Run "features_30"                                            # 其餘特徵
Run "universe"                                               # 每週可交易名單與決策日
Run "03d_garch_oo"                                           # 第 18 項特徵：開盤到開盤 GARCH
Run "05_model1_v7"                                           # Model 1（約 2.5 分鐘）
Run "07_model2_v7"                                           # Model 2 與 A–D 回測（約 1 分鐘）
Run "11_figures_v7"                                          # 結果圖
Run "12_correlation_checks"                                  # 相關性檢查
Run "13_fixed_split_check"                                   # 與小組固定切分版比對
if (-not $SkipPit) { Run "10_pit_check" }                    # PIT 驗證（約 3–5 分鐘）
Run "14_export_predictions"                                  # 每週預測波動率整理成 CSV
Run "15_build_dashboard"                                     # 互動式儀表板
Write-Host ""
Write-Host ("=== {0} 全部完成。打開 outputs\v7\dashboard\dashboard.html 看結果。" -f (Get-Date -Format "HH:mm:ss"))
