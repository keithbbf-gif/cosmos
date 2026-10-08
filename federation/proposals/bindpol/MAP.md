# bindpol

## What this slice read

- `CONTRACT.md` slot `bindpol`, and the shared laws above that slot.
- `README.md`: a day-one window is Core on `127.0.0.1:8770`.
- `cosmos_federation/product.py`: `DEFAULT_HOST` is `127.0.0.1` and `DEFAULT_PORT` is `8770`.
- Live `cosmos/cosmos.py` serve flags. `--port` defaults to `8770`. `--remote` selects host `0.0.0.0`. `--tls` asks for HTTPS. `--no-auth` disables bearer auth and the help text refuses that flag together with `--remote`. `--insecure-http` is a trial cleartext remote bind, and it still cannot pair with `--no-auth` on a remote bind.
- Live `cosmos/cosmos_service.py` `Service.__init__`. A non-loopback host plus `open_access` raises `REMOTE_OPEN_ACCESS` before the socket is bound. A non-loopback host whose scheme is not `https` raises `REMOTE_CLEARTEXT` unless `insecure_http` is set. Loopback plus `open_access` still constructs. `_LOOPBACK_HOSTS` is `127.0.0.1`, `localhost`, and `::1`. The constructor's own default port is `0` (ephemeral). The CLI default is `8770`.

## What is already true

Live serve binds `127.0.0.1` unless `--remote`, which binds `0.0.0.0`. Bearer auth is the access control on that remote bind. `--no-auth` with `--remote` is refused as `REMOTE_OPEN_ACCESS` because an unauthenticated Core on a LAN interface is a full operator console. A remote bind without TLS is refused as `REMOTE_CLEARTEXT`, and `--insecure-http` is the one trial exception. Loopback may still run with bearer auth disabled.

## What this proposal adds

`decide(host, port, remote, tls, no_auth)` returns a frozen slotted `Bind` with `host`, `port`, `scheme` (`http` or `https`), and `auth="bearer"`. The day-one bind is `127.0.0.1`, port `8770`, remote false, tls false, no_auth false, scheme `http`. A remote bind with tls uses scheme `https` and may use host `0.0.0.0`. The only accepted addresses are those two live serve addresses. `localhost` and `::1` are refused so the window URL is one string. Remote true with a loopback address is refused because `cosmos.py` uses `--remote` to mean the wildcard, and the flag has to match the address. Loopback with tls and without remote is `https`. The module does not open a socket. `SCHEMA` is `cosmos-federation-bindpol/1`.

## Refusal codes

- `OPEN_AUTH` — `no_auth` is true on any interface, including loopback, and a `Bind` whose `auth` is not `bearer`. Live serve refuses that pairing only with `--remote` (`REMOTE_OPEN_ACCESS`). The distributed app also refuses it on loopback so a stranger cannot ship an open console.
- `REMOTE_PLAIN` — `remote` is true and `tls` is false, and a wildcard `Bind` whose scheme is not `https`. This is the live `REMOTE_CLEARTEXT` door with no `--insecure-http` opt-out.
- `PORT` — the port is not an int in `1..65535`. Port `0` is the live ephemeral constructor default, and the installer window cannot discover it.
- `HOST` — the host is not `127.0.0.1` or `0.0.0.0`, or `0.0.0.0` is paired with remote false, or remote true is paired with a host other than `0.0.0.0`.
- `BOUND` — a flag is not a bool, or the host string fails `bound_text` (empty or longer than 15 characters).
- `SCHEME` — a hand-built `Bind` carries a scheme other than `http` or `https`.

## How CCr would land it later

CCr calls `decide` on the installer serve path before `Service` is constructed, using the same host choice as `cosmos.py` (`0.0.0.0` when remote, otherwise `127.0.0.1`). A `Refuse` prints the code and returns exit 2, which is the current `ServiceError` path. `OPEN_AUTH` is the installer form of `REMOTE_OPEN_ACCESS`, extended to loopback for the distributed app. `REMOTE_PLAIN` is the installer form of `REMOTE_CLEARTEXT` without `--insecure-http`. The installer never offers `no_auth`. The operator checkout's loopback trial stays a separate door and is not this slice. The bearer file remains `config/api_token.txt`. This proposal does not edit `V:\A\Ai\COSMOS`.
