#!/bin/bash
# run_v7.sh — 依 V7 說明書的順序，一次執行全部程式
# 用法（在專案資料夾 mlqt_group5 裡執行）：
#   bash run_v7.sh              # 全部執行（約 8–12 分鐘）
#   bash run_v7.sh --skip-pit   # 跳過最慢的 PIT 驗證（約 5 分鐘）
#   bash run_v7.sh --download   # 先重新下載 FinMind 原始資料再全部執行（需要網路，下載可能要數十分鐘）
set -e                                                       # 任何一步出錯就立刻停下來，不會帶著錯誤繼續跑
cd "$(dirname "$0")"                                         # 切換到這個檔案所在的資料夾（專案根目錄）
PY=.venv/bin/python                                          # 優先使用專案自己的虛擬環境
[ -x "$PY" ] || PY=python3                                   # 沒有虛擬環境時改用系統的 python3
SKIP_PIT=0; DOWNLOAD=0                                       # 預設：要跑 PIT、不重新下載
for arg in "$@"; do                                          # 讀取指令後面的選項
  [ "$arg" = "--skip-pit" ] && SKIP_PIT=1
  [ "$arg" = "--download" ] && DOWNLOAD=1
done
run() { echo; echo "=== $(date +%H:%M:%S) 執行 $1"; "$PY" "src/$1.py"; }  # 定義：印出時間與程式名，再執行
if [ "$DOWNLOAD" = 1 ]; then run 01_download; run 01b_listing; fi  # 重新下載原始資料（選用）
run 02_build_dataset                                         # 清理資料、還原權值
run 03_features_labels                                       # 標籤（未來 5 日開盤到開盤波動）與第一批特徵
run 03b_features_v2                                          # 第二批特徵
run features_30                                              # 其餘特徵
run universe                                                 # 每週可交易名單與決策日
run 03d_garch_oo                                             # 第 18 項特徵：開盤到開盤 GARCH
run 05_model1_v7                                             # Model 1：117 個候選、選模、預測區間（約 2.5 分鐘）
run 07_model2_v7                                             # Model 2：選窗口、目標波動率、α，A–D 回測（約 1 分鐘）
run 11_figures_v7                                            # 結果圖
run 12_correlation_checks                                    # 相關性檢查
run 13_fixed_split_check                                     # 與小組固定切分版比對
if [ "$SKIP_PIT" = 0 ]; then run 10_pit_check; fi            # PIT 驗證（約 3–5 分鐘）
run 14_export_predictions                                    # 每週預測波動率整理成 CSV
run 15_build_dashboard                                       # 互動式儀表板
echo; echo "=== $(date +%H:%M:%S) 全部完成。打開 outputs/v7/dashboard/dashboard.html 看結果。"
