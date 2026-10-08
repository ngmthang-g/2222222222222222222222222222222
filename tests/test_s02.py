"""S02 unit tests: stub verifier is TEST-ONLY, never a license bypass."""
import pathlib
import sys
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'src'))
from permission_guard import PermissionGuard, PermissionSnapshot, VerifiedClaims
from info_state import InfoState


def fake_test_verifier(token: str) -> VerifiedClaims:
    if token != 'test-signed-token':
        raise ValueError('invalid test signature')
    return VerifiedClaims(frozenset({'info_tab','login_tab','farm_tab','debug_tab'}),
                          'vip', 3, developer=False)


class S02PermissionTests(unittest.TestCase):
    def test_denies_unknown_and_no_server(self):
        p=PermissionGuard()
        self.assertTrue(p.snapshot.blocked)
        self.assertEqual(p.snapshot.authorized_keys,frozenset({'info_tab'}))
        self.assertFalse(p.has_permission('login_tab'))
        self.assertFalse(p.has_permission_with_limit('login_tab',0))

    def test_rejects_raw_json_bools_and_incorrect_token(self):
        p=PermissionGuard()
        self.assertFalse(p.receive_token('{"permissions":["login_tab"]}',lambda _:True))
        self.assertFalse(p.receive_token('wrong',fake_test_verifier))
        self.assertFalse(p.receive_token('test-signed-token',lambda _:{'permissions':['login_tab']}))
        self.assertEqual(p.snapshot.authorized_keys,frozenset({'info_tab'}))

    def test_accepts_only_adapter_decoded_claims_and_no_dev_escalation(self):
        p=PermissionGuard()
        self.assertTrue(p.receive_token('test-signed-token',fake_test_verifier))
        self.assertEqual(p.snapshot.max_windows,3)
        self.assertTrue(p.has_permission('login_tab'))
        self.assertFalse(p.has_permission('debug_tab'))
        self.assertTrue(p.has_permission_with_limit('login_tab',3))
        self.assertFalse(p.has_permission_with_limit('login_tab',4))

    def test_ban_version_lock_server_lock_and_expire(self):
        for replacement in [dict(plan_status='banned'),dict(version_locked=True),
                            dict(server_locked=True),dict(expires=True)]:
            claims=VerifiedClaims(frozenset({'info_tab','farm_tab'}),'vip',6,**{
                k:v for k,v in replacement.items() if k!='plan_status'})
            if 'plan_status' in replacement:
                claims=VerifiedClaims(claims.permissions,replacement['plan_status'],6)
            p=PermissionGuard()
            self.assertTrue(p.receive_token('test',lambda _:claims))
            self.assertEqual(p.snapshot.authorized_keys,frozenset({'info_tab'}))

    def test_unknown_account_limit_or_bad_claim_denies(self):
        p=PermissionGuard()
        bad=VerifiedClaims(frozenset({'info_tab','secret_admin_tab'}),'vip',20)
        self.assertFalse(p.receive_token('x',lambda _:bad))
        self.assertFalse(p.check_account_limit(-1)[0])
        claims=VerifiedClaims(frozenset({'info_tab','farm_tab'}),'vip',0)
        self.assertTrue(p.receive_token('x',lambda _:claims))
        self.assertFalse(p.check_account_limit(0)[0])

    def test_info_state_propagates_revocation_and_server_loss(self):
        events=[]
        i=InfoState(on_update=lambda snapshot:events.append(snapshot))
        self.assertEqual(i.CURRENT_VERSION,'2.1.2')
        self.assertTrue(i.receive_server_token('test-signed-token',fake_test_verifier))
        self.assertTrue(i.permission_guard.has_permission('farm_tab'))
        i.on_server_error()
        self.assertFalse(i.permission_guard.has_permission('farm_tab'))
        self.assertEqual(i.server_last_result,'SERVER_UNAVAILABLE')
        self.assertGreaterEqual(len(events),2)

    def test_server_error_cannot_retain_previous_entitlements(self):
        i=InfoState()
        self.assertTrue(i.receive_server_token('test-signed-token',fake_test_verifier))
        self.assertFalse(i.receive_server_token('bad',fake_test_verifier))
        self.assertEqual(i.permission_guard.snapshot.authorized_keys,frozenset({'info_tab'}))

if __name__ == '__main__': unittest.main()
