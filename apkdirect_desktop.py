#!/usr/bin/env python3
"""APKDirect for Windows PC - native desktop app, no emulator needed.
Store-style interface like the APKDirect mobile app: header + search,
category tabs, Featured / Trending / Latest Updates / New Releases /
Top downloads sections, bottom navigation, and a Login screen
(Google / Email / Anonymous - UI only until a Google Cloud OAuth
setup is done, same as the mobile app).
Downloads save straight to Downloads/APKDirect. No Play Store redirect.
Real listings come from the backend API when a live host is set;
until then the store shows APKDirect's own app, which is a real file.
Stdlib only (tkinter + urllib). Run: python apkdirect_desktop.py
"""
import json
import os
import threading
import tkinter as tk
import urllib.request
import urllib.parse
import webbrowser
from tkinter import messagebox

BACKEND_URL = "https://apkdirect.example"  # live backend host yahan daalo
OWN_APP_URL = "https://super-quokka-ec144c.netlify.app/APKDirect-v5.apk"
WEBSITE_URL = "https://thunderous-palmier-cb6add.netlify.app/"
CATEGORIES = ["All", "Apps", "Games", "Mod APK", "Premium APK"]
BG = "#f4f6f8"
GREEN = "#0a9d5c"
DARK = "#10201c"


def fetch_apps(category, query):
    if BACKEND_URL == "https://apkdirect.example":
        return []
    cat = "" if category == "All" else urllib.parse.quote(category)
    url = f"{BACKEND_URL}/api/apps?cat={cat}&q={urllib.parse.quote(query)}"
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            return json.loads(r.read().decode())["apps"]
    except Exception:
        return []


def download_file(name, url, status):
    try:
        dest_dir = os.path.join(os.path.expanduser("~/Downloads"), "APKDirect")
        os.makedirs(dest_dir, exist_ok=True)
        dest = os.path.join(dest_dir, os.path.basename(urllib.parse.urlparse(url).path) or (name + ".apk"))
        status.set(f"Downloading {name}...")
        urllib.request.urlretrieve(url, dest)
        status.set(f"Ho gaya: {dest}")
        messagebox.showinfo("APKDirect", f"Download ho gaya:\n{dest}")
    except Exception as e:
        status.set("Download fail hua.")
        messagebox.showerror("APKDirect", f"Download fail hua: {e}")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("APKDirect")
        self.geometry("900x680")
        self.configure(bg=BG)
        self.category = tk.StringVar(value="All")
        self.query = tk.StringVar()
        self.status = tk.StringVar(value="Pick a category, search, press Download - the file downloads directly.")

        # Header (dark, like the store)
        header = tk.Frame(self, bg=DARK)
        header.pack(fill="x")
        tk.Label(header, text="APKDirect", font=("Segoe UI", 26, "bold"), bg=DARK, fg="white").pack(side="left", padx=14, pady=10)
        tk.Button(header, text="Login", bg=GREEN, fg="white", font=("Segoe UI", 11, "bold"),
                  command=self.show_login).pack(side="right", padx=14)
        tk.Label(header, text="Direct APK Downloads - no Play Store redirect", bg=DARK, fg="#bfd8c9").pack(side="left")

        # Search
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=14, pady=10)
        tk.Entry(top, textvariable=self.query, font=("Segoe UI", 12), width=50).pack(side="left", padx=(0, 8))
        tk.Button(top, text="Search", command=self.refresh, bg=GREEN, fg="white", font=("Segoe UI", 11)).pack(side="left")

        # Category tabs
        cats = tk.Frame(self, bg=BG)
        cats.pack(pady=(0, 8))
        self.cat_buttons = {}
        for c in CATEGORIES:
            b = tk.Button(cats, text=c, font=("Segoe UI", 11, "bold"),
                          command=lambda v=c: self.set_cat(v))
            b.pack(side="left", padx=4)
            self.cat_buttons[c] = b
        self.update_cat_buttons()

        # Scrollable list
        canvas_frame = tk.Frame(self, bg=BG)
        canvas_frame.pack(fill="both", expand=True, padx=14)
        self.list_frame = tk.Frame(canvas_frame, bg=BG)
        self.list_frame.pack(fill="both", expand=True)

        # Bottom nav
        bottom = tk.Frame(self, bg=DARK)
        bottom.pack(fill="x")
        for label, cat in [("Home", "All"), ("Games", "Games"), ("Categories", "All"), ("Website", None)]:
            def handler(v=cat, l=label):
                if l == "Website":
                    webbrowser.open(WEBSITE_URL)
                else:
                    self.set_cat(v)
            tk.Button(bottom, text=label, bg=DARK, fg="white", font=("Segoe UI", 11, "bold"),
                      command=handler).pack(side="left", expand=True, padx=4, pady=8)
        tk.Label(self, textvariable=self.status, bg=BG, wraplength=850, justify="left").pack(fill="x", padx=14, pady=6)
        self.refresh()

    def set_cat(self, v):
        self.category.set(v)
        self.update_cat_buttons()
        self.refresh()

    def update_cat_buttons(self):
        cur = self.category.get()
        for c, b in self.cat_buttons.items():
            b.configure(bg=GREEN if c == cur else "white", fg="white" if c == cur else "black")

    def show_login(self):
        win = tk.Toplevel(self)
        win.title("APKDirect Login")
        win.geometry("360x260")
        tk.Label(win, text="Login", font=("Segoe UI", 20, "bold")).pack(pady=14)
        tk.Button(win, text="LOG IN WITH GOOGLE", bg=GREEN, fg="white", font=("Segoe UI", 11, "bold"),
                  command=lambda: (messagebox.showinfo("APKDirect", "Google sign-in: UI only for now. Full Google account link needs a Google Cloud OAuth setup."), win.destroy())).pack(fill="x", padx=20, pady=6)
        tk.Button(win, text="LOG IN WITH EMAIL", bg=GREEN, fg="white", font=("Segoe UI", 11, "bold"),
                  command=win.destroy).pack(fill="x", padx=20, pady=6)
        tk.Button(win, text="Enter as anonymous user", command=win.destroy).pack(fill="x", padx=20, pady=6)

    def refresh(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        cat, q = self.category.get(), self.query.get()
        self.status.set("Load ho raha hai...")
        def work():
            apps = fetch_apps(cat, q)
            self.after(0, lambda: self.show(apps))
        threading.Thread(target=work, daemon=True).start()

    def app_card(self, parent, name, meta, url):
        card = tk.Frame(parent, bg="white", bd=1, relief="solid")
        card.pack(fill="x", pady=5, padx=2)
        tk.Label(card, text=name, font=("Segoe UI", 14, "bold"), bg="white").pack(anchor="w", padx=10, pady=(6, 0))
        tk.Label(card, text=meta, bg="white", fg="#40544c").pack(anchor="w", padx=10)
        tk.Label(card, text="★★★★★", bg="white", fg="#f59e0b").pack(anchor="w", padx=10)
        tk.Button(card, text="⬇ Download", bg=GREEN, fg="white",
                  command=lambda: threading.Thread(target=download_file, args=(name, url, self.status), daemon=True).start()
                  ).pack(anchor="w", padx=10, pady=8)

    def section(self, title):
        tk.Label(self.list_frame, text=title, font=("Segoe UI", 16, "bold"), bg=BG).pack(anchor="w", pady=(10, 2))

    def show(self, apps):
        for w in self.list_frame.winfo_children():
            w.destroy()
        cat, q = self.category.get(), self.query.get().lower()
        # Own real app, shown in All / Apps (and as Featured / Trending / Latest)
        show_own = (cat in ("All", "Apps")) and ("apkdirect" in q or not q)
        if show_own:
            self.section("Featured")
            self.app_card(self.list_frame, "APKDirect", "APKDirect - v5.0 - 25 KB", OWN_APP_URL)
            self.section("Trending today")
            self.app_card(self.list_frame, "APKDirect", "APKDirect - v5.0 - 25 KB", OWN_APP_URL)
            self.section("Latest Updates")
            self.app_card(self.list_frame, "APKDirect", "APKDirect - v5.0 - 25 KB", OWN_APP_URL)
        self.section("New Releases")
        tk.Label(self.list_frame, text="No new release yet. The first owner-uploaded app will appear here.",
                 bg=BG, fg="#40544c", wraplength=800, justify="left").pack(anchor="w")
        self.section("Top downloads")
        tk.Label(self.list_frame, text="No downloads yet.", bg=BG, fg="#40544c").pack(anchor="w")
        if apps:
            self.section("Backend apps")
            for app in apps:
                self.app_card(self.list_frame, app["name"],
                              f"{app['category']} · v{app.get('version', '')} · {app.get('size_mb', 0)} MB",
                              f"{BACKEND_URL}/download/{app['id']}")
        self.status.set("Ready. Downloads save to Downloads/APKDirect.")


if __name__ == "__main__":
    App().mainloop()
