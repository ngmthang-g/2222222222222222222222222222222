"""S200 original-TLM character diagnostics shared by independent Party/Train.

One app-owned worker consumes only S09 real native Start HWND/PID windows,
the selected F04 game folder, and the S196-S199 READ-ONLY actual memory
reader. Observations are DIAGNOSTIC CANDIDATES, not RoleReading nor
TrainCharacterSample, and cannot enable login/Party/Train/game actions.

A real role string/HP/MapID candidate is clearly labelled UNVERIFIED
until final owner Win64/game acceptance of the ABI and live data source.
No simulated role names, window-title fallback, third-party Auto Train,
original license/token/heartbeat/Proxy, game writes or injections.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import threading
import time

from login_path import GameDirectoryStore
from independent_role_continuity import OriginalRoleContinuityLedger
from start_polling import StartWindowProducer, WindowSnapshot
from start_windows import GameWindow
from tlm_existing_game_reader import (
    ExistingGameOriginalReader,
    ExistingTlmGameReaderReport,
)

OBSERVE_INTERVAL_SECONDS = 3.0    # local safety cadence, not original timer
MAX_WINDOWS_TRACKED = 48          # bounded observations, NOT game account cap
MAX_NATIVE_READS_PER_PASS = 1      # avoid hashing many DLLs in one burst
OBSERVATION_TTL_SECONDS = 16.0     # stale HP is NOT a verified live value
SUCCESS_DIAGNOSTIC = "ORIGINAL_READONLY_CHARACTER_CANDIDATE_UNVERIFIED"


@dataclass(frozen=True)
class UnverifiedGameCharacter:
    hwnd: int
    pid: int
    code: str
    # No data from saved accounts, UI titles or mock memory sources.
    role_name_candidate: str | None = None
    role_id_candidate: int | None = None
    current_hp_candidate: int | None = None
    max_hp_candidate: int | None = None
    map_id_candidate: int | None = None
    team_id_candidate: int | None = None
    role_name_confirmed: bool = False
    hp_verified: bool = False
    party_ready: bool = False
    train_game_sender_enabled: bool = False
    captured_monotonic: float | None = None
    # Number of independent *actual native* matching RoleName+RoleID reads.
    # Never changes role_name_confirmed, party_ready or game_sender flags.
    independent_identity_reads: int = 0
    process_creation_filetime: int | None = None

    @property
    def hp_percent_candidate(self) -> int | None:
        if (self.current_hp_candidate is None
                or self.max_hp_candidate is None
                or self.max_hp_candidate <= 0):
            return None
        return round(self.current_hp_candidate * 100 /
                     self.max_hp_candidate)


@dataclass(frozen=True)
class UnverifiedCharacterBatch:
    status: str
    source_revision: int = 0
    observed_monotonic: float | None = None
    members: tuple[UnverifiedGameCharacter, ...] = ()
    # This diagnostic batch must never be cast to a PartyRosterResult.
    ready_for_game_actions: bool = False


def _candidate(report: ExistingTlmGameReaderReport,
               window: GameWindow) -> UnverifiedGameCharacter:
    """Project source evidence only if all nested original fences passed."""
    def empty(code):
        return UnverifiedGameCharacter(window.hwnd, window.pid, code)

    if (type(report) is not ExistingTlmGameReaderReport
            or report.pid != window.pid
            or report.hwnd != window.hwnd):
        return empty("HWND_PID_PROVENANCE_REJECTED")
    if report.code != SUCCESS_DIAGNOSTIC:
        return empty(report.code)
    native = report.native
    if (native is None or native.pid != window.pid
            or native.hwnd != window.hwnd
            or native.status !=
            "ORIGINAL_ROLE_UTF16_CANDIDATE_NOT_RUNTIME_VERIFIED"
            or not native.original_session_anchor_observed
            or native.numeric_candidate is None
            or native.role_name_candidate is None
            or type(native.process_creation_filetime) is not int
            or native.process_creation_filetime <= 0):
        return empty("NATIVE_READER_PROCESS_GENERATION_UNVERIFIED")
    role = native.numeric_candidate
    name = native.role_name_candidate
    if (role.status != "ORIGINAL_42_FIELD_NUMERIC_CANDIDATE_NO_ROLENAME_PROOF"
            or name.status !=
            "IL2CPP_UTF16_CANDIDATE_NEEDS_ACTUAL_GAME_ATTESTATION"
            or not isinstance(name.role_name, str)
            or not name.role_name.strip()
            or any(type(n) is not int for n in (
                role.role_id, role.current_hp, role.max_hp,
                role.map_id, role.team_id))):
        return empty("INVALID_MEMORY_ROLE_FIELDS")
    # Explicitly unverified even on plausible original Reader results.
    return UnverifiedGameCharacter(
        window.hwnd, window.pid, SUCCESS_DIAGNOSTIC,
        name.role_name, role.role_id, role.current_hp,
        role.max_hp, role.map_id, role.team_id,
        process_creation_filetime=native.process_creation_filetime)


class IndependentCharacterDiagnosticObserver:
    """One cancelable, read-only app-scoped polling worker, not a game sender."""

    def __init__(self, start_producer: StartWindowProducer, settings_file, *,
                 clock=time.monotonic, interval_seconds=OBSERVE_INTERVAL_SECONDS):
        if (not isinstance(start_producer, StartWindowProducer)
                or interval_seconds <= 0 or not callable(clock)):
            raise ValueError("REAL_S09_SOURCE_REQUIRED")
        self.producer = start_producer
        self.store = GameDirectoryStore(settings_file)
        self.clock = clock
        self.interval = float(interval_seconds)
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = None
        self._closed = False
        self._batch = UnverifiedCharacterBatch("WAITING_FOR_NATIVE_GAME_WINDOWS")
        self._cursor = 0
        self._generation = 0
        self._continuity = OriginalRoleContinuityLedger()

        def selected_exe():
            # Worker-only, bounded original F04 read, never from Tk widgets.
            try:
                return self.store.get_exe_path(self.store.load())
            except (OSError, ValueError, RuntimeError):
                return None

        self._reader = ExistingGameOriginalReader(
            start_producer, selected_game_exe=selected_exe,
            clock=clock)

    def start(self) -> bool:
        with self._lock:
            if self._closed:
                return False
            if self._thread is not None and self._thread.is_alive():
                return True
            self._stop.clear()
            self._thread = threading.Thread(
                target=self._run, name="TLM-S200-OriginalReadOnly-Observer",
                daemon=True)
            try:
                self._thread.start()
            except RuntimeError:
                self._thread = None
                return False
            return True

    def read_batch(self) -> UnverifiedCharacterBatch:
        """One immutable snapshot; does not block on Win32 or disk reads."""
        with self._lock:
            batch = self._batch
            closed = self._closed
        if closed:
            return UnverifiedCharacterBatch("STOPPED")
        if (batch.observed_monotonic is None
                or self.clock()-batch.observed_monotonic >
                OBSERVATION_TTL_SECONDS):
            return UnverifiedCharacterBatch("STALE_OR_WAITING")
        snap = self.producer.read_snapshot()
        if (not self.producer.active
                or type(snap) is not WindowSnapshot or not snap.valid
                or len({(w.hwnd, w.pid) for w in snap.windows}) !=
                len(snap.windows)
                or {w.hwnd for w in snap.windows} !=
                {w.hwnd for w in batch.members}):
            return UnverifiedCharacterBatch("SOURCE_WINDOW_SET_CHANGED")
        # Current PID membership must match too; a reused HWND cannot show
        # a previous character candidate, even between two refresh cycles.
        if {(w.hwnd, w.pid) for w in snap.windows} != {
                (w.hwnd, w.pid) for w in batch.members}:
            return UnverifiedCharacterBatch("SOURCE_PID_REUSED")
        # A candidate that is still shown after its own 16s expiry would
        # falsely suggest its HP and MapID are continuously current.
        result = tuple(
            item if (item.captured_monotonic is not None
                     and 0 <= self.clock()-item.captured_monotonic
                     <= OBSERVATION_TTL_SECONDS)
            else UnverifiedGameCharacter(
                item.hwnd, item.pid, "CANDIDATE_EXPIRED_OR_NOT_SCANNED")
            for item in batch.members)
        return replace(batch, members=result)

    def invalidate(self):
        """F04 folder change must immediately hide ALL old role/HP data.

        A slow in-flight hash/native read may finish later; generation check
        prevents it from publishing into the new selected game folder.
        """
        with self._lock:
            self._generation += 1
            self._batch = UnverifiedCharacterBatch(
                "GAME_FOLDER_CHANGED_CANDIDATES_INVALIDATED")

    def _publish(self, batch, generation):
        with self._lock:
            if (not self._closed and not self._stop.is_set()
                    and generation == self._generation):
                self._batch = batch

    def _run(self):
        while not self._stop.is_set():
            with self._lock:
                generation = self._generation
            if getattr(self, "_worker_generation", None) != generation:
                # All historical candidates belong to the previous F04
                # folder/provenance epoch, even if Windows PID is the same.
                self._previous = {}
                self._previous_exe = None
                self._continuity.reset()
                self._worker_generation = generation
            try:
                snap = self.producer.read_snapshot()
                if (not self.producer.active
                        or type(snap) is not WindowSnapshot
                        or not snap.valid):
                    self._continuity.reset()
                    batch = UnverifiedCharacterBatch("START_CACHE_UNAVAILABLE")
                elif len(snap.windows) > MAX_WINDOWS_TRACKED:
                    self._continuity.reset()
                    batch = UnverifiedCharacterBatch(
                        "TOO_MANY_WINDOWS_FOR_BOUNDED_DIAGNOSTIC")
                elif not snap.windows:
                    self._continuity.reset()
                    batch = UnverifiedCharacterBatch(
                        "NO_CURRENT_GAME_WINDOWS", snap.revision,
                        self.clock())
                else:
                    selected_path = self._reader.selected_game_exe()
                    if selected_path is None:
                        batch = UnverifiedCharacterBatch(
                            "NO_EXPLICIT_SELECTED_GAME_EXE")
                        self._previous = {}
                        self._previous_exe = None
                        self._continuity.reset()
                    else:
                        # Changing the F04 game folder invalidates *every*
                        # previous source attribution, even if PID is same.
                        if getattr(self, "_previous_exe", None) != str(selected_path):
                            self._previous = {}
                            self._continuity.reset()
                            self._previous_exe = str(selected_path)
                        previous = getattr(self, "_previous", {})
                        keys = {(w.hwnd, w.pid) for w in snap.windows}
                        previous = {k: v for k, v in previous.items() if k in keys}
                        self._continuity.retain_current(keys)
                        # Round-robin ONE native read per cycle; do not
                        # repeatedly hash dozens of GameAssembly DLLs in
                        # a single burst (background tool remains usable).
                        windows = snap.windows
                        for _ in range(min(MAX_NATIVE_READS_PER_PASS, len(windows))):
                            window = windows[self._cursor % len(windows)]
                            self._cursor += 1
                            if self._stop.is_set():
                                break
                            observation = self._reader.inspect(window)
                            candidate = _candidate(observation, window)
                            captured = self.clock()
                            if (candidate.code == SUCCESS_DIAGNOSTIC
                                    and candidate.role_id_candidate is not None
                                    and candidate.role_name_candidate is not None):
                                continuity = self._continuity.accept(
                                    window.hwnd, window.pid,
                                    candidate.role_id_candidate,
                                    candidate.role_name_candidate, captured,
                                    candidate.process_creation_filetime)
                                count = (continuity.independent_read_count
                                         if continuity is not None else 0)
                            else:
                                self._continuity.failed(window.hwnd, window.pid)
                                count = 0
                            previous[(window.hwnd, window.pid)] = replace(
                                candidate, captured_monotonic=captured,
                                independent_identity_reads=count)
                        latest = self.producer.read_snapshot()
                        if (not self._stop.is_set()
                                and type(latest) is WindowSnapshot
                                and latest.valid
                                and {(w.hwnd, w.pid) for w in latest.windows}
                                == keys):
                            self._previous = previous
                            members = tuple(previous.get(
                                (w.hwnd, w.pid),
                                UnverifiedGameCharacter(
                                    w.hwnd, w.pid, "NOT_SCANNED_YET"))
                                for w in latest.windows)
                            batch = UnverifiedCharacterBatch(
                                "CANDIDATE_ONLY_NOT_GAME_ATTESTED",
                                latest.revision, self.clock(), members)
                        else:
                            self._previous = {}
                            self._continuity.reset()
                            batch = UnverifiedCharacterBatch(
                                "WINDOW_SET_CHANGED_DURING_READ")
                self._publish(batch, generation)
            except (OSError, ValueError, RuntimeError, TypeError,
                    AttributeError):
                self._continuity.reset()
                self._publish(UnverifiedCharacterBatch(
                    "ORIGINAL_NATIVE_READ_DIAGNOSTIC_FAILED"), generation)
            self._stop.wait(self.interval)

    def shutdown(self):
        with self._lock:
            self._closed = True
            self._generation += 1
            self._batch = UnverifiedCharacterBatch("STOPPED")
            self._stop.set()
        # Bounded join: no indefinite wait on Win32/FS I/O on the Tk thread.
        thread = self._thread
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=0.2)
