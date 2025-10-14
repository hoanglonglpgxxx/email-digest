# main.py (with Client ID input)
import streamlit as st
import requests
import tempfile
import os
import subprocess
import shlex
from pathlib import Path

# ---------- Config ----------
# MODIFIED: We no longer hardcode the client_id here.
API_BASE = "https://api-v2.soundcloud.com"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0"
# ----------------------------

st.set_page_config(page_title="SoundCloud Downloader", page_icon="🎵", layout="centered")
st.title("🎵 SoundCloud Downloader")
st.caption("Paste SoundCloud URLs and your Client ID. Respect copyrights.")

# NEW: Add an input field for the Client ID
st.subheader("1. Enter your SoundCloud Client ID")
client_id_input = st.text_input(
    "SoundCloud Client ID",
    placeholder="Paste your Client ID here",
    help="This is required for the app to communicate with SoundCloud's API."
)

with st.expander("How to find your Client ID?"):
    st.info("""
    SoundCloud periodically changes its public `client_id`. If the app stops working, you'll need a new one.
    1.  Open **SoundCloud.com** in a new browser tab.
    2.  Press **F12** to open Developer Tools.
    3.  Click the **Network** tab.
    4.  In the filter box, type `client_id`.
    5.  Refresh the SoundCloud page. A request should appear in the network log.
    6.  Click the request and find the full **Request URL**.
    7.  Copy the long alphanumeric string from the `client_id=` parameter and paste it above.
    """)

# MODIFIED: Changed header to reflect the new step-by-step flow
st.subheader("2. Paste Track URLs")
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
        # Check specifically for 401 Unauthorized
        if e.response and e.response.status_code == 401:
            st.warning(f"The provided Client ID is invalid or has expired. Please find a new one.")
        else:
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

    for t in transcodings:
        if t.get("format", {}).get("protocol") == "progressive":
            try:
                r = requests.get(f"{t['url']}?client_id={client_id}", headers={"User-Agent": USER_AGENT}, timeout=15)
                r.raise_for_status()
                return r.json().get("url"), "progressive"
            except Exception:
                continue

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
    for title, path in st.session_state.downloaded_files:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                print(f"Error cleaning up {path}: {e}")
    st.session_state.downloaded_files = []


# MODIFIED: Changed header to reflect the new step-by-step flow
st.subheader("3. Fetch and Download")
if st.button("Fetch & Download All"):
    # NEW: Validate inputs first
    if not client_id_input:
        st.error("❌ Please provide a SoundCloud Client ID first.")
    elif not urls_input:
        st.error("❌ Please paste at least one SoundCloud URL.")
    else:
        cleanup_old_files()
        urls = [url.strip() for url in urls_input.strip().split('\n') if url.strip()]
        progress_bar = st.progress(0)
        total_urls = len(urls)
        processed_files = []

        for i, url in enumerate(urls):
            st.markdown("---")
            st.info(f"**Processing URL {i + 1}/{total_urls}**: `{url}`")

            # MODIFIED: Pass the client_id from the input field
            track = resolve_track(url, client_id_input)
            if not track:
                progress_bar.progress((i + 1) / total_urls)
                continue  # Error messages are handled inside resolve_track

            track_id = track.get("id")
            # MODIFIED: Pass the client_id from the input field
            track_json = get_track_json_by_id(track_id, client_id_input) if track_id else track
            title = (track_json or track).get("title", "track")

            with st.spinner(f"Finding stream for '{title}'..."):
                # MODIFIED: Pass the client_id from the input field
                stream_url, proto = find_stream_url(track_json, client_id_input)

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
                with st.spinner("Converting HLS stream with ffmpeg..."):
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
        if not processed_files and urls:
            st.warning("No tracks were successfully processed. Check the error messages above.")

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
                        key=f"dl_{path}"
                    )
            except Exception as e:
                st.error(f"Failed to create download button for '{title}': {e}")
    st.caption("Files will be removed from the server on your next run.")