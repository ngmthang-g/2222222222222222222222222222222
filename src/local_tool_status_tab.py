"""Local Info slot for the independent owner rebuild (not TLM licensing).

Only truthful locally implemented features are shown; this is not the
original InfoTab, server validation, license activator or real game status.
"""
from __future__ import annotations

from tkinter import ttk


class LocalToolStatusTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="TLMTool — bản xây dựng độc lập",
                  font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=10, pady=(10, 7))
        ttk.Label(self,
                  text="Không sử dụng cơ chế cấp/thu hồi bản quyền của TLM gốc.",
                  wraplength=410).pack(anchor="w", padx=10, pady=4)
        ttk.Label(self,
                  text="Các tab có module thật: ▶, Login, Party, Train và Train LSV (cấu hình).",
                  wraplength=410).pack(anchor="w", padx=10, pady=4)
        ttk.Label(self,
                  text="Chưa hoàn thiện điều khiển game, xác thực phiên game và nhiều tab khác.",
                  wraplength=410).pack(anchor="w", padx=10, pady=4)
        ttk.Label(self,
                  text="An toàn HWND/PID, giữ dữ liệu cấu hình và dừng worker vẫn được kiểm tra.",
                  wraplength=410).pack(anchor="w", padx=10, pady=4)
