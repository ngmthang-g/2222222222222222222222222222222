# E02 — Root/window construction flow

```text
Tk root
→ title("TLMTool")
→ transient geometry("250x20")
→ attributes("-topmost", True)
→ resolve frozen icon.ico via sys.frozen/_MEIPASS
→ iconbitmap(...)
→ withdraw()

global font
→ ("Segoe UI", 9)
→ option_add("*Font", default_font)

ttk.Notebook(root)
→ pack(fill=tk.BOTH, expand=<effective true>, padx=5, pady=5)
→ configure TNotebook.Tab padding
→ configure TNotebook tabmargins
→ build tab frames

position_window_top_right()
→ update_idletasks()
→ winfo_screenwidth()
→ winfo_screenheight()
→ constants 80 / 450 / 10
→ HIGH-CONFIDENCE model:
     w = 450
     h = screen_height - 80
     x = max(0, screen_width - w - 10)
     y = 0
→ geometry(...)
→ deiconify()

Gate-B observed result in supplied environment:
→ client 450 × 1000
→ outer raster 452 × 1032
```

## Evidence boundaries

- `250x20` is startup/transient, not final UI geometry.
- `350x450+1621+0` exists in the compiled block but is quarantined as stale/example/unknown-flow because it conflicts with both the active constants and 12/12 screenshots.
- Exact arithmetic operators in `position_window_top_right` are not directly source-visible from the Nuitka constant table; the formula above is a high-confidence reconstruction model.
- Exact `TNotebook.Tab` padding and `TNotebook` tabmargin list values remain unknown.
- No main-shell `resizable`, `minsize` or `maxsize` source policy was recovered.
