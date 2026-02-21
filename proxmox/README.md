# Proxmox Installation and Configuration Walkthrough

---

[Proxmox Virtual Environment](https://www.proxmox.com/en/proxmox-ve) (a.k.a Proxmox VE) is an open-source server virtualization management platform that allows you to easily create and manage virtual machines and containers. It is based on Debian Linux and uses KVM (Kernel-based Virtual Machine) for virtualization. Proxmox VE provides a web-based UI for managing your virtual environment, making it easy to create, configure, and monitor your virtual machines and containers. It also supports features like high availability, live migration, and storage management, making it a powerful tool for both homelabs and enterprise environments.

---

## 1. Installing Proxmox

Before we start, make sure you have a bootable USB drive with Proxmox on it. You can follow the [official Proxmox installation guide](https://proxmox.com/en/products/proxmox-virtual-environment/get-started) to create one. Once you have your bootable USB drive ready, insert it into your machine and boot from it. Follow the on-screen instructions to install Proxmox on your machine.

After the installation is complete, you can access the Proxmox web interface by navigating to `https://<your-node-ip>:8006` in your web browser. Now, you will be prompted to log in. Use the username `root` and the password you set during the installation process to log in. Once you are logged in, you will see the Proxmox dashboard where you can manage your virtual machines, containers, storage, and more.

![Proxmox dashboard](../.github/assets/images/proxmox-dashboard.png)

## 2. Updating Repos

By default, Proxmox uses the enterprise apt repository which requires a subscription. Since we're using Proxmox for personal usage, we will change it to the no-subscription repository to get access to updates without needing a subscription.

To get started, in your Proxmox web interface, navigate to **Your node** > **Updates** > **Repositories**. You will see a warning that says `"The enterprise repository is enabled, but there is no active subscription!"`

![Proxmox Updates Repositories](../.github/assets/images/updates-repos.png)

In the **APT Repositories** section, navigate to the options that have **Components** labeled `enterprise` (those that have URIs starting with `https://enterprise.proxmox.com/`), and click on the **Disable** button to disable it. You will see the pop-up warning, click **OK** to skip it.

![Disable enterprise repository](../.github/assets/images/disabling-enterprise.png)

After that, click on the **Add** button to add a new repository. In the pop-up window, in the **Repository** line, click on the toggle-list and choose **No-Subscription**. Then, click **Add** to add the no-subscription repository. The URI should now be `https://download.proxmox.com/debian/pve`, and the components should be `pve-no-subscription`.

To have the changes take effect, enter the following command to update the package lists from the new repository.

```bash
apt update && apt upgrade -y
```

## 3. Deleting local-lvm *(optional)*

> Skip this step if you would like to use the LVM (Logical Volume Management) created by default by Proxmox

You may have noticed that there is a storage labeled `local-lvm` in your Proxmox dashboard. This storage is created by Proxmox by default and uses LVM to manage the storage. In my case, I don't want to keep it, and I want to have my things (ISO images, containers, backups) in `local` (a.k.a the standard directory-based storage).

> **WARNING:**
> This action is destructive and irreversible. Make sure no VM or CT is using local-lvm before removing it.

To remove the `local-lvm`, first, navigate to **Datacenter** > **Storage**. Choose the `local-lvm` option, click **Remove**, and click **Yes** to confirm. This will remove the `local-lvm` storage from your Proxmox. However, it will not delete the LVM itself, so we need to do that manually. To do that, navigate to **Node** > **Shell** and enter the following commands to remove the LVM and resize the root partition to use the full disk space.

```bash
lvremove /dev/pve/data                # remove the LVM
lvresize -l +100%FREE /dev/pve/root   # resize the root partition to use the full disk space
resize2fs /dev/mapper/pve-root        # resize the filesystem to use the full partition
```

To check if the changes are successful, you can use the following command to check the disk space.

```bash
df -h
lvdisplay
```

You should see that the `local-lvm` storage is removed and the root partition is resized to use the full disk space. If you don't see the changes, try rebooting your Proxmox server, and check again (repeat the above steps if necessary).

## 4. Enabling IOMMU *(optional)*

> Skip this step at your demand. Highly recommended if you plan to use hardware passthrough in the future.

An Input-Output Memory Management Unit (IOMMU) is a hardware component that allows the system to manage memory for I/O devices, such as graphics cards, network cards, and storage controllers. It provides a way for the system to map device memory to physical memory, which can improve performance and security. Enabling IOMMU can be beneficial for virtualization and hardware passthrough, as it allows virtual machines to directly access hardware resources without going through the hypervisor. You can learn more about IOMMU at its [Wikipedia page](https://en.wikipedia.org/wiki/Input%E2%80%93output_memory_management_unit).

To enable IOMMU, we will need to edit the GRUB configuration file.

```bash
nano /etc/default/grub
```

Scroll down until you find the line that says `GRUB_CMDLINE_LINUX_DEFAULT="quiet"`. This line is responsible for passing kernel parameters to the Linux kernel at boot time when the system is in normal mode. To enable IOMMU, change it to

```bash
GRUB_CMDLINE_LINUX_DEFAULT="quiet intel_iommu=on iommu=pt"
```

***Note:*** *If you are using AMD CPU, you should use `amd_iommu=on` instead.*

After that, save the file and exit. For the changes to take effect, update GRUB and reboot.

```bash
update-grub
reboot
```

When your system is back up, you can check if IOMMU is enabled with the following command.

```bash
dmesg | grep -e IOMMU
dmesg | grep 'remapping'
```

If you don't see any errors, it's a good sign that your system is working properly. If you happen to get any errors, reference to the [wiki](https://pve.proxmox.com/wiki/PCI_Passthrough) for more information.

You should see something like this, which indicates that IOMMU is enabled and working properly.

```bash
DMAR: IOMMU enabled

DMAR-IR: Enabled IRQ remapping in xapic mode    # x2apic mode in some systems
```

## 5. Keeping your server awake *(optional)*

> Skip this step at your demand. Highly recommended for servers running on laptops.

For me, due to availabibility purposes, I want to have my server awake even the lid is accidentially closed. To achieve that, we will need to edit the `logind.conf` file.

```bash
nano /etc/systemd/logind.conf   # you can use any text editor you like, but I will use nano for this example
```

Scroll down until you find the section that says `#HandleLidSwitch=...`, `#HandleLidSwitchExternalPower=...`, and `#HandleLidSwitchDocked=...`. These options are responsible for what happens when you close the lid of your laptop. To keep your server awake when the lid is closed, remove the `#` to uncomment and change them to

```bash
HandleLidSwitch=ignore
HandleLidSwitchExternalPower=ignore
HandleLidSwitchDocked=ignore
```

Make sure to save the file before exiting. For the changes to take effect, we need to restart the `systemd-logind.service` with the following command.

```bash
systemctl restart systemd-logind.service
```

## 6. Setting screen timeout *(optional)*

> Skip this step at your demand. Highly recommended for servers running on laptops.

To protect your screen from getting burnt due to constant workload, you may want to set a screen timeout to turn off the display after a certain period of inactivity. To do that, we will need to edit the GRUB configuration file.

First, open the GRUB configuration file with the following command.

```bash
nano /etc/default/grub
```

Scroll down until you find the line that says `GRUB_CMDLINE_LINUX=""`. This line is responsible for passing kernel parameters to the Linux kernel at boot time. To set the screen timeout, change it to

```bash
GRUB_CMDLINE_LINUX="consoleblank=<some value>"
```

***Note:*** *Set `<some-value>` (in seconds) to your desired timeout value (e.g: 300, which is 5 minutes).*

After that, save the file and exit. For the changes to take effect, update GRUB with the following command.

```bash
update-grub
```

## 7. Setting up firewall *(optional)*

> Skip this step at your demand. Highly recommended for security purposes.

Proxmox has a built-in firewall that you can use to secure your server. In this guide, we will use the **Shell** to set up the firewall, but you can also use the Proxmox web UI if you prefer a graphical user interface.

### Cluster-wide Setup

The cluster-wide firewall configuration is located at `/etc/pve/firewall/cluster.fw`.

```bash
nano /etc/pve/firewall/cluster.fw
```

The cluster-wide firewall is disabled by default. You can enable it by setting the `enable` option to `1`. You can also add your own rules to the file to allow or block specific traffic. In this example, we will allow ping and SSH traffic from the LAN, and block everything else.

```bash
[OPTIONS]
enable: 1

policy_in: DROP
policy_out: ACCEPT

log_ratelimit: enable=1,burst=10,rate=5/second

[RULES]
IN ACCEPT -source 192.168.50.0/24 -p icmp -log nolog -icmp-type any     # Allow ping from LAN
IN ACCEPT -source 192.168.50.0/24 -p tcp -dport 22 -log warning         # Allow SSH from LAN
IN ACCEPT -source 192.168.50.0/24 -p tcp -dport 8006 -log warning       # Allow Proxmox Web UI from LAN
```

### Host-specific Setup

The host-specific firewall configuration is located at `/etc/pve/nodes/<nodename>/host.fw`.

***Note:*** *You can find your node name using the `hostname` command in the shell.*

```bash
nano /etc/pve/nodes/<nodename>/host.fw
```

The host-specific firewall is enabled by default. You can add your own rules to the file to allow or block specific traffic. In this example, we will allow ping and SSH traffic from the LAN, and block everything else.

```bash
[OPTIONS]
enable: 1

log_level_in: warning
log_level_out: nolog
log_level_forward: nolog

nosmurfs: 1
smurf_log_level: warning

tcpflags: 1
tcp_flags_log_level: warning

ndp: 1
```

After finishing the configuration, save the file and exit. For the changes to take effect, you need to restart the firewall with the following command.

```bash
systemctl restart pve-firewall.service
```

To check if the firewall is working properly, you can use the following command to check the status of the firewall.

```bash
systemctl status pve-firewall.service
pve-firewall status
```

You should see that the firewall is active and running without any errors. You can also check the logs to see if any traffic is being blocked or allowed according to your rules.

## 8. Connecting to Cloudflare Tunnel *(optional)*

> Skip this step at your demand. Highly recommended for remote access to your Proxmox server.

Cloudflare Tunnel is a service that allows you to securely expose your local server to the internet without having to open any ports on your router. It creates a secure tunnel between your local server and Cloudflare's network, allowing you to access your server from anywhere in the world using a unique URL provided by Cloudflare. You can learn more about Cloudflare Tunnel at its [official documentation](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/).

> Before we start, make sure you have a Cloudflare account and a domain name that you can use for your tunnel.

To connect your Proxmox server to Cloudflare Tunnel, we need to install the `cloudflared` daemon on your Proxmox server.

```bash
# Add cloudflare gpg key
mkdir -p --mode=0755 /usr/share/keyrings
curl -fsSL https://pkg.cloudflare.com/cloudflare-public-v2.gpg | tee /usr/share/keyrings/cloudflare-public-v2.gpg >/dev/null

# Add this repo to your apt repositories
echo 'deb [signed-by=/usr/share/keyrings/cloudflare-public-v2.gpg] https://pkg.cloudflare.com/cloudflared any main' | tee /etc/apt/sources.list.d/cloudflared.list

# Install cloudflared
apt-get update && apt-get install cloudflared -y
```

After you have installed `cloudflared`, you can install a service to automatically run your tunnel whenever your machine starts with the following command.

```bash
cloudflared service install <tunnel-token>
```

You should see the following messages, which indicates that the tunnel is successfully installed and running.

```bash
<date-time> INF Using Systemd
<date-time> INF Linux service for cloudflared installed successfully
```

***Note:*** *Make sure to replace `<tunnel-token>` with the actual tunnel token that you can get from the Cloudflare dashboard when you create a new tunnel. After running the command, it will automatically create a systemd service for your tunnel and start it.*

Please note that this is not the only way to securely expose your Proxmox server to the Internet, but it's one of the easiest and trusted ways to do it without having to deal with port forwarding and DDNS. There are many options out there like [Ngrok](https://ngrok.com/), [Tailscale](https://tailscale.com/), [NetBird](https://netbird.io/), and more, so feel free to explore and choose the one that suits your needs the best.

---

Now, you have successfully installed Proxmox and done some basic configurations. You can now start creating virtual machines, containers, and more to explore the capabilities of Proxmox. You can check out the [How To Use This Repo](../README.md#how-to-use-this-repo) in the [README](../README.md) for more.

I hope this guide is helpful for you in your homelab journey. If you have any questions or suggestions, feel free to reach out to me through email or opening an issue in this repository.

**HAPPY SELF-HOSTING!!!**
