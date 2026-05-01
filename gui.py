import tkinter as tk
from tkinter import ttk, messagebox
from database import (add_project, get_projects, delete_project,
                      update_project, get_project_stats)
import pandas as pd

# ─────────────────────────────────────────────
#  THEME TOKENS
# ─────────────────────────────────────────────
BG         = "#0A0E1A"
PANEL      = "#111827"
CARD       = "#161F30"
BORDER     = "#1F2A40"
ACCENT     = "#3B82F6"
ACCENT_H   = "#2563EB"
ACCENT_DIM = "#1E3A6E"
SUCCESS    = "#10B981"
DANGER     = "#EF4444"
WARN       = "#F59E0B"
PURPLE     = "#8B5CF6"
TEXT       = "#F1F5F9"
MUTED      = "#64748B"
INPUT_BG   = "#1E293B"
ROW_ODD    = "#111827"
ROW_EVEN   = "#141E2E"
SEL_ROW    = "#1E3A6E"

FONT_H1    = ("Segoe UI Semibold", 18)
FONT_H2    = ("Segoe UI Semibold", 13)
FONT_H3    = ("Segoe UI Semibold", 10)
FONT_BODY  = ("Segoe UI", 10)
FONT_SMALL = ("Segoe UI", 9)
FONT_TINY  = ("Segoe UI", 8)
FONT_NUM   = ("Segoe UI Semibold", 20)


# ─────────────────────────────────────────────
#  WIDGET FACTORIES
# ─────────────────────────────────────────────

def make_btn(parent, text, cmd, bg=ACCENT, fg=TEXT,
             width=None, icon="", font=FONT_BODY):
    label = f" {icon}  {text}" if icon else text
    darker = {ACCENT: ACCENT_H, SUCCESS: "#059669", DANGER: "#DC2626",
              PURPLE: "#7C3AED", WARN: "#D97706",
              CARD: BORDER, "#1F2A40": "#18222F"}.get(bg, bg)
    b = tk.Button(parent, text=label, command=cmd,
                  bg=bg, fg=fg, relief="flat", font=font,
                  cursor="hand2", bd=0, padx=14, pady=8,
                  activebackground=darker, activeforeground=TEXT)
    if width:
        b.config(width=width)
    b.bind("<Enter>", lambda e: b.config(bg=darker))
    b.bind("<Leave>", lambda e: b.config(bg=bg))
    return b


def make_entry(parent, **kw):
    e = tk.Entry(parent, bg=INPUT_BG, fg=TEXT,
                 insertbackground=ACCENT, relief="flat",
                 font=FONT_BODY, bd=0,
                 highlightthickness=1,
                 highlightbackground=BORDER,
                 highlightcolor=ACCENT, **kw)
    e.bind("<FocusIn>",  lambda ev: e.config(highlightbackground=ACCENT))
    e.bind("<FocusOut>", lambda ev: e.config(highlightbackground=BORDER))
    return e


def field(parent, label_text, **entry_kw):
    tk.Label(parent, text=label_text,
             font=("Segoe UI Semibold", 8), fg=MUTED,
             bg=PANEL).pack(anchor="w")
    e = make_entry(parent, **entry_kw)
    e.pack(fill=tk.X, ipady=7, pady=(3, 10))
    return e


def stat_card(parent, title, value, color, icon):
    card = tk.Frame(parent, bg=CARD,
                    highlightthickness=1,
                    highlightbackground=BORDER)
    card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0, 8))
    inner = tk.Frame(card, bg=CARD, padx=16, pady=14)
    inner.pack(fill=tk.BOTH)
    top = tk.Frame(inner, bg=CARD)
    top.pack(fill=tk.X)
    tk.Label(top, text=icon, font=("Segoe UI", 16),
             fg=color, bg=CARD).pack(side=tk.LEFT)
    tk.Label(top, text=title, font=FONT_TINY,
             fg=MUTED, bg=CARD).pack(side=tk.LEFT, padx=6)
    tk.Label(inner, text=value, font=("Segoe UI Semibold", 22),
             fg=color, bg=CARD).pack(anchor="w", pady=(6, 0))
    return card


# ─────────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────────

class Dashboard:
    def __init__(self, username: str, role: str):
        self.username = username
        self.role     = role

        self.root = tk.Tk()
        self.root.title("FMCC — Construction Management")
        self.root.geometry("1150x660")
        self.root.minsize(960, 580)
        self.root.config(bg=BG)
        self.root.eval("tk::PlaceWindow . center")

        self._apply_styles()
        self._build()
        self.load_projects()
        self.root.mainloop()

    def _apply_styles(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("Treeview",
            background=ROW_ODD, foreground=TEXT,
            fieldbackground=ROW_ODD, rowheight=32,
            font=FONT_BODY, borderwidth=0)
        s.configure("Treeview.Heading",
            background=CARD, foreground=MUTED,
            font=("Segoe UI Semibold", 9),
            borderwidth=0, relief="flat", padding=(10, 7))
        s.map("Treeview",
            background=[("selected", SEL_ROW)],
            foreground=[("selected", TEXT)])
        s.map("Treeview.Heading",
            background=[("active", BORDER)])
        s.configure("Dark.Vertical.TScrollbar",
            troughcolor=PANEL, background=BORDER,
            arrowcolor=MUTED, borderwidth=0, relief="flat")
        s.configure("TCombobox",
            fieldbackground=INPUT_BG, background=INPUT_BG,
            foreground=TEXT, selectbackground=ACCENT,
            borderwidth=0, arrowcolor=MUTED)

    def _build(self):
        self._build_topbar()
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill=tk.X)
        self._build_body()
        self._build_statusbar()

    # ── TOP BAR ────────────────────────────────
    def _build_topbar(self):
        tb = tk.Frame(self.root, bg=PANEL, height=56)
        tb.pack(fill=tk.X)
        tb.pack_propagate(False)

        tk.Label(tb, text="⬡", font=("Segoe UI", 28),
                 fg=ACCENT, bg=PANEL).pack(side=tk.LEFT, padx=(16, 4))
        tk.Label(tb, text="FMCC",
                 font=("Segoe UI Semibold", 16), fg=TEXT,
                 bg=PANEL).pack(side=tk.LEFT)
        tk.Label(tb, text="Construction Management",
                 font=FONT_SMALL, fg=MUTED, bg=PANEL).pack(
                 side=tk.LEFT, padx=(8, 0), pady=(6, 0))

        right = tk.Frame(tb, bg=PANEL)
        right.pack(side=tk.RIGHT, padx=16)

        role_color = WARN if self.role == "admin" else SUCCESS
        tk.Label(right, text=f" {self.role.upper()} ",
                 font=("Segoe UI Semibold", 8),
                 bg=role_color, fg="#000",
                 padx=4, pady=2).pack(side=tk.LEFT, padx=(0, 6))
        tk.Label(right, text=self.username,
                 font=FONT_H3, fg=TEXT, bg=PANEL).pack(
                 side=tk.LEFT, padx=(0, 12))
        make_btn(right, "Log Out", self._logout,
                 bg=BORDER, icon="⏻").pack(side=tk.LEFT)

    # ── BODY ───────────────────────────────────
    def _build_body(self):
        body = tk.Frame(self.root, bg=BG)
        body.pack(expand=True, fill=tk.BOTH)
        self._build_sidebar(body)
        tk.Frame(body, bg=BORDER, width=1).pack(side=tk.LEFT, fill=tk.Y)
        self._build_content(body)

    # ── SIDEBAR ────────────────────────────────
    def _build_sidebar(self, parent):
        sb = tk.Frame(parent, bg=PANEL, width=252)
        sb.pack(side=tk.LEFT, fill=tk.Y)
        sb.pack_propagate(False)

        def sec(txt):
            tk.Label(sb, text=txt,
                     font=("Segoe UI Semibold", 8), fg=MUTED,
                     bg=PANEL).pack(anchor="w", padx=18, pady=(12, 2))
            tk.Frame(sb, bg=BORDER, height=1).pack(
                fill=tk.X, padx=18, pady=(0, 8))

        def sb_btn(text, cmd, bg, icon):
            make_btn(sb, text, cmd, bg=bg, icon=icon).pack(
                fill=tk.X, padx=18, pady=3)

        tk.Frame(sb, bg=PANEL, height=8).pack()
        sec("PROJECT DETAILS")

        wrap = tk.Frame(sb, bg=PANEL)
        wrap.pack(fill=tk.X, padx=18)

        self.name_entry     = field(wrap, "PROJECT NAME")
        self.location_entry = field(wrap, "LOCATION")
        self.budget_entry   = field(wrap, "BUDGET (PKR)")

        tk.Label(wrap, text="STATUS",
                 font=("Segoe UI Semibold", 8), fg=MUTED,
                 bg=PANEL).pack(anchor="w")
        self.status_var = tk.StringVar(value="Ongoing")
        self.status_combo = ttk.Combobox(
            wrap, textvariable=self.status_var,
            values=["Ongoing", "Completed", "On Hold", "Cancelled"],
            state="readonly", font=FONT_BODY)
        self.status_combo.pack(fill=tk.X, ipady=5, pady=(3, 10))

        tk.Frame(sb, bg=BORDER, height=1).pack(
            fill=tk.X, padx=18, pady=(4, 10))

        sb_btn("Add Project",    self.save_project,    ACCENT,  "＋")
        sb_btn("Update Project", self.update_selected, PURPLE,  "✎")

        if self.role == "admin":
            sb_btn("Delete Project", self.delete_selected, DANGER, "✕")

        sb_btn("Clear Fields", self.clear_fields, "#1F2A40", "↺")

        sec("TOOLS")
        sb_btn("Export to Excel", self.export_excel, SUCCESS, "⬇")
        if self.role == "admin":
            sb_btn("Refresh Data", self.load_projects, "#1F2A40", "⟳")

        tk.Frame(sb, bg=PANEL).pack(expand=True, fill=tk.Y)
        tk.Label(sb, text="FMCC v2.0  •  2025",
                 font=FONT_TINY, fg=BORDER, bg=PANEL).pack(pady=8)

    # ── CONTENT ────────────────────────────────
    def _build_content(self, parent):
        content = tk.Frame(parent, bg=BG)
        content.pack(expand=True, fill=tk.BOTH)

        # Stat cards
        self.stats_row = tk.Frame(content, bg=BG, pady=14)
        self.stats_row.pack(fill=tk.X, padx=16)

        # Toolbar
        toolbar = tk.Frame(content, bg=BG, pady=2)
        toolbar.pack(fill=tk.X, padx=16)

        sf = tk.Frame(toolbar, bg=INPUT_BG,
                      highlightthickness=1,
                      highlightbackground=BORDER)
        sf.pack(side=tk.LEFT)

        tk.Label(sf, text="⌕", font=("Segoe UI", 13),
                 fg=MUTED, bg=INPUT_BG).pack(side=tk.LEFT, padx=(8, 2))
        self.search_entry = tk.Entry(
            sf, bg=INPUT_BG, fg=MUTED,
            insertbackground=ACCENT, relief="flat",
            font=FONT_BODY, bd=0, width=28)
        self.search_entry.pack(side=tk.LEFT, ipady=7, padx=(0, 8))
        self.search_entry.insert(0, "Search by name or location…")
        self.search_entry.bind("<FocusIn>",  self._search_focus_in)
        self.search_entry.bind("<FocusOut>", self._search_focus_out)
        self.search_entry.bind("<KeyRelease>", lambda e: self.search_project())

        tk.Label(toolbar, text="Filter:", font=FONT_SMALL,
                 fg=MUTED, bg=BG).pack(side=tk.LEFT, padx=(12, 4))
        self.filter_var = tk.StringVar(value="All")
        flt = ttk.Combobox(toolbar, textvariable=self.filter_var,
                           values=["All", "Ongoing", "Completed",
                                   "On Hold", "Cancelled"],
                           state="readonly", font=FONT_SMALL, width=10)
        flt.pack(side=tk.LEFT)
        flt.bind("<<ComboboxSelected>>", lambda e: self.search_project())

        self.count_var = tk.StringVar(value="0 projects")
        tk.Label(toolbar, textvariable=self.count_var,
                 font=FONT_SMALL, fg=MUTED, bg=BG).pack(
                 side=tk.RIGHT)

        # Table
        tbl_wrap = tk.Frame(content, bg=BG, padx=16, pady=8)
        tbl_wrap.pack(expand=True, fill=tk.BOTH)

        border_f = tk.Frame(tbl_wrap, bg=BORDER)
        border_f.pack(expand=True, fill=tk.BOTH)

        tf = tk.Frame(border_f, bg=ROW_ODD)
        tf.pack(expand=True, fill=tk.BOTH, padx=1, pady=1)

        cols = ("ID", "Name", "Location", "Budget (PKR)", "Status")
        self.tree = ttk.Treeview(tf, columns=cols,
                                 show="headings", selectmode="browse")

        widths = {"ID": 48, "Name": 230, "Location": 180,
                  "Budget (PKR)": 140, "Status": 110}
        for c in cols:
            self.tree.heading(c, text=c, anchor="w")
            self.tree.column(c, width=widths[c], anchor="w",
                             minwidth=widths[c])

        self.tree.tag_configure("odd",       background=ROW_ODD)
        self.tree.tag_configure("even",      background=ROW_EVEN)
        self.tree.tag_configure("ongoing",   foreground=ACCENT)
        self.tree.tag_configure("completed", foreground=SUCCESS)
        self.tree.tag_configure("on hold",   foreground=WARN)
        self.tree.tag_configure("cancelled", foreground=DANGER)

        vsb = ttk.Scrollbar(tf, orient="vertical",
                            command=self.tree.yview,
                            style="Dark.Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self.select_project)

    def _build_statusbar(self):
        tk.Frame(self.root, bg=BORDER, height=1).pack(
            fill=tk.X, side=tk.BOTTOM)
        sb = tk.Frame(self.root, bg=PANEL, height=28)
        sb.pack(fill=tk.X, side=tk.BOTTOM)
        sb.pack_propagate(False)
        self.status_msg = tk.StringVar(value="Ready")
        tk.Label(sb, textvariable=self.status_msg,
                 font=FONT_SMALL, fg=MUTED, bg=PANEL).pack(
                 side=tk.LEFT, padx=16)
        tk.Label(sb,
                 text=f"Logged in as  {self.username}  ({self.role})",
                 font=FONT_SMALL, fg=BORDER, bg=PANEL).pack(
                 side=tk.RIGHT, padx=16)

    # ── SEARCH PLACEHOLDER ─────────────────────
    def _search_focus_in(self, e):
        if self.search_entry.get() == "Search by name or location…":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg=TEXT)

    def _search_focus_out(self, e):
        if not self.search_entry.get():
            self.search_entry.insert(0, "Search by name or location…")
            self.search_entry.config(fg=MUTED)

    # ── STATUS MSG ─────────────────────────────
    def set_status(self, msg):
        self.status_msg.set(msg)
        self.root.after(4000, lambda: self.status_msg.set("Ready"))

    # ── STAT CARDS ─────────────────────────────
    def _refresh_stats(self):
        for w in self.stats_row.winfo_children():
            w.destroy()
        s = get_project_stats()
        stat_card(self.stats_row, "TOTAL PROJECTS",
                  str(s["total"]),     ACCENT,  "📁")
        stat_card(self.stats_row, "ONGOING",
                  str(s["ongoing"]),   WARN,    "🔨")
        stat_card(self.stats_row, "COMPLETED",
                  str(s["completed"]), SUCCESS, "✅")
        stat_card(self.stats_row, "TOTAL BUDGET",
                  f"₨ {s['total_budget']:,.0f}", PURPLE, "💰")

    # ── LOAD ───────────────────────────────────
    def load_projects(self, data=None):
        for row in self.tree.get_children():
            self.tree.delete(row)
        rows = data if data is not None else get_projects()
        for i, p in enumerate(rows):
            tag  = "even" if i % 2 == 0 else "odd"
            stag = str(p[4]).lower() if len(p) > 4 else ""
            vals = list(p)
            try:
                vals[3] = f"{float(vals[3]):,.2f}"
            except Exception:
                pass
            self.tree.insert("", tk.END, values=vals,
                             tags=(tag, stag))
        self.count_var.set(
            f"{len(rows)} project{'s' if len(rows) != 1 else ''}")
        self._refresh_stats()

    # ── CLEAR ──────────────────────────────────
    def clear_fields(self):
        self.name_entry.delete(0, tk.END)
        self.location_entry.delete(0, tk.END)
        self.budget_entry.delete(0, tk.END)
        self.status_var.set("Ongoing")
        self.set_status("Fields cleared.")

    # ── SEARCH ─────────────────────────────────
    def search_project(self):
        kw  = self.search_entry.get().lower()
        ph  = "search by name or location…"
        if kw == ph:
            kw = ""
        flt = self.filter_var.get()
        filtered = [
            p for p in get_projects()
            if (not kw or kw in str(p[1]).lower()
                       or kw in str(p[2]).lower())
            and (flt == "All" or str(p[4]).lower() == flt.lower())
        ]
        self.load_projects(filtered)
        self.set_status(f"{len(filtered)} result(s) found.")

    # ── SAVE ───────────────────────────────────
    def save_project(self):
        n = self.name_entry.get().strip()
        l = self.location_entry.get().strip()
        b = self.budget_entry.get().strip()
        if not n or not l or not b:
            messagebox.showwarning("Missing Fields",
                "Please fill in all fields.")
            return
        try:
            float(b)
        except ValueError:
            messagebox.showerror("Invalid Budget",
                "Budget must be a number.")
            return
        add_project(n, l, float(b), self.status_var.get().lower())
        self.load_projects()
        self.clear_fields()
        self.set_status(f"✔  Project '{n}' added.")

    # ── DELETE ─────────────────────────────────
    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("No Selection",
                "Select a project first.")
            return
        vals = self.tree.item(sel[0])["values"]
        if not messagebox.askyesno("Confirm Delete",
                f"Delete '{vals[1]}'?\nThis cannot be undone."):
            return
        delete_project(vals[0])
        self.load_projects()
        self.clear_fields()
        self.set_status(f"🗑  '{vals[1]}' deleted.")

    # ── UPDATE ─────────────────────────────────
    def update_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("No Selection",
                "Select a project first.")
            return
        n = self.name_entry.get().strip()
        l = self.location_entry.get().strip()
        b = self.budget_entry.get().strip()
        if not n or not l or not b:
            messagebox.showwarning("Missing Fields",
                "Please fill in all fields.")
            return
        try:
            float(b)
        except ValueError:
            messagebox.showerror("Invalid Budget",
                "Budget must be a number.")
            return
        vals = self.tree.item(sel[0])["values"]
        update_project(vals[0], n, l, float(b),
                       self.status_var.get().lower())
        self.load_projects()
        self.set_status(f"✔  '{n}' updated.")

    # ── SELECT ─────────────────────────────────
    def select_project(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0])["values"]
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, vals[1])
        self.location_entry.delete(0, tk.END)
        self.location_entry.insert(0, vals[2])
        raw_b = str(vals[3]).replace(",", "")
        self.budget_entry.delete(0, tk.END)
        self.budget_entry.insert(0, raw_b)
        if len(vals) > 4:
            self.status_var.set(str(vals[4]).capitalize())
        self.set_status(f"Selected: {vals[1]}")

    # ── EXPORT ─────────────────────────────────
    def export_excel(self):
        data = get_projects()
        df = pd.DataFrame(data,
            columns=["ID", "Name", "Location", "Budget", "Status"])
        df.to_excel("projects.xlsx", index=False)
        self.set_status("✔  Exported to projects.xlsx")
        messagebox.showinfo("Export Complete",
            "Saved as projects.xlsx")

    # ── LOGOUT ─────────────────────────────────
    def _logout(self):
        if messagebox.askyesno("Log Out",
                "Are you sure you want to log out?"):
            self.root.destroy()
