# F04 — Game path flow

User clicks "Chọn thư mục game"
→ tkinter.filedialog.askdirectory
→ selected directory

selected directory
→ trim trailing slash/backslash
→ _resolve_game_dir(selected)
    1. selected contains "Thần Long  Mobile.exe"
       → resolved = selected
    2. selected/Game contains executable
       → resolved = selected/Game
    3. selected is a child inside Game
       → step upward to parent containing executable
    4. otherwise scan one child level
       → prioritize child names containing "game"
       → choose child containing executable
    5. otherwise
       → unresolved + note

unresolved
→ _show_game_dir_status(error)
→ messagebox.showerror("Thư mục game không hợp lệ", selected + required executable + example path)
→ no launchable path

resolved
→ update _game_dir
→ _show_game_dir_status("✅ Đã chọn game thành công: " + resolved + optional resolver note)
→ enable path-dependent profile controls
→ Login config lifecycle persists game_dir

Later launch/login request
→ require non-empty _game_dir
→ _get_exe_path
→ usable canonical executable path
→ launch-facing code receives exe_path
→ profile launch also receives profile_idx 1..5

Important boundaries:
- folder resolver/path persistence = F04
- process creation / cwd / suspend+inject = F05
- account login click/input = F06

Explicit unknowns:
- exact source-level _get_exe_path revalidation branch sequence
- exact write-to-disk instant immediately after a successful directory selection
- exact filesystem predicate implementation
- exact cwd derivation
