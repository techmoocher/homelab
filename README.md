# A Journey of a Hobbyist

<div align="center">
    <h1>【 techmoocher's homelab 】</h1>
</div>

---

<div align="center">
    <img src="https://img.shields.io/github/last-commit/techmoocher/homelab?&style=for-the-badge&color=87FFAF&logo=git&logoColor=D9E0EE&labelColor=1E202B" />
    <img src="https://img.shields.io/github/stars/techmoocher/homelab?style=for-the-badge&logo=andela&color=FFFF7D&logoColor=D9E0EE&labelColor=1E202B" />
    <img src="https://img.shields.io/github/repo-size/techmoocher/homelab?color=A5E1FF&label=SIZE&logo=protondrive&style=for-the-badge&logoColor=D9E0EE&labelColor=1E202B" />
</div>

---

You are reading my personal notes on setting up a self-hosted server (a.k.a homelab) using Proxmox. This is not a tutorial, but more of an anecdotal documentation of my own experience. My main reason for writing this is to log my journey in self-hosting and to share my experience with hobbyists who are interested in self-hosting but don't know where to start. I know that there are already many good tutorials on setting up a homelab, but I hope this can be a good starting point for you to get into self-hosting and have fun with it!

## My Hardware

As a full-time student and part-time hobbyist, I have a limited budget for my homelab. Thus, I digged into the pile of old tech gadgets in my dad's garage and decided to utilized the following as my set up:

- **ThinkPad T450 (Intel i5-5300U/Intel HD Graphics 5500/8GB RAM/228GB SSD)** *(Proxmox server)*
- **A 2TB WD Purple** *(storage)*

## Getting Started

### 1. Installing Proxmox

Before we start, make sure you have a bootable USB drive with Proxmox on it. You can follow the [official Proxmox installation guide](https://proxmox.com/en/products/proxmox-virtual-environment/get-started) to create one. Once you have your bootable USB drive ready, insert it into your machine and boot from it. Follow the on-screen instructions to install Proxmox on your machine. After the installation is complete, you can access the Proxmox web interface by navigating to `https://<your-node-ip>:8006` in your web browser.

### 2. First login

After you have successfully installed Proxmox and accessed the web interface, you will be prompted to log in. Use the username `root` and the password you set during the installation process to log in. Once you are logged in, you will see the Proxmox dashboard where you can manage your virtual machines, containers, storage, and more.

[Proxmox dashboard](.github/images/proxmox-dashboard.png)

<h3>2. Updating repos</h3>
<p>Proxmox has enterprise apt repo by default. Since we're using it for personal usage, we will change it to no-subscription</p>
<p>To get started, navigate to your node (aka click on the button that labeled your <b><i>hostname</i></b>)</p>
<p>Go to <b>Updates</b> -> <b>Repositories</b></p>
<p>You will see a warning <i>"The enterprise repository is enabled, but there is no active subscription!"</i></p>
<p>Scroll down to the options that has <b>Components</b> labeld <b><i>enterprise</i></b> (aka those that has URIs <i>"https://enterprise.proxmox.com/..."</i>), click on <b>Disable</b> button to disable it.</p>
<p>Now, click the <b>Add</b> button. There would be a warning popping up so click <b>OK</b> to skip it. Then, you will be shown a menu, in the <b>Repository</b> line, click on the toggle-list and choose <b>No-Subscription</b>, then click <b>Add</b>.</p>
<p>You're not done yet!</p>
<p>Now, go to <b>Shell</b> and enter the following commands to finish updating your apt repository and have your programs up-to-date</p>

```bash
apt update && apt upgrade
```

<h3>3. Deleting local-lvm <i>(optional)</i></h3>
<p><i>Skip this step if you would like to use the LVM (Logical Volume Management) created by default by Proxmox</i></p>
<p>If you check the machine, you will see there is a storage labeled <mark>local-lmv</mark>. This one is created by Proxmox by default. In my case, I don't want to keep it, but I want to have my things (ISO images, containers, backups) in <mark>local</mark> (aka standard directory-based storage).</p>
<p>To remove the <mark>local-lvm</mark>, first, navigate to <b>Datacenter</b> > <b>Storage</b>. Choose the <mark>lvm-local</mark> option, click <b>Remove</b>, and click <b>Yes</b> to confirm.</p>
<p>Next, navigate to <b>Node</b> > <b>Shell</b> and enter the following commands</p>

```bash
lvremove /dev/pve/data
lvresize -l +100%FREE /dev/pve/root
resize2fs /dev/mapper/pve-root
```
<p>To check whether you have your full hard drive in the `local` storage, navigate to `local` and check <b>Usage</b></p>

<h3>4. Keeping your server awake ☕ <i>(optional)</i></h3>
<p><i>Skip this step as your demand. Highly recommended for servers running on laptops</i></p>
<p>For me, I would love to have my laptop awake even when I close the lid. Also, I don't want my screen to get burnt due to constant workload. That's the reason why I highly recommend doing the following steps.</p>

<p><b>Keeping the laptop on even when you close the lid</b></p>
<p>We will edit the <mark>logind.conf</mark> in this section to achieve that.</p>
<p>First, let's edit the file <mark>/etc/systemd/logind.conf</mark>.</p>

```bash
nano /etc/systemd/logind.conf
```

<p>You will see the two lines <b><mark>HandleLidSwitch</mark></b> and <b><mark>HandleLidSwitchDocked</mark></b>. Uncomment those and change them to <b><mark>HandleLidSwitch=ignore</mark></b> and <b><mark>HandleLidSwitchDocked=ignore</mark></b>, respective.</p>
<p>After that, close the nano editing with <b>Ctrl+X</b> > <b>Y</b> > <b>Enter</b>.</p>
<p>After completing the above steps, we need to restart the <mark>systemd-logind.service</mark> for changes to take effect.</p>

```bash
systemctl restart systemd-logind.service
```

<p><b>Setting screen timeout</b></p>
<p>This step is to help protect your laptop/PC screen from getting burnt due to constant stress.</p>
<p>First, we need to edit the <mark>/etc/default/grub</mark></p>

```bash
nano /etc/default/grub
```

<p>You will see the line <b><mark>GRUB_CMDLINE_LINUX=""</mark></b>. Next, change it to <b><mark>GRUB_CMDLINE_LINUX="consoleblank=<i>{some value}</i>"</mark></b></p>
<p><i><b>Note:</b> Change the <mark>{some value}</mark> to your desired timeout value (e.g: 300) (the unit for {some value} is seconds).</i></p>
<p>Finally, all you need to do is exit and save changes with <mark>Ctrl+X</mark> and enter the following commands in the <b>Shell</b></p>

```bash
update-grub
```

<h3>5. Enabling IOMMU</h3>
<p>An IOMMU (Input-Output Memory Management Unit) is a hardware component that provides memory management for direct memory access (DMA) capable devices, such as GPUs, network cards, or storage controllers. It translates device-visible virtual addresses to physical memory addresses, similar to how a CPU's MMU works for processes. <i>(read more at <a href="https://en.wikipedia.org/wiki/Input%E2%80%93output_memory_management_unit" target="_blank">Wikipedia</a>)</i></p>
<p>To enable IOMMU, we have to configure our Grub</p>

```bash
nano /etc/default/grub
```

<p>Then, you will need to find the line <mark>GRUB_CMDLINE_LINUX_DEFAULT="quiet"</mark>. Change it to <mark>GRUB_CMDLINE_LINUX_DEFAULT="quiet intel_iommu=on"</mark>. <i><b>Note:</b> If you are using AMD CPU, you should change <mark>intel_iommu</mark> to <mark>amd_iommu</mark>.</i></p>
<p>After that, you need to update GRUB. A reboot is also recommended to make sure the changes take effect.</p>

```bash
update-grub
reboot
```

<p>To make sure the changes you made are working properly, use the following commands to check.</p>

```bash
dmesg | grep -e DMAR -e IOMMU
dmesg | grep 'remapping'
```
<p>If you don't see any errors or unknowns, it's a good sign that your system is working properly. If you happen to get any erros, reference to the wiki for troubleshooting.</p>
<p>For the second command, you should get something like</p>

```bash
DMAR-IR: Enabled IRQ remapping in xapic mode
```
<p>or</p>

```bash
DMAR-IR: Enabled IRQ remapping in x2apic mode
```

