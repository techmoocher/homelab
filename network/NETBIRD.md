# NetBird Installation and Configuration

---

NetBird is a WireGuard-based VPN solution that allows you to create a secure and private network between your devices. It is designed to be easy to set up and use, and it provides a simple web interface for managing your network. In this guide, I will walk you through the installation and configuration of NetBird on your Proxmox server.

You can learn more about NetBird and its features on the [official website](https://netbird.io/).

---

## NetBird on VM

This is the quickest and most straightforward way to set up NetBird. It is also the recommended way for most users, especially if you are new to self-hosting and don't have much experience with Linux. If you already have a VM set up and a registered domain name, it should take you less than 10 minutes to get NetBird up and running.

Learn more at the [official documentation](https://docs.netbird.io/selfhosted/selfhosted-quickstart).

### 1. Prerequisites

#### Hardware

- A **Linux VM** with at least **1 CPU** and **2 GB of memory**.
- The VM must be publicly accessible on **TCP ports 80 and 443**, and **UDP port 3478**.
- A **public domain name** that resolves to the VM's public IP address (e.g. `netbird.example.com`).
- *(Optional, for Proxy feature)* A separate domain for the proxy with a wildcard DNS record pointing to the same server IP. For example, if your management domain is `netbird.example.com`, add a wildcard record for `*.proxy.netbird.example`.com.

#### Software

- **[Docker](https://docs.docker.com/engine/install/)** with docker-compose plugin or docker-compose version 2 or higher.
- **jq** - can be install with `sudo apt install jq` or `sudo yum install jq`
- **curl** - can be install with `sudo apt install curl` or `sudo yum install curl`

### 2. Installation

First, you need to download the NetBird installation script and run it on your VM.

```bash
curl -fsSL https://github.com/netbirdio/netbird/releases/latest/download/getting-started.sh | bash
```

## NetBird on LXC


