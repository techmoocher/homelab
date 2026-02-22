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

NetBird can also be installed on an LXC container. This method is more complex than installing on a VM, but it can be more efficient in terms of resource usage. If you are comfortable with Linux and have experience with LXC containers, this may be a good option for you.

### 1. Container Setup

First, we need to create an LXC container for NetBird. You can do this using the Proxmox web UI or the command line. In this example, we will use the web UI.

#### a. General

- Set CT ID (e.g. 100).
- Set Hostname (e.g. netbird).
- Set Password or SSH key for authentication.
- Set `unprivileged` to `true`.

#### b. Template

- Choose a Linux distro template (e.g. Debian 12).

#### c. Disks

- Set Disk size (8 GB is enough).
- Choose storage location (preferably SSD/NVME).

#### d. CPU

- Set the number of CPU cores (1-2 is enough).

#### e. Memory

- Set Memory size (1024 MB is enough).
- Set Swap size as needed (512 MB is recommended).

#### f. Network

- Configure the network settings:
  - Set Bridge to `vmbr0` (or your default bridge).
  - Set Firewall to `enabled` if you want to use Proxmox's firewall features.
  - Set VLAN tag if needed (optional).
- Set IP address to DHCP (managed by your router) or a static IP (e.g. `192.168.1.100/24`).

#### g. DNS

- Configure DNS servers at your demand.

#### h. Confirm

- Review the settings and click "Finish" to create the container.

A container will be created. Enable `start-on-boot` so that it starts automatically when the Proxmox server boots up.

### 2. /dev/tun Passthrough

Network TUNnel (or TUN) is a virtual network kernel device that provides an interface for user applications, such as NetBird, to deal with the raw network traffic. Since we set our container up as an unprivileged container, there is no access to this interface. Therefore, we have to add some lines manually to the configuration for this container. Under your main node, access the shell. Find your container number, like 100. Use nano or another text editor to open the configuration.

```bash
nano /etc/pve/lxc/100.conf
```

Add the following lines to the end of the file:

```bash
lxc.cgroup2.devices.allow: c 10:200 rwm
lxc.mount.entry: /dev/net dev/net none bind,create=dir
lxc.mount.entry: /dev/net/tun dev/net/tun none bind,create=file
```

Now, start the container and check if the TUN device is available.

```bash
# On the Proxmox host
pct start 100

# On the container
ls /dev/net
```

If you see `tun` is listed, you're ready to proceed to the next step.

### 3. NetBird Installation


