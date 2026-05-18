# 💻 VinylNode

**VinylNode** is a lightweight, terminal-optimized, high-fidelity local audio streaming server built with Python, Flask, and vanilla JavaScript. Designed to run seamlessly inside resource-constrained environments like Termux on Android or local machines, it transforms any device into a dedicated wireless audio node.

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
* **Unlimited Inertial Scrubbing Engine:** Re-engineered touch-action math using absolute angular displacement tracking. Users can grab and spin the vinyl disc like a physical DJ deck to scrub backwards or forwards through massive, minutes-long tracks without encountering micro-frame boundary limits.
* **Dynamic Content Extraction:** Automatically matches running audio tracks with random album backgrounds sourced over-the-air from your local `covers/` folder, falling back to an elegant minimal asset design if empty.

### 🎬 Immersive Cinematic Focus Mode
* **Ambient Clean UI:** A single click instantly hides the entire layout—including navigation headers, file lists, sliders, and upload forms—collapsing the webpage into a pure pitch-black workspace.
* **Expanded Center-Disk Layout:** The vinyl album art container scales up dynamically, locking itself directly into the absolute vertical and horizontal center of the display.
* **Tactile Dismissal:** Tapping anywhere on the centralized spinning vinyl artwork natively fires the HTML5 Fullscreen exit handler, smoothly scaling the dashboard control panel back into view.
