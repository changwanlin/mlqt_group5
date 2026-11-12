# 03_features_labels.py — 建立 15 項特徵（10/20/40 日三種回看版本）與開盤到開盤 5 日實現波動標籤
import numpy as np, pandas as pd                             # 載入：數值運算、表格
from common import ROOT, CFG, PROC, TAB                      # 載入：路徑與設定

panel = pd.read_parquet(PROC/"panel.parquet")                # 讀清理後面板
panel["avolume"] = panel.volume / panel.adj                  # 還原後成交量（股數依公司行動同步調整）
panel.loc[~panel.valid, ["avolume", "amount"]] = np.nan      # 無效日的量與金額設為空值
cal = pd.DatetimeIndex(sorted(panel.date.unique()))          # 交易日曆
H = CFG["schedule"]["label_horizon_days"]                    # 預測期間 5 日

def rmean(x, n): return x.rolling(n, min_periods=n).mean()   # 定義：n 日移動平均（窗內有空值就給空值）
def rsum(x, n):  return x.rolling(n, min_periods=n).sum()    # 定義：n 日移動加總
def rstd(x, n):  return x.rolling(n, min_periods=n).std()    # 定義：n 日移動標準差

def make_features(g, L):                                     # 定義：對單一股票、回看期 L 計算 15 項特徵
    a, b, c = max(2, round(L / 4)), round(L / 2), L          # 三個波動窗：20 日版為 5/10/20
    k = round(0.7 * L)                                       # RSI/ATR 窗：20 日版為 14
    C, O, Hh, Lw = g.aclose, g.aopen, g.ahigh, g.alow        # 取出還原後收、開、高、低
    r = np.log(C / C.shift(1))                               # 每日收盤對數報酬
    f = pd.DataFrame(index=g.index)                          # 準備空表放特徵
    for n in (a, b, c): f[f"hv{n}"] = np.sqrt(252 / n * rsum(r ** 2, n))  # 歷史波動（年化，與標籤同定義）
    f["ret1"] = r                                            # 1 日報酬
    f[f"ret{a}"] = np.log(C / C.shift(a))                    # 短期報酬
    f[f"ret{c}"] = np.log(C / C.shift(c))                    # 回看期報酬
    f["hl"] = (Hh - Lw) / C                                  # 當日高低價差比例
    f["oc"] = (C - O) / O                                    # 當日開收盤價差比例
    f[f"ma{a}_dist"] = C / rmean(C, a) - 1                   # 與短均線距離
    f[f"ma{c}_dist"] = C / rmean(C, c) - 1                   # 與長均線距離
    f["vol_ratio"] = g.avolume / rmean(g.avolume, c)         # 成交量比
    f["vol_cv"] = rstd(g.avolume, c) / rmean(g.avolume, c)   # 量的變動（標準差 ÷ 平均）
    f["amt_ratio"] = g.amount / rmean(g.amount, c)           # 成交金額比
    d = C.diff()                                             # 每日價格變化
    up, dn = rmean(d.clip(lower=0), k), rmean((-d).clip(lower=0), k)  # 固定窗平均漲幅與跌幅
    f["rsi"] = np.where(dn > 0, 100 - 100 / (1 + up / dn.replace(0, np.nan)), 100.0)  # RSI（無跌幅時為 100）
    f.loc[up.isna() | dn.isna(), "rsi"] = np.nan             # 窗內有空值就設空值
    tr = pd.concat([Hh - Lw, (Hh - C.shift()).abs(), (Lw - C.shift()).abs()], axis=1).max(axis=1, skipna=False)  # 真實波幅
    f["atr_p"] = rmean(tr, k) / C                            # ATR ÷ 股價
    return f                                                 # 回傳 15 項特徵

def realized(aO, h):                                         # 定義：t+1 開盤起 h 日的開盤到開盤實現波動
    ro = np.log(aO / aO.shift(1))                            # 開盤對數報酬
    return np.sqrt(252 / h * rsum(ro ** 2, h)).shift(-(h + 1))  # 加總 t+2…t+h+1 的報酬平方並年化

out = []                                                     # 收集每檔結果
for sid, g in panel.groupby("sid"):                          # 逐一股票
    g = g.set_index("date").sort_index()                     # 以日期為索引
    parts = [g[["valid", "open", "close", "amount", "aopen", "aclose", "adj"]]]  # 保留回測需要的原始欄位
    for L in (10, 20, 40):                                   # 三種回看期
        parts.append(make_features(g, L).add_suffix(f"_L{L}"))  # 計算並加上後綴
    lab = pd.DataFrame({"y": realized(g.aopen, H),           # 主標籤：5 日
                        "y10": realized(g.aopen, 10),        # IC 衰減用：10 日
                        "y20": realized(g.aopen, 20)}, index=g.index)  # IC 衰減用：20 日
    pos = cal.get_indexer(g.index)                           # 每天在日曆中的位置
    lab["label_end"] = [cal[p + H + 1] if p + H + 1 < len(cal) else pd.NaT for p in pos]  # 標籤結束日 t+6
    lab["adv20"] = rmean(g.amount, 20)                       # 過去 20 日平均成交金額（容量限制用）
    x = pd.concat(parts + [lab], axis=1); x["sid"] = sid     # 合併並加上代號
    out.append(x.reset_index())                              # 收進清單
df = pd.concat(out, ignore_index=True)                       # 合併所有股票

start = pd.Timestamp(CFG["data"]["study_start"])             # 研究起點
grid = cal[cal >= start][::CFG["schedule"]["decision_every_n_days"]]  # 決策日：起點後每 5 個交易日
df["is_decision"] = df.date.isin(grid)                       # 標記決策日
F20 = [c for c in df.columns if c.endswith("_L20")]          # 20 日版特徵欄位
df["eligible"] = df.valid & df[F20].notna().all(axis=1)      # 合格：t 日有成交且 15 項特徵齊全
df = df[df.date >= start - pd.Timedelta(days=0)]             # 只留研究期間
df.to_parquet(PROC/"samples.parquet", index=False)           # 存檔
pd.Series(grid).to_csv(TAB/"decision_dates.csv", index=False, header=["decision_date"])  # 存決策日

stk = df[~df.sid.isin(["0050", "00635U"])]                   # 只看 15 檔股票
cov = stk[stk.is_decision & stk.eligible].groupby("date").size()  # 每個決策日合格股票數
cov.to_csv(TAB/"coverage_eligible_names.csv", header=["n_eligible"])  # 存覆蓋率
print("features:", F20)                                      # 印出特徵名稱
print("decision dates:", len(grid), grid[0].date(), grid[-1].date())  # 印出決策日數量
print(cov.describe())                                        # 印出覆蓋率摘要
