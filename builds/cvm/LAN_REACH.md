# LAN reach for Core `:8770` — recorded, not worked around

**Measured 2026-08-31T02:35:34-0500** on this box. Machine-readable record:
`builds/cvm/LAN_REACH.json` (`schema cvm-lan-reach/1`). Re-run:

    py -3.14 builds\cvm\lan_reach.py --root V:\A\Ai\COSMOS\live --port 8770

## Verdict: `LOOPBACK_ONLY`

Core answers, but only to this host. A phone on the LAN cannot reach it, and
**no firewall rule would change that** — there is no LAN socket to open.

| reading | value |
| --- | --- |
| `connect_ex 127.0.0.1:8770` | `0` (OK, 0.209 ms) |
| `connect_ex 192.168.1.107:8770` | `10035` WSAEWOULDBLOCK — timed out after 1027 ms |
| LISTEN socket (kernel socket table) | `127.0.0.1:8770`, pid **28484** — the only one |
| spawn argv (`live/logs/core_serve.json`, pid **28484**) | `cosmos.py serve --root … --port 8770` — **no `--remote`** |

The two readings are independent and agree, which is why the cause is stated
rather than guessed. A single failed connect cannot tell a loopback bind from a
dropped SYN; the socket table plus the spawn record can. `cosmos.py:112` sets
`host = "0.0.0.0" if a.remote else "127.0.0.1"` — this process took the second
branch.

## What LAN reach requires — all four are blocking

1. **Bind the LAN.** `cosmos.py serve --remote` → `host="0.0.0.0"`. Restarting
   the resident authority is the operator's call, not an agent's.
2. **TLS, because the code refuses cleartext.** `cosmos_service.py:1503` raises
   `REMOTE_CLEARTEXT` and the service **will not start** on a non-loopback bind
   over HTTP. Use `--tls` (self-signed into `config/`, SAN covers the bind IP)
   or `--cert/--key`. `cryptography` **is importable on this box** (verified),
   so `--tls` will actually produce HTTPS rather than silently staying HTTP and
   then tripping the same refusal.
3. **Keep bearer auth on.** Do **not** pass `--no-auth`. Over the LAN the token
   is the access control and TLS is what stops it being captured in flight.
   `--no-auth`+`--insecure-http` is Keith's reversible trial pair, not a
   deployment.
4. **A Windows Firewall inbound rule** for the port. COSMOS cannot enforce this
   one; it needs elevation and is an operator action.

Optional but practical: the phone must **trust the cert**. With a self-signed
cert that means installing the CA on the phone — or skip the LAN entirely and
use `cosmos up` (Tailscale), where the tailnet is the transport.

## Consequence for the CVM latency work (F-15)

Every number in `builds/cvm-dt/BENCH_LATENCY.json` is a **desktop** number,
measured over loopback on this host. **The phone half of CVM is UNMEASURED**
and is recorded as absent with this reason. It is not estimated from the
desktop figures: a phone's transit crosses Wi-Fi and TLS, which loopback does
not exercise at all, so extrapolating would fabricate the dominant term.
