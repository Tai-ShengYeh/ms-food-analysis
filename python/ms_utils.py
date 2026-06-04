# -*- coding: utf-8 -*-
"""
ms_utils.py — Shared loaders / preprocessing / style for the wine GC-MS course.

Dataset: NIH Metabolomics Workbench study ST000006 "White Wine Study"
         (Fiehn lab), GC-TOF MS, analysis AN000020 (peak heights).
         101 white wines x 108 named metabolites, 7 grape varieties.
         Public domain (CC0). Raw datatable cached in ../data/_wine_mw_raw.txt
"""
import os, io, sys
import numpy as np
import pandas as pd

# ---- force UTF-8 stdout on Windows (GOTCHAS F-1) --------------------------
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
FIGDIR = os.path.join(HERE, "figures")
os.makedirs(FIGDIR, exist_ok=True)

# ---- brand palette (matches videos/DESIGN.md) -----------------------------
INK   = "#1A1A1A"
PAPER = "#FAF7EE"
PAPER2= "#F2EDDC"
TEAL  = "#0E7C7B"
CORAL = "#E36414"
GOLD  = "#C8941F"
SLATE = "#6C757D"

# categorical colour per grape variety (on-brand, high contrast)
VARIETY_COLORS = {
    "Chardonnay":      TEAL,
    "Sauvignon Blanc": CORAL,
    "Fume Blanc":      "#F0894B",   # SB family -> lighter coral
    "Pinot gris":      GOLD,
    "Riesling":        "#2A6F97",   # blue
    "Viognier":        "#7B4B94",   # purple
    "Elevage Blanc":   SLATE,
}

RAW_TXT = os.path.join(DATA, "_wine_mw_raw.txt")
CLEAN_CSV = os.path.join(DATA, "wine_gcms.csv")
ORANGE_TAB = os.path.join(DATA, "wine_orange.tab")

META_COLS = ["sample_id", "label", "variety", "variety_group"]


# ---------------------------------------------------------------------------
def build_clean(verbose=True):
    """Parse the raw Metabolomics Workbench datatable into a tidy CSV + Orange .tab."""
    df = pd.read_csv(RAW_TXT, sep="\t")
    samples = df["Samples"].astype(str)
    cls = df["Class"].astype(str)
    # strip the "White wine type and source:" prefix
    label = cls.str.replace(r"^[^:]*:", "", regex=True).str.strip()
    variety = label.str.split(",").str[0].str.strip()
    # Fume Blanc is a marketing synonym for Sauvignon Blanc -> chemical group
    variety_group = variety.replace({"Fume Blanc": "Sauvignon Blanc"})

    feats = df.drop(columns=["Samples", "Class"]).apply(pd.to_numeric, errors="coerce")
    feats = feats.fillna(0.0)

    out = pd.DataFrame({
        "sample_id": samples,
        "label": label,
        "variety": variety,
        "variety_group": variety_group,
    })
    out = pd.concat([out, feats.reset_index(drop=True)], axis=1)
    out.to_csv(CLEAN_CSV, index=False, encoding="utf-8")

    _write_orange_tab(out, feats.columns.tolist())
    if verbose:
        print(f"[build_clean] wrote {CLEAN_CSV}  shape={out.shape}")
        print(f"[build_clean] wrote {ORANGE_TAB}")
        print("[build_clean] variety counts:\n", variety.value_counts().to_string())
    return out


def _write_orange_tab(out, feat_cols):
    """Orange native .tab: 3 header rows (names / types / flags)."""
    # variety_group = class target (Sauvignon Blanc absorbs Fume Blanc -> matches the video's
    # 36 vs 24 binary task); variety kept as meta so students can still colour PCA by all 7.
    names = ["sample_id", "label"] + list(feat_cols) + ["variety", "variety_group"]
    types = ["string", "string"] + ["continuous"] * len(feat_cols) + ["discrete", "discrete"]
    flags = ["meta", "meta"] + [""] * len(feat_cols) + ["meta", "class"]
    lines = ["\t".join(names), "\t".join(types), "\t".join(flags)]
    for _, r in out.iterrows():
        row = [str(r["sample_id"]), str(r["label"])] + \
              [f"{r[c]:.6g}" for c in feat_cols] + \
              [str(r["variety"]), str(r["variety_group"])]
        lines.append("\t".join(row))
    with open(ORANGE_TAB, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
def load(verbose=False):
    """Return (meta_df, X_df, feature_names). Builds the clean CSV on first call."""
    if not os.path.exists(CLEAN_CSV):
        build_clean(verbose=verbose)
    df = pd.read_csv(CLEAN_CSV)
    feat_cols = [c for c in df.columns if c not in META_COLS]
    meta = df[META_COLS].copy()
    X = df[feat_cols].copy()
    return meta, X, feat_cols


def preprocess(X):
    """
    Standard GC-MS metabolomics preprocessing (parallels SNV in the NIR course):
      1. log10(x+1)  -> tame the >6-order-of-magnitude peak-height range
      2. autoscale   -> z-score each metabolite so all contribute equally
    Returns a numpy array.
    """
    Xv = np.asarray(X, dtype=float)
    Xlog = np.log10(Xv + 1.0)
    mu = Xlog.mean(axis=0, keepdims=True)
    sd = Xlog.std(axis=0, ddof=1, keepdims=True)
    sd[sd == 0] = 1.0
    return (Xlog - mu) / sd


def variety_palette(varieties):
    return [VARIETY_COLORS.get(v, SLATE) for v in varieties]


def apply_style():
    import matplotlib as mpl
    mpl.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "axes.edgecolor": "#C2CBC9",
        "axes.labelcolor": INK,
        "text.color": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "axes.grid": True,
        "grid.color": "#E9E9E9",
        "grid.linewidth": 0.8,
        "font.size": 13,
        "axes.titlesize": 16,
        "axes.titleweight": "bold",
        "figure.dpi": 130,
    })


if __name__ == "__main__":
    build_clean()
