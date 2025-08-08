# Proxmox LXC Updater Script

A simple and robust Python script to automate the process of updating all Debian/Ubuntu-based LXC containers on a Proxmox host. The script handles reboots, logs all actions, and sends status notifications to a Slack channel.

## Features

* **Automated Updates**: Runs `apt-get update` and `apt-get upgrade -y` on all LXC containers.
* **Intelligent Reboots**: Automatically detects if a reboot is required and initiates it.
* **Detailed Logging**: Creates a log file (`lxc-updater.log`) with timestamped entries for every action and error.
* **Slack Notifications**: Sends real-time success or failure notifications to a configured Slack channel.
* **Performance Timing**: Measures and reports the time taken to update each container and the total script execution time.
* **Error Handling**: Robustly handles errors, ensuring that a failure in one container does not stop the entire process.

## Requirements

* Python 3 (`python3`).
* Pip for Python 3 (`python3-pip`).
* The following Python libraries:
  * `requests`
  * `python-dotenv`

## ⚙️ Setup Instructions

### 1. Place Files

Make a folder for your script (e.g., `/usr/helper/lxcs/update/`) and download the script.

```bash
mkdir /path/to/lxcs/update # Replace '/path/to/...' with your actual path
cd /path/to/lxcs/update
curl -L -o update-lxcs.py https://raw.githubusercontent.com/techmoocher/homelab/main/helper-scripts/lxcs/update/update-lxcs.py
```

Ensure the following files are in your project directory:

```
/update/
├── update-lxcs.py
├── lxcs-updater.log
└── .env
```

### 2. Install Dependencies

Install `pip` and the required Python libraries using the following commands:

```bash
# Update package lists
sudo apt update

# Install pip for Python 3
sudo apt install python3-pip -y

# Install required Python libraries
python3 -m pip install requests python-dotenv
```

### 3. Configure Slack Webhook

Create the `.env` file and add your Slack Incoming Webhook URL.

**`.env`**

```env
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

If you don't have this, the script will still run but won't send notifications.

## 🚀 Usage

You can run the script manually for testing or one-off updates.

```bash
# Navigate to the script's directory
cd /path/to/lxcs/update/

# Run the script
python3 update-lxcs.py
```

## 🤖 Automation (Cron Job)

To run the script automatically on a schedule, turn it into a system command and schedule it with `cron`.

### 1. Make the Script a Command

This will create a symbolic link, allowing you to run the script from anywhere while keeping the file in your project folder.

```bash
# 1. Make the script executable
chmod +x /path/to/lxcs/update/update-lxcs.py

# 2. Create a symbolic link in /usr/local/bin
sudo ln -s /path/to/lxcs/update/update-lxcs.py /usr/local/bin/update-lxcs
```

You can now run the script from any location by simply typing `update-lxcs`.

### 2. Schedule with Cron

Edit the crontab to add the schedule.

```bash
# Open the crontab editor
sudo crontab -e
```

Add the following line to the file to run the script at your desired time.

**Example: Run every Sunday at 12:15 PM**

```cron
15 12 * * 0 /usr/local/bin/update-lxcs
```

Save the file and exit. The script is now fully automated.
