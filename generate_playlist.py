import requests
import json

# Konstanta dan Header, sama seperti di kode Javascript
API_BASE_URL = 'https://kltrar2.elutuna.workers.dev/vip'
EVENT_URL = f'{API_BASE_URL}/event.json'
SERVER_URL = f'{API_BASE_URL}/servereventapk.json'

API_HEADERS = {
    'X-App-Auth': 'kltraid-secret-Rahasiaku69456',
    'User-Agent': 'okhttp/4.12.0',
    'Accept': 'application/json'
}

def generate_m3u_playlist():
    """
    Mengambil data dari API, memprosesnya, dan menghasilkan string playlist M3U.
    """
    try:
        # Mengambil data dari kedua URL secara bersamaan (mirip Promise.all)
        print("Mengambil data dari API...")
        event_response = requests.get(EVENT_URL, headers=API_HEADERS, timeout=15)
        server_response = requests.get(SERVER_URL, headers=API_HEADERS, timeout=15)

        # Memastikan kedua permintaan berhasil
        event_response.raise_for_status()
        server_response.raise_for_status()
        
        print("Data berhasil diambil.")

        events = event_response.json()
        all_servers = server_response.json()

        # Membuat 'map' server untuk pencarian cepat, di Python kita pakai dictionary
        server_map = {item['id']: item['servers'] for item in all_servers}

        # Mulai membangun playlist M3U
        m3u_lines = ['#EXTM3U']

        # Loop melalui setiap event
        for event in events:
            event_id = event.get('id')
            servers_for_event = server_map.get(event_id)

            if servers_for_event:
                # Loop melalui setiap server untuk event ini
                for server in servers_for_event:
                    stream_url = server.get('url')
                    
                    # Pastikan server memiliki URL yang valid
                    if stream_url and stream_url.strip():
                        team1_name = event.get('team1', {}).get('name', 'Tim 1')
                        team2_name = event.get('team2', {}).get('name', 'Tim 2')
                        base_channel_name = f"{team1_name} vs {team2_name}"
                        
                        label_suffix = f" ({server['label']})" if server.get('label') else ''
                        full_channel_name = f"{base_channel_name}{label_suffix}"

                        group_title = event.get('league', 'Lainnya')
                        tvg_logo = event.get('icon', '')

                        # Tambahkan baris #EXTINF
                        extinf_line = f'#EXTINF:-1 tvg-logo="{tvg_logo}" group-title="{group_title}",{full_channel_name}'
                        m3u_lines.append(f"\n{extinf_line}")

                        # LOGIKA BARU: Tambahkan #EXTVLCOPT hanya jika ada data header
                        if server.get('headers'):
                            headers = server['headers']
                            user_agent = headers.get('User-Agent', '')
                            origin = headers.get('Origin', '')
                            referer = headers.get('Referer', '')
                            
                            m3u_lines.append(f'#EXTVLCOPT:http-user-agent={user_agent}')
                            m3u_lines.append(f'#EXTVLCOPT:http-origin={origin}')
                            m3u_lines.append(f'#EXTVLCOPT:http-referrer={referer}')
                        
                        # Tambahkan URL stream
                        m3u_lines.append(stream_url)
        
        print("Playlist M3U berhasil dibuat.")
        return '\n'.join(m3u_lines)

    except requests.exceptions.RequestException as e:
        print(f"Error saat mengambil data dari API: {e}")
        return None
    except Exception as e:
        print(f"Terjadi kesalahan internal: {e}")
        return None

if __name__ == "__main__":
    # Jalankan fungsi utama
    playlist_content = generate_m3u_playlist()

    # Jika konten berhasil dibuat, simpan ke file
    if playlist_content:
        # Simpan hasil ke file bernama playlist.m3u
        with open('playlist.m3u', 'w', encoding='utf-8') as f:
            f.write(playlist_content)
        print("File 'playlist.m3u' telah berhasil disimpan.")
    else:
        print("Gagal membuat file playlist karena terjadi error sebelumnya.")
