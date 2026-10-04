# G01 — Party UI/control wiring flow

Original EXE PartyTab initialization
→ create Party ttk frame
→ initialize Party run/cancel/refresh/member/group state
→ initialize refs to Phó Bản / Train / Train LSV / Dồn vàng
→ build UI
→ load config
→ bind Destroy cleanup
→ start refresh lifecycle

Visible Party UI
→ Sau khi party
   → StringVar _after_party
   → Chờ / Train / Train LSV / Dồn vàng / Phó bản
   → trace write → save config

→ Cấu hình tổ đội
   → Danh sách acc sẵn sàng
   → _team_body
   → contents come from shared HWND/character refresh

→ Cấu hình nhóm
   → dynamic group cluster(s)
   → + Thêm nhóm → _add_group_cluster

Each cluster
→ leader label
→ six readonly account Comboboxes (B04: 2×3)
   → Button-1 → _open_dropdown
   → ComboboxSelected → _on_group_selected
   → leader labels refreshed
→ Rời nhóm → _leave_group
→ Xóa → _remove_group
→ Tạo nhóm → _run_single_cluster
→ renumber/update after structural changes

Bottom
→ Bắt đầu → _toggle_run

Shared window boundary
→ start_tab.get_windows
→ Party background refresh worker
→ utils.get_character_info / RoleName
→ bind/unbind window identity
→ Party _member_rows
→ Tk after applies UI changes

Permission boundary
→ permission_guard
→ has_permission / check_account_limit / has_permission_with_limit
→ set_children_state / _apply_group_permission
→ Combo keeps readonly semantics when enabled

Config boundary
→ read_settings / write_settings under Settings
→ party_after
→ party_groups / party_group1 for active team group section
→ JSON member lists
→ compatibility surfaces party_corps_groups / party_corps_group1
→ dormant compatibility surfaces party_follow / party_pick

Important negative ownership
→ PartyTab does not own DWM preview
→ PartyTab does not own layout sync
→ PartyTab does not own keyboard/mouse sync
→ those remain in Start/window subsystem

G01 correction
→ old Party module prose mentions Theo sau đội trưởng / Tự nhặt đồ
→ active PartyTab implementation has no matching BooleanVar/widget/method surface
→ actual matching controls/methods are in PhoBanTab
→ do not add these controls to reconstructed Party UI.
