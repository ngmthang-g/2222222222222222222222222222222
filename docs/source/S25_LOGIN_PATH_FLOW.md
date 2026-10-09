# S25 — Real Login game directory selection: F01 + F04 + E05

```text
TEST-only independent Info authorization:
  TLMMainApp -> lazy Login builder -> TLMLoginPathTab
  [Login F01 "Cấu hình game" game section]
     real tk.Button "Chọn thư mục game"
       -> tkinter.filedialog.askdirectory("Chọn thư mục chứa Thần Long Mobile")
       -> resolve_game_dir(selected)
            [selected/Thần Long__Mobile.exe] OR
            [selected/Game/] OR
            [selected is subfolder, parent has EXE] OR
            [one child scan, 'game' name preferred]
       -> failure: original title "Thư mục game không hợp lệ", no persisted change
       -> success: [Settings] game_dir -> E05 atomic write with dated backup
          -> actual Tk conditional path text
  restart -> read [Settings] game_dir -> confirm real EXE still exists -> show status
  revoke -> hide Login via E03/Info gate
  root <Destroy> -> Login owner shutdown; invalidates cached path
```

**Source:** `src/login_path.py` (pure F04 typed resolver + GameDirectoryStore), `src/login_tab.py` (real blue Tk chooser, F01 game LabelFrame partial layout). **No separate game launch, captcha, accounts, scheduling, Proxy or standalone product entitlement implementation.**

**F04 exact:** `Thần Long  Mobile.exe` contains TWO adjacent spaces between Long and Mobile; example `D:\\ThanLongMobile_PC\\Game` is informational only. Picker `askdirectory`, `Settings.game_dir`. Immediate write timing and child-order details not recovered from original; S25 deterministically chooses name priority and write-on-success.

**Native proof:** [Windows S25 37900241256](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37900241256) SUCCESS; 331/331 combined unit tests; actual Windows Tk blue button real command invoked, test-local filesystem game executable filename & INI persisted/reloaded, invalid/cancel safe, authorization revoke and root destroy; S24/S23/S22/S21/S20/S10 native regressions PASS. [Evidence artifact 11602351174](https://github.com/ngmthang-g/2222222222222222222222222222222/actions/runs/37900241256/artifacts/11602351174).

**Not proven:** original full Login geometry/pixel parity, real game process, genuine Info verification, F05 suspend+inject+resume, F06 login clicks, product EXE. `Mở game` intentionally NOT represented as a nonworking button.
