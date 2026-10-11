"""S127 real Windows Tk H12 colored Farm labels; TEST-OWNED HWND only."""
from __future__ import annotations
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "artifacts" / "s127"
OUT.mkdir(parents=True, exist_ok=True)


def run():
    q = {"status": "NOT_RUN", "real_game": False, "signed_info": False,
         "proxy": "EXCLUDED"}
    root = None
    try:
        if os.name != "nt":
            raise RuntimeError("WINDOWS_TK_REQUIRED")
        import tkinter as tk
        from permission_guard import PermissionGuard, VerifiedClaims
        from farm_saved_editor import FarmSavedCoordinatesEditor
        from train_saved_coordinates import FarmCoordinate, FarmCoordinatesStore
        from train_account_rows import TkTrainAccountRows
        from start_windows import NativeWin32Backend, GameWindow
        from start_polling import WindowSnapshot

        with tempfile.TemporaryDirectory(prefix="S127_NATIVE_STATE_") as td:
            path = Path(td) / "settings.ini"
            path.write_bytes(
                b"[Settings]\r\ncredentials = untouched\r\n[Farm]\r\nkeep = yes\r\n")
            store = FarmCoordinatesStore(path)
            store.save([FarmCoordinate("TrainA", 26, "1", "2")])
            root = tk.Tk()
            root.geometry("860x530+0+0")
            editor = FarmSavedCoordinatesEditor(root, store=store)
            editor.pack()
            root.update()
            native = NativeWin32Backend()
            hwnd = int(root.winfo_id())
            pid = native.process_id(hwnd)
            win = GameWindow(hwnd, pid, "TEST-only", "TkTopLevel", "NOT_GAME.exe")
            q["actual_native_test_hwnd_pid"] = (
                hwnd > 0 and pid == os.getpid()
                and native.is_window(hwnd) and native.is_visible(hwnd))
            gate = PermissionGuard()
            owner = TkTrainAccountRows(
                root, editor, permission_guard=gate, running_count=lambda: 1,
                allow_account=lambda _: True)
            owner.apply_snapshot(WindowSnapshot(revision=1, windows=(win,), valid=True))
            row = owner._rows[hwnd]
            q["observed_initial"] = {
                "dot": str(row["state_dot"].cget("text")),
                "text": str(row["state_label"].cget("text")),
                "fg": str(row["state_label"].cget("foreground")),
                "dot_fg": str(row["state_dot"].cget("foreground")),
                "generation": row["passive_state"].generation}
            q["initial_original_dot_and_state_gray"] = (
                row["state_dot"].cget("text") == "⬤"
                and row["state_label"].cget("text") == "Đã dừng"
                and row["state_label"].cget("foreground") == "#555555"
                and row["state_dot"].cget("foreground") == "#555555"
                and row["passive_state"].generation == -1)
            q["unsigned_auth_blocks_game_state"] = (
                not owner.apply_confirmed_state(hwnd, pid, "Đang train", 1)
                and row["state_label"].cget("text") == "Đã dừng")
            gate.receive_token(
                "CI_ONLY_STUB_NEVER_PRODUCT_SIGNED",
                lambda _: VerifiedClaims(frozenset({"farm_tab"}), "active", 2))
            owner.reapply_permissions()
            q["permission_does_not_auto_start_farm"] = (
                not row["tracker"].active
                and row["state_label"].cget("text") == "Đã dừng")
            green_applied = owner.apply_confirmed_state(hwnd, pid, "Đang train", 7)
            q["observed_green"] = {
                "applied": green_applied,
                "allowed": owner._allowed(win),
                "row_pid": row["pid"],
                "text": str(row["state_label"].cget("text")),
                "fg": str(row["state_label"].cget("foreground")),
                "dot_fg": str(row["state_dot"].cget("foreground")),
                "generation": row["passive_state"].generation}
            q["future_confirmed_state_renders_actual_tk_green"] = (
                green_applied
                and row["state_label"].cget("text") == "Đang train"
                and row["state_label"].cget("foreground") == "#2e7d32"
                and row["state_dot"].cget("foreground") == "#2e7d32")
            q["stale_generation_is_not_applied"] = (
                not owner.apply_confirmed_state(hwnd, pid, "Mất kết nối", 6)
                and row["state_label"].cget("text") == "Đang train")
            q["wrong_pid_is_not_applied"] = (
                not owner.apply_confirmed_state(hwnd, pid + 1, "Mất kết nối", 8)
                and row["state_label"].cget("text") == "Đang train")
            blue_a = owner.apply_confirmed_state(hwnd, pid, "Về bán đồ", 7)
            blue_b = owner.apply_confirmed_state(hwnd, pid, "Bán đồ", 7)
            q["observed_blue"] = {
                "a": blue_a, "b": blue_b,
                "state": str(row["state_label"].cget("text")),
                "foreground": str(row["state_label"].cget("foreground")),
                "generation": row["passive_state"].generation}
            q["same_generation_genuine_tk_transition_blue"] = (
                blue_a and blue_b
                and row["state_label"].cget("foreground") == "#1565c0")
            unknown_ok = owner.apply_confirmed_state(hwnd, pid, "Đang đợi", 8)
            q["observed_unknown"] = {
                "applied": unknown_ok,
                "state": str(row["state_label"].cget("text")),
                "foreground": str(row["state_label"].cget("foreground")),
                "generation": row["passive_state"].generation}
            q["unknown_original_dynamic_label_is_gray"] = (
                unknown_ok and row["state_label"].cget("foreground") == "#555555")
            gate.clear()
            owner.reapply_permissions()
            q["observed_revoked"] = {
                "text": str(row["state_label"].cget("text")),
                "fg": str(row["state_label"].cget("foreground")),
                "dot_fg": str(row["state_dot"].cget("foreground"))}
            q["info_revoke_returns_safe_initial_state"] = (
                row["state_label"].cget("text") == "Đã dừng"
                and row["state_dot"].cget("foreground") == "#555555"
                and not owner.apply_confirmed_state(hwnd, pid, "Đang train", 9))
            owner.apply_snapshot(WindowSnapshot(revision=2, windows=(), valid=True))
            q["closed_native_hwnd_row_removed"] = (
                not owner._rows and editor.account_bindings.active_count() == 0)
            owner.shutdown()
            owner.container.destroy()
            editor.destroy()
            root.destroy()
            root = None
            q["credentials_preserved"] = (
                b"credentials = untouched\r\n" in path.read_bytes()
                and b"keep = yes\r\n" in path.read_bytes())
        checks = [k for k, v in q.items()
                  if type(v) is bool and k not in ("real_game", "signed_info")]
        if not all(q[k] for k in checks):
            raise RuntimeError("S127_NATIVE_STATE_ASSERTION_FAILED")
        q["status"] = "PASS_NATIVE_S127_TK_FARM_STATE_COLOR_NO_GAME"
    except Exception as exc:
        q["status"] = "FAIL_NATIVE_S127"
        q["error_type"] = type(exc).__name__
        q["error_detail"] = str(exc)[:180]
    finally:
        if root is not None:
            try:
                root.destroy()
            except Exception:
                pass
        (OUT / "native_h12_state.json").write_text(
            json.dumps(q, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        for key, value in q.items():
            print("S127_" + key.upper() + "=" +
                  json.dumps(value, ensure_ascii=True))
    return 0 if q["status"].startswith("PASS_NATIVE_S127_") else 1


if __name__ == "__main__":
    raise SystemExit(run())
