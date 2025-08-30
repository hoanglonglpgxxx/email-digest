# main.py (simple single-button flow)
import streamlit as st
import requests
import tempfile
import os
import subprocess
import shlex
from pathlib import Path

# ---------- Config ----------
CLIENT_ID = "OeDHpok8199e6vW8pnF7SljVEa4tYz6z"  # fixed as requested
API_BASE = "https://api-v2.soundcloud.com"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0"
# ----------------------------

st.set_page_config(page_title="SoundCloud Downloader — Simple", page_icon="🎵", layout="centered")
st.title("🎵 SoundCloud Downloader — Simple")
st.caption("Paste a SoundCloud URL and click Fetch & Download. Only for personal use; respect copyrights.")

# Inputs
url = st.text_input("SoundCloud track URL (e.g. https://soundcloud.com/artist/track)")

# session_state to persist tmp file path between reruns
if "tmp_path" not in st.session_state:
    st.session_state.tmp_path = None
if "last_url" not in st.session_state:
    st.session_state.last_url = None
if "track_title" not in st.session_state:
    st.session_state.track_title = None

# ---------- Helpers ----------
def resolve_track(url, client_id):
    try:
        resolve_url = f"{API_BASE}/resolve?url={url}&client_id={client_id}"
        r = requests.get(resolve_url, allow_redirects=True, headers={"User-Agent": USER_AGENT}, timeout=15)
        if r.status_code == 200:
            j = r.json()
            if j.get("kind") == "track":
                return j
        return None
    except Exception as e:
        st.write("resolve exception:", e)
        return None

def get_track_json_by_id(track_id, client_id):
    try:
        r = requests.get(f"{API_BASE}/tracks/{track_id}?client_id={client_id}", headers={"User-Agent": USER_AGENT}, timeout=15)
        if r.status_code == 200:
            return r.json()
        else:
            return None
    except Exception as e:
        st.write("get_track_by_id exception:", e)
        return None

def find_stream_url(track_json, client_id):
    # prefer progressive, fallback to hls; returns (stream_url, protocol) or (None, None)
    if not track_json:
        return (None, None)
    media = track_json.get("media")
    if not media:
        return (None, None)
    for t in media.get("transcodings", []) or []:
        proto = (t.get("format") or {}).get("protocol", "")
        if proto == "progressive":
            try:
                r = requests.get(t["url"] + f"?client_id={client_id}", headers={"User-Agent": USER_AGENT}, timeout=15)
                if r.status_code == 200:
                    return (r.json().get("url"), "progressive")
            except Exception:
                pass
    for t in media.get("transcodings", []) or []:
        proto = (t.get("format") or {}).get("protocol", "")
        if "hls" in proto:
            try:
                r = requests.get(t["url"] + f"?client_id={client_id}", headers={"User-Agent": USER_AGENT}, timeout=15)
                if r.status_code == 200:
                    return (r.json().get("url"), "hls")
            except Exception:
                pass
    return (None, None)

def download_url_to_tempfile(stream_url, title="track"):
    try:
        headers = {"User-Agent": USER_AGENT}
        r = requests.get(stream_url, headers=headers, stream=True, timeout=60)
        if r.status_code != 200:
            st.write("download status:", r.status_code)
            return None
        suffix = ".mp3" if "audio" in (r.headers.get("content-type") or "") or ".mp3" in stream_url else ".bin"
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        with tmp as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return tmp.name
    except Exception as e:
        st.write("download exception:", e)
        return None

def ffmpeg_hls_to_mp3(hls_url, out_path):
    cmd = f'ffmpeg -y -i "{hls_url}" -c:a libmp3lame -b:a 192k "{out_path}"'
    try:
        proc = subprocess.run(shlex.split(cmd), capture_output=True, text=True, timeout=1800)
        if proc.returncode == 0 and Path(out_path).exists():
            return True, proc.stderr
        else:
            return False, proc.stderr or proc.stdout
    except FileNotFoundError:
        return False, "ffmpeg not found"
    except subprocess.TimeoutExpired:
        return False, "ffmpeg timeout"

def cleanup_tmp():
    p = st.session_state.get("tmp_path")
    if p and os.path.exists(p):
        try:
            os.remove(p)
        except Exception:
            pass
    st.session_state.tmp_path = None
    st.session_state.track_title = None

# ---------- Single action: Fetch & Download ----------
if st.button("Fetch & Download"):
    # clear old tmp if URL changed
    if st.session_state.last_url != url:
        cleanup_tmp()
        st.session_state.last_url = url

    if not url:
        st.error("Paste a SoundCloud URL first.")
    else:
        st.info("Resolving track and fetching stream URL (this run will attempt download).")
        track = resolve_track(url, CLIENT_ID)
        if not track:
            st.error("Could not resolve track. (client_id may be blocked or track private)")
        else:
            # some resolve responses are partial - get the full track JSON by id if possible
            track_id = track.get("id")
            if track_id:
                track_json = get_track_json_by_id(track_id, CLIENT_ID) or track
            else:
                track_json = track

            title = track_json.get("title") or "track"
            st.session_state.track_title = title

            stream_url, proto = find_stream_url(track_json, CLIENT_ID)
            if not stream_url:
                st.error("Couldn't find progressive or HLS stream URL for this track.")
            else:
                st.success(f"Found stream ({proto}). Attempting to produce MP3...")
                st.write(stream_url)
                # if progressive -> download directly
                if proto == "progressive":
                    tmp = download_url_to_tempfile(stream_url, title=title)
                    if tmp:
                        st.session_state.tmp_path = tmp
                        st.success("Downloaded progressive stream to temporary file.")
                    else:
                        st.error("Failed to download progressive stream.")
                else:
                    # HLS path -> convert with ffmpeg
                    safe_name = "".join(c for c in (title or "track") if c.isalnum() or c in " -_").strip()[:80] or "track"
                    out_path = Path(tempfile.gettempdir()) / f"{safe_name}.mp3"
                    # remove if exists
                    try:
                        if out_path.exists():
                            out_path.unlink()
                    except Exception:
                        pass
                    ok, ffout = ffmpeg_hls_to_mp3(stream_url, str(out_path))
                    if ok and out_path.exists():
                        st.session_state.tmp_path = str(out_path)
                        st.success("Converted HLS to MP3 and saved to temporary file.")
                    else:
                        if ffout == "ffmpeg not found":
                            st.error("ffmpeg not found on server. Install ffmpeg to convert HLS to MP3.")
                        else:
                            st.error("Failed to convert HLS to MP3. ffmpeg output:")
                            st.code(str(ffout))

# ---------- If tmp file exists show download button ----------
if st.session_state.tmp_path and os.path.exists(st.session_state.tmp_path):
    title = st.session_state.track_title or "track"
    safe_name = "".join(c for c in title if c.isalnum() or c in " -_").strip()[:80] or "track"
    file_name = f"{safe_name}.mp3"
    try:
        with open(st.session_state.tmp_path, "rb") as f:
            data = f.read()
        st.download_button("⬇️ Download MP3", data, file_name=file_name, mime="audio/mpeg")
        # cleanup after providing download
        try:
            os.remove(st.session_state.tmp_path)
        except Exception:
            pass
        st.session_state.tmp_path = None
        st.success("Temporary file removed from server.")
    except Exception as e:
        st.error("Failed to read temporary file for download: " + str(e))
        st.session_state.tmp_path = None

st.markdown("---")
st.caption("Simple flow: Fetch & Download. If you only see an HLS link, install ffmpeg to convert it.")
