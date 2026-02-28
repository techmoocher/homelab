# Nextcloud in LXC

---

[Nextcloud](https://nextcloud.com) is a popular open-source self-hosted cloud storage solution. It allows you to store and access your files, calendars, contacts, and more from any device.

**Why Nextcloud?**

- **Privacy**: Nextcloud gives you full control over your data. You can host it on your own server, ensuring that your files are not stored on third-party servers.
- **Customization**: Nextcloud offers a wide range of apps and plugins that allow you to customize your cloud storage experience. You can add features such as file sharing, calendar integration, and more.
- **Collaboration**: Nextcloud allows you to collaborate with others by sharing files and folders. You can set permissions for each user, ensuring that your data is secure.
- **Accessibility**: Nextcloud can be accessed from any device with an internet connection. You can use the web interface, desktop clients, or mobile apps to access your files and data.

---

## 1. LXC Setup

Before we start installing Nextcloud, we need to set up an LXC container to host our Nextcloud instance. Follow the instructions in the [LXC Setup](../../proxmox/README.md#9-creating-your-first-container-optional) guide to create a new container for Nextcloud. I recommend choosing **Ubuntu 24.04 LTS** as the operating system for your container, and allocating allocating at least **2 CPU cores**, **2GB of RAM *(1-2GB of SWAP at your demand)***, and **16GB of storage** for the container. We would recommend adding a mount point for your Nextcloud data if you have additional storage available. This will allow you to store your Nextcloud data on a separate partition or disk, which can improve performance and make it easier to manage your data.

## 2. Installing Dependencies

Nextcloud requires a web server, a database server, and a runtime environment. In this guide, we will be using **Nginx** as our web server, **MariaDB** as our database server, and **PHP** as our runtime environment. To learn more about the installation process, check out the [Nextcloud documentation](https://docs.nextcloud.com/server/stable/admin_manual/installation/index.html).

Before we start installing the dependencies, make sure to update your package list and upgrade your system by running the following commands:

```bash
apt update && apt upgrade -y && apt install -y curl wget unzip ffmpeg imagemagick
```

### Apache2

[Nginx](https://www.nginx.com/) is a popular open-source web server that is widely used to serve web applications. It is known for its high performance, scalability, and security. In this guide, we will be using **Nginx 1.24**. You can install other versions of Nginx if you prefer, but make sure to check the official documentation before doing so.

To install Nginx, run the following command:

```bash
apt install nginx -y
```

Once the installation is complete, you can start Nginx and enable it to run on boot with the following commands:

```bash
systemctl start nginx
systemctl enable nginx
```

To check if Nginx is running properly, you can use the following command:

```bash
systemctl status nginx
```

#### AND

```bash
curl http://localhost
```

which should return the content of the [default Nginx welcome page](./assets/index.nginx-debian.html)

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

[![MariaDB Security Installation](https://raw.githubusercontent.com/techmoocher/homelab/main/storage/nextcloud/assets/mariadb-secure-installation-thumbnail.png)](https://raw.githubusercontent.com/techmoocher/homelab/main/storage/nextcloud/assets/mariadb-secure-installation.mp4)

Once you have completed the security installation process, you're good to go.

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

By default, the configuration files for PHP are located in the `/etc/php/X.x/` directory *(`X.x` is the PHP version which, in this case, is `8.3`)*. The configuration for the web server (which is what we will use) lives in `/etc/php/8.3/apache2/php.ini`.

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
