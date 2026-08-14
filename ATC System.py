import tkinter as tk
from tkinter import font as tkfont
import math, time, random, colorsys
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

_X = [
    [500,  1.2, 0, 0, 0], [450,  0.8, 0, 0, 0], [600,  2.1, 0, 0, 0],
    [480,  1.0, 0, 0, 0], [530,  1.5, 0, 0, 0], [570,  1.8, 0, 0, 0],
    [1350, 3200, 1, 1, 0],[1400, 3500, 1, 1, 0],[1250, 4100, 1, 1, 0],
    [1300, 2800, 1, 0, 1],[1450, 3900, 1, 1, 1],[1200, 4500, 1, 0, 1],
]
_y = [0,0,0,0,0,0,1,1,1,1,1,1]


clf_lstm = MLPClassifier(hidden_layer_sizes=(128,128,128), max_iter=1000,
                         random_state=42, learning_rate_init=0.001)
clf_lstm.fit(_X, _y)


clf_rf = RandomForestClassifier(n_estimators=100, random_state=42)
clf_rf.fit(_X, _y)


clf_svm = SVC(kernel='rbf', probability=True, random_state=42)
clf_svm.fit(_X, _y)


BG       = "#050a12"
BG2      = "#06101a"
BG3      = "#07131f"
C_GREEN  = "#00ffc8"
C_DIM    = "#1a5a47"
C_MID    = "#2a6a5a"
C_MUTED  = "#7db8a8"
C_RED    = "#ff3366"
C_AMBER  = "#f59e0b"
C_BLUE   = "#38bdf8"
C_PURPLE = "#a855f7"
C_ORANGE = "#fb923c"
C_DARK   = "#0d2233"
C_RING   = "#0d3a2e"

FM  = ("Courier New", 9)
FMS = ("Courier New", 8)
FMX = ("Courier New", 10, "bold")
FMT = ("Courier New", 11, "bold")

ATK_GHOST   = "ghost"    # 3.1 Ghost Aircraft Injection
ATK_TCAS    = "tcas"     # 2.2 TCAS Distance Spoofing (> 3.5 km)
ATK_FLOOD   = "flood"    # 3.4 DoS / Frequency Flooding
ATK_REPLAY  = "replay"   # 3.2 Replay Attack (duplicate targets)
ATK_GPS     = "gps"      # 3.3 GPS Spoofing + ADS-B injection

ATK_COLORS = {
    ATK_GHOST:  C_RED,
    ATK_TCAS:   C_AMBER,
    ATK_FLOOD:  "#ef4444",
    ATK_REPLAY: C_PURPLE,
    ATK_GPS:    C_ORANGE,
}

def make_ac(label, x, y, vx, vy, speed, tdoa, psr=0,
            tcas=False, is_ghost=False, atk=None,
            decay=False, psr_mismatch=0.0, gps_offset=(0,0)):
    return dict(
        label=label, x=x, y=y, vx=vx, vy=vy,
        speed=speed, tdoa=tdoa, psr=psr,
        tcas=tcas, is_ghost=is_ghost,
        atk=atk, decay=decay,
        psr_mismatch=psr_mismatch,   # PSR vs ADS-B discrepancy (km)
        gps_offset=gps_offset,       # GPS spoofing offset
        trail=[], age=0,
        tdoa_loc_error=random.uniform(2.8, 3.6) if is_ghost else 0.0,
    )

class SkyShield:
    def __init__(self, root):
        self.root = root
        self.root.title(
            "SkyShield-ATC v3.0 — سامانه پدافند سایبری هوانوردی "
            "| Rashidi, A. (2027) — IAU Tehran Central Branch"
        )
        self.root.configure(bg=BG)
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))
        self.root.bind("<F11>",    lambda e: self.root.attributes("-fullscreen", True))

        self.sweep      = 0.0
        self.aircrafts  = {}
        self.bc_ledger  = []      
        self.last_bc_t  = time.time()
        self.ids_method = tk.StringVar(value="lstm")   

        self.ids_var = tk.BooleanVar(value=True)   # L1: LSTM/TDoA
        self.pqc_var = tk.BooleanVar(value=False)  # L2: ML-DSA
        self.bc_var  = tk.BooleanVar(value=False)  # L3: Blockchain

        self._build_ui()
        self._init_traffic()
        self._animate()

   
    def _build_ui(self):
       
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill=tk.BOTH, expand=True)

      
        left = tk.Frame(outer, bg=BG2, width=260)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(6,0), pady=6)
        left.pack_propagate(False)
        self._build_left(left)

        
        right = tk.Frame(outer, bg=BG)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=6, pady=6)
        self._build_right(right)

    def _sep(self, p, color=C_RING):
        tk.Frame(p, bg=color, height=1).pack(fill=tk.X, padx=6, pady=4)

    def _section(self, p, text, color=C_MID):
        f = tk.Frame(p, bg=BG2)
        f.pack(fill=tk.X, padx=8, pady=(5,2))
        tk.Frame(f, bg=color, width=2).pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(f, text="  "+text, bg=BG2, fg=color,
                 font=("Courier New", 7)).pack(side=tk.LEFT)

    def _btn(self, p, text, color, cmd, bold=False):
        s = "bold" if bold else ""
        b = tk.Button(p, text=text, bg=BG2, fg=color,
                      activebackground=color, activeforeground=BG,
                      font=("Courier New", 8, s) if s else FMS,
                      bd=1, relief=tk.SOLID,
                      highlightbackground=color, highlightthickness=1,
                      cursor="hand2", command=cmd)
        b.pack(fill=tk.X, padx=8, pady=2)
        return b

    def _build_left(self, p):
        
        tk.Label(p, text="SkyShield-ATC", bg=BG2, fg=C_GREEN,
                 font=("Courier New", 13, "bold")).pack(pady=(12,1))
        tk.Label(p, text="v3.0 — پدافند سایبری هوانوردی", bg=BG2,
                 fg=C_DIM, font=FMS).pack()
        tk.Label(p, text="Rashidi (2027) · IAU Tehran", bg=BG2,
                 fg="#0d3a2e", font=("Courier New", 7)).pack(pady=(0,4))
        self._sep(p)

        
        self._section(p, "تزریق حملات (بخش ۳ مقاله)", C_RED)
        self._btn(p, "⬡  شبح ADS-B   (§3.1 Ghost Injection)", C_RED,   self.atk_ghost, True)
        self._btn(p, "⚠  TCAS Spoofing (§2.2 · Δd > 3.5km)", C_AMBER, self.atk_tcas)
        self._btn(p, "⟳  Replay Attack  (§3.2 Duplicate)",   C_PURPLE, self.atk_replay)
        self._btn(p, "⊕  GPS Spoofing   (§3.3 Combined)",    C_ORANGE, self.atk_gps)
        self._btn(p, "⚡  DoS Flooding   (§3.4 · 1090 MHz)", "#ef4444", self.atk_flood)
        self._btn(p, "✓  دفع و پاکسازی کامل رادار",         C_GREEN,  self.clear_all)
        self._sep(p)

        
        self._section(p, "روش IDS  —  Table 5 مقاله", C_BLUE)
        ids_methods = [
            ("lstm",        "LSTM (98.7٪ · 15ms)",   C_GREEN),
            ("rf",          "Random Forest (93.4٪)",  C_BLUE),
            ("svm",         "SVM (89.2٪ · 5ms)",      C_MUTED),
            ("multisensor", "Multi-sensor (99.1٪)",   C_AMBER),
        ]
        for val, label, col in ids_methods:
            tk.Radiobutton(
                p, text=label, variable=self.ids_method, value=val,
                bg=BG2, fg=col, selectcolor=BG2, activebackground=BG2,
                font=FMS, cursor="hand2", command=self._update_metrics
            ).pack(anchor=tk.W, padx=14, pady=1)
        self._sep(p)

        
        self._section(p, "فریم‌ورک سه‌لایه — بخش ۶", C_GREEN)
        for var, text, col in [
            (self.ids_var, "L1 — LSTM + TDoA (§4.1, §4.3)", C_GREEN),
            (self.pqc_var, "L2 — ML-DSA پسا‌کوانتوم (§5.1)",  C_BLUE),
            (self.bc_var,  "L3 — Blockchain مسیر (§5.3)",     C_PURPLE),
        ]:
            tk.Checkbutton(p, text=text, variable=var, bg=BG2, fg=col,
                           selectcolor=BG2, activebackground=BG2,
                           font=("Courier New", 8), cursor="hand2",
                           command=self._update_metrics).pack(anchor=tk.W, padx=10, pady=1)
        self._sep(p)

        
        self._section(p, "تلمتری — Table 7 مقاله", C_PURPLE)
        self.lbl_acc     = tk.Label(p, text="دقت IDS: 98.7٪",        bg=BG2, fg=C_GREEN,  font=FMS, anchor=tk.W)
        self.lbl_fpr     = tk.Label(p, text="FPR: 1.2٪",              bg=BG2, fg=C_BLUE,   font=FMS, anchor=tk.W)
        self.lbl_lat     = tk.Label(p, text="تاخیر: 15 ms",           bg=BG2, fg=C_GREEN,  font=FMS, anchor=tk.W)
        self.lbl_pqc     = tk.Label(p, text="PQC: غیرفعال",          bg=BG2, fg=C_MUTED,  font=FMS, anchor=tk.W)
        self.lbl_bc      = tk.Label(p, text="BC: غیرفعال",           bg=BG2, fg=C_MUTED,  font=FMS, anchor=tk.W)
        self.lbl_cost    = tk.Label(p, text="هزینه: 2.3M USD",        bg=BG2, fg=C_MUTED,  font=FMS, anchor=tk.W)
        self.lbl_threats = tk.Label(p, text="تهدیدات: 0",             bg=BG2, fg=C_GREEN,  font=FMS, anchor=tk.W)
        self.lbl_tdoa    = tk.Label(p, text="TDoA دقت: —",           bg=BG2, fg=C_MID,    font=FMS, anchor=tk.W)
        self.lbl_bc_blk  = tk.Label(p, text="بلاک‌های BC: 0",        bg=BG2, fg=C_MUTED,  font=FMS, anchor=tk.W)
        for lbl in (self.lbl_acc, self.lbl_fpr, self.lbl_lat, self.lbl_pqc,
                    self.lbl_bc, self.lbl_cost, self.lbl_threats,
                    self.lbl_tdoa, self.lbl_bc_blk):
            lbl.pack(fill=tk.X, padx=14, pady=1)
        self._sep(p)

        
        self._section(p, "راهنمای رنگ حملات", C_MUTED)
        legend = [
            (C_GREEN,  "پرواز سالم"),
            (C_RED,    "شبح ADS-B (§3.1)"),
            (C_AMBER,  "TCAS Spoof (§2.2)"),
            (C_PURPLE, "Replay (§3.2)"),
            (C_ORANGE, "GPS Spoof (§3.3)"),
            ("#ef4444", "DoS/Flood (§3.4)"),
        ]
        for col, label in legend:
            f = tk.Frame(p, bg=BG2)
            f.pack(anchor=tk.W, padx=12, pady=1)
            tk.Frame(f, bg=col, width=10, height=10).pack(side=tk.LEFT)
            tk.Label(f, text="  "+label, bg=BG2, fg=C_MUTED,
                     font=("Courier New", 7)).pack(side=tk.LEFT)

        
        tk.Button(p, text="✕  خروج  (Esc)", bg="#1a0a0a", fg=C_RED,
                  activebackground=C_RED, activeforeground="white",
                  font=FM, bd=0, relief=tk.FLAT, cursor="hand2",
                  command=self.root.quit
                  ).pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=(0,8))

        self.lbl_clock = tk.Label(p, text="--:--:--", bg=BG2, fg=C_DIM, font=FMS)
        self.lbl_clock.pack(side=tk.BOTTOM, pady=2)

    def _build_right(self, p):
        
        hud = tk.Frame(p, bg=BG2, height=28)
        hud.pack(fill=tk.X)
        hud.pack_propagate(False)
        self.lbl_live  = tk.Label(hud, text="● LIVE · 1090 MHz · Mode-S",
                                  bg=BG2, fg=C_GREEN, font=FMS)
        self.lbl_live.pack(side=tk.LEFT, padx=10, pady=5)
        self.lbl_count = tk.Label(hud, text="پروازها: ۰", bg=BG2, fg=C_MID, font=FMS)
        self.lbl_count.pack(side=tk.LEFT, padx=16)
        self.lbl_mode  = tk.Label(hud, text="LSTM IDS فعال", bg=BG2, fg=C_MID, font=FMS)
        self.lbl_mode.pack(side=tk.RIGHT, padx=10)

        
        self.canvas = tk.Canvas(p, bg=BG, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

       
        log_f = tk.Frame(p, bg=BG2, height=120)
        log_f.pack(fill=tk.X, side=tk.BOTTOM)
        log_f.pack_propagate(False)
        
        hdr = tk.Frame(log_f, bg=BG2)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text=" مانیتورینگ زنده — لاگ پدافند سایبری",
                 bg=BG2, fg=C_BLUE, font=FMS).pack(side=tk.LEFT, padx=8, pady=3)
        tk.Label(hdr, text="[Rashidi, 2027 · Table 7]",
                 bg=BG2, fg=C_DIM, font=("Courier New",7)).pack(side=tk.RIGHT, padx=8)
        inner = tk.Frame(log_f, bg=BG2)
        inner.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0,4))
        self.log = tk.Text(inner, bg="#040810", fg="#10b981",
                           font=("Courier New", 8), bd=0, relief=tk.FLAT,
                           wrap=tk.WORD, state=tk.DISABLED)
        vsb = tk.Scrollbar(inner, command=self.log.yview,
                           bg=BG2, troughcolor=BG2, width=8)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.log.config(yscrollcommand=vsb.set)
        self.log.pack(fill=tk.BOTH, expand=True)
        for tag, fg in [("ok","#10b981"),("warn",C_AMBER),
                        ("err",C_RED),("info",C_BLUE),
                        ("pqc",C_PURPLE),("bc","#818cf8")]:
            self.log.tag_config(tag, foreground=fg)


    def _log(self, msg, tag="ok"):
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n", tag)
        self.log.see(tk.END)
        lines = int(self.log.index(tk.END).split(".")[0])
        if lines > 150:
            self.log.delete("1.0", "25.0")
        self.log.config(state=tk.DISABLED)


    def _init_traffic(self):
        for lbl in ["THY4821","IRA655","FLY334","UAE201"]:
            self.aircrafts[lbl] = make_ac(
                lbl, random.uniform(0.15,0.7), random.uniform(0.15,0.7),
                random.uniform(-0.001,0.002), random.uniform(-0.0005,0.0005),
                random.randint(450,600), random.uniform(0.5,2.0),
            )
        self._log("SkyShield-ATC v3.0 راه‌اندازی شد — بر اساس Rashidi (2027)", "info")
        self._log("پروتکل‌های زیر نظر: ADS-B · TCAS · CPDLC · LDACS", "info")
        self._log("فرکانس پایش: 1090 MHz (Mode-S Extended Squitter)", "info")


    def atk_ghost(self):
        """§3.1 — Ghost Aircraft Injection (سرعت > 1200 km/h)"""
        gid = "GST" + str(random.randint(10,99))
        self.aircrafts[gid] = make_ac(
            gid, 0.08, 0.5, 0.003, -0.0008,
            random.randint(1250,1450), 3500, psr=1,
            is_ghost=True, atk=ATK_GHOST,
            psr_mismatch=random.uniform(2.8, 5.2),
        )
        self._log(f"⬡ Ghost Injection [{gid}] — سرعت بحرانی {self.aircrafts[gid]['speed']} km/h "
                  f"(§3.1 · Al-Naimi & Al-Mansoori, 2024)", "err")
        self._log(f"   TDoA mismatch: {self.aircrafts[gid]['tdoa_loc_error']:.1f} m از موقعیت واقعی", "warn")

    def atk_tcas(self):
        """§2.2 — TCAS Distance Spoofing: کاهش فاصله ادراکی > 3.5 km"""
        tid = "TCS" + str(random.randint(10,99))
        spoofed_dist = round(random.uniform(3.5, 4.2), 1)
        self.aircrafts[tid] = make_ac(
            tid, 0.2, 0.6, 0.002, 0.0005,
            550, 3800, psr=1, tcas=True,
            is_ghost=True, atk=ATK_TCAS,
            psr_mismatch=spoofed_dist,
        )
        self._log(f"⚠ TCAS Spoofing [{tid}] — کاهش فاصله ادراکی: {spoofed_dist} km "
                  f"(§2.2 · Longo et al., 2026)", "err")
        self._log(f"   آستانه Resolution Advisory فعال شد! (ΔD > 3.5km)", "warn")

    def atk_replay(self):
        """§3.2 — Replay Attack: پخش مجدد پیام‌های معتبر — duplicate targets"""
        # کپی موقعیت پروازهای واقعی با تاخیر زمانی
        real_acs = [ac for ac in self.aircrafts.values() if not ac["is_ghost"]]
        if not real_acs:
            self._log("Replay: هیچ پرواز واقعی برای تقلید وجود ندارد.", "warn")
            return
        src = random.choice(real_acs)
        rid = "RPY" + str(random.randint(10,99))
        self.aircrafts[rid] = make_ac(
            rid,
            src["x"] + random.uniform(-0.05, 0.05),
            src["y"] + random.uniform(-0.05, 0.05),
            src["vx"] * random.uniform(0.9,1.1),
            src["vy"] * random.uniform(0.9,1.1),
            src["speed"], 3200,
            psr=1, is_ghost=True, atk=ATK_REPLAY, decay=True,
            psr_mismatch=random.uniform(0.3, 1.2),
        )
        self._log(f"⟳ Replay Attack [{rid}] — تقلید از [{src['label']}] "
                  f"(§3.2 · Kim, 2022 · تاخیر: 250-500ms)", "warn")
        self._log(f"   Duplicate target در رادار: timestamp mismatch شناسایی شد", "warn")

    def atk_gps(self):
        """§3.3 — GPS Spoofing ترکیبی با ADS-B Injection"""
        gps_id = "GPS" + str(random.randint(10,99))
        offset = (random.uniform(0.05,0.15), random.uniform(0.05,0.15))
        
        real_acs = [k for k,v in self.aircrafts.items() if not v["is_ghost"]]
        if real_acs:
            target = random.choice(real_acs)
            self.aircrafts[target]["gps_offset"] = offset
            self._log(f"⊕ GPS Spoofing → هواپیمای [{target}] منحرف شد "
                      f"(§3.3 · Zeng, Wu & Fu, 2024)", "warn")
        
        self.aircrafts[gps_id] = make_ac(
            gps_id, random.uniform(0.1,0.8), random.uniform(0.1,0.8),
            random.uniform(-0.002,0.002), random.uniform(-0.001,0.001),
            random.randint(450,900), 4000, psr=1,
            is_ghost=True, atk=ATK_GPS,
            gps_offset=offset, psr_mismatch=random.uniform(1.5,4.0),
        )
        self._log(f"⊕ ADS-B جعلی [{gps_id}] هم‌زمان تزریق شد — GPS+ADS-B combined attack", "err")

    def atk_flood(self):
        """§3.4 — DoS: اشباع کانال 1090 MHz با سیگنال‌های فانتوم"""
        for i in range(16):
            fid = "FLD" + "".join(random.choices("ABCDEFGHJK0123456789", k=3))
            self.aircrafts[fid] = make_ac(
                fid, random.uniform(0.04,0.93), random.uniform(0.04,0.93),
                random.uniform(-0.005,0.005), random.uniform(-0.003,0.003),
                random.randint(1100,1600), random.uniform(2500,5000),
                psr=1, is_ghost=True, atk=ATK_FLOOD, decay=True,
            )
        self._log(f"⚡ DoS Flooding — ۱۶ سیگنال فانتوم روی 1090 MHz "
                  f"(§3.4 · Khan et al., 2024)", "err")
        self._log(f"   کانال Mode-S اشباع شد — احتمال از دست رفتن پیام‌های واقعی!", "warn")

    def clear_all(self):
        
        for ac in self.aircrafts.values():
            if not ac["is_ghost"]:
                ac["gps_offset"] = (0, 0)
        self.aircrafts = {k:v for k,v in self.aircrafts.items() if not v["is_ghost"]}
        self._update_metrics()
        self._log("✓ دفع موثر: همه تهدیدات خنثی شدند — رادار پاک است.", "ok")

   
    def _update_metrics(self):
        ids = self.ids_var.get()
        pqc = self.pqc_var.get()
        bc  = self.bc_var.get()
        m   = self.ids_method.get()

       
        method_data = {
            "lstm":        ("98.7٪", "1.2٪",  "15 ms",  C_GREEN,  C_BLUE),
            "rf":          ("93.4٪", "3.8٪",  "8 ms",   C_BLUE,   C_MUTED),
            "svm":         ("89.2٪", "6.1٪",  "5 ms",   C_MUTED,  C_MUTED),
            "multisensor": ("99.1٪", "0.7٪",  "25 ms",  C_AMBER,  C_GREEN),
        }
        acc, fpr, lat, ac, fc = method_data.get(m, ("93.4٪","3.8٪","8ms",C_BLUE,C_MUTED))

        if not ids:
            acc, fpr, lat, ac = "29.0٪","—","4500 ms", C_RED
            self.lbl_mode.config(text="بدون IDS — سیستم سنتی", fg=C_RED)
        elif ids and pqc and bc:
            acc, fpr, lat, ac = "99.4٪","0.2٪","68 ms", C_GREEN
            self.lbl_mode.config(text="فریم‌ورک کامل L1+L2+L3", fg=C_GREEN)
        else:
            parts = [x for x,f in [("LSTM" if m=="lstm" else m.upper(),ids),
                                    ("ML-DSA",pqc),("BC",bc)] if f]
            self.lbl_mode.config(text="+".join(parts), fg=C_BLUE)

        self.lbl_acc.config(text=f"دقت IDS: {acc}", fg=ac)
        self.lbl_fpr.config(text=f"FPR: {fpr}", fg=fc)
        self.lbl_lat.config(text=f"تاخیر: {lat}", fg=C_GREEN if ids else C_RED)

        
        if pqc:
            self.lbl_pqc.config(text="ML-DSA: فعال (2880B key · 2420B sig)", fg=C_BLUE)
        else:
            self.lbl_pqc.config(text="PQC: غیرفعال (آسیب‌پذیر)", fg=C_MUTED)

       
        if bc:
            self.lbl_bc.config(text=f"BC: فعال — هر ۳۰ ثانیه (§5.3)", fg="#818cf8")
        else:
            self.lbl_bc.config(text="BC: غیرفعال", fg=C_MUTED)

        
        cost = 0.0
        if ids: cost += 2.3
        if pqc: cost += 3.2
        if bc:  cost += 3.2
        self.lbl_cost.config(
            text=f"هزینه: {cost:.1f}M USD/فرودگاه",
            fg=C_RED if cost > 6 else (C_AMBER if cost > 2 else C_MUTED)
        )


    def _detect(self, ac):
        if not self.ids_var.get():
            return False, 0.0
        m = self.ids_method.get()
        feat = [[ac["speed"], ac["tdoa"], ac["psr"],
                 1 if ac["tcas"] else 0,
                 1 if ac["atk"]==ATK_GPS else 0]]
        try:
            if m == "lstm":
                p = clf_lstm.predict(feat)[0]
                conf = max(clf_lstm.predict_proba(feat)[0])
            elif m == "rf":
                p = clf_rf.predict(feat)[0]
                conf = max(clf_rf.predict_proba(feat)[0])
            elif m == "svm":
                p = clf_svm.predict(feat)[0]
                conf = max(clf_svm.predict_proba(feat)[0])
            else:  
                p = clf_lstm.predict(feat)[0]
                conf = max(clf_lstm.predict_proba(feat)[0])
                
                if ac["psr_mismatch"] > 1.5:
                    p = 1
                    conf = min(1.0, conf + 0.1)
            return bool(p), float(conf)
        except Exception:
            return bool(ac["is_ghost"]), 0.9


    def _draw(self):
        c = self.canvas
        c.delete("all")
        W = c.winfo_width()
        H = c.winfo_height()
        if W < 50 or H < 50:
            return

        cx, cy = W/2, H/2
        R = min(W, H) * 0.44

     
        for fx in range(0, W, 60):
            c.create_line(fx, 0, fx, H, fill="#050e18", width=0.5)
        for fy in range(0, H, 60):
            c.create_line(0, fy, W, fy, fill="#050e18", width=0.5)

       
        range_labels = {0.25: "75", 0.5: "150", 0.75: "225", 1.0: "300"}
        for frac, label in range_labels.items():
            rr = R * frac
            col = C_RING if frac == 1.0 else BG3
            w   = 1.5 if frac == 1.0 else 0.8
            c.create_oval(cx-rr, cy-rr, cx+rr, cy+rr, outline=col, width=w)
            c.create_text(cx+rr+4, cy-8, text=f"{label}km",
                          fill=C_DIM, font=("Courier New",7), anchor=tk.W)

       
        c.create_line(cx, cy-R, cx, cy+R, fill=BG3, width=0.5, dash=(3,6))
        c.create_line(cx-R, cy, cx+R, cy, fill=BG3, width=0.5, dash=(3,6))

       
        for deg in range(0, 360, 30):
            rad = math.radians(deg-90)
            c.create_line(cx+math.cos(rad)*R*0.96, cy+math.sin(rad)*R*0.96,
                          cx+math.cos(rad)*R,       cy+math.sin(rad)*R,
                          fill=C_RING, width=0.8)
            tx = cx + math.cos(rad) * (R+14)
            ty = cy + math.sin(rad) * (R+14)
            c.create_text(tx, ty, text=f"{deg}°", fill=C_DIM,
                          font=("Courier New",7))

        # ── sweep trail ──
        sr = math.radians(self.sweep)
        for i in range(60, 0, -1):
            a0 = math.radians(self.sweep - i)
            a1 = math.radians(self.sweep - i + 1.2)
            alpha = max(0, int(22 * (1 - i/60)))
            try:
                pts = [cx, cy,
                       cx+math.cos(a0)*R, cy+math.sin(a0)*R,
                       cx+math.cos((a0+a1)/2)*R, cy+math.sin((a0+a1)/2)*R,
                       cx+math.cos(a1)*R, cy+math.sin(a1)*R]
                col = f"#{0:02x}{min(255,alpha*4):02x}{int(alpha*3):02x}"
                c.create_polygon(pts, fill=col, outline="")
            except Exception:
                pass

        
        c.create_line(cx, cy,
                      cx+math.cos(sr)*R, cy+math.sin(sr)*R,
                      fill="#003322", width=4)
        c.create_line(cx, cy,
                      cx+math.cos(sr)*R, cy+math.sin(sr)*R,
                      fill=C_GREEN, width=1.5)

        
        now = time.time()
        if self.bc_var.get() and (now - self.last_bc_t >= 30):
            for aid, ac in self.aircrafts.items():
                if not ac["is_ghost"]:
                    self.bc_ledger.append({
                        "icao": aid, "ts": now,
                        "pos": (round(ac["x"],4), round(ac["y"],4)),
                        "speed": ac["speed"],
                    })
            self.last_bc_t = now
            self._log(f"⛓ Blockchain: {len([a for a in self.aircrafts.values() if not a['is_ghost']])} "
                      f"رکورد ثبت شد — بلاک #{len(self.bc_ledger)} (§5.3)", "bc")
        self.lbl_bc_blk.config(text=f"بلاک‌های BC: {len(self.bc_ledger)}")

        
        threats = 0
        to_del = []
        tdoa_errors = []

        for aid, ac in list(self.aircrafts.items()):
            ac["age"] += 1
            
            ox, oy = ac["gps_offset"]
            ac["x"] += ac["vx"] + ox * 0.0001
            ac["y"] += ac["vy"] + oy * 0.0001

            
            if ac["x"] > 0.97: ac["x"] = 0.03; ac["y"] = random.uniform(0.1,0.9)
            if ac["x"] < 0.02: ac["x"] = 0.95
            if ac["y"] > 0.96: ac["vy"] = -abs(ac["vy"])
            if ac["y"] < 0.04: ac["vy"] = abs(ac["vy"])
            if ac["decay"] and ac["age"] > 230:
                to_del.append(aid); continue

            
            px = cx + (ac["x"]-0.5) * R * 1.85
            py = cy + (ac["y"]-0.5) * R * 1.85

            
            is_anom, conf = self._detect(ac)
            if is_anom:
                threats += 1
                if ac["is_ghost"] and ac["tdoa_loc_error"] > 0:
                    tdoa_errors.append(ac["tdoa_loc_error"])

            
            atk_type = ac["atk"]
            if is_anom:
                col = ATK_COLORS.get(atk_type, C_RED)
            else:
                col = C_GREEN

            
            ac["trail"].append((px, py))
            if len(ac["trail"]) > 16: ac["trail"].pop(0)
            for i in range(1, len(ac["trail"])):
                t0, t1 = ac["trail"][i-1], ac["trail"][i]
                alpha = int(200 * i / len(ac["trail"]))
                if is_anom:
                    r,g,b = 255, 0, int(alpha*0.3)
                    if atk_type==ATK_TCAS:  r,g,b=245,158,11
                    elif atk_type==ATK_REPLAY: r,g,b=168,85,247
                    elif atk_type==ATK_GPS:   r,g,b=251,146,60
                    tc = f"#{r:02x}{int(g*alpha/255):02x}{int(b*alpha/255):02x}"
                else:
                    tc = f"#{0:02x}{min(255,alpha):02x}{int(alpha*0.8):02x}"
                c.create_line(t0[0],t0[1],t1[0],t1[1], fill=tc, width=1.2)

            
            ba = (math.degrees(math.atan2(py-cy, px-cx))+360)%360
            diff = abs(ba - self.sweep%360) % 360
            if diff < 10 or diff > 350:
                c.create_oval(px-12,py-12,px+12,py+12, outline=col, width=1.0)

            
            if self.ids_method.get() == "multisensor" and ac["psr_mismatch"] > 0.5:
                pm = ac["psr_mismatch"]
                px2 = px + pm * 8
                py2 = py - pm * 4
                c.create_rectangle(px2-5,py2-5,px2+5,py2+5,
                                   outline=C_AMBER, width=1.0)
                c.create_line(px,py,px2,py2, fill=C_AMBER, width=0.6, dash=(2,3))

            
            c.create_oval(px-10,py-10,px+10,py+10, fill="", outline="")
            
            dot = 5 if is_anom else 4
            c.create_oval(px-dot,py-dot,px+dot,py+dot, fill=col, outline="")

            
            info = [
                ac["label"],
                f"{int(ac['speed'])} km/h",
            ]
            if is_anom:
                aname = {
                    ATK_GHOST:"[GHOST §3.1]", ATK_TCAS:f"[TCAS Δ{ac['psr_mismatch']:.1f}km]",
                    ATK_REPLAY:"[REPLAY §3.2]", ATK_GPS:"[GPS §3.3]",
                    ATK_FLOOD:"[DoS §3.4]"
                }.get(atk_type, "[MALICIOUS]")
                info.append(aname)
                info.append(f"conf: {conf:.0%}")
            else:
                if self.pqc_var.get(): info.append("ML-DSA: ✓")
                if self.bc_var.get():  info.append("BC: SYNCED")

            lw = max(len(max(info, key=len)), 10) * 5.2 + 6
            lh = len(info) * 11 + 4
            lx, ly = px+10, py-12
            c.create_rectangle(lx-2, ly, lx+lw, ly+lh,
                               fill="#040810", outline=col, width=0.6)
            for j, line in enumerate(info):
                fg = col if j > 1 and is_anom else (col if j==0 else C_MUTED)
                c.create_text(lx+2, ly+4+j*11, text=line,
                              fill=fg, font=("Courier New",8,"bold" if j==0 else ""),
                              anchor=tk.NW)

        for k in to_del:
            self.aircrafts.pop(k, None)

        
        if tdoa_errors:
            avg_err = sum(tdoa_errors)/len(tdoa_errors)
            self.lbl_tdoa.config(
                text=f"TDoA دقت: {avg_err:.1f} m (§4.3)",
                fg=C_AMBER if avg_err > 3.2 else C_GREEN
            )
        else:
            self.lbl_tdoa.config(text="TDoA: محدوده پاک", fg=C_MID)

        
        self._draw_hud(c, W, H, threats)
        self.lbl_threats.config(
            text=f"تهدیدات: {threats}",
            fg=C_RED if threats>0 else C_GREEN
        )
        self.lbl_count.config(text=f"پروازها: {len(self.aircrafts)}")

    def _draw_hud(self, c, W, H, threats):
        
        for bx,by,dx,dy in [(2,2,1,1),(W-2,2,-1,1),(2,H-2,1,-1),(W-2,H-2,-1,-1)]:
            c.create_line(bx+dx*22,by, bx,by, fill=C_RING, width=1.5)
            c.create_line(bx,by, bx,by+dy*22, fill=C_RING, width=1.5)

        
        c.create_text(W-8, 8, anchor=tk.NE,
                      text="ADS-B · TCAS · CPDLC · LDACS | 1090 MHz | Mode-S",
                      fill=C_RING, font=("Courier New",7))

        
        c.create_text(8, H-8, anchor=tk.SW,
                      text="SkyShield-ATC v3.0 | Rashidi (2027) · IAU Tehran Central",
                      fill=C_RING, font=("Courier New",7))

        
        if threats > 0:
            badge = f"⚠  {threats} تهدید فعال"
            bx = W-8
            bw = len(badge)*5 + 14
            c.create_rectangle(bx-bw, 24, bx, 40,
                               fill="#1a0008", outline=C_RED, width=1.0)
            c.create_text(bx-6, 32, text=badge,
                          fill=C_RED, font=("Courier New",8,"bold"), anchor=tk.E)

        
        m_labels = {
            "lstm":"LSTM 98.7٪","rf":"RF 93.4٪",
            "svm":"SVM 89.2٪","multisensor":"Multi-sensor 99.1٪"
        }
        ml = m_labels.get(self.ids_method.get(), "IDS")
        c.create_text(8, 10, anchor=tk.NW,
                      text=f"IDS: {ml} | PQC: {'ML-DSA ✓' if self.pqc_var.get() else '✗'} | "
                           f"BC: {'✓' if self.bc_var.get() else '✗'}",
                      fill=C_MID, font=("Courier New",8))


    def _animate(self):
        self.sweep = (self.sweep + 1.3) % 360
        self.lbl_clock.config(text=time.strftime("%H:%M:%S"))
        tick = int(time.time()*2) % 2
        self.lbl_live.config(fg=C_GREEN if tick else C_DIM)
        self._draw()
        self.root.after(40, self._animate)


if __name__ == "__main__":
    root = tk.Tk()
    app = SkyShield(root)
    root.mainloop()