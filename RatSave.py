import yt_dlp

def get_available_formats(url):
    ydl_opts = {
        'quiet': True,
        'force_generic_extractor': True,
        'skip_download': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = info.get('formats', [])
        return formats

def display_formats(formats):
    video_formats = {}
    audio_formats = {}
    video_count = 1
    audio_count = 1

    unique_video_formats = {}
    unique_audio_formats = {}

    for fmt in formats:
        if fmt.get('vcodec') != 'none':
            height = fmt.get('height', 'N/A')
            if height not in unique_video_formats:
                unique_video_formats[height] = fmt['format_id']
        if fmt.get('acodec') != 'none':
            abr = fmt.get('abr')
            if abr:
                abr = f"{abr} kbps"
            else:
                abr = 'N/A'
            if abr not in unique_audio_formats:
                unique_audio_formats[abr] = fmt['format_id']

    print("\nVerfügbare Videoqualitäten:")
    for quality, fmt_id in unique_video_formats.items():
        print(f"  {video_count}: {quality}")
        video_formats[video_count] = fmt_id
        video_count += 1

    print("\nVerfügbare Soundqualitäten:")
    for quality, fmt_id in unique_audio_formats.items():
        print(f"  {audio_count}: {quality}")
        audio_formats[audio_count] = fmt_id
        audio_count += 1

    return video_formats, audio_formats

def download_videos(url, custom_name, output_format, quality):
    formats = get_available_formats(url)
    video_formats, audio_formats = display_formats(formats)

    if output_format == 'mp4':
        best_format = max((fmt for fmt in formats if fmt.get('ext') == 'mp4' and fmt.get('acodec') != 'none' and fmt.get('vcodec') != 'none'), key=lambda x: x.get('height', 0), default=None)
        if best_format:
            format_str = best_format['format_id']
            ydl_opts = {
                'outtmpl': f'{custom_name}-RatSave.%(ext)s',
                'format': format_str,
                'noplaylist': False,
                'progress_hooks': [progress_hook],
                'quiet': False,
            }
        else:
            print("Keine geeigneten MP4-Formate gefunden.")
            return

    elif output_format == 'mp3':
        if int(quality) not in audio_formats:
            print("Ungültige Audioqualität gewählt. Bitte überprüfen Sie die verfügbaren Formate.")
            return
        audio_format_id = audio_formats[int(quality)]
        ydl_opts = {
            'outtmpl': f'{custom_name}-RatSave.%(ext)s',
            'format': audio_format_id,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': audio_format_id.split()[0], 
            }],
            'noplaylist': False,
            'progress_hooks': [progress_hook],
            'quiet': False,
        }
    else:
        print("Ungültiges Ausgabeformat ausgewählt.")
        return

    print(f"Willkommen! Der Download für {url} beginnt jetzt.")
    print(f"Benutzerdefinierter Name für die Datei: {custom_name}-RatSave")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
        except Exception as e:
            print(f"Ein Fehler ist aufgetreten: {e}")

def progress_hook(d):
    if d['status'] == 'downloading':
        print(f"Herunterladen: {d['_percent_str']} ({d['_eta_str']})")
    elif d['status'] == 'finished':
        print(f"Download abgeschlossen: {d['filename']}")
    elif d['status'] == 'error':
        print(f"Fehler beim Download: {d.get('error', 'Unbekannter Fehler')}")

if __name__ == '__main__':
    print("Willkommen zum RatSave Video-Downloader!")

    video_url = input("Bitte geben Sie die URL des Videos oder der Playlist ein: ")
    custom_name = input("Bitte geben Sie den gewünschten Namen für die Datei ein (ohne Erweiterung): ")

    if not custom_name.isalnum():
        print("Der Name enthält ungültige Zeichen. Bitte verwenden Sie nur alphanumerische Zeichen.")
    else:
        output_format = input("Möchten Sie das Video als MP4 oder MP3 herunterladen? (mp4/mp3): ").strip().lower()
        
        if output_format == 'mp4':
            # MP4-Downloads verwenden automatisch die beste verfügbare Qualität
            print("Für MP4 wird die beste verfügbare Qualität verwendet.")
            download_videos(video_url, custom_name, output_format, None)
        elif output_format == 'mp3':
            formats = get_available_formats(video_url)
            _, audio_formats = display_formats(formats)
            quality = input("Bitte wählen Sie die gewünschte Audioqualität (ID aus der Liste oben): ").strip()
            download_videos(video_url, custom_name, output_format, quality)
        else:
            print("Ungültiges Ausgabeformat ausgewählt.")
            exit()