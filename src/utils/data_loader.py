import os
import requests
import gdown

def is_google_drive_url(url):
    return "drive.google.com" in url

def download_file(url, dest_path):
    if os.path.exists(dest_path):
        print(f"[INFO] {os.path.basename(dest_path)} already exists. Skipping download.")
        return

    print(f"[INFO] Downloading {os.path.basename(dest_path)} from {url}...")

    try:
        folder = os.path.dirname(dest_path)
        if folder:
            os.makedirs(folder, exist_ok=True)

        if is_google_drive_url(url):
            gdown.download(url, dest_path, quiet=False)
        else:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(dest_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

        print(f"[INFO] Downloaded {os.path.basename(dest_path)} successfully.")

    except Exception as e:
        print(f"[ERROR] Failed to download {os.path.basename(dest_path)}: {e}")
        raise

def ensure_required_files():
    MODEL_URL = os.getenv("MODEL_URL")
    DB_JSON_URL = os.getenv("DRUGBANK_JSON_URL")
    DB_XML_URL = os.getenv("DRUGBANK_XML_URL")

    if not MODEL_URL:
        raise EnvironmentError("Missing MODEL_URL in environment variables.")
    if not DB_JSON_URL:
        raise EnvironmentError("Missing DRUGBANK_JSON_URL in environment variables.")
    if not DB_XML_URL:
        raise EnvironmentError("Missing DRUGBANK_XML_URL in environment variables.")

    download_file(MODEL_URL, "models/model_checkpoint.pt")
    download_file(DB_JSON_URL, "backend/drugbank_data/drugbank_slim.json")
    download_file(DB_XML_URL, "backend/drugbank_data/drugbank_all_drug_links.xml")

