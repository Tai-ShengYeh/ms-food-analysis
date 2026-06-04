# -*- coding: utf-8 -*-
"""03_plsda.py — supervised PLS-DA: classify grape variety from the GC-MS fingerprint.

Binary task: Chardonnay vs Sauvignon Blanc (Fume Blanc merged into Sauvignon Blanc).
Honest validation: log+autoscale live INSIDE each cross-validation fold.
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cross_decomposition import PLSRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, FunctionTransformer
from sklearn.model_selection import StratifiedKFold, cross_val_predict
import ms_utils as U

U.apply_style()
meta, X, feat = U.load()

# --- binary subset ----------------------------------------------------------
TWO = ["Chardonnay", "Sauvignon Blanc"]
mask = meta["variety_group"].isin(TWO).values
Xs = X.values[mask]
g = meta["variety_group"].values[mask]
y = (g == "Chardonnay").astype(int)        # 1 = Chardonnay, 0 = Sauvignon Blanc
n0, n1 = int((y == 0).sum()), int((y == 1).sum())


def make_pipe(k):
    return Pipeline([
        ("log", FunctionTransformer(lambda x: np.log10(x + 1.0))),
        ("scale", StandardScaler()),
        ("pls", PLSRegression(n_components=k)),
    ])


# --- CV accuracy vs number of latent variables ------------------------------
ks = range(1, 16)
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
acc = []
for k in ks:
    yhat = cross_val_predict(make_pipe(k), Xs, y.astype(float), cv=cv).ravel()
    acc.append(((yhat >= 0.5).astype(int) == y).mean() * 100)
acc = np.array(acc)
best_k = int(np.array(list(ks))[acc.argmax()])
best_acc = float(acc.max())

# --- fig ms07: accuracy vs LV (the overfitting lesson) ----------------------
fig, ax = plt.subplots(figsize=(8.4, 4.6))
ax.plot(list(ks), acc, "-o", color=U.TEAL, lw=2.4)
ax.scatter([best_k], [best_acc], s=160, color=U.CORAL, zorder=5,
           label=f"best: {best_k} LV, {best_acc:.0f}%")
ax.set_xlabel("Number of latent variables (LV)")
ax.set_ylabel("5-fold CV accuracy (%)")
ax.set_title("Choosing model complexity — more is not better")
ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(os.path.join(U.FIGDIR, "ms07_plsda_cv.png")); plt.close(fig)

# --- final model at best_k (full subset) for scores + VIP -------------------
pipe = make_pipe(best_k).fit(Xs, y.astype(float))
pls = pipe.named_steps["pls"]
Xtr = pipe.named_steps["scale"].transform(
    pipe.named_steps["log"].transform(Xs))
T = pls.x_scores_

# --- fig ms06: PLS-DA score plot (supervised separation) --------------------
fig, ax = plt.subplots(figsize=(8.0, 5.6))
for lab, val, col in [("Chardonnay", 1, U.TEAL), ("Sauvignon Blanc", 0, U.CORAL)]:
    m = y == val
    ax.scatter(T[m, 0], T[m, 1], s=80, alpha=0.85, color=col,
               edgecolor="white", linewidth=0.6, label=f"{lab} (n={m.sum()})")
ax.set_xlabel("PLS LV1"); ax.set_ylabel("PLS LV2")
ax.set_title("PLS-DA scores — supervised axes split the two varieties")
ax.legend(frameon=False); ax.axhline(0, color="#bbb", lw=0.8); ax.axvline(0, color="#bbb", lw=0.8)
fig.tight_layout(); fig.savefig(os.path.join(U.FIGDIR, "ms06_plsda_scores.png")); plt.close(fig)

# --- fig ms08: cross-validated confusion matrix at best_k -------------------
yhat = (cross_val_predict(make_pipe(best_k), Xs, y.astype(float), cv=cv).ravel() >= 0.5).astype(int)
cm = np.zeros((2, 2), int)
for t, p in zip(y, yhat):
    cm[1 - t, 1 - p] += 1      # order rows/cols: Chardonnay(top/left), SauvBlanc
labels = ["Chardonnay", "Sauvignon Blanc"]
fig, ax = plt.subplots(figsize=(5.6, 5.0))
im = ax.imshow(cm, cmap="BuGn")
for i in range(2):
    for j in range(2):
        ax.text(j, i, cm[i, j], ha="center", va="center",
                fontsize=22, fontweight="bold",
                color="white" if cm[i, j] > cm.max() * 0.6 else U.INK)
ax.set_xticks([0, 1]); ax.set_xticklabels(labels)
ax.set_yticks([0, 1]); ax.set_yticklabels(labels, rotation=90, va="center")
ax.set_xlabel("Predicted"); ax.set_ylabel("Actual")
ax.set_title(f"Cross-validated confusion ({best_k} LV)")
ax.grid(False)
fig.tight_layout(); fig.savefig(os.path.join(U.FIGDIR, "ms08_plsda_confusion.png")); plt.close(fig)

# --- VIP scores -------------------------------------------------------------
W = pls.x_weights_                  # p x k
Tsc = pls.x_scores_                 # n x k
Q = pls.y_loadings_.ravel()         # k
ssy = (Tsc ** 2).sum(axis=0) * (Q ** 2)
Wn = W / np.linalg.norm(W, axis=0, keepdims=True)
vip = np.sqrt(W.shape[0] * ((Wn ** 2) * ssy).sum(axis=1) / ssy.sum())
top = np.argsort(-vip)[:15]

# --- fig ms09: top discriminating metabolites (VIP) -------------------------
fig, ax = plt.subplots(figsize=(8.6, 6.0))
yy = np.arange(len(top))[::-1]
ax.barh(yy, vip[top], color=U.CORAL, alpha=0.9)
ax.axvline(1.0, color=U.INK, ls="--", lw=1.2, alpha=0.7)
ax.text(1.02, len(top) - 1, "VIP = 1", color=U.INK, fontsize=10)
ax.set_yticks(yy); ax.set_yticklabels([feat[j] for j in top], fontsize=10)
ax.set_xlabel("VIP score"); ax.set_title("Which metabolites separate the varieties?")
ax.grid(axis="y", alpha=0)
fig.tight_layout(); fig.savefig(os.path.join(U.FIGDIR, "ms09_plsda_vip.png")); plt.close(fig)

# --- metrics ----------------------------------------------------------------
sens = cm[0, 0] / cm[0].sum() * 100   # Chardonnay recall
spec = cm[1, 1] / cm[1].sum() * 100   # SauvBlanc recall
with open(os.path.join(U.DATA, "metrics_plsda.txt"), "w", encoding="utf-8") as f:
    f.write("# PLS-DA metrics (Chardonnay vs Sauvignon Blanc)\n")
    f.write(f"n_chardonnay={n1}\nn_sauvblanc={n0}\nn_total={len(y)}\n")
    f.write(f"best_LV={best_k}\nbest_cv_accuracy={best_acc:.1f}%\n")
    f.write(f"acc_1LV={acc[0]:.1f}%\nacc_2LV={acc[1]:.1f}%\n")
    f.write(f"chardonnay_recall={sens:.1f}%\nsauvblanc_recall={spec:.1f}%\n")
    f.write(f"confusion=[[{cm[0,0]},{cm[0,1]}],[{cm[1,0]},{cm[1,1]}]]\n")
    f.write("top_VIP_metabolites=" + ", ".join(feat[j] for j in top[:10]) + "\n")
print(f"[03_plsda] {n1} Chard vs {n0} SauvBlanc | best {best_k} LV "
      f"-> CV acc {best_acc:.1f}%  ->figures+metrics_plsda.txt")
