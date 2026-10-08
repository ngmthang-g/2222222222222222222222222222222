# M03 — Rao channel selection / mapping audit

## Authority

M03 re-inspected the exact frozen Rao and memory-items constant surfaces:

- archive SHA-256: `c1d51ffcc2c9f4c8f11c1ae70a90f63eb7c58e06b972ef08e48c71c0517c02cd`
- inner EXE SHA-256: `15c8044f215680d6851c8f901a5dc7d181068d91a8938f2a628077cf21a2df22`
- Rao authority: `rao_tab.py / RaoTab`
- send authority used by Rao: `memory_items.send_chat`.

M03 does not deep-audit interval scheduling, account assignment, or start/stop lifecycle.

## 1. Exact Rao display-name → channel-ID map

The current Rao serialized constant block contains the seven display names followed immediately by seven tagged integer constants.

Exact current mapping:

| Rao display name | Channel ID |
|---|---:|
| Thế giới | 8 |
| Bang hội | 2 |
| Môn phái | 6 |
| Tổ đội | 4 |
| Liên minh | 3 |
| Quân đoàn | 11 |
| Lân cận | 5 |

Raw evidence order in the Rao constant block:

```text
Thế giới
Bang hội
Môn phái
Tổ đội
Liên minh
Quân đoàn
Lân cận
l\x08 l\x02 l\x06 l\x04 l\x03 l\x0b l\x05
```

This is the frozen `RAO_CHANNELS` mapping for reconstruction.

## 2. Cross-check against memory_items.CHAT_CHANNELS

The independent `memory_items` module contains the broader chat-channel map:

| Chat display name | Channel ID |
|---|---:|
| Đặc biệt | 9 |
| Lân cận | 5 |
| Nói thầm | 7 |
| Tổ đội | 4 |
| Thế giới | 8 |
| Bang hội | 2 |
| Liên minh | 3 |
| Môn phái | 6 |
| Liên máy chủ | 10 |
| Quân đoàn | 11 |

Rao is therefore a strict seven-channel subset of the shared chat system. The IDs independently match the Rao constants exactly.

Rao intentionally does **not** expose:
- Đặc biệt / 9
- Nói thầm / 7
- Liên máy chủ / 10.

Do not add those three channels to the Rao combobox during reconstruction.

## 3. Default channel

The Rao constant block serializes:

`RAO_DEFAULT_CHANNEL = "Thế giới"`.

Therefore the current default Rao channel is:

- display name: **Thế giới**
- channel ID: **8**.

The `RAO_DEFAULT_CHANNEL` reference is inside the current `_add_rao_row` channel-StringVar/readonly-combobox construction surface, so newly created rows use the default-channel policy rather than an arbitrary numeric ID.

The user-supplied Rao screenshot, checked only after static extraction, shows `Thế giới`, consistent with this exact default.

## 4. Persistence stores the display name, not the numeric ID

M02 froze the current Rao payload:

```json
{
  "content": "...",
  "channel": "...",
  "sec": "..."
}
```

The `channel` field comes from the row's `chan_var`, whose UI values are `RAO_CHANNELS` display names.

Therefore persistent Rao definitions store the **channel display name string**, not the integer channel ID.

Example semantic shape:

```json
{
  "content": "Nội dung...",
  "channel": "Bang hội",
  "sec": "30"
}
```

At runtime, `_resolve_rao` maps that name to the corresponding numeric ID.

This distinction must be preserved:
- config = stable/current display-name value;
- send call = numeric chat channel ID.

## 5. _resolve_rao channel contract

M02 already froze the exact method contract:

> Tên rao → (nội dung, interval_giây, channel_id, tên_kênh).
> (None, lý_do) nếu không dùng được.

Recovered local variables include:

- `content`
- `chan_name`
- `total`.

No independent persisted `chan_id` exists in the row model.

Therefore channel ID is derived during resolution from the current `RAO_CHANNELS` map.

Exact no-channel failure text:

`'<Rao name>' chưa chọn kênh`.

A successfully resolved Rao definition always returns:
1. content;
2. interval seconds;
3. numeric mapped channel ID;
4. original channel display name.

## 6. Exact memory_items.send_chat argument contract

The frozen `memory_items` post-marker local metadata exposes the seven-local send function surface:

```text
hwnd
channel_id
content
text
chan
lua_msg
code
```

The first three are the call parameters; the remaining names are internal send construction.

Thus the current send signature used by Rao is:

`memory_items.send_chat(hwnd, channel_id, content)`.

Rao `_slot_loop` independently exposes locals:

- `content`
- `interval`
- `chan_id`
- `chan_name`
- `ok`
- `stamp`
- `hit`

and the same function block carries `MI` + `send_chat`.

The reconstruction boundary is therefore:

```text
_resolve_rao(name)
    -> content, interval, chan_id, chan_name

memory_items.send_chat(hwnd, chan_id, content)
```

Do **not** pass the Vietnamese channel name directly to `send_chat`.

## 7. What send_chat does with the ID

The shared chat-send constant/doc surface builds a Lua packet with:

- Base64 content;
- packet field `Channel=`;
- `Network.SendPacket(G_TCPPacketDefine.CMD_CLIENT_CHAT, packetData)`.

Its embedded documentation explicitly describes:

- `channel_id: int theo C_ChatChannel`
- example `8 = Thế giới, 2 = Bang hội`
- content encoded Base64 in Lua to support Vietnamese text;
- return True means the Lua command was queued, not that server echo is guaranteed.

This independently validates the Rao ID interpretation.

## 8. Invalid / stale channel handling boundary

Current valid-send universe is exactly the seven keys in `RAO_CHANNELS`.

The exact resolve surface has a fail-closed no-channel branch and only successful resolution yields a mapped numeric `channel_id`.

No path was recovered that sends:
- an arbitrary persisted string as the packet channel;
- a persisted integer directly without current map resolution.

Therefore an invalid/stale value cannot become an arbitrary chat-channel packet ID through normal Rao resolution.

What is **not** fully source-visible from the frozen constant/local surface is the exact load-time UI treatment of a non-empty retired/invalid channel string:

- normalize immediately to `RAO_DEFAULT_CHANNEL`;
- preserve the stale text until resolution rejects it;
- or clear it to blank.

That load-time presentation choice remains **EXPLICIT_UNKNOWN**.

The reconstruction safety requirement is nevertheless exact:

> Only names present in the current `RAO_CHANNELS` mapping may produce a sendable numeric channel ID.

Do not silently invent a different channel ID for a stale value.

## 9. Missing/empty channel default boundary

For a newly created Rao row, the current channel constructor references `RAO_DEFAULT_CHANNEL`, so the creation default is **Thế giới / 8**.

For malformed/legacy persisted records whose channel field is absent or empty, the exact point at which defaulting is applied (load parser versus `_add_rao_row`) is not fully distinguishable from the constant surface. The effective default-channel policy is still `RAO_DEFAULT_CHANNEL`.

A non-empty invalid/retired channel must remain a separate stale-data case and must not be claimed to normalize unless stronger evidence is recovered.

## 10. Screenshot / runtime cross-check

Screenshot cross-check after static extraction:

- captured Rao row channel: **Thế giới**
- exact static default: **Thế giới**
- mapped ID: **8**.

Frozen packaged `automove_log.txt`:
- SHA-256 `17f6daf02916e42b562e09a41afdf6affbdad8129c3f3bd25b92f80e9d259500`
- no correlated `[Rao]`, channel-name, `send_chat`, or `CMD_CLIENT_CHAT` Rao trace was present.

Therefore live packet/server-echo parity remains runtime-required.

## M03 boundary

Verified:
- exact seven Rao channel labels;
- exact display-name→ID mapping;
- shared CHAT_CHANNELS cross-check;
- default Thế giới / 8;
- config stores display name, not ID;
- `_resolve_rao` returns mapped numeric ID + display name;
- `memory_items.send_chat(hwnd, channel_id, content)` argument order;
- CMD_CLIENT_CHAT numeric-channel interpretation;
- invalid channels cannot produce arbitrary normal-send IDs.

Explicit unknown:
- exact UI/load normalization of a non-empty retired channel name;
- exact layer that applies the default for missing/empty legacy channel values;
- live server echo/timing.

Deferred:
- M04 interval normalization/scheduling;
- M05 account assignment;
- M06 worker start/stop;
- M07 parity/reconstruction gate.
