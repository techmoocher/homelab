# A Journey of a Hobbyist

---

<div align="center">
    <h1>【 techmoocher's homelab 】</h1>
</div>

---

<div align="center">
    <img src="https://img.shields.io/github/last-commit/techmoocher/homelab?&style=for-the-badge&color=87FFAF&logo=git&logoColor=D9E0EE&labelColor=1E202B" />
    <img src="https://img.shields.io/github/stars/techmoocher/homelab?style=for-the-badge&logo=andela&color=FFFF7D&logoColor=D9E0EE&labelColor=1E202B" />
    <img src="https://img.shields.io/github/repo-size/techmoocher/homelab?color=A5E1FF&label=SIZE&logo=protondrive&style=for-the-badge&logoColor=D9E0EE&labelColor=1E202B" />
</div>

---

You are reading my personal notes on setting up a self-hosted server (a.k.a homelab) using Proxmox. This is not a tutorial, but more of an anecdotal documentation of my own experience. My main reason for writing this is to log my journey in self-hosting and to share my experience with hobbyists who are interested in self-hosting but don't know where to start. I know that there are already many good tutorials on setting up a homelab, but I hope this can be a good starting point for you to get into self-hosting and have fun with it!

## How To Use This Repo

- **[Installation and Initial setup](./GUIDE.md)**: My step-by-step walkthrough of installing Proxmox and setting up the initial configuration.

## My Hardware

As a full-time student and part-time hobbyist, I have a limited budget for my homelab. Thus, I digged into the pile of old tech gadgets in my dad's garage and decided to utilized the following as my set up:

- **ThinkPad T450 (Intel i5-5300U/Intel HD Graphics 5500/8GB RAM/228GB SSD)** *(Proxmox server)*
- **A 2TB WD Purple** *(storage)*

![My homelab setup](./.github/assets/images/homelab-setup.png)

## My Softwares

After a few months of tinkering and experimenting, I decided to settle on the following softwares for my homelab. However, as a hobbyist, I am always open to trying out new softwares and tools, so this list is not exhaustive and may change in the future. You are welcome to suggest anything you think is worth trying out!

For the time being, I am using the following in my homelab.

- **[Proxmox VE][proxmox-ve]** *(virtualization platform)*
- **[Portainer][portainer]** *(Docker management)*
- **[Nextcloud][nextcloud]** *(personal cloud storage)*
- **[AdGuard Home][adguard-home]** *(network-wide ad blocker)*
- **[Immich][immich]** *(self-hosted photo management)*
- **[Navidrome][navidrome]** *(self-hosted music streaming server)*
- **[Jellyfin][jellyfin]** *(self-hosted media server)*
- **[Vaultwarden][vaultwarden]** *(self-hosted password manager)*
- **[Nginx Proxy Manager][nginx-proxy-manager]** *(reverse proxy management)*
- **[Prometheus][prometheus]** *(monitoring and alerting toolkit)*
- **[Grafana][grafana]** *(analytics and monitoring platform)*
- **[n8n][n8n]** *(workflow automation)*

## License

This project is licensed under the [MIT License](https://en.wikipedia.org/wiki/MIT_License).

You are free to use, modify, and distribute this project for any purpose, as long as you include the original license and copyright notice in any copies or substantial portions of the software.

For more details, please refer to the [LICENSE](./LICENSE) file.

[proxmox-ve]: https://www.proxmox.com/en/proxmox-ve
[portainer]: https://www.portainer.io/
[nextcloud]: https://nextcloud.com/
[adguard-home]: https://adguard.com/en/adguard-home/overview.html
[immich]: https://immich.app/
[navidrome]: https://www.navidrome.org/
[jellyfin]: https://jellyfin.org/
[vaultwarden]: https://github.com/dani-garcia/vaultwarden
[nginx-proxy-manager]: https://nginxproxymanager.com/
[prometheus]: https://prometheus.io/
[grafana]: https://grafana.com/
[n8n]: https://n8n.io/
