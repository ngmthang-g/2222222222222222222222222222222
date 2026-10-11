"""S132 original-backed FarmTab composition, fail-closed source invariants.

Native Tk/real Windows HWND and disk integration lives in dedicated CI smoke.
These tests prevent silently claiming game/runtime features or regressing
verified S121/S123/S128–S131 public widget interfaces.
"""
import ast
import inspect
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from farm_train_composition import TkTrainComposition, TRAIN_SECTIONS
from farm_town_panel import TkFarmTownConfig
from farm_town_trade_panel import TkFarmTownTradeSettings
from farm_train_panel import TkFarmTrainSettings
from farm_buff_editor import TkFarmBuffEditor
from farm_saved_editor import FarmSavedCoordinatesEditor
from train_account_rows import TkTrainAccountRows
from farm_town_config import FarmTownSettingsStore
from farm_train_settings import FarmTrainSettingsStore
from farm_town_trade_settings import TownTradeStore
from farm_buff_settings import FarmBuffSettingsStore
from start_polling import WindowSnapshot

SRC=(ROOT/"src/farm_train_composition.py").read_text(encoding="utf-8")


class S132CompositionSourceTests(unittest.TestCase):
    def test_01_original_group_order_is_fixed(self):
        self.assertEqual(TRAIN_SECTIONS,(
            "Cấu hình Về thành","Cấu hình Train",
            "Cấu hình tọa độ lưu sẵn","Danh sách tài khoản"))

    def test_02_compose_real_s128_control(self):
        self.assertIn("TkFarmTownConfig(",SRC)
        self.assertIsNotNone(TkFarmTownConfig)

    def test_03_compose_s130_into_existing_hidden_lower(self):
        self.assertIn("self.town.lower",SRC)
        self.assertIn("TkFarmTownTradeSettings(",SRC)

    def test_04_compose_s129_after_town(self):
        self.assertLess(SRC.index("self.town = "),SRC.index("self.train = "))
        self.assertIn("TkFarmTrainSettings(",SRC)

    def test_05_compose_buff_under_train_group(self):
        self.assertIn("self.train.group",SRC)
        self.assertIn("TkFarmBuffEditor(",SRC)

    def test_06_coords_only_created_inside_permitted(self):
        f=inspect.getsource(TkTrainComposition._make_sensitive)
        self.assertIn("not self._authorized()",f)
        self.assertIn("FarmSavedCoordinatesEditor(",f)

    def test_07_account_owner_requires_real_H11_editor(self):
        self.assertIn("TkTrainAccountRows(",SRC)
        self.assertIn("self.accounts_host,editor",SRC)

    def test_08_account_row_source_5000_milliseconds(self):
        self.assertIn("interval_ms=TRAIN_ACCOUNT_REFRESH_MS",SRC)

    def test_09_explicit_shared_farm_file_mandatory(self):
        self.assertIn("EXPLICIT_SHARED_FARM_SETTINGS_REQUIRED",SRC)

    def test_10_source_keys_all_same_settings_file(self):
        for name in ("FarmTownSettingsStore(self.settings_file)",
                     "TownTradeStore(self.settings_file)",
                     "FarmTrainSettingsStore(self.settings_file)",
                     "FarmBuffSettingsStore(self.settings_file)",
                     "FarmCoordinatesStore(self.settings_file)"):
            self.assertIn(name,SRC)

    def test_11_all_four_existing_commit_callbacks_rebased(self):
        self.assertIn("for panel in (self.town, self.trade, self.train, self.buffs)",SRC)
        self.assertIn("def sync_from_disk(",SRC)

    def test_12_rebase_is_read_only(self):
        f=inspect.getsource(TkTrainComposition.sync_from_disk)
        self.assertIn("panel.store.load()",f)
        self.assertNotIn("panel.store.save(",f)

    def test_13_actual_saved_med_and_heal_refresh(self):
        self.assertIn("self.trade.refresh_destinations()",SRC)
        self.assertIn("self.train.refresh_heal_destinations()",SRC)

    def test_14_disallow_unsigned_coordinate_edits(self):
        f=inspect.getsource(TkTrainComposition._bind_coordinate_actions)
        self.assertIn("not self._authorized()",f)
        for action in ("commit_row","delete_row","apply_row_to_all"):
            self.assertIn(action,f)

    def test_15_permission_revoke_tears_down_sensitive(self):
        f=inspect.getsource(TkTrainComposition.reapply_permissions)
        self.assertIn("self._teardown_sensitive()",f)

    def test_16_shutdown_calls_actual_native_owner_shutdown(self):
        f=inspect.getsource(TkTrainComposition._teardown_sensitive)
        self.assertIn("self.accounts.shutdown()",f)
        self.assertIn("self.coords.destroy()",f)

    def test_17_no_fake_start_or_live_Farm_buttons(self):
        for forbidden in ("text=\"Bắt đầu\"", "command=self._toggle_farm",
                          "command=self._sell_all", "command=self._farm_all"):
            self.assertNotIn(forbidden,SRC)

    def test_18_no_playing_game_input_apis(self):
        for bad in ("ReadProcessMemory(", "WriteProcessMemory(",
                    "PostMessage(", "SendInput(", "SendMessage(",
                    "RequestSellItem(", "click_at(", "inject_into_pid("):
            self.assertNotIn(bad,SRC)

    def test_19_no_proxy_evasion_or_fabricated_auth(self):
        for bad in ("ProxyTab(", "VerifiedClaims(", ".receive_token(",
                    "allow_account=lambda", "fake_signed", "bypass_info"):
            self.assertNotIn(bad,SRC)

    def test_20_no_production_tab_builder_registration(self):
        self.assertNotIn('SOURCE_BACKED_KEYS.add("farm_tab")',SRC)
        self.assertNotIn("source_backed_tab_builders(",SRC)

    def test_21_disabled_user_cannot_force_refresh(self):
        self.assertIn("if not self.reapply_permissions()",SRC)
        self.assertIn("self.accounts._start_refresh()",SRC)

    def test_22_trusted_snapshot_type_boundary(self):
        self.assertIn("WindowSnapshot",inspect.getsource(TkTrainComposition.apply_trusted_window_snapshot))

    def test_23_prior_modules_have_original_methods(self):
        for cls, method in (
            (TkFarmTownConfig,"toggle_lower_body"),
            (TkFarmTownTradeSettings,"refresh_destinations"),
            (TkFarmTrainSettings,"refresh_heal_destinations"),
            (TkFarmBuffEditor,"refresh_from_disk"),
            (FarmSavedCoordinatesEditor,"register_account_combos"),
            (TkTrainAccountRows,"apply_snapshot"),
        ):
            self.assertTrue(callable(getattr(cls,method,None)))

    def test_24_three_town_stores_and_buff_distinct(self):
        self.assertEqual(len({
            FarmTownSettingsStore,TownTradeStore,
            FarmTrainSettingsStore,FarmBuffSettingsStore}),4)

    def test_25_no_new_game_memory_reader_parameter(self):
        params=inspect.signature(TkTrainComposition.__init__).parameters
        self.assertNotIn("memory_reader",params)
        self.assertNotIn("game_packet_sender",params)

    def test_26_no_invented_geometry(self):
        for bad in ("place(x=", "place(y=", "x=133", "y=420",
                    "orig_game_pixel_coordinates"):
            self.assertNotIn(bad,SRC)

    def test_27_external_only_real_account_source(self):
        self.assertIn("allow_account=self.allow_account",SRC)
        self.assertNotIn("allow_account=lambda _: True",SRC)

    def test_28_source_ast_compiles(self):
        ast.parse(SRC)
        compile(SRC,"farm_train_composition.py","exec")


if __name__=="__main__":
    unittest.main()
