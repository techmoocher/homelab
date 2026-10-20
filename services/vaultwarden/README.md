# Vaultwarden with Docker Compose and Caddy

[Vaultwarden](https://github.com/dani-garcia/vaultwarden) is an unofficial,
Bitwarden-compatible, self-hosted password manager. Treat this service as
security-critical: use strong account credentials and MFA, restrict the
administration interface, patch it promptly, and test encrypted off-site backups.

This is a **reusable guide**, not a copy of any particular homelab. Replace
`vault.example.com`, `192.0.2.20` and example ports with your own values.
Examples use Debian/Linux hosts and Docker Compose, but the reverse proxy and
TLS concepts apply equally to VMs, LXCs, physical machines and other networks.

## 1. Choose a topology

| Mode | Browser to edge | Edge to central proxy | Central proxy to Vaultwarden host | When to use |
| --- | --- | --- | --- | --- |
| A — private HTTP | HTTPS (Cloudflare or Caddy) | HTTP over localhost (with Tunnel) | HTTP on a restricted private network | Simple, trusted host-to-host environment |
| B — internal HTTPS | HTTPS (Cloudflare or Caddy) | HTTP over localhost (with Tunnel) | Verified HTTPS to a Caddy sidecar | Encrypt/authenticate the second host-to-host hop |
| C — direct Caddy | HTTPS to Caddy on port 443 | Not applicable | HTTP or HTTPS | Public access without Cloudflare Tunnel |

**You do not need internal TLS just because Vaultwarden requires an HTTPS
browser origin.** Cloudflare or a public-facing Caddy instance can provide that
origin. Mode B adds protection to traffic *between the reverse proxy and the
Vaultwarden host*; it does not make the reverse proxy unable to read requests.

**Isolation:** A dedicated VM is a sensible default for a password manager.
Docker in an unprivileged Proxmox LXC is possible but adds nested-container
compatibility and shares the host kernel. Never make an LXC privileged or
disable security controls just to get Docker running.

## 2. Prerequisites

- A supported Docker Engine and Docker Compose plugin. See
  [the repository's Docker guide](../../tutorials/docker/README.md) or
  [Docker's official installation guide](https://docs.docker.com/engine/install/).
- An external domain name and an HTTPS-capable entry point (Cloudflare Tunnel,
  Caddy on public port 443, or another trusted TLS reverse proxy).
- A dedicated data directory with sufficient storage and a separate encrypted
  backup destination.
- If the reverse proxy runs on another host: private routing and firewall rules
  permitting only that proxy to reach the published backend port.

Copy the files from this directory onto the machine that will run Vaultwarden:

```text
vaultwarden/
├── compose.yaml                 # Mode A: HTTP backend
├── compose.internal-tls.yaml    # Mode B: Caddy TLS sidecar
├── .env.example
├── .env                        # Create locally; never commit
├── data/                       # Personal vault data; never commit
└── caddy-internal/Caddyfile
```

`compose.yaml` and `compose.internal-tls.yaml` are **alternatives**, not
files to start together. Both use `./data` for the same vault state.

## 3. Configure environment and persistent data

```bash
cp .env.example .env
chmod 600 .env
mkdir -p data
chmod 700 data
$EDITOR .env
```

Set `DOMAIN` to the **external** HTTPS URL, such as
`https://vault.example.com`. The domain must be the one used by your browser
and Bitwarden clients, even if the backend serves plain HTTP internally.

`BIND_IP` is an **address assigned to the Docker host**. If the reverse proxy
runs in a *different* VM/CT, replace `127.0.0.1` with the Docker host's private
IP and restrict access to the ingress proxy using your host/hypervisor
firewall. Docker port publishing can bypass some guest firewall policies; do
not rely on UFW alone. If Caddy and Docker share a network namespace,
`127.0.0.1` is preferable.

The Compose examples default to `SIGNUPS_ALLOWED=false` and do not enable an
admin token. To create your first account, temporarily enable signups **only
after restricting access to yourself**; see section 7.

## 4A. Deploy with an HTTP backend (simplest)

```bash
docker compose -f compose.yaml config -q
docker compose -f compose.yaml up -d
docker compose -f compose.yaml ps
docker compose -f compose.yaml logs --tail=50 vaultwarden
```

The Vaultwarden image listens on port **80 inside Docker**. Compose publishes
it to `BIND_IP:HTTP_PORT` (default `127.0.0.1:8080`). Other machines can reach
it only if you bind to an address reachable by them and permit access.

For a central Caddy in another VM/CT, start with the
[HTTP backend site example](../../network/caddy/examples/sites/vaultwarden-http.caddy),
using your private backend IP and published HTTP port.

## 4B. Deploy with independently verified internal HTTPS (optional)

Use this alternative **instead of Mode A**, with the same `.env` and `data/`.
The included Caddy sidecar obtains an internal certificate for the *backend*
name `vaultwarden.internal`; it does not attempt Let's Encrypt validation.

```bash
docker compose -f compose.internal-tls.yaml config -q
docker compose -f compose.internal-tls.yaml up -d
docker compose -f compose.internal-tls.yaml ps
docker compose -f compose.internal-tls.yaml logs --tail=50 caddy
```

Vaultwarden's HTTP port is accessible only on its Docker network. The Caddy
sidecar publishes HTTPS at `BIND_IP:TLS_PORT` (default 8443). Allow only your
ingress proxy's address through the host/hypervisor firewall.

Export **only the public internal CA root certificate**, never `root.key`:

```bash
docker compose -f compose.internal-tls.yaml cp \
  caddy:/data/caddy/pki/authorities/local/root.crt ./vaultwarden-root.crt
```

Move this public certificate to the **central Caddy host**, for example at
`/sites/certs/vaultwarden-root.crt` (using `scp` or your hypervisor's file
copy facility). Never place the private key on the ingress host.

Configure the ingress reverse proxy using the
[TLS backend site example](../../network/caddy/examples/sites/vaultwarden-tls.caddy).
It connects to `https://PRIVATE_IP:8443`, sets SNI/certificate verification to
`vaultwarden.internal`, and trusts the exported internal CA. **Never use**
`tls_insecure_skip_verify` as a workaround.

Test from the central Caddy host, substituting the backend private IP:

```bash
curl -Iv \
  --cacert /sites/certs/vaultwarden-root.crt \
  --resolve vaultwarden.internal:8443:192.0.2.20 \
  https://vaultwarden.internal:8443/api/config
```

Keep `caddy-data/` persistent: it contains the local CA's **private key**. If
it is lost and Caddy creates a new CA, export and install the new `root.crt`
again. Do not put `caddy-data/` or real certificate/key files in Git.

## 5. Choose how clients enter your network

### Cloudflare Tunnel + central Caddy

When `cloudflared` and central Caddy run in the **same network namespace**,
a dashboard-managed published application route can be:

```text
Public hostname:  vault.example.com
Service type:    HTTP
Service URL:     http://127.0.0.1:8080
```

`127.0.0.1` means localhost **of cloudflared**, not of the Vaultwarden CT. If
Cloudflare runs in a separate container, localhost is usually a *different*
namespace: use a reachable Caddy address or an explicitly shared network.

The central Caddy listener on 8080 selects a backend from the incoming HTTP
Host header (see [Caddy guide](../../network/CADDY.md)). In Mode A it proxies
to the HTTP backend; in Mode B it proxies to the backend Caddy over verified
HTTPS. Keep the Cloudflare HTTP Host Header override unset unless you have a
specific reason to change it. Cloudflare provides browser-facing HTTPS, and
the tunnel is encrypted between Cloudflare and `cloudflared`.

### Direct, public-facing Caddy

If you do **not** use Cloudflare Tunnel, publish Caddy on ports 80/443 and
configure a site such as:

```caddyfile
vault.example.com {
    reverse_proxy 192.0.2.20:8080
}
```

Caddy can obtain a publicly trusted certificate automatically when DNS points
to it and ACME requirements are satisfied. Use the private HTTPS upstream
configuration instead if you deploy Mode B.

## 6. Verify each hop

From central Caddy's host (using the actual listening port):

```bash
curl -i -H 'Host: vault.example.com' \
  http://127.0.0.1:8080/api/config
```

From a client with access to the public URL:

```bash
curl -I https://vault.example.com/
curl -i https://vault.example.com/api/config
```

Then open the site and test login in a private browser window. Verify the
Bitwarden mobile/desktop clients with the configured self-hosted URL. An HTTP
200 response alone does not confirm working JavaScript or client sync.

## 7. Create the first account securely

`SIGNUPS_ALLOWED=false` protects against arbitrary public registration. To
bootstrap, **first restrict the public hostname** (for example, with a
short-lived Cloudflare Access allow policy for your own identity or a private
network connection). Then set `SIGNUPS_ALLOWED=true` in `.env`, recreate the
service, register the first account, restore `false`, and recreate it again:

```bash
# Use the compose filename for whichever mode you deployed.
docker compose -f compose.yaml up -d --force-recreate vaultwarden
```

Cloudflare Access login challenges may be incompatible with Bitwarden API
clients. Treat Access as a temporary bootstrap restriction unless thoroughly
tested with all your clients. Enable MFA, save recovery codes securely,
keep administrator access disabled unless needed, and test that public signup
is blocked afterwards.

For managed invites or administration, see upstream Vaultwarden documentation;
admin tokens are privileged credentials and should be hashed, protected and
never stored in a public repository.

## 8. Backup, update and restore

A reliable, simple backup is to **stop Vaultwarden briefly**, copy the entire
`data/` directory and then start it. Do not copy an active SQLite database
without using a transactionally consistent SQLite backup method. Store backups
encrypted **off the host**, rotate them and test restoring onto a fresh server.

```bash
# Example for Mode A; replace the file name for Mode B.
docker compose -f compose.yaml stop vaultwarden
mkdir -p /secure/backup-location
sudo tar -czf /secure/backup-location/vaultwarden-$(date +%Y%m%d-%H%M).tgz data/
docker compose -f compose.yaml start vaultwarden
```

For Mode B, also back up `caddy-data/` and `caddy-config/` if you want to
preserve the internal CA identity. If restoring without that CA, re-establish
trust on the central proxy. Snapshot/backup the VM or CT **in addition to**
the off-host vault backup, not instead of it.

Before updates, back up first, then review release notes:

```bash
docker compose -f compose.yaml pull
docker compose -f compose.yaml up -d
docker compose -f compose.yaml ps
```

When using Mode B, replace the `-f` filename in these commands with
`compose.internal-tls.yaml`.

## 9. Troubleshooting

| Symptom | Check |
| --- | --- |
| `cannot assign requested address` | `BIND_IP` must be assigned to the **Docker host**, not the ingress host (`ip -br -4 addr`). |
| `service "caddy" is not running` | Sidecar may not have started; check `docker compose -f compose.internal-tls.yaml ps -a` and logs. |
| `502 Bad Gateway` | Backend IP/port, firewall, sidecar logs, certificate trust and hostname verification. |
| Certificate hostname mismatch | Upstream IP is not the certificate name; set `tls_server_name vaultwarden.internal` and use the exported CA root. |
| White/blank web vault | Confirm `DOMAIN` matches the external URL, verify `/api/config` and JavaScript asset HTTP responses, inspect browser Console/Network for blocked assets or JS errors. |
| HTTP-to-HTTPS redirect loop | Review edge TLS termination, forwarded scheme and proxy headers; avoid double redirects on the loopback hop. |
| Works locally but not from Cloudflare | Check Cloudflare published hostname, service URL, Host header, Caddy listener and tunnel health. |

## References

- [Vaultwarden Wiki](https://github.com/dani-garcia/vaultwarden/wiki)
- [Official Vaultwarden Docker Compose examples](https://github.com/dani-garcia/vaultwarden/wiki/Using-Docker-Compose)
- [Vaultwarden proxy examples](https://github.com/dani-garcia/vaultwarden/wiki/Proxy-examples)
- [Vaultwarden backup guidance](https://github.com/dani-garcia/vaultwarden/wiki/Backing-up-your-vault)
- [Caddy reverse_proxy documentation](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy)
- [Caddy internal TLS](https://caddyserver.com/docs/caddyfile/directives/tls)
