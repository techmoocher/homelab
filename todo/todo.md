Below is the **clean, production-ready way** to install **Nginx + PHP-FPM + MariaDB + Redis for Nextcloud** on **Ubuntu** inside your LXC.

This assumes:

* Fresh Ubuntu 24.04 container
* 2 cores / 3GB RAM
* You’ll expose it via Cloudflare Tunnel (so no local TLS needed)

---

# 1️⃣ Update System

```bash
apt update && apt upgrade -y
```

---

# 2️⃣ Install Required Packages

Ubuntu 24.04 ships with PHP 8.3 by default (good for Nextcloud).

Install everything:

```bash
apt install -y nginx mariadb-server redis-server \
php-fpm php-mysql php-gd php-curl php-xml php-mbstring \
php-zip php-intl php-bcmath php-gmp php-imagick php-apcu
```

Enable and start services:

```bash
systemctl enable nginx mariadb redis-server php8.3-fpm
systemctl start nginx mariadb redis-server php8.3-fpm
```

---

# 3️⃣ Tune PHP (Important)

Edit:

```
/etc/php/8.3/fpm/php.ini
```

Set:

```ini
memory_limit = 1024M
max_execution_time = 360
upload_max_filesize = 2048M
post_max_size = 2048M

opcache.enable=1
opcache.memory_consumption=192
opcache.interned_strings_buffer=16
opcache.max_accelerated_files=20000
opcache.revalidate_freq=60
```

Leave:

```ini
disable_functions =
```

Restart PHP:

```bash
systemctl restart php8.3-fpm
```

---

# 4️⃣ Tune PHP-FPM Pool (For 2 Cores)

Edit:

```
/etc/php/8.3/fpm/pool.d/www.conf
```

Set:

```ini
pm = dynamic
pm.max_children = 12
pm.start_servers = 3
pm.min_spare_servers = 2
pm.max_spare_servers = 4
```

Restart:

```bash
systemctl restart php8.3-fpm
```

---

# 5️⃣ Secure MariaDB

Run:

```bash
mysql_secure_installation
```

Then create database:

```bash
mysql -u root -p
```

Inside MariaDB:

```sql
CREATE DATABASE nextcloud CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
CREATE USER 'ncuser'@'localhost' IDENTIFIED BY 'STRONG_PASSWORD';
GRANT ALL PRIVILEGES ON nextcloud.* TO 'ncuser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

---

# 6️⃣ Tune MariaDB (Important for 3GB RAM)

Edit:

```
/etc/mysql/mariadb.conf.d/50-server.cnf
```

Add under `[mysqld]`:

```ini
innodb_buffer_pool_size = 512M
innodb_log_file_size = 128M
innodb_flush_method = O_DIRECT
```

Restart:

```bash
systemctl restart mariadb
```

---

# 7️⃣ Download Nextcloud

Go to:

```bash
cd /var/www
wget https://download.nextcloud.com/server/releases/latest.zip
apt install unzip -y
unzip latest.zip
chown -R www-data:www-data nextcloud
chmod -R 750 nextcloud
```

---

# 8️⃣ Create Nginx Config for Nextcloud

Create:

```
/etc/nginx/sites-available/nextcloud
```

Paste:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    root /var/www/nextcloud;
    index index.php index.html;

    client_max_body_size 2048M;

    location / {
        try_files $uri $uri/ /index.php$request_uri;
    }

    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/run/php/php8.3-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }

    location ~ /\.ht {
        deny all;
    }
}
```

Enable site:

```bash
ln -s /etc/nginx/sites-available/nextcloud /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

---

# 9️⃣ Configure Redis in Nextcloud

After installation completes, edit:

```
/var/www/nextcloud/config/config.php
```

Add:

```php
'memcache.local' => '\OC\Memcache\APCu',
'memcache.locking' => '\OC\Memcache\Redis',
'redis' => [
    'host' => 'localhost',
    'port' => 6379,
],
```

---

# 🔟 Configure Cron (Do NOT Skip)

```bash
crontab -u www-data -e
```

Add:

```bash
*/5 * * * * php -f /var/www/nextcloud/cron.php
```

---

# 11️⃣ Cloudflare Tunnel

Install cloudflared and configure it to proxy:

```
http://localhost:80
```

In `config.php` add:

```php
'trusted_domains' => [
    'yourdomain.com',
],
'trusted_proxies' => ['127.0.0.1'],
'overwrite.cli.url' => 'https://yourdomain.com',
'overwriteprotocol' => 'https',
```

No need to configure HTTPS locally.

---

# ✅ Final Result

You now have:

* Nginx
* PHP 8.3 FPM tuned for 2 cores
* MariaDB tuned for 3GB RAM
* Redis for locking
* Ready for Cloudflare Tunnel exposure

This is a proper production-grade setup for your hardware.

---

If you want, I can next give you:

* A hardened Nginx config optimized specifically for Nextcloud
* Or a checklist to verify everything is configured correctly before exposing it to the internet
