import requests
import json
from flask import Flask, Response

# --- Konfigurasi ---
# Lebih baik gunakan environment variable untuk data sensitif
# import os
# API_BASE_URL = os.environ.get('API_BASE_URL', 'https://kltrar2.elutuna.workers.dev/vip')
# API_AUTH = os.environ.get('API_AUTH', 'kltraid-secret-Rahasiaku69456')

API_BASE_URL = 'https://kltrar2.elutuna.workers.dev/vip'
API_AUTH = 'kltraid-secret-Rahasiaku69456'
# --------------------

app = Flask(__name__)

def get_m3u_playlist():
    """Fungsi inti untuk mengambil data dan membuat playlist M3U"""
    event_url = f"{API_BASE_URL}/event.json"
    server_url = f"{API_BASE_URL}/servereventapk.json"

    headers = {
        'X-App-Auth': API_AUTH,
        'User-Agent': 'okhttp/4.12.0',
        'Accept': 'application/json'
    }

    try:
        # Mengambil data dari dua sumber secara bersamaan
        event_response = requests.get(event_url, headers=headers, timeout=30)
        server_response = requests.get(server_url, headers=headers, timeout=30)

        # Memastikan request berhasil
        event_response.raise_for_status()
        server_response.raise_for_status()

        events = event_response.json()
        all_servers = server_response.json()

        # Membuat peta (dictionary) untuk pencarian server yang cepat berdasarkan event ID
        server_map = {item['id']: item['servers'] for item in all_servers}

        m3u_playlist = "#EXTM3U\n"

        # Loop melalui setiap event
        for event in events:
            servers_for_event = server_map.get(event.get('id'))

            if servers_for_event and len(servers_for_event) > 0:
                # Loop melalui SETIAP server untuk event ini
                for server in servers_for_event:
                    stream_url = server.get('url', '').strip()
                    
                    # Pastikan server memiliki URL yang valid
                    if stream_url:
                        base_channel_name = f"{event.get('team1', {}).get('name', '')} {event.get('team2', {}).get('name', '')}"
                        label_suffix = f" ({server.get('label', '')})" if server.get('label') else ''
                        full_channel_name = f"{base_channel_name}{label_suffix}"
                        
                        group_title = event.get('league', 'Unknown')
                        tvg_logo = event.get('icon', '')

                        # --- LOGIKA HEADER: Buat blok header HANYA JIKA ada data header ---
                        header_lines = ""
                        server_headers = server.get('headers')
                        if server_headers:
                            user_agent = server_headers.get('User-Agent', '')
                            origin = server_headers.get('Origin', '')
                            referer = server_headers.get('Referer', '')
                            
                            header_lines = (
                                f"#EXTVLCOPT:http-user-agent={user_agent}\n"
                                f"#EXTVLCOPT:http-origin={origin}\n"
                                f"#EXTVLCOPT:http-referrer={referer}\n"
                            )
                        # ----------------------------------------------------------------

                        # Gabungkan semua bagian menjadi entri M3U
                        m3u_playlist += (
                            f"\n#EXTINF:-1 tvg-logo=\"{tvg_logo}\" group-title=\"{group_title}\",{full_channel_name}\n"
                            f"{header_lines}"
                            f"{stream_url}\n"
                        )
        return m3u_playlist

    except requests.exceptions.RequestException as e:
        print(f"Error saat mengambil data API: {e}")
        return "#EXTM3U\n# Error: Gagal mengambil data dari sumber."
    except Exception as e:
        print(f"Terjadi error tidak terduga: {e}")
        return "#EXTM3U\n# Error: Terjadi kesalahan internal."


@app.route('/playlist.m3u')
def serve_playlist():
    """Endpoint untuk menyajikan playlist M3U"""
    playlist_content = get_m3u_playlist()
    return Response(playlist_content, mimetype='application/vnd.apple.mpegurl; charset=utf-8')


if __name__ == '__main__':
    # Untuk menjalankan secara lokal
    # Buka http://127.0.0.1:5000/playlist.m3u
    app.run(debug=True, port=5000)
