# techmoocher-homelab
<p><i>Created May 7, 2025</i> by {techmoocher}</p>
<br>
<p>The following is my experience when building my own homelab as high school junior with two Thinkpads and some old hard drives.</p>
<br>
<h1>1. Getting started</h1>


<br>
<h1>2. Preparing Proxmox</h1>
<h3>1. Updating repos</h3>
<p>Proxmox has enterprise apt repo by default. Since we're using it for personal usage, we will change it to no-subscription</p>
<p>To get started, navigate to your machine (aka click on the button that labeled your <b><i>hostname</i></b>)</p>
<p>Go to <b>Updates</b>, then <b>Repositories</b></p>
<p>You will see a warning <i>"The enterprise repository is enabled, but there is no active subscription!"</i></p>
<p>Scroll down to the options that has <b>Components</b> labeld <b><i>enterprise</i></b> (aka those that has URIs <i>"https://enterprise.proxmox.com/..."</i>), click on <b>Disable</b> button to disable it.</p>
<p>Now, click the <b>Add</b> button. There would be a warning popping up so click <b>OK</b> to skip it. Then, you will be shown a menu, in the <b>Repository</b> line, click on the toggle-list and choose <b>No-Subscription</b>, then click <b>Add</b>.</p>
<p>You're not done yet!</p>
<p>Now, go to <b>Shell</b> and enter the following commands to finish updating your apt repository and have your programs up-to-date</p>
```bash
apt update && apt upgrade
```
<p>Take a break while the machine running it updates. When it's done with no error and/or warning, it's done!</p>

<br>
<h3>2. Deleting local-lvm <i>optional</i></h3>
<p>If you check the machine, you will see there is a </p>
