"""S169 source-backed B06/I01/I06 Train LSV top-configuration contracts."""
from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from train_lsv_top_settings import (
    LSV_KEEP_RADIOS, LSV_DISCARD_PRESETS, TrainLsvTopConfig,
    TrainLsvTopStore, TrainLsvSettingsError,
)
from TLMToolIndependent import make_independent_builders
from start_polling import StartWindowProducer
from local_feature_policy import LocalFeaturePolicy


class S169LsvTopStore(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "settings.ini"
        self.store = TrainLsvTopStore(self.path)

    def test_01_missing_file_is_safe_no_write(self):
        snapshot = self.store.load()
        self.assertEqual(snapshot.value, TrainLsvTopConfig())
        self.assertFalse(self.path.exists())

    def test_02_original_section_and_exact_4_allowed_keys(self):
        self.assertEqual(tuple(LSV_KEEP_RADIOS), (
            ("Không", "none"), ("Chỉ vũ khí", "weapons"), ("Tất cả", "all")))
        self.assertEqual(TrainLsvTopConfig().discard_preset_keys(), ())
        self.assertEqual(TrainLsvTopConfig(pickup_mode="weapons").discard_preset_keys(),
                         ("discard_nonweapon",))
        self.assertEqual(TrainLsvTopConfig(pickup_mode="none").discard_preset_keys(),
                         ("discard_weapons", "discard_nonweapon"))

    def test_03_change_only_one_key_no_invented_others(self):
        self.path.write_bytes(
            b"[Settings]\r\nsecret = keep\r\n[Farm]\r\nrespawn = True\r\n"
            b"[TrainLSV]\r\nbuff_0 = 1|1|0|5\r\n"
            b"[Party]\r\nmode = abc\r\n")
        before=self.store.load()
        current=self.store.save_change("pickup_mode","weapons",
                                       expected_bytes=before.file_bytes)
        result=self.path.read_bytes()
        self.assertIn(b"[TrainLSV]\r\nbuff_0 = 1|1|0|5\r\npickup_mode = weapons\r\n",result)
        self.assertIn(b"secret = keep\r\n",result)
        self.assertIn(b"[Farm]\r\nrespawn = True\r\n",result)
        self.assertIn(b"[Party]\r\nmode = abc\r\n",result)
        self.assertNotIn(b"auto_reconnect = ",result)
        self.assertEqual(current.value.pickup_mode,"weapons")

    def test_04_save_boolean_in_existing_section_preserves_line_style(self):
        self.path.write_bytes(b"[TrainLSV]\n  respawn : false\ncoord_1 = Map|10014|2|3\n")
        snap=self.store.load()
        result=self.store.save_change("respawn",True,expected_bytes=snap.file_bytes)
        self.assertIn(b"  respawn : True\n",result.file_bytes)
        self.assertIn(b"coord_1 = Map|10014|2|3\n",result.file_bytes)
        self.assertEqual(self.store.load().value.respawn,True)

    def test_05_create_section_without_rewriting_unterminated_secret(self):
        self.path.write_bytes(b"[Login]\npassword = PRESERVE")
        snap=self.store.load()
        self.store.save_change("trist",True,expected_bytes=snap.file_bytes)
        self.assertEqual(self.path.read_bytes(),
             b"[Login]\npassword = PRESERVE\n[TrainLSV]\ntrist = True\n")

    def test_06_stale_load_never_overwrites_user_external_edit(self):
        self.path.write_text("[TrainLSV]\nrespawn = False\n",encoding="utf-8")
        old=self.store.load()
        self.path.write_text("[TrainLSV]\nrespawn = True\n",encoding="utf-8")
        with self.assertRaisesRegex(TrainLsvSettingsError,"STALE_LSV_SETTINGS"):
            self.store.save_change("pickup_mode","none",expected_bytes=old.file_bytes)
        self.assertNotIn("pickup_mode",self.path.read_text("utf-8"))

    def test_07_duplicate_trainlsv_section_denied(self):
        self.path.write_text("[TrainLSV]\nrespawn = True\n[trainlsv]\ntrist = False\n")
        with self.assertRaisesRegex(TrainLsvSettingsError,"DUPLICATE_TRAINLSV_SECTION"):
            self.store.load()

    def test_08_duplicate_editable_key_denied(self):
        self.path.write_text("[TrainLSV]\nrespawn = True\nRESPAWN = False\n")
        with self.assertRaisesRegex(TrainLsvSettingsError,"AMBIGUOUS_LSV_SETTING"):
            self.store.load()

    def test_09_bad_boolean_does_not_get_clobbered(self):
        self.path.write_text("[TrainLSV]\nrespawn = perhaps\n")
        with self.assertRaisesRegex(TrainLsvSettingsError,"INVALID_LSV_BOOLEAN"):
            self.store.load()

    def test_10_unknown_pickup_denied_instead_of_fake_mode(self):
        self.path.write_text("[TrainLSV]\npickup_mode = unicorn\n")
        with self.assertRaisesRegex(TrainLsvSettingsError,"UNKNOWN_LSV_PICKUP_MODE"):
            self.store.load()

    def test_11_other_trainlsv_keys_preserved_when_updating(self):
        raw=b"[TrainLSV]\r\nheal_map = unknown_coords\r\nacc_character_train = custom\r\n"
        self.path.write_bytes(raw)
        snap=self.store.load()
        self.store.save_change("auto_reconnect",False,expected_bytes=snap.file_bytes)
        self.assertTrue(self.path.read_bytes().startswith(raw))

    def test_12_invalid_action_key_type_and_value_denied(self):
        snap=self.store.load()
        for key,value in (("heal_map","anything"),("buff_0","x"),
                          ("pickup_mode","other"),("respawn",1),
                          ("trist","false"),(1,True)):
            with self.subTest(key=key,value=value),self.assertRaises(TrainLsvSettingsError):
                self.store.save_change(key,value,expected_bytes=snap.file_bytes)
        self.assertFalse(self.path.exists())

    def test_13_encoding_and_multiline_malformed_denied(self):
        for raw in (b"\xef\xbb\xbf[TrainLSV]\nrespawn = True\n",
                    b"[TrainLSV]\ntrist = False\n continuation\n",
                    b"[TrainLSV]\npickup_mode just-all\n"):
            with self.subTest(raw=raw):
                self.path.write_bytes(raw)
                with self.assertRaises(TrainLsvSettingsError):
                    self.store.load()

    def test_14_config_is_data_only(self):
        cfg=TrainLsvTopConfig().change("auto_reconnect",True)
        self.assertTrue(cfg.auto_reconnect)
        self.assertEqual(cfg.pickup_mode,"all")
        for bad in (("trist",None),("pickup_mode",False)):
            with self.assertRaises(TrainLsvSettingsError):
                cfg.change(*bad)

    def test_15_backup_created_without_disclosing_secrets(self):
        self.path.write_bytes(b"[TrainLSV]\ntrist = False\n[Login]\nsecret = 123\n")
        snap=self.store.load()
        self.store.save_change("trist",True,expected_bytes=snap.file_bytes)
        backups=tuple(self.path.parent.glob("settings.*.ini"))
        self.assertEqual(len(backups),1)
        self.assertIn(b"secret = 123\n",backups[0].read_bytes())

    def test_16_independent_app_includes_only_real_lsv_tab(self):
        b=make_independent_builders(self.path,StartWindowProducer())
        self.assertIn("trainlsv_tab",b)
        self.assertNotIn("proxy_tab",b)
        self.assertNotIn("phoban_tab",b)
        self.assertTrue(LocalFeaturePolicy(frozenset({"trainlsv_tab"}))
                        .config_available("trainlsv_tab"))

    def test_17_old_original_license_issuer_not_added(self):
        code=(ROOT/"src/train_lsv_top_tab.py").read_text("utf-8")
        for forbidden in ("PermissionGuard(", "InfoState(", "receive_token(",
                          "SendInput(", "PostMessage(", "RequestSellItem(",
                          "_farm_all(", "_toggle_farm("):
            self.assertNotIn(forbidden,code)

if __name__=="__main__":
    unittest.main()
