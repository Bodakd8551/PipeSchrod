"""
plotter.py  —  SchrodPlotter: publication-quality figures for PipeSchrod.
"""

from __future__ import annotations
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from typing import Dict, Optional, Union

from .result import SchrodResult

matplotlib.rcParams.update({
    "font.family"      : "DejaVu Sans",
    "axes.spines.top"  : False,
    "axes.spines.right": False,
    "figure.dpi"       : 120,
})

# ── Palette ───────────────────────────────────────────────────────────────────
PAL  = ["#58a6ff","#ff7b72","#3fb950","#ffa657","#d2a8ff","#f78166"]
BG   = "#0d1117"; GRID = "#21262d"; AX = "#8b949e"; TEXT = "#e6edf3"
MC   = {"Matrix":"#58a6ff","Numerov":"#3fb950","FGH":"#ffa657","Salpeter":"#ff7b72"}


def _dark(ax, title="", xl="", yl=""):
    ax.set_facecolor(BG)
    ax.tick_params(colors=AX, labelsize=9)
    for sp in ax.spines.values(): sp.set_color(GRID)
    ax.grid(True, color=GRID, lw=0.5, alpha=0.7)
    if title: ax.set_title(title, color=TEXT, fontsize=11, fontweight="bold", pad=6)
    if xl:    ax.set_xlabel(xl, color=AX, fontsize=10)
    if yl:    ax.set_ylabel(yl, color=AX, fontsize=10)

def _fig(nr=1, nc=1, w=9, h=5):
    fig, axes = plt.subplots(nr, nc, figsize=(w*nc, h*nr))
    fig.patch.set_facecolor(BG)
    return fig, axes

def _save(fig, save_dir, name):
    if save_dir:
        import os; os.makedirs(save_dir, exist_ok=True)
        p = os.path.join(save_dir, name)
        fig.savefig(p, bbox_inches="tight", facecolor=BG, dpi=150)
        print(f"  [PipeSchrod] Saved → {p}")


class SchrodPlotter:
    """
    Visualisation toolkit for PipeSchrod results.

    Accepts either a single SchrodResult or a dict {method: SchrodResult}.
    """

    def __init__(self,
                 result: Union[SchrodResult, Dict[str, SchrodResult]],
                 save_dir: Optional[str] = None):
        if isinstance(result, SchrodResult):
            self._single  = result
            self._results = {result.method: result}
        elif isinstance(result, dict) and result:
            self._results = result
            for m in ["FGH","Numerov","Matrix","Salpeter"]:
                if m in result: self._single = result[m]; break
            else: self._single = next(iter(result.values()))
        else:
            self._single = None; self._results = {}
        self.save_dir = save_dir

    # ── 1. Wave functions ─────────────────────────────────────────────────────

    def wave_functions(self, n_states=4, r_cut=None, show_prob=False):
        res    = self._single
        if res is None or res.n_bound == 0: return None, None
        n      = min(n_states, res.n_bound)
        r_cut  = r_cut or 0.7 * res.rmax
        mask   = res.r <= r_cut
        nc, nr = min(n, 2), (n+1)//2
        fig, axes = _fig(nr, nc, w=5, h=4)
        axes  = np.array(axes).flatten()
        ylab  = "|u(r)|²" if show_prob else "u(r)"
        for i in range(n):
            ax  = axes[i]; col = PAL[i % len(PAL)]
            y   = (res.bound_psi[i]**2 if show_prob else res.bound_psi[i])
            if show_prob: ax.fill_between(res.r[mask], y[mask], alpha=0.18, color=col)
            ax.plot(res.r[mask], y[mask], color=col, lw=2.2)
            ax.axhline(0, color=AX, lw=0.9, ls="--", alpha=0.6)
            _dark(ax, f"{res.state_label(i)}  E={res.bound_energies[i]:.4f} GeV",
                  "r  (GeV⁻¹)", ylab)
            ax.set_xlim(0, r_cut)
        for j in range(n, len(axes)): axes[j].set_visible(False)
        fig.suptitle(f"Wave Functions [{res.method}]  {res.pot_name}  L={res.L}",
                     color=TEXT, fontsize=13, fontweight="bold", y=1.01)
        plt.tight_layout()
        _save(fig, self.save_dir, "wave_functions.png")
        return fig, axes

    def probability_densities(self, n_states=4, r_cut=None):
        return self.wave_functions(n_states=n_states, r_cut=r_cut, show_prob=True)

    # ── 2. Potential + energy levels ──────────────────────────────────────────

    def potential_and_levels(self, n_levels=4, r_cut=None):
        res   = self._single
        if res is None: return None, None
        r_cut = r_cut or min(res.rmax, 12.0)
        mask  = res.r <= r_cut
        fig, ax = _fig(1, 1, w=10, h=5); ax = fig.axes[0]
        col_V = PAL[0]
        ax.plot(res.r[mask], res.potential[mask], color=col_V, lw=2.8,
                label=f"V(r)  [{res.pot_name}]")
        n = min(n_levels, res.n_bound)
        for i in range(n):
            E = float(res.bound_energies[i])
            ax.axhline(E, color=PAL[i % len(PAL)], lw=1.5, ls="--", alpha=0.85,
                       label=f"{res.state_label(i)}  E={E:.4f} GeV")
        V_clip = res.potential[mask][np.isfinite(res.potential[mask])]
        ax.set_ylim(max(float(np.nanmin(V_clip))*1.1, -5.5),
                    float(res.bound_energies[n-1])*1.2 if n else 2.0)
        ax.set_xlim(0, r_cut)
        ax.axhline(0, color=AX, lw=0.7, ls=":", alpha=0.4)
        ax.axhline(res.threshold, color="#d2a8ff", lw=1.2, ls=":",
                   alpha=0.6, label=f"Threshold {res.threshold:.4f} GeV")
        _dark(ax, f"Potential & Bound-State Levels  [{res.method}]",
              "r  (GeV⁻¹)", "V(r) / Eₙ  (GeV)")
        ax.legend(fontsize=9, facecolor="#111b2b", edgecolor=GRID, labelcolor=TEXT, ncol=2)
        plt.tight_layout()
        _save(fig, self.save_dir, "potential_levels.png")
        return fig, ax

    # ── 3. Spectrum ───────────────────────────────────────────────────────────

    def spectrum(self, n_states=6):
        res   = self._single
        if res is None or res.n_bound == 0: return None, None
        n     = min(n_states, res.n_bound)
        fig, ax = _fig(1, 1, w=9, h=5); ax = fig.axes[0]
        ns    = np.arange(1, n+1)
        Es    = res.bound_energies[:n]
        bars  = ax.bar(ns, Es, color=[PAL[i%len(PAL)] for i in range(n)],
                       alpha=0.82, edgecolor="#ffffff22", width=0.55)
        for bar, E, ni in zip(bars, Es, ns):
            ax.text(ni, float(E)+0.04, f"{float(E):.4f}",
                    ha="center", va="bottom", color=TEXT, fontsize=9, fontweight="bold")
        ax.axhline(res.threshold, color="#d2a8ff", lw=1.8, ls="--",
                   label=f"Threshold {res.threshold:.4f} GeV")
        ax.set_xticks(ns)
        _dark(ax, f"Mass Spectrum  [{res.method}  ·  {res.pot_name}]",
              "Principal quantum number  n", "Meson mass  (GeV)")
        ax.legend(fontsize=10, facecolor="#111b2b", edgecolor=GRID, labelcolor=TEXT)
        plt.tight_layout()
        _save(fig, self.save_dir, "spectrum.png")
        return fig, ax

    # ── 4. Compare wave functions across methods ──────────────────────────────

    def compare_wave_functions(self, n=0, r_cut=None):
        fig, ax = _fig(1, 1, w=10, h=5); ax = fig.axes[0]
        r_cut   = r_cut or 12.0
        for method, res in self._results.items():
            if res.n_bound <= n: continue
            mask = res.r <= r_cut
            col  = MC.get(method, PAL[0])
            E    = float(res.bound_energies[n])
            ax.plot(res.r[mask], res.bound_psi[n][mask], color=col, lw=2.2,
                    ls="--" if method=="Salpeter" else "-",
                    label=f"{method}  E={E:.5f} GeV")
        ax.axhline(0, color=AX, lw=0.9, ls="--", alpha=0.6)
        ax.set_xlim(0, r_cut)
        state = next(iter(self._results.values())).state_label(n)
        _dark(ax, f"Wave Function Comparison  —  {state}",
              "r  (GeV⁻¹)", "u(r)  (normalised)")
        ax.legend(fontsize=10, facecolor="#111b2b", edgecolor=GRID, labelcolor=TEXT)
        plt.tight_layout()
        _save(fig, self.save_dir, f"compare_wf_n{n+1}.png")
        return fig, ax

    # ── 5. Compare energies across methods ───────────────────────────────────

    def compare_energies(self, n_states=5):
        methods = list(self._results.keys())
        n_m     = len(methods)
        fig, ax = _fig(1, 1, w=11, h=5); ax = fig.axes[0]
        ns      = np.arange(1, n_states+1)
        w       = 0.8 / n_m
        for k, method in enumerate(methods):
            res = self._results[method]
            Es  = [float(res.bound_energies[i]) if i < res.n_bound else np.nan
                   for i in range(n_states)]
            ax.bar(ns + (k - n_m/2 + 0.5)*w, Es, width=w,
                   color=MC.get(method, PAL[k%len(PAL)]), alpha=0.82,
                   edgecolor="#ffffff22", label=method)
        first = next(iter(self._results.values()))
        ax.axhline(first.threshold, color="#d2a8ff", lw=1.5, ls="--",
                   alpha=0.7, label=f"Threshold {first.threshold:.4f} GeV")
        ax.set_xticks(ns)
        _dark(ax, "Energy Spectrum Comparison  —  All Methods",
              "Principal quantum number  n", "Meson mass  (GeV)")
        ax.legend(fontsize=10, facecolor="#111b2b", edgecolor=GRID, labelcolor=TEXT)
        plt.tight_layout()
        _save(fig, self.save_dir, "compare_energies.png")
        return fig, ax

    # ── 6. Convergence ────────────────────────────────────────────────────────

    def convergence(self, solver_classes=None, potential_fn=None,
                    N_values=None, n_state=0, m1=1.4495, m2=1.4495, L=0):
        from .solvers import MatrixSolver, NumerovSolver, FGHSolver
        from .potentials import cornell as _c
        solver_classes = solver_classes or [MatrixSolver, NumerovSolver, FGHSolver]
        potential_fn   = potential_fn or _c(m1=m1, m2=m2)
        N_values       = N_values or [30,50,75,100,125,150,175,200,250,300]
        fig, ax = _fig(1, 1, w=10, h=5); ax = fig.axes[0]
        for cls in solver_classes:
            name = cls.__name__.replace("Solver","")
            Es   = []
            for N in N_values:
                try:
                    r = cls(N=N, rmax=20.0, m1=m1, m2=m2, L=L).solve(potential_fn)
                    Es.append(float(r.bound_energies[n_state]) if r.n_bound > n_state else np.nan)
                except Exception: Es.append(np.nan)
            ax.plot(N_values, Es, "o-", color=MC.get(name, PAL[0]), lw=2, ms=5, label=name)
        _dark(ax, f"Convergence: E₁ vs Grid Size N",
              "N (grid points)", "Energy  (GeV)")
        ax.legend(fontsize=10, facecolor="#111b2b", edgecolor=GRID, labelcolor=TEXT)
        plt.tight_layout()
        _save(fig, self.save_dir, "convergence.png")
        return fig, ax

    # ── 7. Parameter sensitivity ──────────────────────────────────────────────

    def parameter_sensitivity(self, param="alpha", values=None,
                               m1=1.4495, m2=1.4495,
                               base_alpha=0.5317, base_b=0.1497):
        from .potentials import cornell as _c
        from .solvers import FGHSolver
        values = values or np.linspace(0.3, 0.8, 6) if param=="alpha" \
                           else np.linspace(0.05, 0.35, 6)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        fig.patch.set_facecolor(BG)
        r_ref = np.linspace(0.1, 12, 300)
        E1s   = []
        for k, val in enumerate(values):
            kw = dict(alpha=base_alpha, b=base_b, m1=m1, m2=m2)
            kw[param] = float(val)
            Vf  = _c(**kw)
            col = PAL[k % len(PAL)]
            Vp  = Vf(r_ref)
            msk = np.isfinite(Vp) & (Vp > -6) & (Vp < 4)
            ax1.plot(r_ref[msk], Vp[msk], color=col, lw=2,
                     label=f"{param}={float(val):.3f}")
            res = FGHSolver(N=150, rmax=20.0, m1=m1, m2=m2).solve(Vf)
            E1s.append(float(res.bound_energies[0]) if res.n_bound > 0 else np.nan)
        _dark(ax1, f"V(r) sensitivity to {param}",
              "r  (GeV⁻¹)", "V(r)  (GeV)")
        ax1.set_ylim(-5, 3); ax1.set_xlim(0, 12)
        ax1.axhline(0, color=AX, lw=0.7, ls=":", alpha=0.5)
        ax1.legend(fontsize=9, facecolor="#111b2b", edgecolor=GRID, labelcolor=TEXT)
        _dark(ax2, f"E₁ vs {param}", param, "E₁  (GeV)")
        ax2.plot(values, E1s, "o-", color=PAL[0], lw=2, ms=6)
        for v, E in zip(values, E1s):
            if np.isfinite(E):
                ax2.annotate(f"{E:.4f}", (v, E), textcoords="offset points",
                             xytext=(0, 8), ha="center", color=TEXT, fontsize=8)
        plt.tight_layout()
        _save(fig, self.save_dir, f"sensitivity_{param}.png")
        return fig, (ax1, ax2)

    # ── 8. All-in-one dashboard ───────────────────────────────────────────────

    def dashboard(self, n_states=4):
        res = self._single
        if res is None or res.n_bound == 0: return None, None
        n   = min(n_states, res.n_bound)

        fig = plt.figure(figsize=(16, 11))
        fig.patch.set_facecolor(BG)
        gs  = gridspec.GridSpec(2, 2, hspace=0.38, wspace=0.30,
                                left=0.07, right=0.97, top=0.92, bottom=0.07)

        r_cut = min(res.rmax*0.65, 14.0)
        mask  = res.r <= r_cut

        # top-left: wave functions
        ax1 = fig.add_subplot(gs[0, 0]); ax1.set_facecolor(BG)
        for i in range(n):
            col = PAL[i%len(PAL)]
            ax1.fill_between(res.r[mask], res.bound_psi[i][mask], alpha=0.1, color=col)
            ax1.plot(res.r[mask], res.bound_psi[i][mask], color=col, lw=2.1,
                     label=f"{res.state_label(i)}  {res.bound_energies[i]:.4f} GeV")
        ax1.axhline(0, color=AX, lw=0.9, ls="--", alpha=0.5)
        ax1.set_xlim(0, r_cut)
        _dark(ax1,"Radial Wave Functions  u(r)","r  (GeV⁻¹)","u(r)")
        ax1.legend(fontsize=8, facecolor="#111b2b", edgecolor=GRID, labelcolor=TEXT)

        # top-right: potential + levels
        ax2 = fig.add_subplot(gs[0, 1]); ax2.set_facecolor(BG)
        r_p = res.r[res.r <= min(res.rmax, 12)]
        V_p = res.potential[:len(r_p)]
        ax2.plot(r_p, V_p, color=PAL[0], lw=2.5, label="V(r)")
        for i in range(n):
            E   = float(res.bound_energies[i])
            ax2.axhline(E, color=PAL[i%len(PAL)], lw=1.4, ls="--", alpha=0.8,
                        label=f"{res.state_label(i)} = {E:.4f}")
        V_min = max(float(np.nanmin(V_p[np.isfinite(V_p)]))*1.1, -5.5)
        ax2.set_ylim(V_min, float(res.bound_energies[n-1])*1.2)
        ax2.set_xlim(0, min(res.rmax, 12))
        ax2.axhline(0, color=AX, lw=0.7, ls=":", alpha=0.4)
        _dark(ax2,"Potential  &  Energy Levels","r  (GeV⁻¹)","V(r) / Eₙ  (GeV)")
        ax2.legend(fontsize=8, facecolor="#111b2b", edgecolor=GRID, labelcolor=TEXT, ncol=2)

        # bot-left: probability densities
        ax3 = fig.add_subplot(gs[1, 0]); ax3.set_facecolor(BG)
        for i in range(n):
            col = PAL[i%len(PAL)]
            u2  = res.bound_psi[i][mask]**2
            ax3.fill_between(res.r[mask], u2, alpha=0.15, color=col)
            ax3.plot(res.r[mask], u2, color=col, lw=2, label=res.state_label(i))
        ax3.set_xlim(0, r_cut)
        _dark(ax3,"Probability Densities  |u(r)|²","r  (GeV⁻¹)","|u(r)|²")
        ax3.legend(fontsize=8, facecolor="#111b2b", edgecolor=GRID, labelcolor=TEXT)

        # bot-right: spectrum
        ax4 = fig.add_subplot(gs[1, 1]); ax4.set_facecolor(BG)
        n_sp = min(6, res.n_bound)
        ns   = np.arange(1, n_sp+1)
        Es   = res.bound_energies[:n_sp]
        bars = ax4.bar(ns, Es, color=[PAL[i%len(PAL)] for i in range(n_sp)],
                       alpha=0.82, edgecolor="#ffffff22", width=0.55)
        for bar, E, ni in zip(bars, Es, ns):
            ax4.text(ni, float(E)+0.035, f"{float(E):.4f}",
                     ha="center", va="bottom", color=TEXT, fontsize=8, fontweight="bold")
        ax4.axhline(res.threshold, color="#d2a8ff", lw=1.8, ls="--",
                    label=f"Threshold {res.threshold:.4f} GeV")
        ax4.set_xticks(ns)
        _dark(ax4,"Mass Spectrum","n","Meson mass  (GeV)")
        ax4.legend(fontsize=9, facecolor="#111b2b", edgecolor=GRID, labelcolor=TEXT)

        fig.suptitle(
            f"PipeSchrod  ·  {res.method}  ·  {res.pot_name}  "
            f"·  L={res.L} S={res.S} J={res.J}  ·  m={res.m1} GeV",
            color=TEXT, fontsize=13, fontweight="bold")

        _save(fig, self.save_dir, "dashboard.png")
        return fig, (ax1, ax2, ax3, ax4)
