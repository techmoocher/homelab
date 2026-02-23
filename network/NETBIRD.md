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

Once the script is finished, it will prompt you to enter your domain name and email address for SSL certificate generation. After you provide the required information, the script will set up NetBird using Docker and docker-compose. You can configure the installation by editing the `docker-compose.yml`. Check out the [official documentation](https://docs.netbird.io/selfhosted/configuration-files) for more details.

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

### 3. LXC Nameserver Configuration

The TUN passthrough may cause DNS resolution issues in the container. To fix this, we need to configure the nameservers manually. Open the `/etc/pve/lxc/100.conf` file on your host and add the following line:

```bash
nameserver: <your_dns_server_ip>
```

***Note:*** *Replace `<your_dns_server_ip>` with the IP address of your DNS server (e.g. `1.1.1.1` or your router's IP address).*

### 4. NetBird Setup Key

> Skip this step if you already have a setup key from a previous installation. You can reuse the same key for multiple installations.

Before we can install NetBird, we need to generate a setup key. This key is used to authenticate the installation and link it to your NetBird account. You can generate a setup key from the NetBird web UI.

To generate a setup key, follow these steps:

1. Go to your [NetBird Dashboard](https://app.netbird.io/).
2. Navigate to the **Setup Keys** section.
3. Click on **Create Setup Key**.
4. Enter a name for the setup key (e.g. "Proxmox LXC").
5. Set an expiration date for the key *(optional, recommended for enhanced security)*.
6. Add the key to group(s) *(optional)*.
7. Click on **Create** to generate the key.
8. Copy the key and store it securely, as you will need it for the installation process.

### 5. NetBird Installation

To install NetBird on the LXC container, you can use the same installation script as for the VM. On the container's shell, run the following command:

```bash
apt update && apt upgrade -y
apt install curl -y
curl -fsSL https://pkgs.netbird.io/install.sh | sh
```

Once the installation is complete, connect the LXC to your NetBird account using the setup key you generated earlier.

```bash
netbird up --setup-key <your_setup_key>
```

You should see a message confirming that the connection was successful. You can now manage your NetBird network from the web UI.

---

Now that you have NetBird installed and configured, you can start adding devices to your network and enjoy secure and private connectivity between them. For more information on how to use NetBird and its features, check out the [official documentation](https://docs.netbird.io/).
