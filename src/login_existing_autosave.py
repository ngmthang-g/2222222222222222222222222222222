"""S116 real F02 300ms Tk autosave for existing legacy row user/pass only.

Original checkbox/proxy/captcha fields are opaque. Never serialize or touch
them; only the exact five-field existing-record writer is permitted.
No game login, proxy, token, or launcher activity; closed Tk never writes.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable

from login_existing_account_edits import (
    ExistingAccountEdit, ExistingAccountEditError, update_existing_accounts,
)

AUTOSAVE_MS = 300  # original F02 _schedule_save debounce


class TLMExistingAccountAutosave:
    def __init__(
        self, account_rows, saved_records, *, settings_file: str | Path | None = None,
        show_error: Callable[[str, str], object] | None = None,
    ):
        self.account_rows = account_rows
        self._owner = account_rows.group_accounts
        self._settings_file = settings_file
        self._show_error = show_error
        self._closed = False
        self._after_id = None
        self.last_status = "EXISTING_ROWS_READY"
        self._stored = {
            i: (record.username, record.password)
            for i, record in enumerate(saved_records)
        }
        self._traces: list[tuple[object, str]] = []
        for index in self._stored:
            for variable in (account_rows.username_vars[index],
                             account_rows.password_vars[index]):
                token = variable.trace_add("write", self._on_edit)
                self._traces.append((variable, token))

    def _pending(self) -> tuple[ExistingAccountEdit, ...]:
        out = []
        for index, (old_user, old_pass) in self._stored.items():
            user = self.account_rows.username_vars[index].get()
            password = self.account_rows.password_vars[index].get()
            if (user, password) != (old_user, old_pass):
                out.append(ExistingAccountEdit(index, old_user, old_pass,
                                               user, password))
        return tuple(out)

    def _on_edit(self, *_args) -> None:
        if self._closed:
            return
        if self._after_id is not None:
            self._owner.after_cancel(self._after_id)
            self._after_id = None
        if self._pending():
            self._after_id = self._owner.after(AUTOSAVE_MS, self.flush)

    def flush(self) -> bool:
        if self._closed:
            return False
        if self._after_id is not None:
            self._owner.after_cancel(self._after_id)
            self._after_id = None
        changes = self._pending()
        if not changes:
            return True
        try:
            saved = update_existing_accounts(changes, self._settings_file)
        except (ExistingAccountEditError, OSError, RuntimeError):
            self.last_status = "BLOCKED_ACCOUNT_SAVE"
            if callable(self._show_error):
                self._show_error("Không thể lưu tài khoản",
                                 "Dữ liệu cũ hoặc thay đổi hiện tại chưa an toàn để ghi.")
            return False
        for edit in changes:
            self._stored[edit.row_index] = (edit.username, edit.password)
        self.last_status = saved
        return True

    def shutdown(self) -> bool:
        if self._closed:
            return True
        success = self.flush()  # original F02 independent save-on-destroy path
        self._closed = True
        for variable, token in self._traces:
            try:
                variable.trace_remove("write", token)
            except Exception:
                pass  # widget may have been destroyed externally
        self._traces.clear()
        return success
