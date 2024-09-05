import os
import subprocess
import sys
import time
from urllib.parse import urlparse 

def install_package(package_name):
    print(f"Installing {package_name}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

def ensure_packages():
    packages = ["requests", "dlbar"]
    for package in packages:
        try:
            __import__(package)
        except ImportError:
            install_package(package_name=package)
            print(f"Package {package} installed.")

    global DownloadBar, requests 
    from dlbar import DownloadBar
    import requests

def extract_file_id(full_url):
    parsed_url = urlparse(full_url)
    path = parsed_url.path
    file_id = path.split('/')[-1]
    return file_id

def get_download_ticket(file_id):
    url = "https://api.streamtape.com/file/dlticket"
    params = {
        "file": file_id,
        "login": "c55d533882c652aebfaf",
        "key": "GPa2yVOxXqTAYX"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    if data["status"] == 200:
        return data["result"]["ticket"]
    else:
        raise Exception(f"Fehler beim Abrufen des Download-Tickets: {data['msg']}")

def get_download_link(file_id, ticket):
    url = "https://api.streamtape.com/file/dl"
    params = {
        "file": file_id,
        "ticket": ticket
    }
    
    max_retries = 10
    retry_attempts = 0
    
    while retry_attempts < max_retries:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data["status"] == 200:
            return data["result"]["url"]
        elif "You need to wait" in data["msg"]:
            wait_time = int(data["msg"].split(" ")[4])
            time.sleep(wait_time)
            retry_attempts += 1
        else:
            raise Exception(f"Fehler beim Abrufen des Download-Links: {data['msg']}")
    
    raise Exception("Maximale Anzahl an Wiederholungen erreicht")

def download_file(download_url, filename):
    download_bar = DownloadBar(
        empty_char=f"\033[31m{chr(9472)}\033[0m",
        filled_char=f"\033[32m{chr(9472)}\033[0m",
        width=50
    )
    
    download_bar.download(
        url=download_url,
        dest=filename,
        title=f'Downloading {filename}'
    )
    
    print(f"\nDatei '{filename}' wurde erfolgreich heruntergeladen.")

def download_file_from_url(url):
    try:
        file_id = extract_file_id(url)
        ticket = get_download_ticket(file_id)
        download_url = get_download_link(file_id, ticket)
        filename = os.path.basename(urlparse(download_url).path)
        filename = input(f"Dateiname zum Speichern (Standard: {filename}): ") or filename
        download_file(download_url, filename)
        print(f"Download abgeschlossen für: {filename}")
    except Exception as e:
        print(f"Fehler: {str(e)}")

def main():
    os.system("cls" if os.name == "nt" else "clear")
    print("Willkommen beim RatSave StreamTape Downloader")
    urls = input("Gib die URLs der Dateien ein (durch Kommas getrennt): ").split(',')
    urls = [url.strip() for url in urls]
    
    if not urls:
        print("Keine URLs angegeben.")
        return

    print("Starte Downloads...")
    for url in urls:
        download_file_from_url(url)
    
    print("Alle Downloads abgeschlossen.")

if __name__ == "__main__":
    ensure_packages()
    main()
