"""S05 native Windows Tk smoke & reproducible screenshot *attempt*.

Run on a Windows GitHub Actions VM, not the production TLMTool entrypoint.
No authentication, game commands, network requests or unknown EXE execution.
Outputs real widget metrics, baseline comparison and optional PNG to artifacts.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

REPORT_DIR = ROOT / "artifacts" / "s05"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = REPORT_DIR / "windows_tk_report.json"
PNG_PATH = REPORT_DIR / "info_only_native_tk.png"
EXPECTED_CLIENT_WIDTH = 450
B12_REFERENCE_CLIENT = (450, 1000)
B12_REFERENCE_RASTER = (452, 1032)


def metric(widget):
    return {
        "x": int(widget.winfo_rootx()),
        "y": int(widget.winfo_rooty()),
        "width": int(widget.winfo_width()),
        "height": int(widget.winfo_height()),
        "mapped": bool(widget.winfo_ismapped()),
    }


def record(value):
    REPORT_PATH.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    print("S05_NATIVE_TK_REPORT=" + str(REPORT_PATH))
    print("S05_NATIVE_TK_STATUS=" + value["status"])
    for key in ("desktop", "geometry", "tab_count", "visible_tabs",
                "selected_key", "image_capture", "baseline_comparison"):
        if key in value:
            print("S05_" + key.upper() + "=" + json.dumps(value[key], ensure_ascii=False))


def main():
    result = {
        "task": "S05",
        "os_name": os.name,
        "mode": "isolated readonly InfoTab Tk smoke; no product startup",
        "status": "NOT_RUN",
        "original_b12": {
            "client_450x1000": list(B12_REFERENCE_CLIENT),
            "full_raster_452x1032": list(B12_REFERENCE_RASTER),
            "original_info_tab_index": 10,
            "source": "docs/tasks/B12.md and docs/ui/B12_INFO_GEOMETRY.tsv",
        },
        "image_capture": "NOT_RUN",
        "pixel_parity": "NOT_VERIFIED_ORIGINAL_RASTER_UNAVAILABLE",
    }
    root = None
    binding = None
    try:
        import tkinter as tk
        from info_binding import create_info_only_shell
        from shell import INFO_KEY

        try:
            root = tk.Tk()
        except tk.TclError as err:
            result["status"] = "SKIPPED_NO_NATIVE_TK_DISPLAY"
            result["reason"] = str(err)
            record(result)
            return 0

        binding = create_info_only_shell(root)
        binding.app.position_window_top_right()
        root.update_idletasks()
        root.update()

        info_frame = binding.app._tab_frames[INFO_KEY]
        notebook = binding.app.notebook
        visible = [
            key for key, frame in binding.app._tab_frames.items()
            if notebook.tab(frame, "state") == "normal"
        ]
        selected_id = notebook.select()
        selected_key = binding.app._tab_keys.get(str(selected_id))
        widget_rows = {key: metric(widget) for key, widget in binding.view._values.items()}
        status_text = binding.view._status.cget("text")

        result.update({
            "desktop": {
                "width": int(root.winfo_screenwidth()),
                "height": int(root.winfo_screenheight()),
            },
            "geometry": {
                "tk_geometry": root.geometry(),
                "client_width": int(root.winfo_width()),
                "client_height": int(root.winfo_height()),
                "frame": metric(info_frame),
                "notebook": metric(notebook),
                "info_heading_widgets": widget_rows,
                "status_label": metric(binding.view._status),
            },
            "tab_count": len(notebook.tabs()),
            "visible_tabs": visible,
            "selected_key": selected_key,
            "status_text": status_text,
            "license_value": binding.view._values["license_type"].cget("text"),
            "original_production_tab_visibility": "NOT_RECONSTRUCTED",
        })
        width = int(root.winfo_width())
        height = int(root.winfo_height())
        height_model = max(1, int(root.winfo_screenheight()) - 80)
        result["baseline_comparison"] = {
            "actual_client": [width, height],
            "b12_reference_client": list(B12_REFERENCE_CLIENT),
            "b12_client_exact_match": width == 450 and height == 1000,
            "e02_top_right_model_height": height_model,
            "e02_geometry_model_pass": width == 450 and height == height_model,
            "b12_full_raster_comparison": "NOT_VERIFIED_NO_ORIGINAL_RASTER_AND_THEME_MATCH",
            "b12_info_tab_x_position": "MISMATCH_EXPECTED_INFO_ONLY_GATED_STARTUP",
            "exact_pixel_parity": "NOT_RUN",
        }
        assert len(notebook.tabs()) == 15, "Lost an original potential tab slot"
        assert visible == [INFO_KEY], "Unverified feature or dev tab was exposed"
        assert selected_key == INFO_KEY, "Info fallback not selected"
        assert status_text == "Chưa xác minh dữ liệu máy chủ", "Info status not fail-closed"
        assert result["license_value"] == "Chưa xác minh", "License text misrepresented"
        assert width == EXPECTED_CLIENT_WIDTH, "Wrong client width"
        assert height == height_model, "Position geometry does not follow E02 model"

        # A GUI run and PNG image are independent. A screenshot is useful evidence
        # but screenshot failure must not be reported as pixel parity success.
        try:
            from PIL import ImageGrab
            root.lift()
            root.update_idletasks()
            root.update()
            time.sleep(0.3)
            img = ImageGrab.grab(bbox=(
                root.winfo_rootx(), root.winfo_rooty(),
                root.winfo_rootx() + width, root.winfo_rooty() + height,
            ))
            if img.size != (width, height):
                raise ValueError("capture dimensions unexpected " + repr(img.size))
            img.save(PNG_PATH)
            result["image_capture"] = "CAPTURED_CLIENT_BBOX_NOT_ORIGINAL_MATCH"
            result["image_path"] = str(PNG_PATH)
            result["image_size"] = list(img.size)
        except (ImportError, Exception) as err:
            result["image_capture"] = "UNAVAILABLE"
            result["image_capture_reason"] = type(err).__name__ + ": " + str(err)[:500]

        result["status"] = "PASS_NATIVE_TK_INFO_ONLY_SMOKE"
        return 0

    except Exception as err:
        result["status"] = "FAIL_NATIVE_TK_SMOKE"
        result["error"] = type(err).__name__ + ": " + str(err)
        result["traceback"] = traceback.format_exc(limit=8)
        return 1
    finally:
        if root is not None:
            try:
                root.destroy()
            except Exception as err:
                result["destroy_error"] = type(err).__name__ + ": " + str(err)
                result["status"] = "FAIL_NATIVE_TK_SMOKE"
        if binding is not None:
            result["binding_closed"] = binding._closed
            if not binding._closed:
                result["status"] = "FAIL_NATIVE_TK_SMOKE"
        record(result)


if __name__ == "__main__":
    raise SystemExit(main())
