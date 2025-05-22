# Nextcloud in LXC

<h2>Preparing your storage</h2>
<p>This step really varies depending in your setup. For me, I'm gonna partition my 2TB HDD and use 128GB for Nextcloud data. The following is what I did.</p>

<h3>1. Partitioning and Mounting</h2>
<p>Check if the server recognize the target disk</p>

```bash
lsblk
```
<p>In my case the target disk is /dev/sdb. Now, it's time to start partitioning. I'm using <mark>fdisk</mark> for this task. You may use other tools depending on your preference.</p>

```bash
# Erase disk before starting
wipefs /dev/sdb
fdisk /dev/sdb
```
<ul>
  <li>Enter <mark>g</mark> for creating a new GPT table.</li>
  <li>Enter <mark>n</mark> to create a new partition.</li>
  <li>Type in your desired partition number.</li>
  <li>Enter your desired start block (in most case you just press <mark>Enter</mark> for default start block).</li>
  <li>Enter <mark>+<i>desired-size</i>G</mark> to set the partition to the desired size. Refer to the instruction on the screen for further personalization.</li>
  <li>Enter <mark>w</mark> to exit and write changes.</li>
</ul>

<p>Now, you're having a partition for your data. Next, let's mount it and add it to Proxmox.</p>

```bash
mkdir -p /mnt/pve/nextcloud
mount /dev/sdbX /mnt/pve/nextcloud #Replace X with your partition number
echo "/dev/sdb2 /mnt/sdb2 ext4 defaults 0 2" | tee -a /etc/fstab
mount -a #Test if there's any problem with mounting
```
<p>Next, go to Proxmox Web GUI, navigate to <b>Datacenter</b> > <b>Storage</b>. Click <b>Add</b>, enter an ID <i>(e.g nextcloud)</i>, enter the path which is <mark>/mnt/pve/nextcloud</mark> in this case.</i></p>

<h3>2. Setting up container</h3>
