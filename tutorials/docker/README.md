# Docker
<h2>Prerequisite</h3>
<ul>
  <li>Debian 11/12</li>
  <li>Ubuntu 22.04/24.04</li>
  <li>Fedora 41/42</li>
  <li>RHEL 8/9</li>
  <li>CentOS 9</li>
</ul>

<h2>For Debian</h2>
<p><b>Installing using <mark>apt</mark> repository</b></p>

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
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
<p>If you wanna verify is Docker successfully installed, check with the following commands</p>

```bash
docker -v # Should return the current version of Docker
```
<p>or</p>

```bash
sudo docker run hello-world
```

<p><b>(Optional)</b> Run docker commands without sudo</p>

```bash
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
```
<p>To ensure things are working properly, check it with</p>

```bash
docker run hello-world
```

<h2>For Ubuntu</h2>
<p><b>Installing using <mark>apt</mark> repository</b></p>

```bash
for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do sudo apt-get remove $pkg; done
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.as
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
<p>If you wanna verify is Docker successfully installed, check with the following commands</p>

```bash
docker -v # Should return the current version of Docker
```
<p>or</p>

```bash
sudo docker run hello-world
```

<p><b>(Optional)</b> Run docker commands without sudo</p>

```bash
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
```
<p>To ensure things are working properly, check it with</p>

```bash
docker run hello-world
```

