#!/usr/bin/env python3
"""
A script to update all LXC containers on a Proxmox host, reboot them if
necessary, and send status notifications to Slack.
"""

import subprocess
import datetime
import pathlib
import os
import time
import requests
from dotenv import load_dotenv

# --- Configuration ---
SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
LOG_FILE = SCRIPT_DIR / "lxc-updater.log"
ENV_FILE = SCRIPT_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE)
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


# --- Core Functions ---
def log_message(message: str):
    """
    Logs a message with a specific timestamp to a file and prints it to the console.
    """
    now = datetime.datetime.now().astimezone()
    tz_offset_full = now.strftime("%z")
    tz_offset_short = tz_offset_full[:3]
    timestamp = now.strftime("%Y-%m-%d @ %H:%M:%S")
    log_entry = f"[{timestamp} ({tz_offset_short}) ] {message}"
    
    print(log_entry)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(log_entry + "\n")
    except IOError as e:
        print(f"CRITICAL: Could not write to log file {LOG_FILE}. Error: {e}")

def send_slack_notification(message: str):
    """
    Sends a message to the configured Slack channel via webhook.
    """
    if not SLACK_WEBHOOK_URL:
        log_message("WARNING: SLACK_WEBHOOK_URL not set. Skipping notification.")
        return
        
    try:
        payload = {"text": message}
        response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        log_message(f"ERROR: Could not send Slack notification. Error: {e}")

def run_command(command: list, ctid: str = None):
    """
    Runs a shell command, either on the host or inside a specific LXC container.
    Raises CalledProcessError on failure.
    """
    if ctid:
        full_command = ["pct", "exec", str(ctid), "--"] + command
    else:
        full_command = command

    return subprocess.run(
        full_command, 
        capture_output=True, 
        text=True, 
        check=True
    )

# --- MAIN ---
def main():
    script_start_time = time.monotonic()
    log_message("--- LXC Update Script Started ---")
    
    try:
        result = run_command(["pct", "list"])
        lines = result.stdout.strip().split('\n')[1:]
        ct_ids = [line.split()[0] for line in lines if line]
        log_message(f"Found containers: {', '.join(ct_ids)}")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        error_msg = f"CRITICAL: Could not list LXC containers. Is 'pct' installed and in the PATH? Error: {e.stderr}"
        log_message(error_msg)
        send_slack_notification(error_msg)
        return

    for ctid in ct_ids:
        lxc_start_time = time.monotonic()
        log_message(f"--- Processing LXC {ctid} ---")
        try:
            log_message(f"INFO: [{ctid}] Running 'apt-get update'...")
            run_command(["apt-get", "update", "-q"], ctid=ctid)
            
            log_message(f"INFO: [{ctid}] Running 'apt-get upgrade -y'...")
            run_command(["apt-get", "upgrade", "-y", "-q"], ctid=ctid)
            
            log_message(f"SUCCESS: [{ctid}] Packages updated successfully.")
            status_message = f"✅ SUCCESS: LXC `{ctid}` updated."
            
            reboot_needed = False
            try:
                run_command(["test", "-f", "/var/run/reboot-required"], ctid=ctid)
                reboot_needed = True
            except subprocess.CalledProcessError:
                log_message(f"INFO: [{ctid}] No reboot required.")
                status_message += " No reboot needed."
            
            if reboot_needed:
                log_message(f"INFO: [{ctid}] Reboot is required. Rebooting...")
                run_command(["reboot"], ctid=ctid)
                status_message += " Reboot initiated."

            lxc_duration = time.monotonic() - lxc_start_time
            log_message(f"INFO: [{ctid}] Finished processing in {lxc_duration:.1f}s.")
            status_message += f" (took {lxc_duration:.1f}s)"

            send_slack_notification(status_message)

        except subprocess.CalledProcessError as e:
            lxc_duration = time.monotonic() - lxc_start_time
            error_details = e.stderr.strip() or e.stdout.strip()
            log_message(f"ERROR: [{ctid}] Failed after {lxc_duration:.1f}s. Details below:")
            log_message(error_details)
            send_slack_notification(f"❌ ERROR: Failed to update LXC `{ctid}`.\n```\n{error_details}\n```")
            
        finally:
            log_message(f"--- Finished with LXC {ctid} ---\n")
    
    script_duration = time.monotonic() - script_start_time
    log_message("--- LXC Update Script Finished ---")
    log_message(f"Total execution time: {script_duration:.2f} seconds.")


if __name__ == "__main__":
    main()
