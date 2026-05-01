import tkinter as tk
from tkinter import messagebox
from database import verify_login, register_user

# ─────────────────────────────────────────────
#  THEME
# ─────────────────────────────────────────────
BG       = "#0A0E1A"
PANEL    = "#111827"
BORDER   = "#1F2A40"
ACCENT   = "#3B82F6"
ACCENT_H = "#2563EB"
SUCCESS  = "#10B981"
DANGER   = "#EF4444"
WARN     = "#F59E0B"
TEXT     = "#F1F5F9"
MUTED    = "#64748B"
INPUT_BG = "#1E293B"

F_LABEL  = ("Segoe UI Semibold", 8)
F_BODY   = ("Segoe UI", 10)
F_BTN    = ("Segoe UI Semibold", 10)
F_SMALL  = ("Segoe UI", 9)
F_TINY   = ("Segoe UI", 8)


class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FMCC — Login")
        self.root.geometry("440x560")
        self.root.resizable(False, False)
        self.root.config(bg=BG)
        self.root.eval("tk::PlaceWindow . center")

        self.logged_in_user = None
        self.logged_in_role = None

        self._build()
        self.root.mainloop()

    # ───────────────────────────────────────────
    def _build(self):
        # Top accent stripe
        tk.Frame(self.root, bg=ACCENT, height=4).pack(fill=tk.X)

        # Logo
        logo = tk.Frame(self.root, bg=BG, pady=20)
        logo.pack(fill=tk.X)
        tk.Label(logo, text="⬡", font=("Segoe UI", 38),
                 fg=ACCENT, bg=BG).pack()
        tk.Label(logo, text="FMCC",
                 font=("Segoe UI Semibold", 24), fg=TEXT, bg=BG).pack()
        tk.Label(logo, text="Construction Management System",
                 font=F_SMALL, fg=MUTED, bg=BG).pack(pady=(2, 0))

        # Tab buttons
        tab_row = tk.Frame(self.root, bg=BORDER)
        tab_row.pack(fill=tk.X, padx=40, pady=(14, 0))

        self.login_tab = tk.Button(
            tab_row, text="Sign In", font=F_BTN,
            bg=ACCENT, fg=TEXT, relief="flat",
            cursor="hand2", bd=0, pady=9,
            command=self._show_login)
        self.login_tab.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.reg_tab = tk.Button(
            tab_row, text="Register", font=F_BTN,
            bg=PANEL, fg=MUTED, relief="flat",
            cursor="hand2", bd=0, pady=9,
            command=self._show_register)
        self.reg_tab.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Outer card
        self.card = tk.Frame(self.root, bg=PANEL,
                             highlightthickness=1,
                             highlightbackground=BORDER)
        self.card.pack(fill=tk.BOTH, padx=40, pady=10)

        # ── LOGIN FRAME ────────────────────────
        self.login_frame = tk.Frame(self.card, bg=PANEL,
                                    padx=26, pady=20)

        tk.Label(self.login_frame, text="USERNAME",
                 font=F_LABEL, fg=MUTED, bg=PANEL).pack(anchor="w")
        self.login_user = self._entry(self.login_frame)
        self.login_user.pack(fill=tk.X, ipady=8, pady=(3, 12))

        tk.Label(self.login_frame, text="PASSWORD",
                 font=F_LABEL, fg=MUTED, bg=PANEL).pack(anchor="w")
        self.login_pass = self._entry(self.login_frame, show="●")
        self.login_pass.pack(fill=tk.X, ipady=8, pady=(3, 16))
        self.login_pass.bind("<Return>", lambda e: self._do_login())

        self.login_btn = self._make_btn(
            self.login_frame, "SIGN IN", self._do_login, ACCENT)
        self.login_btn.pack(fill=tk.X)

        self.login_err = tk.StringVar()
        tk.Label(self.login_frame, textvariable=self.login_err,
                 font=F_SMALL, fg=DANGER, bg=PANEL,
                 wraplength=320).pack(pady=(8, 0))

        # ── REGISTER FRAME ─────────────────────
        self.reg_frame = tk.Frame(self.card, bg=PANEL,
                                  padx=26, pady=20)

        tk.Label(self.reg_frame, text="USERNAME",
                 font=F_LABEL, fg=MUTED, bg=PANEL).pack(anchor="w")
        self.reg_user = self._entry(self.reg_frame)
        self.reg_user.pack(fill=tk.X, ipady=8, pady=(3, 12))

        tk.Label(self.reg_frame, text="PASSWORD",
                 font=F_LABEL, fg=MUTED, bg=PANEL).pack(anchor="w")
        self.reg_pass = self._entry(self.reg_frame, show="●")
        self.reg_pass.pack(fill=tk.X, ipady=8, pady=(3, 12))

        tk.Label(self.reg_frame, text="CONFIRM PASSWORD",
                 font=F_LABEL, fg=MUTED, bg=PANEL).pack(anchor="w")
        self.reg_confirm = self._entry(self.reg_frame, show="●")
        self.reg_confirm.pack(fill=tk.X, ipady=8, pady=(3, 12))

        # Role picker
        tk.Label(self.reg_frame, text="SELECT ROLE",
                 font=F_LABEL, fg=MUTED, bg=PANEL).pack(anchor="w")

        self.role_var = tk.StringVar(value="user")
        role_row = tk.Frame(self.reg_frame, bg=PANEL)
        role_row.pack(fill=tk.X, pady=(6, 14))

        self.role_frames = {}
        for val, label, color in [
                ("user",  "👤  User",  SUCCESS),
                ("admin", "🔑  Admin", WARN)]:

            rf = tk.Frame(role_row, bg=INPUT_BG,
                          highlightthickness=2,
                          highlightbackground=BORDER,
                          cursor="hand2")
            rf.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 6))
            self.role_frames[val] = (rf, color)

            rb = tk.Radiobutton(
                rf, text=label,
                variable=self.role_var, value=val,
                bg=INPUT_BG, fg=TEXT,
                selectcolor=INPUT_BG,
                activebackground=INPUT_BG,
                activeforeground=TEXT,
                font=F_BODY, padx=10, pady=8,
                indicatoron=True, cursor="hand2",
                command=self._update_role_highlight)
            rb.pack(fill=tk.X)
            rf.bind("<Button-1>",
                    lambda e, v=val: (self.role_var.set(v),
                                      self._update_role_highlight()))

        self._update_role_highlight()

        self.reg_btn = self._make_btn(
            self.reg_frame, "CREATE ACCOUNT",
            self._do_register, SUCCESS)
        self.reg_btn.pack(fill=tk.X)

        self.reg_err = tk.StringVar()
        tk.Label(self.reg_frame, textvariable=self.reg_err,
                 font=F_SMALL, fg=DANGER, bg=PANEL,
                 wraplength=320).pack(pady=(8, 0))

        # Footer hint
        tk.Label(self.root,
                 text="Default:  admin  /  admin123",
                 font=F_TINY, fg=BORDER, bg=BG).pack(pady=(4, 8))

        # Start on login tab
        self._show_login()

    # ── HELPERS ────────────────────────────────
    def _entry(self, parent, show=None):
        e = tk.Entry(parent, bg=INPUT_BG, fg=TEXT,
                     insertbackground=ACCENT, relief="flat",
                     font=F_BODY, bd=0,
                     highlightthickness=1,
                     highlightbackground=BORDER,
                     highlightcolor=ACCENT)
        if show:
            e.config(show=show)
        e.bind("<FocusIn>",
               lambda ev: e.config(highlightbackground=ACCENT))
        e.bind("<FocusOut>",
               lambda ev: e.config(highlightbackground=BORDER))
        return e

    def _make_btn(self, parent, text, cmd, bg):
        btn = tk.Button(parent, text=text, command=cmd,
                        bg=bg, fg=TEXT, font=F_BTN,
                        relief="flat", cursor="hand2",
                        bd=0, pady=10)
        darker = {"#3B82F6": "#2563EB", "#10B981": "#059669",
                  "#EF4444": "#DC2626"}.get(bg, bg)
        btn.bind("<Enter>", lambda e: btn.config(bg=darker))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))
        return btn

    def _update_role_highlight(self):
        selected = self.role_var.get()
        for val, (frame, color) in self.role_frames.items():
            if val == selected:
                frame.config(highlightbackground=color)
            else:
                frame.config(highlightbackground=BORDER)

    # ── TAB SWITCH ─────────────────────────────
    def _show_login(self):
        self.reg_frame.pack_forget()
        self.login_frame.pack(fill=tk.BOTH)
        self.login_tab.config(bg=ACCENT, fg=TEXT)
        self.reg_tab.config(bg=PANEL, fg=MUTED)
        self.login_err.set("")
        self.root.geometry("440x560")

    def _show_register(self):
        self.login_frame.pack_forget()
        self.reg_frame.pack(fill=tk.BOTH)
        self.reg_tab.config(bg=ACCENT, fg=TEXT)
        self.login_tab.config(bg=PANEL, fg=MUTED)
        self.reg_err.set("")
        self.root.geometry("440x660")

    # ── LOGIN ──────────────────────────────────
    def _do_login(self):
        u = self.login_user.get().strip()
        p = self.login_pass.get()
        if not u or not p:
            self.login_err.set("Please enter username and password.")
            return
        ok, role = verify_login(u, p)
        if ok:
            self.logged_in_user = u
            self.logged_in_role = role
            self.root.destroy()
        else:
            self.login_err.set("❌  Invalid username or password.")
            self.login_pass.delete(0, tk.END)

    # ── REGISTER ───────────────────────────────
    def _do_register(self):
        u = self.reg_user.get().strip()
        p = self.reg_pass.get()
        c = self.reg_confirm.get()
        r = self.role_var.get()

        if not u or not p or not c:
            self.reg_err.set("Please fill in all fields.")
            return
        if len(u) < 3:
            self.reg_err.set("Username must be at least 3 characters.")
            return
        if len(p) < 6:
            self.reg_err.set("Password must be at least 6 characters.")
            return
        if p != c:
            self.reg_err.set("Passwords do not match.")
            return

        ok = register_user(u, p, r)
        if ok:
            messagebox.showinfo(
                "Account Created ✅",
                f"Account '{u}' registered as {r.upper()}!\n\nYou can now sign in.")
            self.login_user.delete(0, tk.END)
            self.login_user.insert(0, u)
            self.login_pass.delete(0, tk.END)
            self.reg_user.delete(0, tk.END)
            self.reg_pass.delete(0, tk.END)
            self.reg_confirm.delete(0, tk.END)
            self._show_login()
        else:
            self.reg_err.set(f"Username '{u}' is already taken.")
