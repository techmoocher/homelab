# Glance Installation and Configuration Guide

[Glance](https://glanceapp.io/) is a modern, open-source dashboard application
that allows you to create customizable dashboards for monitoring and managing
your systems. It provides a user-friendly interface and supports various widgets
and integrations.

![My dashboard preview](preview.png)

---

## 1. Installation

You can install Glance using Docker, which is the recommended method for most
users. Make sure you have Docker and Docker Compose installed on your system
before proceeding. To learn more about Glance installation, you can refer to
the [official documentation](https://glanceapp.io/docs).

First, make a directory for your Glance installation and navigate into it:

1. **Make a directory for your file**
```bash
mkdir glance && cd glance
```

2. **Initialize Git and add the remote repo**
```bash
git init
git remote add -f origin https://github.com/techmoocher/homelab/
```

3. **Enable and configure sparse checkout**
```bash
git config core.sparseCheckout true
echo "services/glance/" >> .git/info/sparse-checkout
```

4. **Pull the files**
```bash
git pull origin main
```

Now, edit the following files as desired:
* `docker-compose.yml` to configure the port, volumes and other containery things
* `config/home.yml` to configure the widgets or layout of the home page
* `config/glance.yml` if you want to change the theme or add more pages

Other files you may want to edit:
* `.env` to configure environment variables that will be available inside configuration files
* `assets/user.css` to add custom CSS

When you're ready, run:
```bash
docker compose up -d
```

If you encounter any issues, you can check the logs:
```bash
docker compose logs
```
