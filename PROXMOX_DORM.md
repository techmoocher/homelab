# Proxmox Installation and Configuration for students living dorms

This guide will help you install and configure Proxmox for college students
living in dorms. Usually, on-campus housing networks are enterprise networks
with strict rules and limited access. This guide will help you set up a Proxmox
server that can be accessed from within the dorm network and provide a secure
environment for running virtual machines.

> **Disclaimer:** This guide is for educational purposes only. It is not a
> guarantee that your university will allow this configuration. Always check with
> your university's IT department before proceeding. Misuse of this guide may
> result in disciplinary action or loss of network access. The author is not
> responsible for any consequences resulting from the misuse of this guide.
> Use at your own risk.

---

## Table of Contents

- [Overview](#overview)
- [1. Installing Proxmox](#1-installing-proxmox)
- [2. Configuring the campus Ethernet connection](#2-configuring-the-campus-ethernet-connection)
- [3. Updating repositories](#3-updating-repositories)
- [4. Setting up NetBird](#4-setting-up-netbird)
- [5. Creating a private bridge](#5-creating-a-private-bridge)
- [6. Enabling NAT for the private network](#6-enabling-nat-for-the-private-network)
- [7. Securing the host and guest network](#7-securing-the-host-and-guest-network)
- [8. Testing with a container](#8-testing-with-a-container)
- [9. Verifying persistence and reliability](#9-verifying-persistence-and-reliability)
- [10. *(Optional)* Ingress](#10-optional-ingress)
- [Troubleshooting quick reference](#troubleshooting-quick-reference)
- [Note](#note)

> **Note:** You can check out the other [Proxmox guide](./README.md) for further
> configuration options.

## Overview

```plaintext
Your personal device (NetBird client)
               |
       NetBird private network
               |
    Proxmox host (NetBird peer)
               |
  Campus Ethernet (DHCP, internet)
               |
      NAT on the Proxmox host
               |
       vmbr0: 10.10.10.1/24
               |
       +-------+--------+
       |                |
  CT: test          Other VMs/CTs
  10.10.10.100      10.10.10.x
```

This is a single-node IPv4 NAT design, not a guide for using campus VLANs,
direct bridging, clustering, or running a public service on a
university-provided IP.

## 1. Installing Proxmox

1. Download the Proxmox installation image and flash it to a USB drive.
2. Boot from the USB drive and follow the installer.
3. For the **Network** configuration, use the correct wired adapter and valid
   settings approved or provided by the campus network. Never reuse your phone's
   or another computer's IP. If the installer cannot accept the network
   configuration available to you, stop rather than inventing an address. You
   can use a proper alternative installation method or work from a local console
   later.
4. Reboot into Proxmox and sign in at the physical console as root.

## 2. Configuring the campus Ethernet connection

First, identify the wired adapter:

```bash
ip -br link
ip -4 -br addr
ip -4 route
cat /etc/network/interfaces
```

Usually, the wired adapter will be named something like `enp0s3`, `ens33`, or
`enx`. Back up the interface file before proceeding to the next step.

```bash
cp -a /etc/network/interfaces /root/interfaces.bak
nano /etc/network/interfaces
```

Then, edit the file to use DHCP for the campus Ethernet interface.

```plaintext
auto enp3s0             # Replace enp3s0 with your actual wired adapter name
iface enp3s0 inet dhcp
```

Apply changes only with physical console access

```bash
ifreload -a
ip -4 -br addr
ip -4 route
cat /etc/resolv.conf
```

A successful DHCP lease should provide a campus address and ideally a default
route. To confirm connectivity besides ping, use

```bash
getent ahostsv4 deb.debian.org
curl -I --connect-timeout 8 https://www.debian.org
```

If there is no default route found or HTTPS fails, inspect your DHCP lease and
ask your campus IT about wired-device requirements. Do not borrow a gateway, IP,
or DNS configuration from a different network or manually assign an unapproved
address.

## 3. Updating repositories

On a fresh installation without an enterprise subscription, `apt update` may
show `401 Unauthorized` errors for Proxmox or Ceph enterprise repositories.
First inspect the repository configuration.

```bash
ls /etc/apt/sources.list.d/
```

If any enterprise-only source files are found, disable them by renaming them
(e.g., `pve-enterprise.sources` to `pve-enterprise.sources.disabled`). Leave
unrelated repository files unchanged.

If you have not had a no-subscription repository enabled, create one with the
following command:

```bash
cat > /etc/apt/sources.list.d/pve-no-subscription.sources <<'EOF'
Types: deb
URIs: http://download.proxmox.com/debian/pve
Suites: trixie
Components: pve-no-subscription
Signed-By: /usr/share/keyrings/proxmox-archive-keyring.gpg
EOF
```

Now, run the following commands to update and upgrade your system.

```bash
apt update && apt upgrade -y
```

## 4. Setting up NetBird

First, install NetBird client on the Proxmox host itself. Check out the
[NetBird installation guide](https://docs.netbird.io/get-started/install) for
more details.

```bash
curl -fsSL https://pkgs.netbird.io/install.sh -o /tmp/netbird-install.sh
less /tmp/netbird-install.sh
bash /tmp/netbird-install.sh
netbird up
```

Next, authenticate the Proxmox host as a NetBird peer. You can do this
interactively on another device or with a pre-generated token. You can verify
the connection with the following commands:

```bash
systemctl is-enabled netbird
netbird status
```

You can also check the NetBird dashboard to see if the Proxmox host is listed as
a peer. Now, access the dashboard over NetBird at
`https://<NETBIRD_IP_OR_DNS_NAME>:8006` (this information is available in the
NetBird dashboard or by running `netbird status`). A self-signed certificate
warning is common with a default Proxmox installation; be sure to verify you are
connecting to the correct host before advancing. Consider disabling session
expiration for this peer in the NetBird dashboard.

## 5. Creating a private bridge

We'll use vmbr0 for guests, with no physical ports. Back up
/etc/network/interfaces again, then add or edit the bridge section:

```plaintext
auto vmbr0
iface vmbr0 inet static
    address 10.10.10.1/24
    bridge-ports none
    bridge-stp off
    bridge-fd 0
```

Do not put the campus-facing Ethernet interface in bridge-ports. Do not add a
gateway to vmbr0; the host's default gateway remains on campus DHCP. If your
initial installation left the node hostname pointing at a temporary IP, edit
/etc/hosts so the Proxmox node name resolves to a stable address actually
assigned to this host, for example:

```plaintext
10.10.10.1 pve-dorm.home.arpa pve-dorm
```

Do not add duplicate entries for the same hostname. After editing the file, you
can verify with:

```bash
ifreload -a
ip -4 addr show vmbr0
getent ahostsv4 pve-dorm
ip -4 route
```

**Expected:** `vmbr0` set to `10.10.10.1/24`, the default route still uses
Ethernet interface, and the host remains reachable through NetBird.

## 6. Enabling NAT for the private network

First, permanently enable IPv4 forwarding on the Proxmox host.

```bash
printf 'net.ipv4.ip_forward=1\n' > /etc/sysctl.d/99-dorm-forwarding.conf
sysctl --system
sysctl net.ipv4.ip_forward
```

Then create a small idempotent script at `/usr/local/sbin/dorm-network.sh`
containing the following. Replace `YOUR_WIRED_INTERFACE` with the actual
interface name from `ip -br link` (for example, `enp3s0`).

```bash
#!/bin/sh
set -eu

WAN='YOUR_WIRED_INTERFACE'    # Replace with the name from 'ip -br link'
SUBNET='10.10.10.0/24'

# Masquerade outbound connections from the private bridge.
iptables -w -t nat -C POSTROUTING -s "$SUBNET" -o "$WAN" -j MASQUERADE 2>/dev/null || \
  iptables -w -t nat -A POSTROUTING -s "$SUBNET" -o "$WAN" -j MASQUERADE

# Proxmox guest firewall bridges may need a separate conntrack zone.
iptables -w -t raw -C PREROUTING -i fwbr+ -j CT --zone 1 2>/dev/null || \
  iptables -w -t raw -I PREROUTING 1 -i fwbr+ -j CT --zone 1
```

The `CT --zone 1` rule matters particularly when the Proxmox firewall is enabled
on a guest's network interface. Without it, packets can fail to reach the
correct NAT path.

Then, make the script executable and test it,

```bash
chmod 700 /usr/local/sbin/dorm-network.sh
sh -n /usr/local/sbin/dorm-network.sh
/usr/local/sbin/dorm-network.sh
```

Once verified, add this line inside the `vmbr0` in `/etc/network/interfaces`:

```plaintext
    post-up /usr/local/sbin/dorm-network.sh
```

## 7. Securing the host and guest network

1. In **Datacenter** > **Firewall** and **Node** > **Firewall**, review the
   active firewall and configure a default-deny inbound host policy with
   explicitly permitted management traffic from your authorized NetBird peers.
   Use the physical console as your recovery path.

2. Explicitly block management traffic arriving on the campus-facing Ethernet
   interface (at least `22/tcp` (SSH) and `8006/tcp` (Proxmox)) for IPv4 and
   IPv6. Check other listening services with `ss -lntup`.

3. Permit guests to initiate outbound internet connections, but deny access to
   campus-managed address ranges, local private networks, and the NetBird
   overlay except for narrowly scoped required services, such as the
   university's DNS. Obtain your institution's ranges from IT; RFC1918-only
   blocking will miss publicly routable campus subnets.

4. Deny unsolicited connections forwarded from campus Ethernet to `vmbr0`.
   Restrict access from guest interfaces to the Proxmox host, not just
   port 8006.

5. Do not configure direct campus bridging, inbound port forwarding, or an
   unrestricted NetBird route into the guest subnet unless explicitly intended,
   authorized, and secured.

6. Keep guest IPv6 unconfigured for this IPv4-only example, confirm
   `net.ipv6.conf.all.forwarding=0`, and audit IPv6 host firewall access
   separately. IPv4 NAT rules do not protect IPv6.

7. Test that these policies survive `pve-firewall` restart, network reloads, and
   a full reboot. If you add custom iptables rules, verify their ordering
   relative to Proxmox- and NetBird-managed chains after every reload.

> Do not copy a hard-coded firewall ruleset from another university. Campus
> address ranges, DNS requirements, firewall backend, and management peer
> addresses differ. This guide deliberately does not claim that an untested
> generic ruleset will fully protect a Proxmox node.

## 8. Testing with a container

Start with a disposable unprivileged Debian 13 LXC. In **Node** → **local** →
**CT Templates**, download the Debian standard template, then use **Create CT**.

| Setting                    | Example                                                         |
| -------------------------- | --------------------------------------------------------------- |
| CT ID / hostname           | `100` / `nat-test`                                              |
| Unprivileged               | Yes                                                             |
| CPU / RAM / disk           | 1 core / 512 MiB–1 GiB / 8 GiB                                  |
| Bridge                     | `vmbr0`                                                         |
| IPv4/CIDR                  | `10.10.10.10/24`                                                |
| Gateway                    | `10.10.10.1`                                                    |
| IPv6                       | Unconfigured for this guide                                     |
| Network firewall           | Enabled; verify the guest's effective policy                    |
| DNS server                 | A campus-approved resolver reachable under your firewall policy |
| DNS domain / search domain | Leave blank unless you have an actual search domain             |

> DNS domain is not DNS server. For example, `172.20.2.2` was a DNS server
> supplied on one particular campus network; it is not a domain name and should
> not be copied by users at other universities.

Inside the container, check:

```bash
ip -4 -br addr
ip -4 route
cat /etc/resolv.conf
timeout 10 getent ahostsv4 deb.debian.org
apt update
```

If DNS hangs, check the container's DNS server and the firewall exceptions
first. If raw TCP cannot connect either, inspect the host's forwarding and
masquerading counters:

```bash
# On the Proxmox host
iptables -nvL FORWARD
iptables -t nat -nvL POSTROUTING
iptables -t raw -S PREROUTING
```

A MASQUERADE rule with zero matching packets while the guest attempts external
connections can mean forwarding is blocked before NAT or that connection
tracking is misconfigured. Check the guest's network firewall and the `fwbr+`
rule before weakening any policy.

Test restrictions from the guest too: verify it cannot access Proxmox management
or unauthorized campus resources. A failed ping alone does not prove access is
blocked; use an appropriate TCP test and inspect firewall counters.

## 9. Verifying persistence and reliability

With physical console access available, reboot the host and confirm:

```bash
ip -4 -br addr
ip -4 route
sysctl net.ipv4.ip_forward
systemctl is-active netbird pveproxy
iptables -t nat -S POSTROUTING
iptables -t raw -S PREROUTING
```

Verify you can reach the Proxmox dashboard through NetBird and that the
disposable container can still resolve DNS and run `apt update`. Restart the
active Proxmox firewall service and re-run the networking, access-control, and
NAT checks.

For laptop hosts, prevent unintended suspend on lid close (using systemd-logind
settings appropriate to your OS), keep airflow unobstructed, and monitor heat
and battery health. Also configure scheduled backups of VMs/CTs to storage
outside the Proxmox machine, and test a restore. Snapshots are not a substitute
for backups.

## 10. *(Optional)* Ingress

A separate unprivileged container (for example `10.10.10.20/24`) can run Caddy
and Cloudflared to publish specifically authorized services through an outbound
Cloudflare Tunnel. Keep Proxmox administration private through NetBird, and use
application-level authentication (such as Cloudflare Access) for nonpublic apps.

You do not need NetBird in every container. Installing it on the ingress CT is
optional and useful only for private access patterns that require it. If you
later need access to more private subnets, consider a dedicated, narrowly scoped
routing peer instead of giving your public-facing ingress CT unrestricted access
to the entire homelab. Confirm that publishing services complies with university
policy.

## Troubleshooting quick reference

| Issue                                            | First check                                                                      |
| ------------------------------------------------ | -------------------------------------------------------------------------------- |
| Ethernet link is up but no internet              | DHCP address, default route, DNS, HTTPS; ICMP may be blocked.                    |
| `apt update` shows 401 Unauthorized              | Disable unused Proxmox/Ceph enterprise repositories.                             |
| Container has an IP but DNS hangs                | Its DNS server, search-domain confusion, firewall DNS allowances.                |
| Container can resolve ARP but cannot connect out | Guest firewall, host FORWARD, masquerade counters, `fwbr+` conntrack zone.       |
| Dashboard works locally but not remotely         | NetBird peer status, policies, service status, host firewall.                    |
| Networking fails after reboot                    | vmbr0 startup, DHCP, forwarding, NAT script, service order, firewall rule order. |

## Note

This is a guide for setting up a homelab, not a claim that every university
network permits or supports the same configuration. Adapt it to your school's
policy as needed, and always follow the rules of your campus network. If you
are unsure about what is allowed, ask your IT department before proceeding.

**HAPPY SELF-HOSTING!!!**
