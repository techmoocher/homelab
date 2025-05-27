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
  <li>Enter your desired start block (in most case you just press <mark>Enter</mark> for the default start block).</li>
  <li>Enter <mark>+<i>desired-size</i>G</mark> to set the partition to the desired size. Refer to the instructions on the screen for further personalization.</li>
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
<p>Assuming that you've got your directory set up. Let's create a container (CT) for our Nextcloud. Follow the below steps if you're struggling with CT.</p>
<uL>
  <li>Click on <b>Create CT</b>. Choose the node to install the CT on, choose a number for <mark>CT ID</mark>, and give it a <mark>Hostname</mark> <i>(e.g. nextcloud, personal-storage, etc.)</i>.Set a <mark>Password</mark> for your CT. Add <mark>Tags</mark> as needed.</li>
  ![image](https://github.com/user-attachments/assets/5f53a9b0-1276-4e14-a325-10f666a3423f)
  
  <li>Choose a <mark>Storage</mark> and choose your <mark>CT template</mark>. <i><b>Note:</b> If you haven't got a CT template, you do get one by go to a storage such as <b>local</b>, navigate to <b>CT Templates</b> > <b>Templates</b> and choose one (preferably Ubuntu 24.04/22.04)</i>.</li>
  ![image](https://github.com/user-attachments/assets/0bdff1ad-1f13-4cda-81a9-1920d2acacb9)

  <li>Set up your disks. Choose a place for your CT root files, in my case, is <b>local</b>. Give the storage a size. Personally, since we will dedicate this CT only to Nextcloud, 20GiB would be enough. The below is my set up.</li>
  ![image](https://github.com/user-attachments/assets/fda3cf31-1697-486e-86d5-957938f9bb85)

  <li>Assign how many <b>CPU cores</b> the CT can use. Since my server only has 4 cores, I will assign 2 for Nextcloud.</li>
  ![image](https://github.com/user-attachments/assets/ebbcae8f-c8e0-41e0-b93d-be835f7a153a)

  <li>Assign how much <b>Memory</b> the CT can use. Personally, I prefer 1024 MiB (1 GiB) of RAM and 2048 MiB (2 GiB) of swap.</li>
  ![image](https://github.com/user-attachments/assets/f1e4981f-e32c-44c5-b432-efa9e52621c1)

  <li>Adjust the values in <b>Network</b> tab as needed. I recommend setting a <b>static IP</b> for your server so you won't need to check its IP address every time you connect to it. About the default gateway, you can find it out with <mark>ipconfig</mark> for <b>Windows</b> and <mark>ip route</mark> on <b>Linux</b>. Below is my setup.</li>
  ![image](https://github.com/user-attachments/assets/a18f736e-cd82-48db-9b00-45dabc105d93)

  <li> To use a specific DNS server, adjust the values as needed. Otherwise, leave them blank.</li>
  <li>Finally, double-check the config in the <b>Confirm</b> tab and click <b>Finish</b>. Proxmox will do the rest for you. If you will see <mark>Task OK</mark> in the log popup, you've successfully created a CT for Nextcloud.</li>
</uL>

<h3>3. Installing dependencies</h3>
<p>There are multiple ways to connect to your CT and start setting things up but this is my preferred way. Go to <b>Node</b> > <b>Shell</b> and enter the following commands</p>

```bash
pct list # List out the available CTs
pct start <CT_ID> # Replace the <CT_ID> with the ID of your Nextcloud CT
pct enter <CT_ID>
```
<p>Before we start doing anything, it's highly recommended to have your system up-to-date. To do that, enter the following commands</p>

```bash
apt update && apt upgrade
```

<p><b>(Optional)</b> Setting locale</p>

```bash
nano /etc/locale.gen
```
<p>Scroll down to <mark>en_US.UTF-8 UTF-8</mark>. Uncomment that line, exit and save changes with Ctrl + X. Finally, update locale choice with</p>

```bash
locale-gen
```

<h3>3.1 Installing <b>Apache2</b>, <b>MariaDB</b>, and <b>PHP</b></h3>
<h3>Apache2</h3>
<p>Enter the following commands to install Apache2</p>

```bash
apt install apache2
```

<p>Enter the following commands to start and enable Apache2</p>

```bash
systemctl start apache2
systemctl enable apache2
```

<p>Use the following command to check if Apache2 is running properly</p>

```bash
systemctl status apache2
```
<p>If Apache2 is running properly, you should see something like this</p>
![image](https://github.com/user-attachments/assets/007d7f6b-e712-415e-82c0-4cad5eabf7c3)

<h3>MariaDB</h3>
<p>Enter the following commands to install MariaDB</p>

```bash
apt install mariadb-server
```

<p>To start MariaDB installation, enter the following commands</p>

```bash
mariadb_secure_installation
```

<h3>PHP</h3>
<p>Enter the following commands to install PHP</p>

```bash
apt install ca-certificates apt-transport-https software-properties-common lsb-release -y
add-apt-repository ppa:ondrej/php -y
apt update && apt upgrade

# Installing PHP
apt install phpX.x libapache2-mod-phpX.x # Replace X.x with your desired PHP version (e.g. 8.2, 8.3, 8.4, etc.)
```
<i>Check out <a href="https://docs.nextcloud.com/server/latest/admin_manual/installation/php_configuration.html" target="_blank">PHP Modules & Configuration</a> for more details</i>

<p>Enter the following commands to install necessary PHP modules</p>

```bash
apt install phpX.x-{curl,gd,zip,xml,mbstring,mysql}
```
