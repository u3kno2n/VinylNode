# 💻 VinylNode

VinylNode is a lightweight, terminal-optimized, high-fidelity local audio streaming server built with Python, Flask, and vanilla JavaScript. Designed to run seamlessly inside resource-constrained environments like Termux on Android, it transforms a recycled, headless smartphone into a dedicated wireless audio node.

The application bypasses standard mobile browser limitations to stream uncompressed, lossless audio formats (FLAC, WAV, etc.) over a local network. It features a responsive web interface centered around an interactive vinyl turntable engine that bridges tactile classic audio aesthetics with modern digital file system hosting.

---

## 🚀 Key Features

### 🎧 Core Audio Streaming Engine
* **Hi-Res Lossless Support:** Natively streams heavy, uncompressed formats including `.flac`, `.wav`, `.m4a`, `.ogg`, and `.mp3` without downsampling or degradation.
* **Wireless Upload Portal:** Includes a built-in wireless file intake section, allowing you to drop new music tracks onto your storage drive over the air from any connected smartphone or laptop.
* **On-Node File Management:** Features an absolute storage control system with layout-embedded delete actions to clean and prune your library directly from the browser view.

### 🔄 Unbreakable Loop Library
* **Hardware-Bound Persistence:** Engineered using an asynchronous promise resolver loop (`audioPlayer.onended`) that forces the mobile OS processor to maintain hardware audio decoder execution.
* **Immune Background Transitions:** Prevents aggressive mobile memory garbage collection from putting the tab to sleep, guaranteeing continuous auto-advancement through your track queue even while your phone is locked in your pocket.

### 🎛️ Interactive Vinyl Turntable UI
* **Automated Rotation Sync:** The virtual vinyl deck automatically spins when audio is playing and pauses cleanly when the stream is stopped, acting as a real-time mechanical visualizer.
* **Unlimited Inertial Scrubbing Engine:** Re-engineered touch-action math using absolute angular displacement tracking. Users can grab and spin the vinyl disc like a physical DJ deck to scrub backwards or forwards through massive tracks without encountering micro-frame boundary limits.
* **Dynamic Content Extraction:** Automatically matches running audio tracks with random album backgrounds sourced over-the-air from your local `covers/` folder.

### 🎬 Immersive Cinematic Focus Mode
* **Ambient Clean UI:** A single click instantly hides the entire layout—including navigation headers, file lists, sliders, and upload forms—collapsing the webpage into a pure pitch-black workspace.
* **Expanded Center-Disk Layout:** The vinyl album art container scales up dynamically, locking itself directly into the absolute vertical and horizontal center of the display.

---

## 🛠️ Step-by-Step Headless  Setup

This guide walks through how this server was built using a recycled Android phone with a broken screen as a dedicated, headless network appliance—controlled entirely from a laptop without touching the phone's glass.

### Step 1: Provisioning the Android Node
We start by prepping the phone's environment. We need to update our mobile Linux packages, pull down Python, install the OpenSSH daemon so the phone can talk to our computer, and download the Flask micro-framework.

Run this command in Termux to enforce the environment installation:
Run this command in Termux to enforce the environment installation:
```bash
pkg update && pkg upgrade -y && pkg install python openssh -y && pip install flask
```
### Step 2: Creating the Remote Control Tunnel
To avoid typing on a broken screen, we spin up the phone's internal secure shell server. This allows us to map the phone to our laptop over local Wi-Fi. Note that Termux runs SSH on port 8022 instead of the traditional port 22.

Run this command to turn on the wireless tunnel receiver:
```bash
sshd
```
💡 The WinSCP Connection: Once sshd is running, open WinSCP on your laptop. Set the file protocol to SFTP, type in your phone's local IP address ( to know the ip type ifconfig in the termux and the wlan0 this is your device's physical Wi-Fi interface. This is the one you need to look at if your Termux server is communicating over your home Wi-Fi network.) , set the port to 8022, and type in your Termux username (to know the usename type whoami in the termux ). You can now access your phone's entire storage structure using a desktop graphic interface.

### Step 3: Enforcing Real-Time Development Changes
Instead of editing files using clunky terminal commands on the phone, you can now open app.py directly inside your laptop's text editor via WinSCP. To ensure that every time you save a change on your laptop it instantly updates the website, we enforce Flask's native hot-reloading debugger at the very bottom of the server file.

( in simple words keep the debug = at the bottom of the code to true intead of false )

This block inside your app.py script enables wireless network access and real-time synchronization:

```bash
if __name__ == '__main__':
    # host='0.0.0.0' broadcasts the server to your entire home Wi-Fi network
    # debug=True watches for file saves and reloads the server automatically
    app.run(host='0.0.0.0', port=5000, debug=True)
```

### Step 4: Initializing the Media Storage Structure
To keep the server lightweight and secure, our audio tracks and artwork are kept private and hidden from our public GitHub page using a .gitignore shield. Because of this, when installing the project fresh, you must manually create the empty storage directory where your media files will sit.

(The easier way would be to just creat the foldrs using the WIN SCP directly into the directory but if this doesnt work )

Run this terminal command to initialize your media folders:

```bash
mkdir music covers
```
music/: Drop your uncompressed lossless audio files (.flac, .mp3, .wav) in here.

covers/: Drop your aspect-square album artwork images in here.
The easier way would be to just creat the foldrs using the WIN SCP directly into the directory but if this doesnt work 

### Step 5: Launching the Server Node
With your remote workspace linked, your real-time debugger running, and your music files loaded into the storage track folders, you are ready to boot up your machine.

Run this final command inside your server folder to launch your wireless hub:

```bash
python app.py
```
Viola! Your high-fidelity audio server is alive. Open your web browser on your laptop or any other device connected to the same Wi-Fi network and navigate to your phone's IP address at port 5000 (e.g., http://192.168.1.5:5000) to access your beautiful, interactive spinning vinyl dashboard!
