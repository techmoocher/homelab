# Uptime Kuma Installation and Configuration Guide

---

[Uptime Kuma](https://github.com/louislam/uptime-kuma) is a self-hosted monitoring tool that allows you to keep track of the uptime and performance of your websites, servers, and other services. It provides a user-friendly interface and supports various monitoring types, including HTTP(s), TCP, ICMP, and more. In this guide, I will walk you through the installation and configuration of Uptime Kuma on your homelab.

---

## 1. LXC Setup

Before we can install Uptime Kuma, we need to set up an LXC container on Proxmox. If you haven't already, please refer to my [Proxmox Installation and Initial Setup Guide](../proxmox/README.md#9-creating-your-first-container-optional) for detailed instructions on how to set up Proxmox and create an LXC container.

### Recommended Specifications

- **CPU**: 1 vCPU
- **RAM**: 512MB
- **Storage**: 8GB *(or more, depending on your needs)*
- **Template**: Debian 12 *(or whatever distro you prefer)*
- **Type**: Unprivileged

## 2. Uptime Kuma Installation


