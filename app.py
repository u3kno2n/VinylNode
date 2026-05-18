import os
import random
from flask import Flask, render_template_string, send_from_directory, abort, request, redirect, url_for

app = Flask(__name__)

MUSIC_DIR = os.path.join(os.getcwd(), 'music')
if not os.path.exists(MUSIC_DIR):
    os.makedirs(MUSIC_DIR)

COVERS_DIR = os.path.join(os.getcwd(), 'covers')
if not os.path.exists(COVERS_DIR):
    os.makedirs(COVERS_DIR)

SUPPORTED_FORMATS = ('.mp3', '.wav', '.ogg', '.m4a', '.flac')
IMAGE_FORMATS = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.jfif')

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lossless Audio Server</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: linear-gradient(to bottom, #1c1c1c, #121212);
            color: #ffffff; 
            padding: 20px; 
            max-width: 450px; 
            margin: 0 auto;
            min-height: 100vh;
            position: relative;
            transition: background 0.5s ease;
        }
        
        /* Main Heading */
        h1.main-title { 
            font-size: 1.5em; 
            text-align: center; 
            padding: 15px 0; 
            font-weight: 700;
            letter-spacing: -0.5px;
            color: #ffffff;
            transition: opacity 0.3s;
        }

        /* Vinyl Container Layout & Transitions */
        .art-container {
            width: 220px;
            height: 220px;
            margin: 10px auto 20px auto;
            background: linear-gradient(135deg, #282828, #181818);
            background-size: cover;
            background-position: center;
            border-radius: 50% !important;
            box-shadow: 0px 12px 30px rgba(0,0,0,0.7), inset 0 0 20px rgba(0,0,0,0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            overflow: hidden;
            border: 4px solid #282828;
            touch-action: none;
            user-select: none;
            -webkit-user-select: none;
            cursor: pointer;
            transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1), 
                        height 0.5s cubic-bezier(0.4, 0, 0.2, 1), 
                        margin 0.5s cubic-bezier(0.4, 0, 0.2, 1),
                        box-shadow 0.5s;
            z-index: 100;
        }

        .art-container::after {
            content: '';
            position: absolute;
            width: 14px;
            height: 14px;
            background: #121212;
            border-radius: 50%;
            border: 2px solid rgba(255,255,255,0.2);
            z-index: 10;
        }

        .art-icon {
            font-size: 50px;
            color: #ffffff;
            opacity: 0.2;
            pointer-events: none;
        }
        
        /* UI Control Panels */
        .player-panel, .playlist-toggle-bar, .collapsible-content, .upload-section, .fullscreen-toggle-btn {
            transition: opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1), transform 0.4s;
        }

        .player-panel {
            background: #181818;
            padding: 15px 20px;
            border-radius: 16px;
            margin-bottom: 25px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        .now-playing {
            text-align: left;
            margin-bottom: 15px;
        }
        .track-name {
            font-size: 1.2em;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 4px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .artist-name {
            font-size: 0.85em;
            color: #a1a1aa;
        }
        
        audio { 
            width: 100%; 
            margin-bottom: 15px; 
            height: 40px;
            border-radius: 8px;
            filter: invert(0.9) brightness(1.2);
        }

        .controls { 
            display: flex; 
            gap: 15px; 
            align-items: center;
            justify-content: center; 
        }
        
        button {
            background: transparent;
            color: #a1a1aa;
            border: none;
            cursor: pointer;
            font-weight: bold;
            font-size: 0.85em;
            transition: 0.2s;
            letter-spacing: 0.5px;
        }
        button:hover { color: #ffffff; }
        
        button#play-all-btn {
            background: #ffffff;
            color: #000000;
            padding: 6px 14px;
            border-radius: 50px;
            font-weight: 700;
        }
        button#play-all-btn.active { background: #1db954; color: #ffffff; }
        
        .fullscreen-toggle-btn {
            background: rgba(255, 255, 255, 0.06);
            color: #e4e4e7;
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 8px 16px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.8em;
            display: block;
            margin: -10px auto 20px auto;
            transition: 0.2s;
        }
        .fullscreen-toggle-btn:hover { background: rgba(255, 255, 255, 0.15); color: #ffffff; }

        .playlist-toggle-bar {
            background: #282828;
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 12px 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            margin-bottom: 10px;
            user-select: none;
        }
        .playlist-toggle-bar:hover { background: #323232; }
        .playlist-title { font-size: 0.9em; font-weight: 700; color: #ffffff; }
        
        .css-arrow {
            width: 8px;
            height: 8px;
            border-right: 2px solid #a1a1aa;
            border-bottom: 2px solid #a1a1aa;
            transform: rotate(45deg);
            transition: transform 0.3s ease, border-color 0.2s;
            margin-right: 5px;
        }
        .playlist-toggle-bar.active .css-arrow { transform: rotate(-135deg); }

        .collapsible-content {
            max-height: 2000px;
            overflow: hidden;
            transition: max-height 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .collapsible-content.collapsed { max-height: 0px !important; }

        .search-container { margin-bottom: 15px; padding: 0 2px; }
        .search-bar {
            width: 100%;
            padding: 10px 15px;
            background: #181818;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 8px;
            color: #ffffff;
            font-size: 0.9em;
            outline: none;
        }

        .track-list { list-style: none; }
        .track-item {
            background: rgba(24, 24, 27, 0.4);
            margin: 6px 0;
            padding: 10px 12px;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid rgba(255,255,255,0.02);
        }
        .track-item:hover { background: #282828; }
        .track-item.playing { background: rgba(255, 255, 255, 0.08); border-color: rgba(255,255,255,0.08); }
        
        .track-meta { display: flex; flex-direction: column; max-width: 70%; cursor: pointer; }
        .track-title-text { font-size: 0.95em; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .track-sub-text { font-size: 0.8em; color: #71717a; margin-top: 2px; }
        
        .item-actions { display: flex; gap: 15px; align-items: center; }
        .play-text { color: #71717a; font-size: 0.8em; font-weight: bold; cursor: pointer; }
        .track-item:hover .play-text, .track-item.playing .play-text { color: #1db954; }
        
        .delete-btn { color: #b3b3b3; font-size: 0.75em; font-weight: 700; letter-spacing: 0.5px; transition: color 0.2s; cursor: pointer; padding: 5px; }
        .delete-btn:hover { color: #ef4444; }

        .upload-section {
            background: #181818;
            border: 1px solid rgba(255,255,255,0.05);
            padding: 15px 20px;
            text-align: center;
            margin-top: 15px;
            border-radius: 16px;
        }
        .upload-title { font-size: 0.75em; color: #a1a1aa; margin-bottom: 10px; display: block; font-weight: 700; letter-spacing: 1px; }
        .file-input { color: #a1a1aa; font-size: 0.8em; margin-bottom: 10px; width: 100%; }
        .submit-btn { background: #ffffff; color: #000000; border: none; padding: 6px 20px; border-radius: 50px; cursor: pointer; font-weight: 700; font-size: 0.8em; }

        /* --- MIND BLOWING FULLSCREEN IMMERSIVE ARCHITECTURE --- */
        body.cinematic-focus {
            background: #050505 !important;
            overflow: hidden;
        }

        body.cinematic-focus .main-title,
        body.cinematic-focus .player-panel,
        body.cinematic-focus .fullscreen-toggle-btn,
        body.cinematic-focus .playlist-toggle-bar,
        body.cinematic-focus .collapsible-content,
        body.cinematic-focus .upload-section {
            opacity: 0 !important;
            transform: scale(0.92);
            pointer-events: none;
        }

        body.cinematic-focus .art-container {
            width: 320px;
            height: 320px;
            position: absolute;
            top: 50%;
            left: 50%;
            margin: 0;
            transform: translate(-50%, -50%) rotate(0deg);
            box-shadow: 0px 25px 60px rgba(0, 0, 0, 0.95), 0 0 40px rgba(29, 185, 84, 0.15);
            border: 6px solid #1e1e1e;
        }
    </style>
</head>
<body>

    <h1 class="main-title">Lossless Node</h1>

    <div class="art-container" id="album-art-box" onclick="handleDiskClick(event)">
        <div class="art-icon" id="art-fallback-icon">?</div>
    </div>

    <button class="fullscreen-toggle-btn" id="fs-btn" onclick="toggleCinematicFocus()">ENTER CINEMATIC FOCUS</button>

    <div class="player-panel" id="main-control-panel">
        <div class="now-playing">
            <div class="track-name" id="current-track-title">Select a track</div>
            <div class="artist-name" id="current-artist-sub">Lossless Storage Server</div>
        </div>
        
        <audio id="main-audio" controls preload="auto"></audio>
        
        <div class="controls">
            <button id="prev-btn" onclick="playPrevious()">PREV</button>
            <button id="play-all-btn" onclick="togglePlayAll()">LOOP LIBRARY: OFF</button>
            <button id="next-btn" onclick="playNext()">NEXT</button>
        </div>
    </div>

    <div class="playlist-toggle-bar active" id="toggle-header" onclick="togglePlaylistPanel()">
        <span class="playlist-title">YOUR AUDIO LIBRARY</span>
        <div class="css-arrow"></div>
    </div>

    <div class="collapsible-content" id="playlist-drawer">
        <div class="search-container">
            <input type="text" id="library-search" class="search-bar" placeholder="Search tracks..." onkeyup="filterLibrary()">
        </div>

        <ul class="track-list" id="main-track-list">
        {% for song in songs %}
            <li class="track-item" id="track-{{ loop.index0 }}">
                <div class="track-meta" onclick="selectTrack({{ loop.index0 }}, '/play/{{ song | urlencode }}', '{{ song }}')">
                    <span class="track-title-text">{{ song }}</span>
                    <span class="track-sub-text">Hi-Res Lossless</span>
                </div>
                <div class="item-actions">
                    <span class="play-text" onclick="selectTrack({{ loop.index0 }}, '/play/{{ song | urlencode }}', '{{ song }}')">PLAY</span>
                    <span class="delete-btn" onclick="deleteTrack('{{ song | urlencode }}')">DELETE</span>
                </div>
            </li>
        {% endfor %}
        </ul>
    </div>

    <div class="upload-section">
        <form action="/upload" method="POST" enctype="multipart/form-data">
            <span class="upload-title">WIRELESS LOSSLESS UPLOAD</span>
            <input type="file" name="music_file" accept="audio/*" class="file-input" required>
            <input type="submit" value="UPLOAD" class="submit-btn">
        </form>
    </div>

    <script>
        const playlist = {{ songs|tojson }};
        const coverImages = {{ covers|tojson }};
        let currentIndex = -1;
        let playAllMode = false;
        let focusActive = false;

        const audioPlayer = document.getElementById('main-audio');
        const trackTitleDisplay = document.getElementById('current-track-title');
        const playAllBtn = document.getElementById('play-all-btn');
        const artBox = document.getElementById('album-art-box');
        const fallbackIcon = document.getElementById('art-fallback-icon');
        const toggleHeader = document.getElementById('toggle-header');
        const playlistDrawer = document.getElementById('playlist-drawer');

        // --- FIXED PERSISTENT SPIN INTERACTION VARIABLES ---
        let isDragging = false;
        let currentRotation = 0;
        let startAngle = 0;
        let lastAngle = 0;
        let baseRotationOnTouch = 0;
        let audioTimeOnTouch = 0;
        const ROTATION_SPEED = 0.5;

        function togglePlaylistPanel() {
            toggleHeader.classList.toggle('active');
            playlistDrawer.classList.toggle('collapsed');
        }

        function filterLibrary() {
            const query = document.getElementById('library-search').value.toLowerCase();
            const trackItems = document.getElementsByClassName('track-item');
            for (let i = 0; i < trackItems.length; i++) {
                const title = trackItems[i].querySelector('.track-title-text').textContent.toLowerCase();
                trackItems[i].style.display = title.includes(query) ? 'flex' : 'none';
            }
        }

        function deleteTrack(encodedFilename) {
            if (confirm("Are you sure you want to permanently delete this track from your server?")) {
                window.location.href = `/delete/${encodedFilename}`;
            }
        }

        // --- HARD-BOUND AUTO SPIN ENGINE ---
        function updateAutomaticSpin() {
            if (!audioPlayer.paused && !isDragging) {
                currentRotation += ROTATION_SPEED;
                if (!focusActive) {
                    artBox.style.transform = `rotate(${currentRotation % 360}deg)`;
                } else {
                    artBox.style.transform = `translate(-50%, -50%) rotate(${currentRotation % 360}deg)`;
                }
            }
            requestAnimationFrame(updateAutomaticSpin);
        }
        updateAutomaticSpin();

        function getTouchAngle(e) {
            const rect = artBox.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;
            const clientX = e.touches ? e.touches[0].clientX : e.clientX;
            const clientY = e.touches ? e.touches[0].clientY : e.clientY;
            return Math.atan2(clientY - centerY, clientX - centerX) * (180 / Math.PI);
        }

        // --- SCRUB MECHANICAL HANDLERS ---
        function handleDragStart(e) {
            if (currentIndex === -1) return;
            isDragging = true;
            audioPlayer.pause();
            startAngle = getTouchAngle(e);
            lastAngle = startAngle;
            baseRotationOnTouch = currentRotation;
            audioTimeOnTouch = audioPlayer.currentTime;
        }

        function handleDragMove(e) {
            if (!isDragging) return;
            const currentAngle = getTouchAngle(e);
            let angleChange = currentAngle - startAngle;
            if (currentAngle - lastAngle > 180) startAngle += 360;
            else if (currentAngle - lastAngle < -180) startAngle -= 360;
            angleChange = currentAngle - startAngle;
            lastAngle = currentAngle;
            currentRotation = baseRotationOnTouch + angleChange;
            
            if (!focusActive) {
                artBox.style.transform = `rotate(${currentRotation}deg)`;
            } else {
                artBox.style.transform = `translate(-50%, -50%) rotate(${currentRotation}deg)`;
            }
            
            if (audioPlayer.duration) {
                let timeOffset = (angleChange / 360) * 25;
                let newTime = audioTimeOnTouch + timeOffset;
                if (newTime < 0) newTime = 0;
                if (newTime > audioPlayer.duration) newTime = audioPlayer.duration - 0.5;
                audioPlayer.currentTime = newTime;
            }
        }

        function handleDragEnd() {
            if (!isDragging) return;
            isDragging = false;
            currentRotation = currentRotation % 360; 
            audioPlayer.play().catch(err => console.log("Stream target wake failed."));
        }

        artBox.addEventListener('mousedown', handleDragStart);
        window.addEventListener('mousemove', handleDragMove);
        window.addEventListener('mouseup', handleDragEnd);
        artBox.addEventListener('touchstart', handleDragStart, { passive: true });
        window.addEventListener('touchmove', handleDragMove, { passive: false });
        window.addEventListener('touchend', handleDragEnd);

        // --- MIND-BLOWING FULLSCREEN INTERACTION CONTROLLER ---
        function toggleCinematicFocus() {
            const docElm = document.documentElement;
            if (!focusActive) {
                if (docElm.requestFullscreen) docElm.requestFullscreen();
                else if (docElm.webkitRequestFullscreen) docElm.webkitRequestFullscreen();
                
                document.body.classList.add('cinematic-focus');
                focusActive = true;
            } else {
                if (document.exitFullscreen) document.exitFullscreen();
                else if (document.webkitExitFullscreen) document.webkitExitFullscreen();
                
                document.body.classList.remove('cinematic-focus');
                focusActive = false;
                // Re-align structural rotation attributes
                artBox.style.transform = `rotate(${currentRotation % 360}deg)`;
            }
        }

        function handleDiskClick(event) {
            // If we are in focus mode, tapping the CD exits fullscreen instantly
            if (focusActive && !isDragging) {
                toggleCinematicFocus();
            }
        }

        // Listen for standard ESC key exits out of native fullscreen to reset layout classes safely
        document.addEventListener('fullscreenchange', exitHandler);
        document.addEventListener('webkitfullscreenchange', exitHandler);
        function exitHandler() {
            if (!document.fullscreenElement && !document.webkitFullscreenElement) {
                document.body.classList.remove('cinematic-focus');
                focusActive = false;
                artBox.style.transform = `rotate(${currentRotation % 360}deg)`;
            }
        }

        // --- BULLETPROOF AUDIO SYNCHRONIZATION RUNTIME ---
        function selectTrack(index, url, filename) {
            if (currentIndex !== -1) {
                const prevElem = document.getElementById(`track-${currentIndex}`);
                if (prevElem) prevElem.classList.remove('playing');
            }

            currentIndex = index;
            const currentElem = document.getElementById(`track-${currentIndex}`);
            if (currentElem) currentElem.classList.add('playing');

            const cleanTitle = filename.replace(/\.[^/.]+$/, "");
            trackTitleDisplay.textContent = cleanTitle;
            
            // Re-allocate target engine buffers explicitly before triggering pipelines
            audioPlayer.src = url;
            audioPlayer.preload = "auto";
            audioPlayer.load();
            
            const runStream = audioPlayer.play();
            if (runStream !== undefined) {
                runStream.then(() => {
                    executeArtAndMediaSync(cleanTitle);
                }).catch(err => {
                    console.log("Device interface blocked execution path. Attempting emergency thread bypass...");
                    audioPlayer.load();
                    audioPlayer.play();
                });
            }
        }

        function executeArtAndMediaSync(cleanTitle) {
            let chosenCoverUrl = '';
            if (coverImages.length > 0) {
                const randomCover = coverImages[Math.floor(Math.random() * coverImages.length)];
                chosenCoverUrl = window.location.origin + `/get_cover/${encodeURIComponent(randomCover)}`;
                artBox.style.backgroundImage = `url('${chosenCoverUrl}')`;
                fallbackIcon.style.display = 'none';
            } else {
                artBox.style.backgroundImage = 'none';
                fallbackIcon.style.display = 'block';
            }

            if ('mediaSession' in navigator) {
                navigator.mediaSession.metadata = new MediaMetadata({
                    title: cleanTitle,
                    artist: 'Lossless Storage Node',
                    album: 'Local Audio Library',
                    artwork: chosenCoverUrl ? [{ src: chosenCoverUrl, sizes: '300x300', type: 'image/jpeg' }] : []
                });
                navigator.mediaSession.setActionHandler('nexttrack', playNext);
                navigator.mediaSession.setActionHandler('previoustrack', playPrevious);
            }
        }

        function playNext() {
            if (playlist.length === 0) return;
            let nextIndex = currentIndex + 1;
            if (nextIndex >= playlist.length) nextIndex = 0;
            const nextTrackName = playlist[nextIndex];
            selectTrack(nextIndex, `/play/${encodeURIComponent(nextTrackName)}`, nextTrackName);
        }

        function playPrevious() {
            if (playlist.length === 0) return;
            let prevIndex = currentIndex - 1;
            if (prevIndex < 0) prevIndex = playlist.length - 1;
            const prevTrackName = playlist[prevIndex];
            selectTrack(prevIndex, `/play/${encodeURIComponent(prevTrackName)}`, prevTrackName);
        }

        function togglePlayAll() {
            playAllMode = !playAllMode;
            if (playAllMode) {
                playAllBtn.classList.add('active');
                playAllBtn.textContent = "LOOP LIBRARY: ON";
                if (currentIndex === -1 && playlist.length > 0) {
                    selectTrack(0, `/play/${encodeURIComponent(playlist[0])}`, playlist[0]);
                }
            } else {
                playAllBtn.classList.remove('active');
                playAllBtn.textContent = "LOOP LIBRARY: OFF";
            }
        }

        // --- IMMUNE AUTO-ADVANCE PIPELINE LOOP ---
        audioPlayer.onended = function() {
            if (playAllMode) {
                console.log("Interrupt captured safely. Advancing queue index state...");
                playNext();
            }
        };
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    all_files = os.listdir(MUSIC_DIR)
    songs = [f for f in all_files if f.lower().endswith(SUPPORTED_FORMATS)]
    songs.sort()
    all_covers = os.listdir(COVERS_DIR)
    covers = [c for c in all_covers if c.lower().endswith(IMAGE_FORMATS)]
    return render_template_string(HTML_TEMPLATE, songs=songs, covers=covers)

@app.route('/upload', methods=['POST'])
def upload_audio():
    if 'music_file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['music_file']
    if file.filename == '':
        return redirect(url_for('index'))
    if file and file.filename.lower().endswith(SUPPORTED_FORMATS):
        target_path = os.path.join(MUSIC_DIR, file.filename)
        file.save(target_path)
    return redirect(url_for('index'))

@app.route('/delete/<path:filename>')
def delete_audio(filename):
    if ".." in filename or filename.startswith("/"):
        abort(400, "Invalid file target path")
    target_file_path = os.path.join(MUSIC_DIR, filename)
    if os.path.exists(target_file_path):
        os.remove(target_file_path)
    return redirect(url_for('index'))

@app.route('/play/<path:filename>')
def play_song(filename):
    if ".." in filename or filename.startswith("/"):
        abort(400, "Invalid track path")
    return send_from_directory(MUSIC_DIR, filename)

@app.route('/get_cover/<path:filename>')
def get_cover_art(filename):
    if ".." in filename or filename.startswith("/"):
        abort(400, "Invalid cover path")
    return send_from_directory(COVERS_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)