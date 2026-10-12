"""S200 independent read-only Party/Train candidate status UI.

Real original-TLM derived memory observations can be displayed as
DIAGNOSTIC CANDIDATES (clearly marked CHUA XAC MINH), not Party-ready
accounts, character login, or an enabled Farm worker. Existing original
PartyReadyList and TrainAccountRows semantics remain intact.
"""
from __future__ import annotations

from tkinter import ttk

from independent_character_diagnostic_observer import (
    IndependentCharacterDiagnosticObserver,
    SUCCESS_DIAGNOSTIC,
)
from party_ready_authorized_tab import AuthorizedPartyReadyTab
from farm_train_composition import TkTrainComposition

DIAGNOSTIC_UI_REFRESH_MS = 2500
MAX_VISIBLE_DIAGNOSTIC_ROWS = 8


class TkOriginalCandidatePanel(ttk.LabelFrame):
    """Tk only reads observer's immutable cache; never opens game memory."""

    def __init__(self, parent, observer: IndependentCharacterDiagnosticObserver):
        if not isinstance(observer, IndependentCharacterDiagnosticObserver):
            raise ValueError("REAL_ORIGINAL_READONLY_OBSERVER_REQUIRED")
        super().__init__(parent, text="Quan sát nhân vật (chưa xác minh)")
        self._observer = observer
        self._active = False
        self._closed = False
        self._after = None
        self.status = ttk.Label(
            self, text="Đang đợi dữ liệu game thật...", wraplength=600,
            justify="left")
        self.status.pack(fill="x", padx=5, pady=4)
        self.bind("<Destroy>", self._on_destroy, add="+")

    def _render(self):
        batch = self._observer.read_batch()
        if not batch.members:
            self.status.configure(text=(
                f"Chưa có thông tin nhân vật: {batch.status}. "
                "Không xác minh được online/HP từ cửa sổ Windows đơn thuần."))
            return
        lines = [
            "Dữ liệu ứng viên đọc từ bộ nhớ; CHƯA XÁC MINH trên game thật.",
        ]
        for row in batch.members[:MAX_VISIBLE_DIAGNOSTIC_ROWS]:
            if (row.code == SUCCESS_DIAGNOSTIC
                    and row.role_name_candidate is not None):
                hp = (str(row.hp_percent_candidate) + "%"
                      if row.hp_percent_candidate is not None else "?")
                lines.append(
                    f"PID {row.pid}: {row.role_name_candidate} "
                    f"| HP ứng viên {hp} "
                    f"| MapID ứng viên {row.map_id_candidate}")
            else:
                lines.append(f"PID {row.pid}: {row.code}")
        if len(batch.members) > MAX_VISIBLE_DIAGNOSTIC_ROWS:
            lines.append(
                f"... còn {len(batch.members)-MAX_VISIBLE_DIAGNOSTIC_ROWS} "
                "cửa sổ, không phải giới hạn tài khoản.")
        self.status.configure(text="\n".join(lines))

    def _tick(self):
        self._after = None
        if not self._active or self._closed:
            return
        self._render()
        self._after = self.after(DIAGNOSTIC_UI_REFRESH_MS, self._tick)

    def start(self):
        if self._closed or self._active:
            return
        self._active = True
        self._tick()

    def stop(self):
        self._active = False
        if self._after is not None:
            after, self._after = self._after, None
            try:
                self.after_cancel(after)
            except Exception:
                pass

    def shutdown(self):
        if self._closed:
            return
        self.stop()
        self._closed = True

    def _on_destroy(self, event):
        if event.widget is self:
            self.shutdown()


class TkIndependentPartyCandidateTab(AuthorizedPartyReadyTab):
    """G02 verified roster unchanged; diagnostic candidates separate."""

    def __init__(self, parent, *, observer, **kwargs):
        super().__init__(parent, **kwargs)
        self._candidate_panel = TkOriginalCandidatePanel(self, observer)
        self._candidate_panel.pack(fill="x", padx=4, pady=(0, 4))

    def _start_refresh(self):
        super()._start_refresh()
        panel = getattr(self, "_candidate_panel", None)
        if panel is not None:
            panel.start()

    def _stop_refresh(self):
        panel = getattr(self, "_candidate_panel", None)
        if panel is not None:
            panel.stop()
        super()._stop_refresh()

    def shutdown(self):
        panel = getattr(self, "_candidate_panel", None)
        if panel is not None:
            panel.shutdown()
        super().shutdown()


class TkIndependentTrainCandidateTab(TkTrainComposition):
    """H12 genuine HWND/PID rows unchanged; candidate observation separate."""

    def __init__(self, parent, *, observer, **kwargs):
        super().__init__(parent, **kwargs)
        self._candidate_panel = TkOriginalCandidatePanel(
            self.accounts_section, observer)
        self._candidate_panel.pack(fill="x", padx=3, pady=3)

    def _start_refresh(self):
        ok = super()._start_refresh()
        panel = getattr(self, "_candidate_panel", None)
        if panel is not None:
            panel.start()
        return ok

    def _stop_refresh(self):
        panel = getattr(self, "_candidate_panel", None)
        if panel is not None:
            panel.stop()
        return super()._stop_refresh()

    def shutdown(self):
        panel = getattr(self, "_candidate_panel", None)
        if panel is not None:
            panel.shutdown()
        return super().shutdown()
