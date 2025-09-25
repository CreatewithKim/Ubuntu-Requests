import os
import requests
from urllib.parse import urlparse
import uuid
import hashlib

def fetch_images():
    # Prompt user for multiple URLs (comma separated)
    urls = input("🌍 Enter image URLs (comma separated): ").split(",")
    urls = [u.strip() for u in urls if u.strip()]

    # Create directory for storing images
    folder = "Fetched_Images"
    os.makedirs(folder, exist_ok=True)

    # Keep track of already-downloaded images (by hash)
    downloaded_hashes = set()

    for url in urls:
        try:
            print(f"🔎 Fetching: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Handle bad responses (404, 500, etc.)

            # --- Precautions: Check headers before saving ---
            content_type = response.headers.get("Content-Type", "")
            if not content_type.startswith("image/"):
                print(f"⚠️ Skipping {url} — not an image (Content-Type: {content_type})")
                continue

            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > 5_000_000:  # 5 MB limit
                print(f"⚠️ Skipping {url} — file too large ({content_length} bytes)")
                continue

            # --- Prevent duplicates by hashing content ---
            file_hash = hashlib.md5(response.content).hexdigest()
            if file_hash in downloaded_hashes:
                print(f"♻️ Skipping {url} — duplicate image detected")
                continue
            downloaded_hashes.add(file_hash)

            # --- Extract or generate filename ---
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            if not filename:  # fallback if URL doesn't end with filename
                filename = f"image_{uuid.uuid4().hex}.jpg"

            filepath = os.path.join(folder, filename)

            # Save image in binary mode
            with open(filepath, "wb") as f:
                f.write(response.content)

            print(f"✅ Saved: {filepath}")

        except requests.exceptions.RequestException as e:
            print(f"⚠️ Could not fetch {url}. Reason: {e}")

if __name__ == "__main__":
    fetch_images()
