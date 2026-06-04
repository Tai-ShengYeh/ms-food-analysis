# -*- coding: utf-8 -*-
"""02_pca.py — unsupervised PCA on the wine GC-MS fingerprints.

Narrative: PCA on all 101 wines flags 5 anomalies (the lone 2001 vintage batch)
via Hotelling's T^2; after setting them aside, wines self-sort by grape variety.
Preprocessing: log10 + autoscale (chosen over Pareto/center — clearest separation).
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from sklearn.decomposition import PCA
from scipy.stats import chi2, f as fdist
import ms_utils as U

U.apply_style()
meta, X, feat = U.load()
Xp = U.preprocess(X)
n = Xp.shape[0]


def hotelling_ellipse(scores, conf):
    cov = np.cov(scores.T)
    vals, vecs = np.linalg.eigh(cov)
    order = vals.argsort()[::-1]; vals, vecs = vals[order], vecs[:, order]
    ang = np.degrees(np.arctan2(vecs[1, 0], vecs[0, 0]))
    w, h = 2 * np.sqrt(vals * chi2.ppf(conf, 2))
    return scores.mean(0), w, h, ang


# ---- PCA on all samples; Hotelling T^2 (2-comp) flags outliers -------------
pca = PCA(n_components=8).fit(Xp); T = pca.transform(Xp)
lam = pca.explained_variance_
t2 = (T[:, :2] ** 2 / lam[:2]).sum(1)
lim99 = (2 * (n - 1) / (n - 2)) * fdist.ppf(0.99, 2, n - 2)
outlier = t2 > lim99

# ---- fig ms04_full: all wines, variety-coloured, outliers ringed -----------
fig, ax = plt.subplots(figsize=(8.8, 6.0))
evr = pca.explained_variance_ratio_ * 100
for var in meta["variety"].unique():
    m = meta["variety"].eq(var).values
    ax.scatter(T[m, 0], T[m, 1], s=66, alpha=.85, color=U.VARIETY_COLORS.get(var, U.SLATE),
               edgecolor="white", lw=.6, label=var)
ax.scatter(T[outlier, 0], T[outlier, 1], s=210, facecolors="none", edgecolors=U.INK, lw=1.8)
cx, w, h, ang = hotelling_ellipse(T[:, :2], 0.95)
ax.add_patch(Ellipse(cx, w, h, angle=ang, fill=False, ls="--", ec=U.INK, lw=1.4, alpha=.7))
ax.set_xlabel(f"PC1 ({evr[0]:.1f}%)"); ax.set_ylabel(f"PC2 ({evr[1]:.1f}%)")
ax.set_title("All 101 wines — PCA flags 5 anomalies (the 2001 batch)")
ax.legend(frameon=False, fontsize=9, ncol=2)
ax.axhline(0, color="#ccc", lw=.8); ax.axvline(0, color="#ccc", lw=.8)
fig.tight_layout(); fig.savefig(os.path.join(U.FIGDIR, "ms04_pca_scores_full.png")); plt.close(fig)

# ---- cleaned PCA (drop outliers) -> scree, scores, loadings ----------------
keep = ~outlier
metac = meta[keep].reset_index(drop=True)
pcac = PCA(n_components=10).fit(Xp[keep]); Tc = pcac.transform(Xp[keep])
evrc = pcac.explained_variance_ratio_ * 100
cumc = np.cumsum(evrc)

# scree
fig, ax = plt.subplots(figsize=(8.4, 4.6))
xs = np.arange(1, 11)
ax.bar(xs, evrc, color=U.TEAL, alpha=.9)
ax.set_xlabel("Principal component"); ax.set_ylabel("Variance explained (%)")
ax.set_title("Scree plot — a fingerprint is higher-dimensional than a spectrum")
ax2 = ax.twinx(); ax2.plot(xs, cumc, "-o", color=U.CORAL, lw=2.4); ax2.set_ylim(0, 105)
ax2.set_ylabel("Cumulative (%)", color=U.CORAL); ax2.grid(False)
for x, c in zip(xs[:3], cumc[:3]):
    ax2.annotate(f"{c:.0f}%", (x, c), textcoords="offset points", xytext=(0, 10),
                 color=U.CORAL, fontweight="bold", ha="center")
fig.tight_layout(); fig.savefig(os.path.join(U.FIGDIR, "ms03_pca_scree.png")); plt.close(fig)

# scores (clean, variety aha)
fig, ax = plt.subplots(figsize=(8.6, 6.0))
for var in metac["variety"].unique():
    m = metac["variety"].eq(var).values
    ax.scatter(Tc[m, 0], Tc[m, 1], s=72, alpha=.85, color=U.VARIETY_COLORS.get(var, U.SLATE),
               edgecolor="white", lw=.6, label=var)
ax.set_xlabel(f"PC1 ({evrc[0]:.1f}%)"); ax.set_ylabel(f"PC2 ({evrc[1]:.1f}%)")
ax.set_title("After cleaning — wines self-sort by grape variety")
ax.legend(frameon=False, fontsize=9, ncol=2)
ax.axhline(0, color="#ccc", lw=.8); ax.axvline(0, color="#ccc", lw=.8)
fig.tight_layout(); fig.savefig(os.path.join(U.FIGDIR, "ms04_pca_scores.png")); plt.close(fig)

# loadings (clean)
P = pcac.components_
fig, ax = plt.subplots(figsize=(8.8, 6.0))
ax.scatter(P[0], P[1], s=26, color=U.SLATE, alpha=.55)
imp = np.argsort(-(P[0] ** 2 + P[1] ** 2))[:8]
for j in imp:
    ax.annotate(feat[j], (P[0, j], P[1, j]), fontsize=9, color=U.INK,
                xytext=(4, 3), textcoords="offset points")
    ax.scatter([P[0, j]], [P[1, j]], s=48, color=U.CORAL, zorder=3)
ax.set_xlabel("PC1 loading"); ax.set_ylabel("PC2 loading")
ax.set_title("Loadings — the metabolites behind the axes")
ax.axhline(0, color="#ccc", lw=.8); ax.axvline(0, color="#ccc", lw=.8)
fig.tight_layout(); fig.savefig(os.path.join(U.FIGDIR, "ms05_pca_loadings.png")); plt.close(fig)

# ---- metrics ---------------------------------------------------------------
top_pc1 = [feat[j] for j in np.argsort(-np.abs(P[0]))[:8]]
with open(os.path.join(U.DATA, "metrics_pca.txt"), "w", encoding="utf-8") as f:
    f.write("# PCA metrics (log10+autoscale)\n")
    f.write(f"n_outliers={int(outlier.sum())}\n")
    f.write("outlier_labels=" + " | ".join(meta['label'][i] for i in np.where(outlier)[0]) + "\n")
    f.write(f"n_clean={int(keep.sum())}\n")
    for i in range(5):
        f.write(f"PC{i+1}_var={evrc[i]:.2f}%  cum={cumc[i]:.2f}%\n")
    f.write(f"n_pc_for_80pct={int(np.argmax(cumc >= 80) + 1)}\n")
    f.write("top_PC1_metabolites=" + ", ".join(top_pc1) + "\n")
print("[02_pca] outliers=%d | clean PC1=%.1f%% PC2=%.1f%% cum3=%.1f%%"
      % (outlier.sum(), evrc[0], evrc[1], cumc[2]))
