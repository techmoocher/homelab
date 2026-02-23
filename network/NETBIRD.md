# NetBird Installation and Configuration

---

NetBird is a WireGuard-based VPN solution that allows you to create a secure and private network between your devices. It is designed to be easy to set up and use, and it provides a simple web interface for managing your network. In this guide, I will walk you through the installation and configuration of NetBird on your Proxmox server.

You can learn more about NetBird and its features on the [official website](https://netbird.io/).

---

## NetBird on VM

This is the quickest and most straightforward way to set up NetBird. It is also the recommended way for most users, especially if you are new to self-hosting and don't have much experience with Linux. If you already have a VM set up and a registered domain name, it should take you less than 10 minutes to get NetBird up and running. Check out the [official documentation](https://docs.netbird.io/selfhosted/selfhosted-quickstart) for more details.

***Note:*** *If you want to set up NetBird on an LXC container, please refer to the [next section](#netbird-on-lxc).*

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

#### Reverse Proxy Setup

The script will prompt you to set up a reverse proxy.

```bash
Which reverse proxy will you use?
  [0] Traefik (recommended - automatic TLS, included in Docker Compose)
  [1] Existing Traefik (labels for external Traefik instance)
  [2] Nginx (generates config template)
  [3] Nginx Proxy Manager (generates config + instructions)
  [4] External Caddy (generates Caddyfile snippet)
  [5] Other/Manual (displays setup documentation)

Enter choice [0-5] (default: 0):
```

For the simplicity of this guide, I will recommend selecting option `[0] (Traefik)`. This option includes a Traefik container in the Docker Compose that handles TLS certificates automatically via Let's Encrypt, requires no additional configuration, and makes it easy to enable the NetBird Proxy in the next step.

> ***Note:*** *If you already have a reverse proxy set up, you can select the appropriate option and follow the instructions provided by the installation script to configure it for NetBird.*
>
> Check out the [official documentation](https://docs.netbird.io/selfhosted/reverse-proxy) for more details on reverse proxy configuration.

If you selected Traefik, the script will ask whether you want to enable the NetBird Proxy feature.

```bash
Do you want to enable the NetBird Proxy service?
The proxy allows you to selectively expose internal NetBird network resources
to the internet. You control which resources are exposed through the dashboard.
Enable proxy? [y/N]:
```

If you select `y`, the script will ask for a **proxy domain**.

```bash
NOTE: The proxy domain must be different from the management domain (netbird.example.com)
to avoid TLS certificate conflicts.

You also need to add two CNAME records with one wildcard for the proxy domain,
e.g. proxy.example.com and *.proxy.example.com pointing to the same server IP as netbird.example.com.

Enter the domain for the NetBird Proxy (e.g. proxy.netbird.example.com):
```

The proxy domain must be different from your NetBird management domain to avoid TLS certificate conflicts. The script then automatically generates a proxy access token, creates a proxy.env configuration file, and starts the proxy container alongside the other services. Point a wildcard DNS record (e.g. `*.proxy.netbird.example.com`) to your server's IP address so that service subdomains resolve correctly.

#### CNAME Records for Proxy Domain

For certificates to work properly, ensure you have the proper records set with your domain name registrar. The first A record below should already be setup prior to starting the quick start script.

| TYPE  | NAME    | CONTENT                | PROXY STATUS (CLOUDFLARE) |
|-------|---------|------------------------|---------------------------|
| A     | @       | YOUR.SERVER.IP.ADDRESS | DNS Only                  |
| CNAME | proxy   | netbird.example.com    | DNS Only                  |
| CNAME | *.proxy | netbird.example.com    | DNS Only                  |

### 3. Onboarding

Once the installation is complete, you can access the NetBird dashboard by navigating to your domain (e.g. `https://netbird.example.com`) in a web browser. By default, the script installs NetBird without any pre-configured users, so you will need to create an account and set up your network before you can start using it.

1. In your browser, go to `https://netbird.example.com`, which will redirect you to the `/setup` page.
2. Create your administrator account.
  a. Enter your email address.
  b. Enter your name.
  c. Create a password.
  d. Click on *Create Account*.

You will then be able to log in with your email and password.

Now that you have access to the dashboard, you can start adding devices to your network and configuring your settings. For more information on how to use NetBird and its features, check out the [official documentation](https://docs.netbird.io/selfhosted/selfhosted-quickstart) for more details.

---

## NetBird on LXC

NetBird can also be installed on an LXC container. This method is more complex than installing on a VM, but it can be more efficient in terms of resource usage. If you are comfortable with Linux and have experience with LXC containers, this may be a good option for you.

### 1. Container Setup

First, we need to create an LXC container for NetBird. You can do this using the Proxmox web UI or the command line. Check the [LXC Setup Guide](../proxmox/README.md#8-creating-your-first-container-optional) for detailed instructions on how to create a container.

***Note:*** *For NetBird, I would recommend allocating at least **1 CPU** and **2 GB of memory** to the container.*

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

### 3. LXC Nameserver Configuration *(optional)*

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

Now that you have NetBird installed and configured, you can start adding devices to your network and enjoy secure and private connectivity between them. Be sure to check out the [official documentation](https://docs.netbird.io/selfhosted/selfhosted-quickstart) for more information on how to use NetBird and its features.
