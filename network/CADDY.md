# Caddy Installation and Configuration Guide

[Caddy](https://caddyserver.com/) is a web server and reverse proxy with
automatic HTTPS. This guide covers multiple deployment patterns, including a
public HTTPS endpoint, Cloudflare Tunnel with a loopback HTTP listener, and
verified internal HTTPS to isolated application hosts.

All domains/IPs are **examples**. `192.0.2.0/24` is an arbitrary address
space, not real network; replace it with your host/CT/VM addresses.

## 1. Separate the three network connections

```plaintext
Browser -> HTTPS --> Cloudflare (optional)
                        |
                        | [encrypted] Cloudflare Tunnel
                        v
                    cloudflared
                        |
                        | HTTP 127.0.0.1:8080
                        v
                      Caddy
                    /       \
        internal HTTP       internal HTTPS
            |                      |
           apps               Caddy sidecar
                                   |
                              Vaultwarden
```

## 2. Install Caddy

Refer to the [official Caddy documentation](https://caddyserver.com/docs/install)
for more information.

```bash
sudo apt update
sudo apt install -y debian-keyring debian-archive-keyring \
  apt-transport-https curl gnupg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' \
  | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' \
  | sudo tee /etc/apt/sources.list.d/caddy-stable.list >/dev/null
sudo chmod o+r /usr/share/keyrings/caddy-stable-archive-keyring.gpg \
  /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install -y caddy
sudo systemctl enable --now caddy
caddy version
```

## 3. Organize configuration files

We can use a main Caddyfile that imports site-specific configuration files. This
allows us to manage multiple hostnames and backends without cluttering a single
file.

An example directory structure might look like this:

```text
/etc/caddy
├── Caddyfile          # Entry point
├── sites/
│   ├── app.caddy                 # One file for each hostname/site
│   ├── vaultwarden.caddy
│   └── certs/                    # Separate directory for root CA certificates
│       └── vaultwarden-root.crt
```

In the main `/etc/caddy/Caddyfile`, be sure to include the following line to
import all site configurations:

```caddyfile
import /sites/*.caddy
```

Create the directory with access for the Caddy service:

```bash
sudo install -d -o root -g caddy -m 0750 /etc/caddy/sites /etc/caddy/sites/certs
```

Ensure each `.caddy` file and any root CA `.crt` files can be read by the
`caddy` service account.

The `*.caddy` glob matters: `import /sites/*` may also include things you
didn't intend to parse as Caddy configuration. Example configurations are
under [`network/caddy/examples/`](./caddy-example/).

## 4. Set up ingress with Caddy

You may choose to run Caddy with one of the following three patterns,
depending on your preferred network architecture and whether you want
public HTTPS, Cloudflare Tunnel, or private-only access.

### A. Public Caddy on standard HTTPS :443

For direct inbound access with working DNS and an accessible ACME challenge
(e.g. ports 80 and 443 or DNS-01 automation):

```caddyfile
app.example.com {
    reverse_proxy 192.0.2.30:3000
}
```

Caddy ordinarily obtains and renews a public certificate automatically.
Its backend remains HTTP unless you explicitly specify an `https://` upstream.
Only expose necessary endpoints; protect administrative services separately.

### B. Cloudflare Tunnel terminates public HTTPS

If `cloudflared` and Caddy run **on the same host/network namespace** and
Cloudflare handles external TLS, prefer a loopback-only HTTP ingress:

```caddyfile
http://app.example.com:8080 {
    bind 127.0.0.1
    reverse_proxy 192.0.2.30:3000 {
        header_up X-Forwarded-Proto https
    }
}
```

In the **Cloudflare dashboard-managed Tunnel**, add a Published Application:

```text
Hostname:     app.example.com
Service type: HTTP
Service URL:  http://127.0.0.1:8080
```

This is **the address of Caddy from cloudflared's perspective**. If
cloudflared runs in another container or VM, its `127.0.0.1` will refer to
itself instead: use an explicitly reachable address and appropriate firewall
rules. Do not point a tunnel's service URL at the public Cloudflare hostname.

The Cloudflare route should not override the original Host header unless
required: Caddy uses the hostname to select a site. When the route is managed
in the dashboard, DNS is usually created/updated with the published route;
check for existing/conflicting records. HTTP between co-located cloudflared
and Caddy over loopback is separate from the public HTTPS connection.

**A single :8080 listener can handle any number of hostnames.** Each `.caddy`
site specifies its own private backend IP and port. If other site blocks
share the same listener, apply the same `bind` settings consistently.

### C. Private-only Caddy

For private applications reachable only through a VPN/overlay, use a private
listener address and appropriate firewall rules. For client-facing HTTPS,
use a publicly trusted certificate via DNS-01 (even for a private service),
or Caddy's `tls internal` with a CA trusted by every client. VPN encryption
alone does not make an `http://` URL a browser-trusted HTTPS origin.

## 5. Optional: verified HTTPS to an application host

Applications may have their **own TLS endpoint**. In this example a Caddy
sidecar on the Vaultwarden host serves `vaultwarden.internal:8443` using its
private CA; the ingress Caddy is on another host. The *public hostname* stays
`vault.example.com`.

```caddyfile
http://vault.example.com:8080 {
    bind 127.0.0.1

    reverse_proxy https://192.0.2.20:8443 {
        header_up Host vaultwarden.internal
        header_up X-Forwarded-Host vault.example.com
        header_up X-Forwarded-Proto https

        transport http {
            tls_server_name vaultwarden.internal
            tls_trust_pool file /sites/certs/vaultwarden-root.crt
        }
    }
}
```

`tls_server_name` ensures the TLS certificate is validated for the private
backend name even when dialing an IP address. `tls_trust_pool file` supplies
the **public** root certificate for the issuing CA. Verify its fingerprint
before trusting it, and never copy the CA `root.key` to the ingress host.

The origin-host Caddy and the central ingress Caddy are two separate
instances. Even with both connections encrypted, the ingress proxy still sees
plaintext HTTP **between its own TLS termination and re-encryption**.

See the complete [Vaultwarden Compose tutorial](../services/vaultwarden/README.md)
for the sidecar's setup and certificate export.

## 6. Validate, reload and test

After editing `/sites/*.caddy`, use the Caddy entry-point file:

```bash
sudo caddy fmt --overwrite /sites/app.caddy
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
sudo systemctl status caddy --no-pager
```

For the loopback listener, test the route by matching the request hostname:

```bash
curl -i -H 'Host: app.example.com' http://127.0.0.1:8080/
```

For public access, test outside your home/LAN as well:

```bash
curl -Iv https://app.example.com/
```

For private backend TLS, verify directly from the ingress host:

```bash
curl -Iv \
  --cacert /sites/certs/vaultwarden-root.crt \
  --resolve vaultwarden.internal:8443:192.0.2.20 \
  https://vaultwarden.internal:8443/
```

`ss -ltnp` shows listening TCP sockets. Use it before deciding which port a
service *actually* uses; don't guess from the application name or typical
port convention.

## 7. Troubleshooting and safety

| Issue | Troubleshooting suggestions |
| --- | --- |
| Cloudflare 502 / Caddy 502 | Wrong origin port or IP, blocked firewall, failing upstream cert validation; inspect Caddy logs. |
| HTTP request answered by wrong service | Site hostname/port, `Host` header, mismatched import or Cloudflare origin rule. |
| Caddy won't bind | Port already owned or requested IP isn't assigned; run `ss -ltnp` and `ip -br addr`. |
| Browser certificate warning | Determine whether TLS terminates at Cloudflare, public Caddy, or internal Caddy before changing certificates. |
| Internal TLS name mismatch | Upstream IP differs from certificate DNS name; use `tls_server_name` and a correctly trusted CA. |
| Cloudflare app works but mobile client doesn't | An Access/WAF challenge may block API clients. |
| Reverse proxy reports HTTP scheme | Set/validate `X-Forwarded-Proto` based on the *trusted* public HTTPS termination point. |

## References

- [Caddy installation](https://caddyserver.com/docs/install)
- [Caddyfile concepts](https://caddyserver.com/docs/caddyfile/concepts)
- [Caddy reverse proxy directive](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy)
- [Caddy automatic HTTPS](https://caddyserver.com/docs/automatic-https)
- [Caddy internal TLS](https://caddyserver.com/docs/caddyfile/directives/tls)
- [Cloudflare Tunnel docs](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/)
