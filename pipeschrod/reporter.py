"""
reporter.py  —  SchrodReporter: rich terminal output and data export.
"""

from __future__ import annotations
import json, csv
from typing import Dict
import numpy as np
from .result import SchrodResult

try:
    from rich.console import Console
    from rich.table   import Table
    from rich.panel   import Panel
    from rich         import box
    _RICH = True
except ImportError:
    _RICH = False


class SchrodReporter:
    """
    Terminal reporter and data exporter for PipeSchrod results.

    Accepts either a single SchrodResult or a dict {method: SchrodResult}.
    """

    def __init__(self, result):
        if isinstance(result, SchrodResult):
            self._results = {result.method: result}
            self._primary = result
        else:
            self._results = result
            for m in ["FGH","Numerov","Matrix","Salpeter"]:
                if m in result: self._primary = result[m]; break
            else: self._primary = next(iter(result.values()))
        self._con = Console() if _RICH else None

    def _p(self, *a, **k):
        if _RICH: self._con.print(*a, **k)
        else: print(*a)

    # ── Summary panel ─────────────────────────────────────────────────────────

    def print_summary(self, result: SchrodResult = None):
        res = result or self._primary
        if _RICH:
            lines = [
                f"[bold cyan]Method    :[/] {res.method}",
                f"[bold cyan]Potential :[/] {res.pot_name}",
                f"[bold cyan]m₁, m₂   :[/] {res.m1} GeV,  {res.m2} GeV",
                f"[bold cyan]μ         :[/] {res.mu:.6f} GeV",
                f"[bold cyan]L, S, J   :[/] {res.L},  {res.S},  {res.J}",
                f"[bold cyan]Grid N    :[/] {res.N}  "
                f"(h = {res.h:.5f} GeV⁻¹,  rmax = {res.rmax} GeV⁻¹)",
                f"[bold cyan]Threshold :[/] {res.threshold:.5f} GeV  (2m)",
                f"[bold cyan]Bound states:[/] {res.n_bound}",
                f"[bold cyan]CPU time  :[/] {res.cpu_time*1000:.1f} ms",
            ]
            self._con.print(Panel(
                "\n".join(lines),
                title=f"[bold white] PipeSchrod — {res.method} ",
                border_style="cyan", padding=(1, 3)))
        else:
            print(f"\n{'='*55}\n  PipeSchrod — {res.method}\n{'='*55}")
            print(f"  Potential  : {res.pot_name}")
            print(f"  m1, m2     : {res.m1}, {res.m2} GeV")
            print(f"  mu         : {res.mu:.6f} GeV")
            print(f"  L,S,J      : {res.L}, {res.S}, {res.J}")
            print(f"  N, h, rmax : {res.N},  {res.h:.5f},  {res.rmax}")
            print(f"  Bound states: {res.n_bound}  |  CPU: {res.cpu_time*1000:.1f} ms")
            print(f"{'='*55}\n")

    # ── Eigenvalue table ──────────────────────────────────────────────────────

    def print_eigenvalue_table(self, result: SchrodResult = None, n_states: int = 8):
        res = result or self._primary
        n   = min(n_states, res.n_bound)
        if _RICH:
            t = Table(
                title=f"Eigenvalue Table  —  {res.method}  ·  {res.pot_name}",
                box=box.ROUNDED, border_style="cyan",
                header_style="bold cyan", show_lines=True)
            for col, sty in [("n","bold yellow"),("State","bold white"),
                              ("E (GeV)","cyan"),("E (MeV)","white"),
                              ("B.E. (MeV)","green"),("Nodes","white"),
                              ("⟨r⟩ (GeV⁻¹)","white"),("rms (GeV⁻¹)","white")]:
                t.add_column(col, style=sty, justify="center")
            for i in range(n):
                t.add_row(
                    str(i+1), res.state_label(i),
                    f"{res.bound_energies[i]:.6f}",
                    f"{res.bound_energies[i]*1000:.3f}",
                    f"{res.binding_energies_mev[i]:.3f}",
                    str(res.node_count(i)),
                    f"{res.mean_radius(i):.4f}",
                    f"{res.rms_radius(i):.4f}",
                )
            self._con.print(t)
        else:
            hdr = (f"{'n':>3} {'State':>6} {'E(GeV)':>12} {'E(MeV)':>10} "
                   f"{'B.E.(MeV)':>11} {'Nodes':>6} {'<r>':>9} {'rms':>9}")
            print(f"\n{'─'*len(hdr)}\n  {res.method}  ·  Eigenvalue Table")
            print(f"{'─'*len(hdr)}\n{hdr}\n{'─'*len(hdr)}")
            for i in range(n):
                print(f"{i+1:>3} {res.state_label(i):>6} "
                      f"{res.bound_energies[i]:>12.6f} "
                      f"{res.bound_energies[i]*1000:>10.3f} "
                      f"{res.binding_energies_mev[i]:>11.3f} "
                      f"{res.node_count(i):>6} "
                      f"{res.mean_radius(i):>9.4f} "
                      f"{res.rms_radius(i):>9.4f}")
            print(f"{'─'*len(hdr)}\n")

    # ── Multi-method comparison ───────────────────────────────────────────────

    def print_comparison(self, n_states: int = 6):
        methods = list(self._results.keys())
        if _RICH:
            t = Table(
                title="PipeSchrod — Method Comparison  (GeV)",
                box=box.SIMPLE_HEAVY, border_style="cyan",
                header_style="bold cyan", show_lines=True)
            t.add_column("n",     style="bold yellow", justify="center")
            t.add_column("State", style="bold white",  justify="center")
            cols_c = {"Matrix":"cyan","Numerov":"green","FGH":"yellow","Salpeter":"magenta"}
            for m in methods:
                t.add_column(m, style=cols_c.get(m,"white"), justify="center")
            t.add_column("Δ (MeV)", style="red", justify="center")

            n_max = max(r.n_bound for r in self._results.values())
            for i in range(min(n_states, n_max)):
                Es    = [float(r.bound_energies[i]) if i < r.n_bound else float("nan")
                         for r in self._results.values()]
                valid = [e for e in Es if not np.isnan(e)]
                delta = f"{(max(valid)-min(valid))*1000:.3f}" if len(valid)>1 else "—"
                state = next(iter(self._results.values())).state_label(i)
                t.add_row(str(i+1), state,
                          *[f"{e:.6f}" if not np.isnan(e) else "—" for e in Es],
                          delta)
            self._con.print(t)
            # CPU table
            tc = Table(box=box.MINIMAL, border_style="dim cyan",
                       header_style="bold cyan")
            tc.add_column("Method",   style="bold white")
            tc.add_column("CPU time", style="green")
            tc.add_column("N",        style="yellow")
            for m, r in self._results.items():
                tc.add_row(m, f"{r.cpu_time*1000:.1f} ms", str(r.N))
            self._con.print(tc)
        else:
            print(f"\n{'─'*65}\n  PipeSchrod — Method Comparison (GeV)\n{'─'*65}")
            hdr = f"{'n':>3}  " + "  ".join(f"{m:>12}" for m in methods) + "  Δ(MeV)"
            print(hdr); print(f"{'─'*65}")
            n_max = max(r.n_bound for r in self._results.values())
            for i in range(min(n_states, n_max)):
                Es    = [float(r.bound_energies[i]) if i < r.n_bound else float("nan")
                         for r in self._results.values()]
                valid = [e for e in Es if not np.isnan(e)]
                delta = f"{(max(valid)-min(valid))*1000:.3f}" if len(valid)>1 else "—"
                print(f"{i+1:>3}  "
                      + "  ".join(f"{e:>12.6f}" if not np.isnan(e)
                                  else f"{'—':>12}" for e in Es)
                      + f"  {delta}")
            print(f"{'─'*65}\n")

    # ── Export ────────────────────────────────────────────────────────────────

    def save_csv(self, path: str, result: SchrodResult = None):
        res = result or self._primary
        fields = ["n","State","E_GeV","E_MeV","BE_MeV","Nodes",
                  "mean_r","rms_r","method","potential","m1","m2","L","S","J","N","rmax"]
        rows = []
        for i in range(res.n_bound):
            rows.append({"n":i+1,"State":res.state_label(i),
                         "E_GeV": round(float(res.bound_energies[i]),8),
                         "E_MeV": round(float(res.bound_energies[i])*1000,5),
                         "BE_MeV":round(float(res.binding_energies_mev[i]),5),
                         "Nodes": res.node_count(i),
                         "mean_r":round(res.mean_radius(i),6),
                         "rms_r": round(res.rms_radius(i),6),
                         "method":res.method,"potential":res.pot_name,
                         "m1":res.m1,"m2":res.m2,
                         "L":res.L,"S":res.S,"J":res.J,
                         "N":res.N,"rmax":res.rmax})
        with open(path,"w",newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader(); w.writerows(rows)
        self._p(f"[green]CSV →[/] {path}" if _RICH else f"CSV → {path}")

    def save_json(self, path: str, result: SchrodResult = None):
        res = result or self._primary
        with open(path,"w") as f:
            json.dump(res.summary_dict(), f, indent=2)
        self._p(f"[green]JSON →[/] {path}" if _RICH else f"JSON → {path}")

    def save_comparison_csv(self, path: str, n_states: int = 8):
        methods = list(self._results.keys())
        n_max   = max(r.n_bound for r in self._results.values())
        rows    = []
        for i in range(min(n_states, n_max)):
            row = {"n":i+1}
            first = next(iter(self._results.values()))
            row["State"] = first.state_label(i) if i < first.n_bound else "—"
            for m, r in self._results.items():
                row[f"{m}_GeV"] = (round(float(r.bound_energies[i]),8)
                                   if i < r.n_bound else None)
            rows.append(row)
        fields = ["n","State"] + [f"{m}_GeV" for m in methods]
        with open(path,"w",newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader(); w.writerows(rows)
        self._p(f"[green]Comparison CSV →[/] {path}" if _RICH
                else f"Comparison CSV → {path}")
