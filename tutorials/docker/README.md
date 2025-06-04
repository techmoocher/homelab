# Docker
<h2>Prerequisite</h3>
<ul>
  <li>Debian 11/12</li>
  <li>Ubuntu 22.04/24.04</li>
  <li>Fedora 41/42</li>
  <li>RHEL 8/9</li>
  <li>CentOS 9</li>
</ul>

<h2>Debian</h2>
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
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
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

<h2>Ubuntu</h2>
<p><b>Installing using <mark>apt</mark> repository</b></p>

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

<h2>Fedora</h2>
<p>Installing using <mark>rpm</mark> repository</p>

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
<p><i><b>Note: </b>If prompted to accept the GPG key, verify that the fingerprint matches <mark>060A 61C5 1B55 8A7F 742B 77AA C52F EB6B 621E 9F35</mark>, and if so, accept it.</i></p>

<p>Start Docker Engine <i>Docker is installed but is not started. A docker group is also created but no users are added to that group by default.</i></p>

```bash
sudo systemctl enable --now docker
```

<p>To verify if docker is successfully installed, use this command</p>

```bash
sudo docker run hello-world
```

<p><b>(Optional)</b> Run docker commands without sudo</p>

```bash
sudo usermod -aG docker $USER
newgrp docker
groups $USER # To verify your user is in the docker group
```

<h2>RHEL</h2>
<p>Installing using <mark>rpm</mark> repository</p>

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
<p><i><b>Note: </b>If prompted to accept the GPG key, verify that the fingerprint matches <mark>060A 61C5 1B55 8A7F 742B 77AA C52F EB6B 621E 9F35</mark>, and if so, accept it.</i></p>

<p>Start Docker Engine <i>Docker is installed but is not started. A docker group is also created but no users are added to that group by default.</i></p>

```bash
sudo systemctl enable --now docker
```

<p>To verify if docker is successfully installed, use this command</p>

```bash
sudo docker run hello-world
```

<p><b>(Optional)</b> Run docker commands without sudo</p>

```bash
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
docker run hello-world # To verify that you can run Docker without sudo
```

<h3><i>(Optional)</i> Connect a CT with Docker to Portainer</h3>
<p>First, make sure that you have Docker installed on your CT and a Portainer server.</p>
<p>Before connecting Portainer to the Environment on our CT, we need to have port 2375 open so we can connect to our daemon.</p>

```bash
sudo systemctl edit docker.service
```
<p>Add the following lines, then save and exit.</p>

```bash
[Service]
ExecStart=
ExecStart=/usr/bin/dockerd -H fd:// -H tcp://0.0.0.0:2375
```

<p>In order to apply the changes we've just made, enter the following commands</p>

```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

<p>Now, go to Portainer Web GUI and click on <b>Add environemt</b>. Choose <b>Docker Standalone</b> and then click on <b>Start Wizard</b>. In <b>Environment Wizard</b>, choose a <b>Name</b> for your environment, then enter the IP Address of your CT, following by <mark>:2375</mark> <i>(e.g. 192.168.1.100:2375)</i>. You may want to adjust other settings depending on your needs. Click <b>Connect</b> to create a connection. If you receive a notification saying "Environment created", you're all set.</p>
