# strategies.py — 產生每個決策日的預測、風險門檻與目標權重（驗證與封存測試共用）
import numpy as np, pandas as pd                             # 載入：數值運算、表格
from common import CFG                                       # 載入：設定
from models import make_model, feat_cols, split, FLOOR, STK  # 載入：模型工具

PF = CFG["portfolio"]; GOLD, BM = CFG["universe"]["gold_etf"], CFG["universe"]["passive_benchmark"]  # 配置設定與代號

def parse(cfg):                                              # 定義：把設定名稱轉回參數
    if cfg.startswith("ridge"): return "ridge", {"alpha": float(cfg.split("alpha")[1])}  # Ridge
    v = [int(x) for x in pd.Series([cfg]).str.extract(r"num_leaves(\d+)_min_child_samples(\d+)_n_estimators(\d+)").iloc[0]]  # 取出數字
    return "lgbm", dict(zip(["num_leaves", "min_child_samples", "n_estimators"], v))  # LightGBM

def predict_period(df, model_cfg, train_end, start, end, fset="all15"):  # 定義：用截至 train_end 的資料訓練，預測 start~end 所有合格決策日（不需標籤）
    cols = feat_cols(20, fset)                               # 特徵欄位（預設 v1 的 15 項；封存測試沿用預設）
    tr, _ = split(df, train_end, start, end)                 # 訓練集（含 purge）
    te = df[df.is_decision & (df.date >= pd.Timestamp(start)) & (df.date <= pd.Timestamp(end))]  # 所有合格決策日列（不看未來標籤）
    if model_cfg == "hv": p = te[cols[2]].values             # 歷史波動基準
    else:                                                    # 機器學習模型
        kind, prm = parse(model_cfg)                         # 解析設定
        p = np.maximum(np.asarray(make_model(kind, prm).fit(tr[cols], tr.y).predict(te[cols]), float), FLOOR)  # 訓練、預測、截下限
    return te[["date", "sid", "y", "label_end"]].assign(p=p) # 回傳預測表

def thresholds(df, train_end, valid_start, q=(33, 67)):      # 定義：訓練期「每決策日平均實現波動」的分位數門檻
    tr = df[df.is_decision & df.y.notna() & (df.date >= pd.Timestamp(CFG["data"]["study_start"]))
            & (df.date <= pd.Timestamp(train_end)) & (df.label_end < pd.Timestamp(valid_start))]  # 只用訓練期
    m = tr.groupby("date").y.mean()                          # 每日平均實現波動
    return np.percentile(m, q[0]), np.percentile(m, q[1])    # 回傳低、高門檻

def make_target(pred, thr_by_date, tiers=(0.7, 0.5, 0.3), gold=PF["gold_weight"], alloc="ew", static=None):  # 定義：產生目標權重函數
    P = pred.set_index(["date", "sid"]).p                    # 以（日期, 代號）查預測
    eps = PF["epsilon_vol"]                                  # 反波動率分母下限
    log = []                                                 # 記錄每日風險等級
    def f(d):                                                # 每個決策日呼叫
        w = pd.Series(0.0, index=STK + [GOLD, BM])           # 先全部設 0
        try: p = P.loc[d]                                    # 當日各股預測
        except KeyError: p = pd.Series(dtype=float)          # 沒有預測就空
        p = p[p.index.isin(STK)].dropna()                    # 只留股票
        if static == "bm": w[BM] = 1.0; return w             # 被動基準：全部 0050
        if len(p) == 0: return w                             # 沒有合格股票：全部現金
        if static == "ew100": sw, g = 1.0, 0.0               # 100% 股票等權
        elif static == "fixed": sw, g = 0.5, gold            # 固定 50/20/30
        else:                                                # 動態配置
            lo, hi = thr_by_date(d); avg = p.mean()          # 門檻與平均預測波動
            tier = 0 if avg < lo else (1 if avg < hi else 2) # 低 / 中 / 高風險
            sw, g = tiers[tier], gold                        # 股票與黃金比例
            log.append({"date": d, "avg_pred": avg, "lo": lo, "hi": hi, "tier": ["低", "中", "高"][tier]})  # 記錄
        iw = (1 / np.maximum(p, eps)) if alloc == "iv" else pd.Series(1.0, index=p.index)  # 等權或反波動
        w[p.index] = sw * iw / iw.sum()                      # 股票總比例 × 股內權重
        w[GOLD] = g                                          # 黃金
        return w                                             # 回傳目標權重（其餘為現金）
    f.log = log                                              # 讓外部讀取風險等級紀錄
    return f                                                 # 回傳函數
