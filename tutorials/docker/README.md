# Docker Installation Guide

## Prerequisites

- Debian 11/12
- Ubuntu 22.04/24.04
- Fedora 41/42
- RHEL 8/9
- CentOS 9

## Debian

**Installing using `apt` repository**

```bash
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
```

To verify that Docker was successfully installed, run:

```bash
docker -v # Should return the current version of Docker
```

or:

```bash
sudo docker run hello-world
```

**Optional:** Run Docker commands without `sudo`:

```bash
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
```

To ensure everything is working properly, run:

```bash
docker run hello-world
```

## Ubuntu

**Installing using `apt` repository**

```bash
for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do sudo apt-get remove $pkg; done
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
```

To verify that Docker was successfully installed, run:

```bash
docker -v # Should return the current version of Docker
```

or:

```bash
sudo docker run hello-world
```

**Optional:** Run Docker commands without `sudo`:

```bash
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
```

To ensure everything is working properly, run:

```bash
docker run hello-world
```

## Fedora

Installing using `rpm` repository:

```bash
sudo dnf remove docker \
                  docker-client \
                  docker-client-latest \
                  docker-common \
                  docker-latest \
                  docker-latest-logrotate \
                  docker-logrotate \
                  docker-selinux \
                  docker-engine-selinux \
                  docker-engine
sudo dnf -y install dnf-plugins-core
sudo dnf-3 config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
sudo dnf install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

> **Note:** If prompted to accept the GPG key, verify that the fingerprint
> matches `060A 61C5 1B55 8A7F 742B 77AA C52F EB6B 621E 9F35`, and if so,
> accept it.

**Start Docker Engine**

Docker is installed but is not started. A Docker group is also created, but
no users are added to that group by default.

```bash
sudo systemctl enable --now docker
```

To verify that Docker was successfully installed, run:

```bash
sudo docker run hello-world
```

**Optional:** Run Docker commands without `sudo`:

```bash
sudo usermod -aG docker $USER
newgrp docker
groups $USER # To verify your user is in the docker group
```

## RHEL

Installing using `rpm` repository:

```bash
sudo dnf remove docker \
                  docker-client \
                  docker-client-latest \
                  docker-common \
                  docker-latest \
                  docker-latest-logrotate \
                  docker-logrotate \
                  docker-engine \
                  podman \
                  runc
sudo dnf -y install dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/rhel/docker-ce.repo
sudo dnf install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

> **Note:** If prompted to accept the GPG key, verify that the fingerprint
> matches `060A 61C5 1B55 8A7F 742B 77AA C52F EB6B 621E 9F35`, and if so,
> accept it.

**Start Docker Engine**

Docker is installed but is not started. A Docker group is also created, but
no users are added to that group by default.

```bash
sudo systemctl enable --now docker
```

To verify that Docker was successfully installed, run:

```bash
sudo docker run hello-world
```

**Optional:** Run Docker commands without `sudo`:

```bash
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
docker run hello-world # To verify that you can run Docker without sudo
```

### (Optional) Connect a CT with Docker to Portainer

First, make sure that you have Docker installed on your CT and a Portainer server.

Before connecting Portainer to the environment on your CT, you need to open
port `2375` so you can connect to your daemon.

```bash
sudo systemctl edit docker.service
```

Add the following lines, then save and exit:

```ini
[Service]
ExecStart=
ExecStart=/usr/bin/dockerd -H fd:// -H tcp://0.0.0.0:2375
```

To apply the changes, run:

```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

Now, go to the Portainer web GUI and click **Add environment**. Choose
**Docker Standalone**, then click **Start Wizard**. In the **Environment
Wizard**, choose a **Name** for your environment, then enter the IP address of
your CT followed by `:2375` (for example, `192.168.1.100:2375`). You may want
to adjust other settings depending on your needs. Click **Connect** to create
a connection. If you receive a notification saying "Environment created",
you're all set.
