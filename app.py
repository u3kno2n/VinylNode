import os, json, mimetypes
from pathlib import Path
from flask import Flask, render_template_string, send_file, abort, request, redirect, url_for, Response

app = Flask(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
BASE      = Path(__file__).parent
MUSIC     = BASE / "music"
COVERS    = BASE / "covers"
AUDIO_EXT = {".mp3", ".flac", ".wav", ".ogg", ".m4a", ".aac", ".opus"}
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".avif"}

MUSIC.mkdir(exist_ok=True)
COVERS.mkdir(exist_ok=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
def get_tracks():
    return sorted(
        f.name for f in MUSIC.iterdir()
        if f.suffix.lower() in AUDIO_EXT
    )

def get_covers():
    return sorted(
        f.name for f in COVERS.iterdir()
        if f.suffix.lower() in IMAGE_EXT
    )

def safe_path(directory: Path, filename: str) -> Path:
    """Resolve path and ensure it stays within directory."""
    resolved = (directory / filename).resolve()
    if not str(resolved).startswith(str(directory.resolve())):
        abort(400)
    return resolved

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template_string(UI, tracks=get_tracks(), covers=get_covers())

@app.route("/stream/<path:name>")
def stream(name):
    path = safe_path(MUSIC, name)
    if not path.exists(): abort(404)
    mime = mimetypes.guess_type(str(path))[0] or "audio/mpeg"
    return send_file(path, mimetype=mime, conditional=True)

@app.route("/cover/<path:name>")
def cover(name):
    path = safe_path(COVERS, name)
    if not path.exists(): abort(404)
    return send_file(path, conditional=True)

@app.route("/upload", methods=["POST"])
def upload():
    f = request.files.get("file")
    if f and Path(f.filename).suffix.lower() in AUDIO_EXT:
        dest = safe_path(MUSIC, Path(f.filename).name)
        f.save(dest)
    return redirect(url_for("index"))

@app.route("/delete/<path:name>", methods=["POST"])
def delete(name):
    path = safe_path(MUSIC, name)
    if path.exists(): path.unlink()
    return redirect(url_for("index"))

@app.route("/api/tracks")
def api_tracks():
    return {"tracks": get_tracks(), "covers": get_covers()}

@app.route("/sw.js")
def sw():
    r = Response(SW_JS, mimetype="application/javascript")
    r.headers["Service-Worker-Allowed"] = "/"
    return r

@app.route("/manifest.json")
def manifest():
    return Response(json.dumps(MANIFEST), mimetype="application/json")

# ── PWA Assets ────────────────────────────────────────────────────────────────
MANIFEST = {
    "name": "Waves", "short_name": "Waves",
    "start_url": "/", "display": "standalone",
    "background_color": "#0d0d0d", "theme_color": "#0d0d0d",
    "description": "Self-hosted music, beautifully played."
}

SW_JS = """
const V = 'waves-v1';
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(clients.claim()));
self.addEventListener('fetch', e => e.respondWith(fetch(e.request).catch(() => caches.match(e.request))));
"""

# ── UI ────────────────────────────────────────────────────────────────────────
UI = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0d0d0d">
<meta name="apple-mobile-web-app-capable" content="yes">
<link rel="manifest" href="/manifest.json">
<title>Waves</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&family=Geist+Mono:wght@300;400&display=swap" rel="stylesheet">
<style>
/* ── Reset & Tokens ───────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --ink:      #f5f0e8;
  --ink2:     #7a7268;
  --ink3:     #3a3830;
  --paper:    #0d0d0d;
  --paper2:   #141414;
  --paper3:   #1c1c1c;
  --line:     rgba(245,240,232,0.07);
  --gold:     #c8a96e;
  --gold2:    #8a6d3e;
  --r:        10px;
  --font-ser: 'Cormorant Garamond', Georgia, serif;
  --font-mon: 'Geist Mono', 'Courier New', monospace;
  --ease:     cubic-bezier(0.4, 0, 0.2, 1);
}
html, body { height: 100%; overflow: hidden; background: var(--paper); color: var(--ink); }
body { font-family: var(--font-mon); font-size: 13px; letter-spacing: 0.01em; }
button { font-family: inherit; font-size: inherit; cursor: pointer; border: none; background: none; color: inherit; }
input  { font-family: inherit; font-size: inherit; }
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-thumb { background: var(--paper3); }
::selection { background: var(--gold2); color: var(--ink); }

/* ── Layout ───────────────────────────────────────────────────────────────── */
.app {
  display: grid;
  height: 100vh;
  grid-template-rows: 48px 1fr;
  grid-template-columns: 1fr;
}

/* ── Top Bar ──────────────────────────────────────────────────────────────── */
.topbar {
  grid-row: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  border-bottom: 1px solid var(--line);
  position: relative;
  z-index: 20;
}
.brand {
  font-family: var(--font-ser);
  font-size: 1.4rem;
  font-weight: 300;
  letter-spacing: 0.15em;
  color: var(--ink);
  font-style: italic;
}
.topbar-right { display: flex; align-items: center; gap: 4px; }
.tb-btn {
  width: 32px; height: 32px;
  border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  color: var(--ink2);
  transition: color 0.2s, background 0.2s;
}
.tb-btn:hover { color: var(--ink); background: var(--paper3); }
.tb-btn.lit   { color: var(--gold); }
.tb-btn svg   { display: block; }

/* ── Main Content ─────────────────────────────────────────────────────────── */
.main {
  grid-row: 2;
  display: grid;
  grid-template-columns: 300px 1fr;
  overflow: hidden;
}

/* ── Left Panel ───────────────────────────────────────────────────────────── */
.left {
  border-right: 1px solid var(--line);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Disc */
.disc-wrap {
  padding: 28px 28px 20px;
  display: flex;
  justify-content: center;
  flex-shrink: 0;
}
.disc {
  width: 200px; height: 200px;
  border-radius: 50%;
  background: var(--paper3);
  background-size: cover; background-position: center;
  position: relative;
  box-shadow: 0 20px 60px rgba(0,0,0,0.7);
  transition: box-shadow 0.6s var(--ease);
  flex-shrink: 0;
}
.disc.glowing { box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 60px rgba(200,169,110,0.06); }
.disc::before {
  content: '';
  position: absolute; inset: 0; border-radius: 50%;
  background: conic-gradient(from 0deg, rgba(255,255,255,0.03) 0%, transparent 40%, rgba(255,255,255,0.01) 100%);
  pointer-events: none;
}
.disc-inner {
  position: absolute; inset: 0; border-radius: 50%;
  background: radial-gradient(circle at 35% 30%, rgba(255,255,255,0.06) 0%, transparent 50%);
  pointer-events: none;
}
.disc-hole {
  position: absolute; top: 50%; left: 50%;
  transform: translate(-50%,-50%);
  width: 16%; height: 16%;
  background: var(--paper);
  border-radius: 50%;
  z-index: 1;
  box-shadow: 0 0 0 1px rgba(255,255,255,0.05);
}
.disc-ph {
  position: absolute; inset: 0; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-ser); font-size: 2.5rem;
  color: var(--ink3); opacity: 1;
  transition: opacity 0.5s;
}
.disc.spinning { animation: spin 12s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Now Playing */
.now-playing {
  padding: 0 24px 20px;
  flex-shrink: 0;
}
.np-title {
  font-family: var(--font-ser);
  font-size: 1.25rem;
  font-weight: 400;
  line-height: 1.3;
  color: var(--ink);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}
.np-fmt {
  font-size: 0.7rem;
  color: var(--ink3);
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

/* Progress */
.progress {
  padding: 0 24px 18px;
  flex-shrink: 0;
}
.seekbar {
  width: 100%; height: 1px;
  background: var(--ink3);
  position: relative;
  cursor: pointer;
  margin-bottom: 8px;
}
.seekbar::before { content: ''; position: absolute; inset: -8px 0; }
.seek-fill {
  position: absolute; top: 0; left: 0;
  height: 100%; width: 0%;
  background: var(--gold);
  transition: width 0.1s linear;
  pointer-events: none;
}
.seek-thumb {
  position: absolute; right: -4px; top: 50%;
  transform: translateY(-50%);
  width: 7px; height: 7px;
  background: var(--gold);
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.2s;
  pointer-events: none;
}
.seekbar:hover .seek-thumb { opacity: 1; }
.times {
  display: flex; justify-content: space-between;
  font-size: 0.68rem; color: var(--ink3);
  letter-spacing: 0.05em;
}

/* Controls */
.controls {
  padding: 0 20px 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  flex-shrink: 0;
}
.ctrl {
  width: 36px; height: 36px;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  color: var(--ink2);
  transition: color 0.2s, background 0.2s, transform 0.15s;
}
.ctrl:hover { color: var(--ink); background: var(--paper3); }
.ctrl:active { transform: scale(0.92); }
.ctrl.on { color: var(--gold); }
.play-ctrl {
  width: 44px; height: 44px;
  border-radius: 50%;
  border: 1px solid rgba(245,240,232,0.12);
  background: var(--paper2);
  color: var(--ink);
  transition: border-color 0.2s, background 0.2s, transform 0.15s;
}
.play-ctrl:hover { border-color: rgba(245,240,232,0.3); background: var(--paper3); }
.play-ctrl:active { transform: scale(0.94); }

/* ── Right Panel ──────────────────────────────────────────────────────────── */
.right {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.lib-head {
  padding: 16px 20px 12px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid var(--line);
}
.lib-label {
  font-family: var(--font-ser);
  font-size: 0.95rem;
  font-style: italic;
  color: var(--ink2);
  flex: 1;
}
.lib-count {
  font-size: 0.68rem;
  color: var(--ink3);
  letter-spacing: 0.08em;
}
.search {
  background: var(--paper2);
  border: 1px solid var(--line);
  border-radius: var(--r);
  padding: 6px 10px 6px 30px;
  color: var(--ink);
  outline: none;
  width: 160px;
  transition: border-color 0.2s, width 0.3s var(--ease);
}
.search:focus { border-color: rgba(245,240,232,0.15); width: 200px; }
.search::placeholder { color: var(--ink3); }
.search-wrap { position: relative; }
.search-icon {
  position: absolute; left: 8px; top: 50%;
  transform: translateY(-50%);
  color: var(--ink3); pointer-events: none;
}

/* Track list */
.tracklist-wrap { flex: 1; overflow-y: auto; }
.tracklist { list-style: none; padding: 6px 0; }
.track {
  display: grid;
  grid-template-columns: 32px 1fr auto;
  align-items: center;
  gap: 0 10px;
  padding: 9px 16px 9px 12px;
  cursor: pointer;
  border-left: 2px solid transparent;
  transition: background 0.15s, border-color 0.15s;
}
.track:hover { background: var(--paper2); }
.track.active {
  background: var(--paper2);
  border-left-color: var(--gold);
}
.track-num {
  font-size: 0.68rem;
  color: var(--ink3);
  text-align: right;
  line-height: 1;
}
.track.active .track-num { display: none; }
.wave-icon {
  display: none;
  align-items: flex-end;
  gap: 1.5px;
  height: 12px;
  justify-content: flex-end;
}
.track.active .wave-icon { display: flex; }
.wave-icon span {
  width: 2px;
  background: var(--gold);
  border-radius: 1px;
  animation: wave 0.6s ease-in-out infinite alternate;
}
.wave-icon span:nth-child(2) { animation-delay: 0.15s; }
.wave-icon span:nth-child(3) { animation-delay: 0.3s; }
@keyframes wave { from { height: 2px; } to { height: 12px; } }
.wave-icon.still span { animation-play-state: paused; height: 3px; }

.track-info { min-width: 0; }
.track-name {
  font-family: var(--font-ser);
  font-size: 1rem;
  font-weight: 400;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--ink);
  line-height: 1.3;
}
.track.active .track-name { color: var(--gold); }
.track-ext {
  font-size: 0.62rem;
  color: var(--ink3);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-top: 2px;
}
.del {
  opacity: 0;
  padding: 5px;
  border-radius: 5px;
  color: var(--ink3);
  transition: opacity 0.15s, color 0.15s, background 0.15s;
}
.track:hover .del { opacity: 1; }
.del:hover { color: #ef4444; background: rgba(239,68,68,0.08); }

/* Empty */
.empty {
  padding: 60px 24px;
  text-align: center;
  color: var(--ink3);
  font-family: var(--font-ser);
  font-style: italic;
  font-size: 1.05rem;
  line-height: 2;
}

/* ── Drawer ───────────────────────────────────────────────────────────────── */
.scrim {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.7);
  backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px);
  z-index: 50;
  opacity: 0; pointer-events: none;
  transition: opacity 0.3s var(--ease);
}
.scrim.open { opacity: 1; pointer-events: all; }
.drawer {
  position: fixed; top: 0; right: -100%;
  width: min(320px, 90vw); height: 100%;
  background: var(--paper2);
  border-left: 1px solid var(--line);
  z-index: 51;
  display: flex; flex-direction: column;
  transition: right 0.35s var(--ease);
}
.drawer.open { right: 0; }
.drawer-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--line);
  flex-shrink: 0;
}
.drawer-title {
  font-family: var(--font-ser);
  font-style: italic;
  font-size: 1.1rem;
  color: var(--ink);
}
.drawer-x {
  width: 28px; height: 28px;
  border-radius: 6px;
  color: var(--ink2);
  display: flex; align-items: center; justify-content: center;
  transition: color 0.2s, background 0.2s;
}
.drawer-x:hover { color: var(--ink); background: var(--paper3); }
.drawer-body { flex: 1; overflow-y: auto; padding: 22px 20px; display: flex; flex-direction: column; gap: 28px; }

.ds-group { display: flex; flex-direction: column; gap: 10px; }
.ds-label {
  font-size: 0.62rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--ink3);
}
.ds-row { display: flex; align-items: center; gap: 10px; }
.ds-row svg { color: var(--ink3); flex-shrink: 0; }
.ds-hint { font-size: 0.68rem; color: var(--ink3); line-height: 1.6; }
.slider {
  flex: 1; -webkit-appearance: none; appearance: none;
  height: 1px; background: var(--ink3); border-radius: 1px; outline: none;
  cursor: pointer;
}
.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 11px; height: 11px;
  background: var(--gold); border-radius: 50%; cursor: pointer;
}
.slider::-moz-range-thumb {
  width: 11px; height: 11px;
  background: var(--gold); border-radius: 50%; border: none;
}
.ds-val { font-size: 0.72rem; color: var(--ink); min-width: 32px; text-align: right; }

/* Pill buttons (sleep timer) */
.pill-group { display: flex; flex-wrap: wrap; gap: 6px; }
.pill {
  padding: 5px 12px;
  border-radius: 50px;
  border: 1px solid var(--line);
  font-size: 0.7rem;
  color: var(--ink2);
  background: var(--paper3);
  letter-spacing: 0.05em;
  transition: all 0.2s;
}
.pill:hover { border-color: rgba(245,240,232,0.2); color: var(--ink); }
.pill.sel { border-color: var(--gold2); color: var(--gold); background: rgba(200,169,110,0.06); }

/* Upload */
.upload-zone {
  border: 1px dashed var(--line);
  border-radius: var(--r);
  padding: 20px 16px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
}
.upload-zone:hover { border-color: rgba(245,240,232,0.18); background: var(--paper3); }
.upload-zone input { display: none; }
.upload-glyph { font-family: var(--font-ser); font-size: 1.8rem; color: var(--ink3); margin-bottom: 8px; }
.upload-hint { font-size: 0.7rem; color: var(--ink3); line-height: 1.7; }
.upload-btn {
  margin-top: 12px;
  padding: 7px 20px;
  border-radius: 50px;
  border: 1px solid var(--gold2);
  color: var(--gold);
  background: rgba(200,169,110,0.06);
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  display: none;
  transition: background 0.2s;
}
.upload-btn.vis { display: inline-block; }
.upload-btn:hover { background: rgba(200,169,110,0.12); }

/* ── Cinematic ────────────────────────────────────────────────────────────── */
.cine {
  position: fixed; inset: 0;
  background: #000;
  z-index: 100;
  display: flex; align-items: center; justify-content: center;
  opacity: 0; pointer-events: none;
  transition: opacity 0.6s var(--ease);
  cursor: pointer;
}
.cine.open { opacity: 1; pointer-events: all; }
.cine-disc {
  width: min(70vmin, 520px);
  height: min(70vmin, 520px);
  border-radius: 50%;
  background: var(--paper3);
  background-size: cover; background-position: center;
  position: relative;
  box-shadow: 0 0 120px rgba(200,169,110,0.05);
}
.cine-disc::before {
  content: '';
  position: absolute; inset: 0; border-radius: 50%;
  background: radial-gradient(circle at 35% 30%, rgba(255,255,255,0.05) 0%, transparent 50%);
}
.cine-hole {
  position: absolute; top: 50%; left: 50%;
  transform: translate(-50%,-50%);
  width: 15%; height: 15%;
  background: #000; border-radius: 50%; z-index: 1;
}
.cine-disc.spinning { animation: spin 12s linear infinite; }
.cine-esc {
  position: fixed; bottom: 28px; left: 50%;
  transform: translateX(-50%);
  font-size: 0.6rem; color: rgba(255,255,255,0.15);
  letter-spacing: 0.2em; text-transform: uppercase;
  pointer-events: none;
}

/* ── Toast ────────────────────────────────────────────────────────────────── */
.toast {
  position: fixed; bottom: 20px; left: 50%;
  transform: translateX(-50%) translateY(10px);
  background: var(--paper2);
  border: 1px solid var(--line);
  color: var(--ink2);
  font-size: 0.72rem; letter-spacing: 0.04em;
  padding: 7px 16px; border-radius: 50px;
  opacity: 0; pointer-events: none;
  transition: all 0.25s var(--ease);
  z-index: 200; white-space: nowrap;
}
.toast.show { opacity: 1; transform: translateX(-50%) translateY(0); }

/* ── Mobile ───────────────────────────────────────────────────────────────── */
@media (max-width: 680px) {
  .app { grid-template-rows: 48px 1fr; }
  .main { grid-template-columns: 1fr; grid-template-rows: auto 1fr; }
  .left {
    border-right: none;
    border-bottom: 1px solid var(--line);
    overflow: visible;
  }
  .disc-wrap { padding: 16px 0 12px; }
  .disc { width: 130px; height: 130px; }
  .now-playing { padding: 0 16px 10px; text-align: center; }
  .np-title { font-size: 1rem; }
  .progress { padding: 0 16px 12px; }
  .controls { padding: 0 16px 16px; gap: 4px; }
  .disc-wrap { justify-content: flex-start; padding: 16px 16px 12px; }
  .left { display: grid; grid-template-columns: 160px 1fr; grid-template-rows: auto auto; gap: 0 16px; padding: 12px 16px; }
  .disc-wrap { grid-row: 1 / 3; grid-column: 1; padding: 0; justify-content: center; align-items: center; }
  .disc { width: 120px; height: 120px; }
  .now-playing { grid-row: 1; grid-column: 2; padding: 4px 0 0 0; text-align: left; }
  .progress { grid-row: 2; grid-column: 2; padding: 8px 0 0 0; }
  .controls { grid-column: 1 / -1; grid-row: 3; border-top: 1px solid var(--line); padding: 12px 16px; justify-content: space-between; }
  .right { overflow: hidden; }
  .lib-head { padding: 10px 14px 8px; }
  .search { width: 120px; }
  .search:focus { width: 150px; }
}
</style>
</head>
<body>
<div class="app">

  <!-- Top Bar -->
  <header class="topbar">
    <div class="brand">Waves</div>
    <div class="topbar-right">
      <button class="tb-btn" id="cineBtn" title="Cinematic">
        <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
          <rect x="2" y="5" width="20" height="14" rx="2"/>
          <polygon points="10,9 16,12 10,15" fill="currentColor" stroke="none"/>
        </svg>
      </button>
      <button class="tb-btn" id="settingsBtn" title="Settings">
        <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="3"/>
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
        </svg>
      </button>
    </div>
  </header>

  <!-- Main -->
  <div class="main">

    <!-- Left: Player -->
    <div class="left">
      <div class="disc-wrap">
        <div class="disc" id="disc">
          <div class="disc-inner"></div>
          <div class="disc-hole"></div>
          <div class="disc-ph" id="discPh">♩</div>
        </div>
      </div>

      <div class="now-playing">
        <div class="np-title" id="npTitle">Nothing playing</div>
        <div class="np-fmt" id="npFmt">—</div>
      </div>

      <div class="progress">
        <div class="seekbar" id="seekbar">
          <div class="seek-fill" id="seekFill">
            <div class="seek-thumb"></div>
          </div>
        </div>
        <div class="times">
          <span id="tCur">0:00</span>
          <span id="tDur">0:00</span>
        </div>
      </div>

      <div class="controls">
        <button class="ctrl" id="shuffleBtn" title="Shuffle">
          <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
            <polyline points="16,3 21,3 21,8"/><line x1="4" y1="20" x2="21" y2="3"/>
            <polyline points="21,16 21,21 16,21"/><line x1="15" y1="15" x2="21" y2="21"/>
            <line x1="4" y1="4" x2="9" y2="9"/>
          </svg>
        </button>
        <button class="ctrl" id="prevBtn" title="Previous">
          <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
            <polygon points="19,20 9,12 19,4" fill="currentColor" stroke="none"/>
            <line x1="5" y1="19" x2="5" y2="5"/>
          </svg>
        </button>
        <button class="ctrl play-ctrl" id="playBtn">
          <svg id="iconPlay" width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><polygon points="5,3 19,12 5,21"/></svg>
          <svg id="iconPause" width="16" height="16" fill="currentColor" viewBox="0 0 24 24" style="display:none"><rect x="6" y="3" width="4" height="18" rx="1"/><rect x="14" y="3" width="4" height="18" rx="1"/></svg>
        </button>
        <button class="ctrl" id="nextBtn" title="Next">
          <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
            <polygon points="5,4 15,12 5,20" fill="currentColor" stroke="none"/>
            <line x1="19" y1="4" x2="19" y2="20"/>
          </svg>
        </button>
        <button class="ctrl" id="loopBtn" title="Loop library">
          <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
            <polyline points="17,1 21,5 17,9"/>
            <path d="M3 11V9a4 4 0 0 1 4-4h14"/>
            <polyline points="7,23 3,19 7,15"/>
            <path d="M21 13v2a4 4 0 0 1-4 4H3"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Right: Library -->
    <div class="right">
      <div class="lib-head">
        <span class="lib-label">Library</span>
        <span class="lib-count" id="libCount">{{ tracks|length }} track{% if tracks|length != 1 %}s{% endif %}</span>
        <div class="search-wrap">
          <svg class="search-icon" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
          </svg>
          <input class="search" type="text" id="searchEl" placeholder="search…" autocomplete="off">
        </div>
      </div>
      <div class="tracklist-wrap">
        <ul class="tracklist" id="tracklist">
          {% for t in tracks %}
          <li class="track" data-i="{{ loop.index0 }}" data-file="{{ t }}">
            <span class="track-num">{{ loop.index }}</span>
            <span class="wave-icon still" id="wi{{ loop.index0 }}">
              <span></span><span></span><span></span>
            </span>
            <div class="track-info">
              <div class="track-name">{{ t | replace('.flac','') | replace('.mp3','') | replace('.wav','') | replace('.ogg','') | replace('.m4a','') | replace('.aac','') | replace('.opus','') }}</div>
              <div class="track-ext">{{ t.split('.')[-1].upper() }}</div>
            </div>
            <form method="POST" action="/delete/{{ t }}" onsubmit="return confirm('Delete {{ t }}?')">
              <button type="submit" class="del" title="Delete" onclick="event.stopPropagation()">
                <svg width="12" height="12" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <polyline points="3,6 5,6 21,6"/><path d="M19,6l-1,14H6L5,6"/><path d="M10,11v6"/><path d="M14,11v6"/><path d="M9,6V4h6v2"/>
                </svg>
              </button>
            </form>
          </li>
          {% endfor %}
          {% if not tracks %}
          <li class="empty">No music yet.<br>Add files via Settings ↗</li>
          {% endif %}
        </ul>
      </div>
    </div>
  </div>
</div>

<!-- Hidden audio elements for crossfade -->
<audio id="audA" preload="auto"></audio>
<audio id="audB" preload="auto"></audio>

<!-- Cinematic overlay -->
<div class="cine" id="cine">
  <div class="cine-disc" id="cineDisc">
    <div class="cine-hole"></div>
  </div>
  <div class="cine-esc">tap to exit · esc</div>
</div>

<!-- Settings drawer -->
<div class="scrim" id="scrim"></div>
<div class="drawer" id="drawer">
  <div class="drawer-head">
    <span class="drawer-title">Settings</span>
    <button class="drawer-x" id="drawerX">
      <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
      </svg>
    </button>
  </div>
  <div class="drawer-body">

    <!-- Volume -->
    <div class="ds-group">
      <div class="ds-label">Volume</div>
      <div class="ds-row">
        <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
          <polygon points="11,5 6,9 2,9 2,15 6,15 11,19"/>
          <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/>
        </svg>
        <input type="range" class="slider" id="volSlider" min="0" max="100" value="90">
        <span class="ds-val" id="volVal">90%</span>
      </div>
    </div>

    <!-- Crossfade -->
    <div class="ds-group">
      <div class="ds-label">Crossfade</div>
      <div class="ds-row">
        <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
          <path d="M17 3l4 4-4 4M7 21l-4-4 4-4"/>
          <path d="M3 7h4a4 4 0 0 1 4 4v0a4 4 0 0 0 4 4h6"/>
        </svg>
        <input type="range" class="slider" id="xfSlider" min="0" max="8" value="3" step="1">
        <span class="ds-val" id="xfVal">3s</span>
      </div>
      <div class="ds-hint">Seamlessly blends tracks. Requires loop.</div>
    </div>

    <!-- Sleep Timer -->
    <div class="ds-group">
      <div class="ds-label">Sleep Timer</div>
      <div class="pill-group">
        <button class="pill sel" data-min="0">Off</button>
        <button class="pill" data-min="15">15 min</button>
        <button class="pill" data-min="30">30 min</button>
        <button class="pill" data-min="45">45 min</button>
        <button class="pill" data-min="60">1 hour</button>
      </div>
      <div class="ds-hint" id="sleepHint"></div>
    </div>

    <!-- Upload -->
    <div class="ds-group">
      <div class="ds-label">Upload</div>
      <form id="uploadForm" action="/upload" method="POST" enctype="multipart/form-data">
        <div class="upload-zone" id="uploadZone">
          <input type="file" id="fileEl" name="file" accept="audio/*" multiple>
          <div class="upload-glyph">♫</div>
          <div class="upload-hint" id="uploadHint">
            Tap to choose audio files<br>
            <span style="font-size:0.62rem;opacity:0.5">MP3 · FLAC · WAV · M4A · OGG · OPUS</span>
          </div>
          <button type="submit" class="upload-btn" id="uploadBtn">Upload</button>
        </div>
      </form>
    </div>

  </div>
</div>

<div class="toast" id="toast"></div>

<script>
'use strict';

// ── Data from server ──────────────────────────────────────────────────────────
const TRACKS  = {{ tracks|tojson }};
const COVERS  = {{ covers|tojson }};

// ── State ─────────────────────────────────────────────────────────────────────
let idx       = -1;       // current track index
let covIdx    = 0;        // sequential cover index
let looping   = false;
let shuffling = false;
let playing   = false;
let xfSec     = 3;        // crossfade seconds
let vol       = 0.9;
let xfading   = false;    // crossfade in progress

// ── Dual audio for crossfade ──────────────────────────────────────────────────
const audA = document.getElementById('audA');
const audB = document.getElementById('audB');
let cur = audA;   // currently playing
let nxt = audB;   // incoming (crossfade)
cur.volume = vol; nxt.volume = 0;

// ── DOM ───────────────────────────────────────────────────────────────────────
const disc      = document.getElementById('disc');
const discPh    = document.getElementById('discPh');
const cineDisc  = document.getElementById('cineDisc');
const npTitle   = document.getElementById('npTitle');
const npFmt     = document.getElementById('npFmt');
const seekbar   = document.getElementById('seekbar');
const seekFill  = document.getElementById('seekFill');
const tCur      = document.getElementById('tCur');
const tDur      = document.getElementById('tDur');
const playBtn   = document.getElementById('playBtn');
const iconPlay  = document.getElementById('iconPlay');
const iconPause = document.getElementById('iconPause');
const loopBtn   = document.getElementById('loopBtn');
const shuffleBtn= document.getElementById('shuffleBtn');
const prevBtn   = document.getElementById('prevBtn');
const nextBtn   = document.getElementById('nextBtn');
const tracklist = document.getElementById('tracklist');
const searchEl  = document.getElementById('searchEl');
const cine      = document.getElementById('cine');
const scrim     = document.getElementById('scrim');
const drawer    = document.getElementById('drawer');
const toast     = document.getElementById('toast');
const volSlider = document.getElementById('volSlider');
const volVal    = document.getElementById('volVal');
const xfSlider  = document.getElementById('xfSlider');
const xfVal     = document.getElementById('xfVal');
const uploadZone= document.getElementById('uploadZone');
const fileEl    = document.getElementById('fileEl');
const uploadHint= document.getElementById('uploadHint');
const uploadBtn = document.getElementById('uploadBtn');
const sleepHint = document.getElementById('sleepHint');

// ── Utilities ─────────────────────────────────────────────────────────────────
const fmt = s => (!s || isNaN(s)) ? '0:00' : `${Math.floor(s/60)}:${String(Math.floor(s%60)).padStart(2,'0')}`;

function toast_(msg, ms = 2200) {
  toast.textContent = msg;
  toast.classList.add('show');
  clearTimeout(toast._t);
  toast._t = setTimeout(() => toast.classList.remove('show'), ms);
}

function setCover(url) {
  const bg = url ? `url('${url}')` : '';
  disc.style.backgroundImage = bg;
  cineDisc.style.backgroundImage = bg;
  disc.classList.toggle('glowing', !!url);
  discPh.style.opacity = url ? '0' : '1';
}

function nextCover() {
  if (!COVERS.length) return null;
  const url = `/cover/${encodeURIComponent(COVERS[covIdx])}`;
  covIdx = (covIdx + 1) % COVERS.length;
  return url;
}

function nextIdx_() {
  if (!TRACKS.length) return -1;
  if (shuffling) {
    let n; do { n = Math.floor(Math.random() * TRACKS.length); } while (n === idx && TRACKS.length > 1);
    return n;
  }
  return (idx + 1) % TRACKS.length;
}

function prevIdx_() {
  if (!TRACKS.length) return -1;
  if (cur.currentTime > 3) return idx;   // restart current
  return ((idx - 1) + TRACKS.length) % TRACKS.length;
}

// ── UI Sync ───────────────────────────────────────────────────────────────────
// Always called from outside events to reflect true cur state.
// Never use element identity comparison for play/pause events.
function syncPlayUI() {
  if (xfading) return;  // mid-crossfade: let crossfadeTo() call us when done
  const p = !cur.paused;
  playing = p;
  iconPlay.style.display  = p ? 'none'  : 'block';
  iconPause.style.display = p ? 'block' : 'none';
  disc.classList.toggle('spinning', p);
  cineDisc.classList.toggle('spinning', p);
  if (idx >= 0) {
    const wi = document.getElementById(`wi${idx}`);
    if (wi) wi.classList.toggle('still', !p);
  }
}

function setActive(i) {
  document.querySelectorAll('.track').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.wave-icon').forEach(wi => wi.classList.add('still'));
  if (i < 0) return;
  const el = document.querySelector(`.track[data-i="${i}"]`);
  if (el) { el.classList.add('active'); el.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); }
}

function setMeta(title) {
  if (!('mediaSession' in navigator)) return;
  navigator.mediaSession.metadata = new MediaMetadata({ title, artist: 'Waves' });
  navigator.mediaSession.setActionHandler('previoustrack', () => skip(-1));
  navigator.mediaSession.setActionHandler('nexttrack',     () => skip(1));
  navigator.mediaSession.setActionHandler('play',  () => cur.play());
  navigator.mediaSession.setActionHandler('pause', () => cur.pause());
}

// ── Playback ──────────────────────────────────────────────────────────────────
function loadTrack(i, autoplay = true) {
  if (!TRACKS.length) return;
  i = ((i % TRACKS.length) + TRACKS.length) % TRACKS.length;
  idx = i;

  const file  = TRACKS[i];
  const title = file.replace(/\.[^.]+$/, '');
  const ext   = file.split('.').pop().toUpperCase();

  npTitle.textContent = title;
  npFmt.textContent   = ext + ' · Lossless';
  setCover(nextCover());
  setActive(i);
  setMeta(title);

  cur.volume = vol;
  cur.src    = `/stream/${encodeURIComponent(file)}`;
  cur.load();

  if (autoplay) {
    cur.addEventListener('canplaythrough', function go() {
      cur.removeEventListener('canplaythrough', go);
      cur.play().catch(() => {});
    });
  }
}

// Crossfade: fade cur out, nxt in — then swap
function crossfadeTo(nextI) {
  if (xfading || nextI < 0) return;
  xfading = true;

  const file  = TRACKS[nextI];
  const title = file.replace(/\.[^.]+$/, '');
  const ext   = file.split('.').pop().toUpperCase();
  const cover = nextCover();

  // Capture physical elements before any swap
  const fadeOut = cur;
  const fadeIn  = nxt;

  // Reset incoming player
  if (fadeIn._onReady) { fadeIn.removeEventListener('canplaythrough', fadeIn._onReady); fadeIn._onReady = null; }
  fadeIn.pause();
  fadeIn.currentTime = 0;
  fadeIn.volume = 0;
  fadeIn.src = `/stream/${encodeURIComponent(file)}`;
  fadeIn.load();

  let fired = false;  // guard against double-fire (cached tracks fire canplaythrough instantly AND via event)

  function beginFade() {
    if (fired) return;
    fired = true;
    fadeIn.removeEventListener('canplaythrough', fadeIn._onReady);
    fadeIn._onReady = null;
    fadeIn.play().catch(() => {});

    const STEPS   = 60;
    const tick    = (xfSec * 1000) / STEPS;
    const volStep = vol / STEPS;
    let   step    = 0;

    const iv = setInterval(() => {
      step++;
      fadeOut.volume = Math.max(0, vol - volStep * step);
      fadeIn.volume  = Math.min(vol, volStep * step);

      if (step < STEPS) return;
      clearInterval(iv);

      // Finish
      fadeOut.pause();
      fadeOut.src    = '';
      fadeOut.volume = vol;   // reset for future use as nxt

      // Swap logical roles
      cur = fadeIn;
      nxt = fadeOut;
      idx = nextI;
      xfading = false;

      // Update UI
      npTitle.textContent = title;
      npFmt.textContent   = ext + ' · Lossless';
      setCover(cover);
      setActive(nextI);
      setMeta(title);
      syncPlayUI();   // safe to call now that xfading = false
    }, tick);
  }

  fadeIn._onReady = beginFade;
  fadeIn.addEventListener('canplaythrough', fadeIn._onReady);
  setTimeout(() => { if (!fired && xfading) beginFade(); }, 1000);  // fallback
}

function skip(dir) {
  const i = dir > 0 ? nextIdx_() : prevIdx_();
  if (i < 0) return;
  if (dir < 0 && i === idx) { cur.currentTime = 0; return; }
  // Cancel any running crossfade
  if (nxt._onReady) { nxt.removeEventListener('canplaythrough', nxt._onReady); nxt._onReady = null; }
  nxt.pause(); nxt.src = ''; nxt.volume = 0;
  xfading = false;
  cur.pause();
  loadTrack(i);
}

// ── Audio events ──────────────────────────────────────────────────────────────
// Key insight: audA and audB swap roles as cur/nxt after each crossfade.
// We cannot use `el === cur` at event bind time. So we attach to both,
// and always query the live `cur` reference inside the handler.

audA.addEventListener('play',  syncPlayUI);
audB.addEventListener('play',  syncPlayUI);
audA.addEventListener('pause', syncPlayUI);
audB.addEventListener('pause', syncPlayUI);

function onTimeUpdate(e) {
  if (e.target !== cur || xfading) return;
  const { currentTime: ct, duration: dur } = e.target;
  if (!dur) return;
  seekFill.style.width = `${(ct / dur) * 100}%`;
  tCur.textContent = fmt(ct);
  tDur.textContent = fmt(dur);

  // Trigger crossfade when `xfSec` seconds remain
  if (looping && !xfading && xfSec > 0) {
    const rem = dur - ct;
    if (rem <= xfSec && rem > xfSec - 0.25) {
      crossfadeTo(nextIdx_());
    }
  }
}
audA.addEventListener('timeupdate', onTimeUpdate);
audB.addEventListener('timeupdate', onTimeUpdate);

function onEnded(e) {
  if (e.target !== cur) return;
  if (looping && xfSec === 0) loadTrack(nextIdx_());
  else if (!looping) syncPlayUI();
}
audA.addEventListener('ended', onEnded);
audB.addEventListener('ended', onEnded);

// ── Controls ──────────────────────────────────────────────────────────────────
playBtn.addEventListener('click', () => {
  if (!cur.src) { if (TRACKS.length) loadTrack(0); return; }
  playing ? cur.pause() : cur.play().catch(() => {});
});
prevBtn.addEventListener('click', () => skip(-1));
nextBtn.addEventListener('click', () => skip(1));

loopBtn.addEventListener('click', () => {
  looping = !looping;
  loopBtn.classList.toggle('on', looping);
  toast_(looping ? '↻  loop on' : 'loop off');
});
shuffleBtn.addEventListener('click', () => {
  shuffling = !shuffling;
  shuffleBtn.classList.toggle('on', shuffling);
  toast_(shuffling ? '⇄  shuffle on' : 'shuffle off');
});

seekbar.addEventListener('click', e => {
  if (!cur.duration) return;
  const r = seekbar.getBoundingClientRect();
  cur.currentTime = ((e.clientX - r.left) / r.width) * cur.duration;
});

// Tracklist clicks
tracklist.addEventListener('click', e => {
  if (e.target.closest('form')) return;  // delete form handles itself
  const row = e.target.closest('.track');
  if (!row) return;
  if (nxt._onReady) { nxt.removeEventListener('canplaythrough', nxt._onReady); nxt._onReady = null; }
  nxt.pause(); nxt.src = ''; nxt.volume = 0;
  xfading = false;
  cur.pause();
  loadTrack(parseInt(row.dataset.i));
});

// Search
searchEl.addEventListener('input', () => {
  const q = searchEl.value.toLowerCase();
  document.querySelectorAll('.track').forEach(el => {
    el.style.display = el.querySelector('.track-name').textContent.toLowerCase().includes(q) ? '' : 'none';
  });
});

// ── Settings drawer ───────────────────────────────────────────────────────────
document.getElementById('settingsBtn').addEventListener('click', openDrawer);
document.getElementById('drawerX').addEventListener('click', closeDrawer);
scrim.addEventListener('click', closeDrawer);
function openDrawer()  { drawer.classList.add('open'); scrim.classList.add('open'); }
function closeDrawer() { drawer.classList.remove('open'); scrim.classList.remove('open'); }

volSlider.addEventListener('input', () => {
  vol = volSlider.value / 100;
  cur.volume = vol;
  volVal.textContent = `${volSlider.value}%`;
});

xfSlider.addEventListener('input', () => {
  xfSec = parseInt(xfSlider.value);
  xfVal.textContent = xfSec === 0 ? 'Off' : `${xfSec}s`;
});

// ── Sleep Timer ───────────────────────────────────────────────────────────────
let sleepTimeout = null, sleepCountInterval = null, sleepEnd = null;

document.querySelectorAll('.pill').forEach(btn => {
  btn.addEventListener('click', () => {
    const mins = parseInt(btn.dataset.min);
    document.querySelectorAll('.pill').forEach(b => b.classList.remove('sel'));
    btn.classList.add('sel');

    clearTimeout(sleepTimeout);
    clearInterval(sleepCountInterval);
    sleepTimeout = null; sleepEnd = null;

    if (mins === 0) {
      sleepHint.textContent = '';
      toast_('sleep timer off');
      return;
    }

    sleepEnd = Date.now() + mins * 60_000;
    toast_(`sleep in ${mins} min`);

    const updateHint = () => {
      const rem = Math.ceil((sleepEnd - Date.now()) / 60_000);
      sleepHint.textContent = rem > 0 ? `Pausing in ${rem} min` : 'Pausing…';
    };
    updateHint();
    sleepCountInterval = setInterval(updateHint, 30_000);

    sleepTimeout = setTimeout(() => {
      cur.pause();
      clearInterval(sleepCountInterval);
      sleepEnd = null;
      sleepHint.textContent = '';
      document.querySelectorAll('.pill').forEach(b => b.classList.remove('sel'));
      document.querySelector('.pill[data-min="0"]').classList.add('sel');
      toast_('goodnight 🌙', 3000);
    }, mins * 60_000);
  });
});

// ── Upload ────────────────────────────────────────────────────────────────────
uploadZone.addEventListener('click', () => fileEl.click());
fileEl.addEventListener('change', () => {
  if (!fileEl.files.length) return;
  const names = Array.from(fileEl.files).map(f => f.name).join(', ');
  uploadHint.textContent = names;
  uploadBtn.classList.add('vis');
});

// ── Cinematic ─────────────────────────────────────────────────────────────────
document.getElementById('cineBtn').addEventListener('click', openCine);
cine.addEventListener('click', closeCine);

function openCine() {
  cine.classList.add('open');
  cineDisc.classList.toggle('spinning', playing);
  cine.requestFullscreen?.().catch(() => {});
  cine.webkitRequestFullscreen?.();
}
function closeCine() {
  cine.classList.remove('open');
  document.fullscreenElement && document.exitFullscreen?.().catch(() => {});
  document.webkitFullscreenElement && document.webkitExitFullscreen?.();
}
document.addEventListener('fullscreenchange', () => { if (!document.fullscreenElement) cine.classList.remove('open'); });
document.addEventListener('webkitfullscreenchange', () => { if (!document.webkitFullscreenElement) cine.classList.remove('open'); });

// ── Keyboard ──────────────────────────────────────────────────────────────────
document.addEventListener('keydown', e => {
  if (['INPUT', 'TEXTAREA'].includes(e.target.tagName)) return;
  if (e.code === 'Space')       { e.preventDefault(); playBtn.click(); }
  if (e.code === 'ArrowRight')  skip(1);
  if (e.code === 'ArrowLeft')   skip(-1);
  if (e.key  === 'l')           loopBtn.click();
  if (e.key  === 's')           shuffleBtn.click();
  if (e.code === 'Escape')      closeCine();
});

// ── PWA ───────────────────────────────────────────────────────────────────────
if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js');
</script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
