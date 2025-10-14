# main.py (multi-link version)
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

st.set_page_config(page_title="SoundCloud Downloader — Multi", page_icon="🎵", layout="centered")
st.title("🎵 SoundCloud Downloader — Multi")
st.caption("Paste one or more SoundCloud URLs (one per line). Respect copyrights.")

# MODIFIED: Use st.text_area for multiple URLs
urls_input = st.text_area(
    "SoundCloud track URLs (one per line)",
    placeholder="https://soundcloud.com/artist/track1\nhttps://soundcloud.com/artist/track2"
)

# MODIFIED: session_state to handle a list of downloaded files
if "downloaded_files" not in st.session_state:
    st.session_state.downloaded_files = []


# ---------- Helpers (No changes needed in these functions) ----------
def resolve_track(url, client_id):
    try:
        resolve_url = f"{API_BASE}/resolve?url={url}&client_id={client_id}"
        r = requests.get(resolve_url, allow_redirects=True, headers={"User-Agent": USER_AGENT}, timeout=15)
        r.raise_for_status()
        j = r.json()
        return j if j.get("kind") == "track" else None
    except requests.exceptions.RequestException as e:
        st.warning(f"Could not resolve '{url}': {e}")
        return None
    except Exception as e:
        st.warning(f"An unexpected error occurred while resolving '{url}': {e}")
        return None


def get_track_json_by_id(track_id, client_id):
    try:
        r = requests.get(f"{API_BASE}/tracks/{track_id}?client_id={client_id}", headers={"User-Agent": USER_AGENT},
                         timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def find_stream_url(track_json, client_id):
    if not track_json: return None, None
    media = track_json.get("media")
    if not media: return None, None
    transcodings = media.get("transcodings", [])

    # Prefer progressive
    for t in transcodings:
        if t.get("format", {}).get("protocol") == "progressive":
            try:
                r = requests.get(f"{t['url']}?client_id={client_id}", headers={"User-Agent": USER_AGENT}, timeout=15)
                r.raise_for_status()
                return r.json().get("url"), "progressive"
            except Exception:
                continue

    # Fallback to HLS
    for t in transcodings:
        if "hls" in t.get("format", {}).get("protocol", ""):
            try:
                r = requests.get(f"{t['url']}?client_id={client_id}", headers={"User-Agent": USER_AGENT}, timeout=15)
                r.raise_for_status()
                return r.json().get("url"), "hls"
            except Exception:
                continue

    return None, None


def download_url_to_tempfile(stream_url):
    try:
        r = requests.get(stream_url, headers={"User-Agent": USER_AGENT}, stream=True, timeout=60)
        r.raise_for_status()
        suffix = ".mp3" if "audio" in r.headers.get("content-type", "") or ".mp3" in stream_url else ".bin"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    tmp.write(chunk)
            return tmp.name
    except Exception as e:
        st.error(f"Download failed: {e}")
        return None


def ffmpeg_hls_to_mp3(hls_url, out_path):
    cmd = f'ffmpeg -y -i "{hls_url}" -c:a libmp3lame -b:a 192k "{out_path}"'
    try:
        proc = subprocess.run(shlex.split(cmd), capture_output=True, text=True, timeout=1800)
        if proc.returncode == 0 and Path(out_path).exists():
            return True, "Success"
        else:
            return False, proc.stderr or proc.stdout
    except FileNotFoundError:
        return False, "ffmpeg not found. Please ensure ffmpeg is installed and in the system's PATH."
    except subprocess.TimeoutExpired:
        return False, "ffmpeg conversion timed out after 30 minutes."


def cleanup_old_files():
    # MODIFIED: Clear the list of old files and delete them from disk
    for title, path in st.session_state.downloaded_files:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                print(f"Error cleaning up {path}: {e}")
    st.session_state.downloaded_files = []


# MODIFIED: Main button logic to handle multiple URLs
if st.button("Fetch & Download All"):
    cleanup_old_files()  # Clean up files from any previous run

    urls = [url.strip() for url in urls_input.strip().split('\n') if url.strip()]

    if not urls:
        st.error("Please paste at least one SoundCloud URL.")
    else:
        progress_bar = st.progress(0)
        total_urls = len(urls)
        processed_files = []

        for i, url in enumerate(urls):
            st.markdown("---")
            st.info(f"**Processing URL {i + 1}/{total_urls}**: `{url}`")

            track = resolve_track(url, CLIENT_ID)
            if not track:
                st.error("Could not resolve track. It might be private or the URL is incorrect.")
                progress_bar.progress((i + 1) / total_urls)
                continue

            track_id = track.get("id")
            track_json = get_track_json_by_id(track_id, CLIENT_ID) if track_id else track
            title = (track_json or track).get("title", "track")

            with st.spinner(f"Finding stream for '{title}'..."):
                stream_url, proto = find_stream_url(track_json, CLIENT_ID)

            if not stream_url:
                st.error(f"Couldn't find a downloadable stream for '{title}'.")
                progress_bar.progress((i + 1) / total_urls)
                continue

            st.write(f"Found **{proto}** stream for '{title}'.")

            tmp_path = None
            if proto == "progressive":
                with st.spinner("Downloading directly..."):
                    tmp_path = download_url_to_tempfile(stream_url)
            else:  # hls
                with st.spinner("Converting HLS stream with ffmpeg (this can take a while)..."):
                    safe_name = "".join(c for c in title if c.isalnum() or c in " -_").strip()[:80] or "track"
                    out_path = Path(tempfile.gettempdir()) / f"{safe_name}.mp3"
                    ok, ffout = ffmpeg_hls_to_mp3(stream_url, str(out_path))
                    if ok and out_path.exists():
                        tmp_path = str(out_path)
                    else:
                        st.error(f"Failed to convert HLS to MP3 for '{title}'.")
                        st.code(ffout, language='bash')

            if tmp_path:
                st.success(f"✔️ Successfully prepared '{title}' for download.")
                processed_files.append({"title": title, "path": tmp_path})

            progress_bar.progress((i + 1) / total_urls)

        st.session_state.downloaded_files = processed_files
        st.markdown("---")
        if not processed_files:
            st.warning("No tracks were successfully processed.")

# MODIFIED: Display download buttons for all successfully processed files
if st.session_state.downloaded_files:
    st.header("Your Downloads Are Ready")
    for file_info in st.session_state.downloaded_files:
        title = file_info["title"]
        path = file_info["path"]

        if path and os.path.exists(path):
            try:
                safe_name = "".join(c for c in title if c.isalnum() or c in " -_").strip()[:80] or "track"
                file_name = f"{safe_name}.mp3"

                with open(path, "rb") as f:
                    st.download_button(
                        label=f"⬇️ Download: {title}",
                        data=f.read(),
                        file_name=file_name,
                        mime="audio/mpeg",
                        key=f"dl_{path}"  # Unique key for each button
                    )
            except Exception as e:
                st.error(f"Failed to create download button for '{title}': {e}")

    # The files are kept on the server until the next run, which calls cleanup_old_files()
    st.caption("Files will be removed from the server on your next 'Fetch & Download' run.")

st.markdown("---")
st.caption("If a track fails, it might be private, region-locked, or use an unsupported format.")