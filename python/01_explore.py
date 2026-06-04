# -*- coding: utf-8 -*-
"""01_explore.py — build the clean dataset + raw-data overview figures."""
import os
import numpy as np
import matplotlib.pyplot as plt
import ms_utils as U

U.apply_style()
meta, X, feat = U.load(verbose=True)
Xv = X.values

# ---- fig ms01: raw metabolite "fingerprints" for a few wines ---------------
fig, ax = plt.subplots(figsize=(9, 4.6))
shown = []
for var in ["Chardonnay", "Sauvignon Blanc", "Riesling", "Viognier", "Pinot gris"]:
    idx = meta.index[meta["variety_group"].eq(var) if var == "Sauvignon Blanc"
                     else meta["variety"].eq(var)]
    if len(idx):
        i = idx[0]
        ax.plot(np.arange(Xv.shape[1]), Xv[i] + 1, lw=1.4,
                color=U.VARIETY_COLORS.get(var, U.SLATE), label=var, alpha=0.9)
        shown.append(var)
ax.set_yscale("log")
ax.set_xlabel("Metabolite index (1–108)")
ax.set_ylabel("GC-MS peak height (log)")
ax.set_title("Each wine = a 108-metabolite GC-MS fingerprint")
ax.legend(frameon=False, fontsize=10, ncol=3)
fig.tight_layout(); fig.savefig(os.path.join(U.FIGDIR, "ms01_raw_profiles.png")); plt.close(fig)

# ---- fig ms02: why preprocess (raw vs log+autoscale distribution) ----------
Xp = U.preprocess(X)
fig, axes = plt.subplots(1, 2, figsize=(9.4, 4.2))
axes[0].hist(Xv[Xv > 0].ravel(), bins=60, color=U.CORAL, alpha=0.85)
axes[0].set_yscale("log")
axes[0].set_title("Raw peak heights\n(>6 orders of magnitude, skewed)")
axes[0].set_xlabel("peak height"); axes[0].set_ylabel("count (log)")
axes[1].hist(Xp.ravel(), bins=60, color=U.TEAL, alpha=0.85)
axes[1].set_title("After log10 + autoscale\n(comparable, ~standard normal)")
axes[1].set_xlabel("z-score"); axes[1].set_ylabel("count")
fig.tight_layout(); fig.savefig(os.path.join(U.FIGDIR, "ms02_preprocess.png")); plt.close(fig)

# ---- metrics ---------------------------------------------------------------
with open(os.path.join(U.DATA, "metrics_explore.txt"), "w", encoding="utf-8") as f:
    f.write("# Explore metrics\n")
    f.write(f"n_samples={Xv.shape[0]}\nn_features={Xv.shape[1]}\n")
    f.write(f"raw_min={Xv.min():.4g}\nraw_max={Xv.max():.4g}\n")
    f.write(f"dynamic_range_orders={np.log10(Xv.max()/max(Xv[Xv>0].min(),1)):.2f}\n")
    f.write("varieties=" + ", ".join(f"{k}:{v}" for k, v in
            meta['variety'].value_counts().items()) + "\n")
    f.write("variety_groups=" + ", ".join(f"{k}:{v}" for k, v in
            meta['variety_group'].value_counts().items()) + "\n")
print("[01_explore] figures + metrics_explore.txt written")
