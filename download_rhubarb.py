import os
import requests
import zipfile

print("Fetching latest Rhubarb release metadata from GitHub...")
r = requests.get("https://api.github.com/repos/DanielSWolf/rhubarb-lip-sync/releases/latest", timeout=15)
release = r.json()
asset = [a for a in release.get("assets", []) if "Windows" in a.get("name", "")][0]
url = asset["browser_download_url"]
print(f"Downloading {asset['name']} from {url}...")

res = requests.get(url, stream=True, timeout=30)
zip_path = "rhubarb.zip"
with open(zip_path, "wb") as f:
    for chunk in res.iter_content(chunk_size=65536):
        if chunk:
            f.write(chunk)

print(f"Downloaded {os.path.getsize(zip_path)} bytes. Extracting to d:/Rim/rhubarb ...")
with zipfile.ZipFile(zip_path, "r") as z:
    z.extractall("d:/Rim/rhubarb")

print("Extraction finished!")
