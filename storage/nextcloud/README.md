# Nextcloud in LXC

---

[Nextcloud](https://nextcloud.com) is a popular open-source self-hosted cloud storage solution. It allows you to store and access your files, calendars, contacts, and more from any device.

**Why Nextcloud?**

- **Privacy**: Nextcloud gives you full control over your data. You can host it on your own server, ensuring that your files are not stored on third-party servers.
- **Customization**: Nextcloud offers a wide range of apps and plugins that allow you to customize your cloud storage experience. You can add features such as file sharing, calendar integration, and more.
- **Collaboration**: Nextcloud allows you to collaborate with others by sharing files and folders. You can set permissions for each user, ensuring that your data is secure.
- **Accessibility**: Nextcloud can be accessed from any device with an internet connection. You can use the web interface, desktop clients, or mobile apps to access your files and data.

---

## Table of Contents

1. [LXC Setup](#1-lxc-setup)
2. [Installing Dependencies](#2-installing-dependencies)
    - [Apache2](#apache2)
    - [MariaDB Server](#mariadb-server)
    - [PHP](#php)
3. [Installing Nextcloud](#3-installing-nextcloud)

---

## 1. LXC Setup

Before we start installing Nextcloud, we need to set up an LXC container to host our Nextcloud instance. Follow the instructions in the [LXC Setup](../../proxmox/README.md#9-creating-your-first-container-optional) guide to create a new container for Nextcloud. I recommend choosing **Ubuntu 24.04 LTS** as the operating system for your container, and allocating allocating at least **2 CPU cores**, **2GB of RAM *(1-2GB of SWAP at your demand)***, and **16GB of storage** for the container. We would recommend adding a mount point for your Nextcloud data if you have additional storage available. This will allow you to store your Nextcloud data on a separate partition or disk, which can improve performance and make it easier to manage your data.

## 2. Installing Dependencies

Nextcloud requires a web server, a database server, and a runtime environment. In this guide, we will be using **Apache2** as our web server, **MariaDB** as our database server, and **PHP** as our runtime environment. To learn more about the installation process, check out the [Nextcloud documentation](https://docs.nextcloud.com/server/stable/admin_manual/installation/index.html).

Before we start installing the dependencies, make sure to update your package list and upgrade your system by running the following commands:

```bash
apt update && apt upgrade -y && apt install -y curl wget unzip ffmpeg imagemagick
```

### Apache2

[Apache2](https://httpd.apache.org/) is a popular open-source web server that is widely used to serve web applications. It is known for its stability, security, and flexibility. In this guide, we will be using **Apache 2.4**. You can install other versions if you prefer, but make sure to check the official documentation before doing so.

To install Apache2, run the following command:

```bash
apt install apache2 -y
```

Once the installation is complete, you can start Apache2 and enable it to run on boot with the following commands:

```bash
systemctl start apache2
systemctl enable apache2
```

To check if Apache2 is running properly, you can use the following command:

```bash
systemctl status apache2
```

You can also check if Apache2 is serving content by navigating to `http://<your-container-ip>` in your web browser. You should see the default Apache2 welcome page.

![Apache2 Welcome Page](./assets/apache2-welcome-page.png)

### MariaDB Server

[MariaDB](https://mariadb.org/) is a popular open-source relational database management system that is widely used to store data for web applications. It is a fork of MySQL and is known for its performance, reliability, and security. In this guide, we will be using **MariaDB 10.11**. You can install other versions of MariaDB if you prefer, but make sure to check the official documentation before doing so.

To install MariaDB, run the following command:

```bash
apt install mariadb-server -y
```

Once the installation is complete, you can start the MariaDB security installation process by running the following command:

```bash
mariadb-secure-installation
```

#### OR

```bash
mysql_secure_installation
```

This will guide you through a series of prompts to secure your MariaDB installation. You will be asked to set a root password, remove anonymous users, disallow remote root login, and remove the test database. If this is your first time installing MariaDB and you have no idea what to do, follow the instructions in the video below:

[![MariaDB Security Installation](./assets/mariadb-secure-installation-thumbnail.png)](./assets/mariadb-secure-installation.mp4)

#### Setting Up Database and User

Nextcloud requires a database and a user to connect to that database. You can create a new database and user for Nextcloud by running the following commands:

```bash
mysql -u root -p
```

This will open the MariaDB shell. Then, run the following commands to create a new database and user for Nextcloud:

```sql
CREATE DATABASE nextcloud CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
CREATE USER 'nextclouduser'@'localhost' IDENTIFIED BY 'strongpassword';
GRANT ALL PRIVILEGES ON nextcloud.* TO 'nextclouduser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

***Note:*** Make sure to replace `nextclouduser` with a username of your choice and `strongpassword` with a strong password of your choice. You will need this password later when you configure Nextcloud.

To check if the database and user were created successfully, you can run the following command:

```bash
mysql -u root -p -e "SHOW DATABASES; SHOW GRANTS FOR 'nextclouduser'@'localhost';"
```

You should see the `nextcloud` listed in the databases and the appropriate privileges for the `nextclouduser`.

### PHP

[PHP](https://www.php.net/) is a popular server-side scripting language that is widely used to develop web applications. Nextcloud is operated using PHP, so we need to install it along with the necessary PHP modules to run Nextcloud smoothly.

For the simplicity of this guide, we will use **PHP 8.3**, which is the version recommended by Nextcloud at the time of writing. You can install other versions of PHP if you prefer. Check out the [System Requirements](https://docs.nextcloud.com/server/latest/admin_manual/installation/system_requirements.html) and [PHP Modules & Configuration](https://docs.nextcloud.com/server/latest/admin_manual/installation/php_configuration.html) documentation for more details.

To install PHP, run the following command:

```bash
apt install -y php8.3 libapache2-mod-php8.3
```

We will also need some PHP modules for Nextcloud to function properly. The below command will install the necessary PHP modules for Nextcloud

```bash
apt install -y php-{curl,dom,gd,mbstring,posix,xml,json,zip,mysql,intl,imagick,exif,avconv,imap,opcache,ldap,fpm}
```

#### Caching Configuration *(optional)*

Nextcloud can use caching to improve performance. We will be using **APCu** for local caching and **Redis** for distributed caching. To install these caching modules, run the following command:

```bash
apt install -y php-{apcu,redis} redis-server
```

Once the installation is complete, you can start the Redis server and enable it to run on boot with the following commands:

```bash
systemctl start redis-server
systemctl enable redis-server
```

To check if the Redis server is running properly, you can use the following command:

```bash
systemctl status redis-server
```

You can also test the Redis server by running the following command:

```bash
redis-cli ping
```

which should return

```bash
PONG
```

#### PHP Configuration

By default, the configuration files for PHP are located in the `/etc/php/X.x/` directory *(`X.x` is the PHP version which, in this case, is `8.3`)*. The configuration for the web server (in this case, Apache2) lives in `/etc/php/8.3/apache2/php.ini`.

To optimize PHP for Nextcloud, we need to make some changes to the `php.ini` file. Open the file with your preferred text editor:

```bash
nano /etc/php/8.3/apache2/php.ini
```

Then, make the following changes:

```ini
memory_limit = 1024M
max_execution_time = 360
upload_max_filesize = 2048M
post_max_size = 2048M

opcache.enable=1
opcache.memory_consumption=256
opcache.interned_strings_buffer=16
opcache.max_accelerated_files=20000
opcache.revalidate_freq=60
```

## 3. Installing Nextcloud

Now that we have all the dependencies installed and configured, we can proceed to install Nextcloud. The latest version of Nextcloud can be downloaded from the [Nextcloud website](https://nextcloud.com/install/). You can also use the following command to download the latest version of Nextcloud:

```bash
mkdir -p /var/cache/nextcloud && cd /var/cache/nextcloud
wget https://download.nextcloud.com/server/releases/latest.zip
```

Once the download is complete, you can unzip the file and move the Nextcloud files to the Apache2 web root directory:

```bash
unzip latest.zip
mv nextcloud /var/www/html/
```
