#!/usr/bin/env python3
"""APKDirect for computer - proper desktop software (not a website wrapper).
Same APKDirect backend as the mobile app: 4 categories, search, direct download.
No Play Store redirect anywhere: Download saves the APK file straight to Downloads/APKDirect.
Admin upload is owner-only via the backend admin page (Google sign-in); visitors
never get an upload button inside this software.

Backend: workspace/apkdirect/app.py - serves GET /api/apps and /download/{id}.
Change BACKEND_URL below to the live backend host when deployed.
Run: python3 apkdirect_desktop.py
Stdlib only (tkinter + urllib). No dependencies.
"""
import json
import os
import threading
import tkinter as tk
import urllib.request
import urllib.parse
import webbrowser
from tkinter import messagebox, ttk

BACKEND_URL = "https://apkdirect.example"  # live backend host yahan daalo
CATEGORIES = ["All", "Apps", "Games", "Mod APK", "Premium APK"]
BG = "#d6f5e3"
STR = {
    "EN": {"tag": "Direct APK Downloads - no Play Store redirect", "search": "Search", "empty": "No app in this category yet. The first app will appear here.",
           "admin": "Owner admin (Google sign-in)", "download": "\u2b07 Download", "hint": "Pick a category, search, press Download - the file downloads directly."},
    "HI": {"tag": "Seedha APK Download - Play Store par koi redirect nahi", "search": "Search", "empty": STR[self.lang]["empty"],
           "admin": "Owner admin (Google sign-in)", "download": "\u2b07 Download", "hint": "Category chuno, app dhoondho, Download dabao - file seedha download hogi."},
}


def fetch_apps(category, query):
    cat = "" if category == "All" else urllib.parse.quote(category)
    url = f"{BACKEND_URL}/api/apps?cat={cat}&q={urllib.parse.quote(query)}"
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            return json.loads(r.read().decode())["apps"]
    except Exception:
        return []


def download_file(app, status):
    try:
        dest_dir = os.path.join(os.path.expanduser("~/Downloads"), "APKDirect")
        os.makedirs(dest_dir, exist_ok=True)
        dest = os.path.join(dest_dir, f"{app['name']}.apk")
        status.set(f"Downloading {app['name']}...")
        urllib.request.urlretrieve(f"{BACKEND_URL}/download/{app['id']}", dest)
        status.set(f"Ho gaya: {dest}")
        messagebox.showinfo("APKDirect", f"Download ho gaya:\n{dest}")
    except Exception as e:
        status.set("Download fail hua.")
        messagebox.showerror("APKDirect", f"Download fail hua: {e}")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("APKDirect")
        self.geometry("820x620")
        self.configure(bg=BG)
        self.category = tk.StringVar(value="All")
        self.query = tk.StringVar()
        self.lang = "EN"
        self.status = tk.StringVar(value=STR["EN"]["hint"])

        tk.Label(self, text="APKDirect", font=("Segoe UI", 26, "bold"), bg=BG, fg="#10201c").pack(pady=(14, 0))
        self.tag_label = tk.Label(self, text=STR["EN"]["tag"], bg=BG, fg="#40544c")
        self.tag_label.pack()
        lang_row = tk.Frame(self, bg=BG)
        lang_row.pack(pady=(4, 0))
        tk.Button(lang_row, text="English", command=lambda: self.set_lang("EN")).pack(side="left", padx=4)
        tk.Button(lang_row, text="Hindi", command=lambda: self.set_lang("HI")).pack(side="left", padx=4)

        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=14, pady=10)
        tk.Entry(top, textvariable=self.query, font=("Segoe UI", 12), width=40).pack(side="left", padx=(0, 8))
        tk.Button(top, text="Search", command=self.refresh, bg="#0a9d5c", fg="white", font=("Segoe UI", 11)).pack(side="left")

        cats = tk.Frame(self, bg=BG)
        cats.pack(pady=(0, 8))
        for c in CATEGORIES:
            tk.Radiobutton(cats, text=c, variable=self.category, value=c, bg=BG,
                           command=self.refresh, font=("Segoe UI", 11)).pack(side="left", padx=6)

        self.list_frame = tk.Frame(self, bg=BG)
        self.list_frame.pack(fill="both", expand=True, padx=14)

        bottom = tk.Frame(self, bg=BG)
        bottom.pack(fill="x", padx=14, pady=10)
        tk.Label(bottom, textvariable=self.status, bg=BG, wraplength=600, justify="left").pack(side="left")
        tk.Button(bottom, text="Owner admin (Google sign-in)", command=lambda: webbrowser.open(f"{BACKEND_URL}/admin"),
                  bg="white").pack(side="right")
        self.refresh()

    def set_lang(self, lang):
        self.lang = lang
        self.tag_label.config(text=STR[lang]["tag"])
        self.status.set(STR[lang]["hint"])
        self.refresh()

    def refresh(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        cat, q = self.category.get(), self.query.get()
        self.status.set("Load ho raha hai...")
        def work():
            apps = fetch_apps(cat, q)
            self.after(0, lambda: self.show(apps))
        threading.Thread(target=work, daemon=True).start()

    def show(self, apps):
        for w in self.list_frame.winfo_children():
            w.destroy()
        if not apps:
            tk.Label(self.list_frame, text=STR[self.lang]["empty"],
                     bg="white", wraplength=700, font=("Segoe UI", 12)).pack(fill="x", pady=10)
            self.status.set("No app found. Check the backend URL (after the live host is set)." if self.lang == "EN" else "Koi app nahi mili. Backend URL check karo (live host lagne ke baad).")
            return
        self.status.set(f"{len(apps)} app mile.")
        for app in apps:
            card = tk.Frame(self.list_frame, bg="white", bd=1, relief="solid")
            card.pack(fill="x", pady=5, padx=2)
            tk.Label(card, text=app["name"], font=("Segoe UI", 13, "bold"), bg="white").pack(anchor="w", padx=10, pady=(6, 0))
            tk.Label(card, text=f"{app['category']} · v{app.get('version', '')} · {app.get('size_mb', 0)} MB",
                     bg="white", fg="#40544c").pack(anchor="w", padx=10)
            if app.get("description"):
                tk.Label(card, text=app["description"], bg="white", wraplength=700, justify="left").pack(anchor="w", padx=10)
            tk.Button(card, text="⬇ Download", bg="#0a9d5c", fg="white",
                      command=lambda a=app: threading.Thread(target=download_file, args=(a, self.status), daemon=True).start()
                      ).pack(anchor="w", padx=10, pady=8)


if __name__ == "__main__":
    App().mainloop()
