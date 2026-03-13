### PHP CONFIGURATION FILE FOR NEXTCLOUD
#
### This is a sample configuration file for Nextcloud. You should copy this file to
### /var/www/nextcloud/config/config.php and adjust the settings according to
### your environment.
#
### /var/www/nextcloud/config/config.php

<?php
$CONFIG = array (
  'instanceid' => 'instance_id',
  'passwordsalt' => 'password_salt',
  'secret' => 'secret',
  
  ### NETWORK ###
  'trusted_domains' => 
  array (
    0 => 'your-container-ip',
    1 => 'nextcloud.example.com',
  ),
  ### Uncomment the following line and adjust the config according to
  ### your reverse proxy setup (if applicable)
  // 'overwritecondaddr' => '^your\.reverse\.proxy\.ip$',
  // 'overwriteprotocol' => 'https',
  // 'overwrite.cli.url' => 'https://nextcloud.example.com',
  'trusted_proxies' => 
  array (
    0 => '127.0.0.1',
    1 => '::1',
    ## Add the IP addresses of your reverse proxy server
    ## according to your reverse proxy setup (if applicable)
    // 2 => 'your-reverse-proxy-ip',
  ),
  'forwarded_for_headers' => 
  array (
    0 => 'HTTP_X_FORWARDED_FOR',
    ## Add additional headers according to your reverse proxy setup (if applicable)
    // 1 => 'HTTP_CF_CONNECTING_IP',
  ),
  ## Uncomment the following lines to restrict access to the admin
  ## interface to specific IP ranges (adjust according to your network setup)
  // 'allowed_admin_ranges' => 
  // array (
  //   0 => '127.0.0.1/8',
  //   1 => '192.168.50.0/24', // Only allows your specific home router's subnet
  // ),

  ### Database Configuration ###
  'datadirectory' => '/nextcloud-data',
  'dbtype' => 'mysql',
  'version' => '33.0.0.16',
  'dbname' => 'nextcloud',
  'dbhost' => 'localhost',
  'dbtableprefix' => 'oc_',
  'mysql.utf8mb4' => true,
  'dbuser' => 'nextclouduser',
  'dbpassword' => 'strongpassword',
  'installed' => true,

  ### CACHING (Redis + APCu) ###
  'memcache.local' => '\OC\Memcache\APCu',
  'memcache.distributed' => '\OC\Memcache\Redis',
  'memcache.locking' => '\OC\Memcache\Redis',
  'redis' => 
  array (
    'host' => '/run/redis/redis-server.sock',
    'port' => 0,
  ),
  ## If you are using Redis with TCP instead of a Unix socket,
  ## use the following configuration instead (uncomment and adjust accordingly).
  ## Make sure to comment out the previous 'redis' configuration if you do this.
  // 'redis' => 
  // array (
  //   'host' => '127.0.0.1',
  //   'port' => 6379,
  //   'timeout' => 0.0,
  // ),

  ### OTHERS ###
  # LOGGING
  'debug' => false,
  'loglevel' => 2,
  'log_type' => 'file',
  'logfile' => '/var/log/nextcloud.log',
  'logfilemode' => 0640,
  'log_rotate_size' => 104857600,   # Rotate log file when it reaches 100 MB
  'log_timezone' => 'UTC',
  'default_language' => 'en',

  # PREVIEWS
  'enable_previews' => true,
  'preview_concurrency_new' => 2,
  'preview_concurrency_all' => 4,
  'preview_max_x' => 1024,
  'preview_max_y' => 1024,
  'preview_max_memory' => 256,  # in MB
  'preview_max_filesize_image' => 50, # in MB
  
  'preview_ffmpeg_path' > '/usr/bin/ffmpeg',
  'preview_ffprobe_path' => '/usr/bin/ffprobe',
  'enabledPreviewProviders' => 
  array (
    0 => 'OC\Preview\PNG',
    1 => 'OC\Preview\JPEG',
    2 => 'OC\Preview\GIF',
    3 => 'OC\Preview\BMP',
    4 => 'OC\Preview\HEIC',
    5 => 'OC\Preview\WebP',
    6 => 'OC\Preview\Movie',
    7 => 'OC\Preview\PDF',
    8 => 'OC\Preview\TXT',
  ),

  # MISCELLANEOUS
  'default_phone_region' => 'US',   # Adjust to your actual region (e.g., 'US', 'DE', 'FR')
  'maintenance_window_start' => 2,  # Start time for maintenance mode (2 AM - UTC)
);