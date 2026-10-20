# Caddy Installation and Configuration Guide

[Caddy](https://caddyserver.com/) is a powerful, open-source web server that is
known for its simplicity and ease of use. It automatically manages HTTPS
certificates and provides a user-friendly configuration format. In this guide,
we will go through the steps to set up Caddy to serve as our server's reverse
proxy and certificate manager.

---

## 1. Install Caddy

To install Caddy, on your server/container, run the following command:

```bash
apt install --yes debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
chmod o+r /usr/share/keyrings/caddy-stable-archive-keyring.gpg
chmod o+r /etc/apt/sources.list.d/caddy-stable.list
apt update
apt install -y caddy
```

## 2. Configure Caddy

Once Caddy is installed, you can choose to configure it using either the
Caddyfile or JSON configuration. The Caddyfile is a simple and human-readable
format, while JSON is more structured and suitable for programmatic configurations.

For me, I prefer using the Caddyfile for its simplicity. Below is an example of
a basic Caddyfile configuration that sets up a reverse proxy for a web
application running on a CT (Container) with the domain `subdomain.example.com`:

```caddyfile
subdomain.example.com {
    reverse_proxy http://<CT_IP_ADDRESS>:<CT_PORT>
}
```
