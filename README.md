# Techmoocher Homelab
<p><i>created May 7, 2025</i> by {techmoocher}</p>
<p>The following is my experience when building my own homelab as a high school junior with two Thinkpads and some old hard drives.</p>

<h1>1. Getting started</h1>
<p>In this project, I'm going to use Proxmox to be my virtual machine's hypervisor.</p>

<h1>2. Setting up Proxmox</h1>
<h3>1. Download and install Proxmox</h3>
<p><i><b>Prerequisite:</b></i></p>
<ul>
  <li><i>A computer/laptop with at least 8GB of RAM and preferrably 200GB of hard drive</i></li>
  <li><i>A solid-state 4GB USB</i></li>
  <li><i>An Ethernet cable (Proxmox will not work well with WiFi)</i></li>
</ul>
<p>Before we start, remember to </p>

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
<p>Take a break while the machine running it updates. When it's done with no error and/or warning, it's done!</p>

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
<p><i>Skip this step as your demand</i></p>
<p><i>Recommended for servers running laptops</i></p>
<p>For me, I would love to have my laptop awake even when I close the lid. Also, I don't want my screen to get broken. To achieve that, follow the steps below.</p>

<p><b>Keeping the laptop on even when you close the lid</b></p>
<p>We will edit the <mark>logind.conf</mark> in this section to achieve that.</p>
<p>First, let's edit the file <mark>/etc/systemd/logind.conf</mark></p>

```bash
nano /etc/systemd/logind.conf
```

<p>Now, scroll down to the line <b><mark>HandleLidSwitch</mark></b>. Uncomment that line and change it to <b><mark>HandleLidSwitch=ignore</mark></b></p>
<p>Next, scroll down to the line <b><mark>HandleLidSwitchDocked</mark></b>. Uncomment that line and change it to <b><mark>HandleLidSwitchDocked=ignore</mark></b></p>
<p>Then, close the nano editing with <b>Ctrl+X</b> > <b>Y</b> > <b>Enter</b></p>
<p>After completing the above steps, we need to restart the <mark>systemd-logind.service</mark> for changes to take effect. To do that, enter the following commands</p>

```bash
systemctl restart systemd-logind.service
```

<p><b>Setting screen timeout</b></p>
<p>This step is to help protect your laptop/PC screen from getting burnt due to constant stress.</p>
<p>First, we need to edit the <mark>/etc/default/grub</mark></p>

```bash
nano /etc/default/grub
```

<p>Now, scroll down to the line <b><mark>GRUB_CMDLINE_LINUX=""</mark></b>. Next, change it to <b><mark>GRUB_CMDLINE_LINUX="consoleblank=<i>{some value}</i>"</mark></b></p>
<p><i><b>Note:</b> Change the <mark>{some value}</mark> to your desired timeout value (e.g: 300) (the unit for {some value} is seconds).</i></p>
<p>Finally, all you need to do is exit and save changes with <mark>Ctrl+X</mark> and enter the following commands in the <b>Shell</b></p>

```bash
update-grub
```

<p>If it shows the success message then you're done in this step! (most of the time it does)</p>

