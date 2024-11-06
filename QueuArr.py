import re
import requests
import argparse

# Sonarr API-Einstellungen
SONARR_URL = 'http://localhost:8989'  # Ersetze mit deiner Sonarr-URL
SONARR_API_KEY = 'DEIN_SONARR_API_KEY'

# Sabnzbd API-Einstellungen
SABNZBD_URL = 'http://localhost:8080'  # Ersetze mit deiner Sabnzbd-URL
SABNZBD_API_KEY = 'DEIN_SABNZBD_API_KEY'

# Aktionseinstellungen für Qualitätsvergleich und doppelte Einträge
better_quality_action = 'delete'  # Optionen: 'delete' oder 'pause'
duplicate_entry_action = 'pause'  # Optionen: 'delete' oder 'pause'

# Qualitätsrangfolge für den Vergleich
quality_rank = {
    "SD": 1,
    "480p": 1,
    "WEBDL-480p": 1,
    "WEBRip-480p": 1,
    "576p": 1,
    "Bluray-480p": 1,
    "Bluray-576p": 1,
    "HDTV-720p": 2,
    "WEBRip-720p": 3,
    "WEBDL-720p": 4,
    "Bluray-720p": 5,
    "HDTV-1080p": 6,
    "WEBRip-1080p": 7,
    "WEBDL-1080p": 8,
    "Bluray-1080p": 9,
    "Bluray-1080p Remux": 10,
    "HDTV-2160p": 11,
    "WEBRip-2160p": 12,
    "WEBDL-2160p": 13,
    "Bluray-2160p": 14,
    "Bluray-2160p Remux": 15
}

def get_queue():
    sonarr_queue_url = f"{SONARR_URL}/api/v3/queue?pageSize=10000" # Abfrage von bis zu 100 Einträgen
    headers = {'X-Api-Key': SONARR_API_KEY}
    response = requests.get(sonarr_queue_url, headers=headers)
    if response.status_code == 200:
        return response.json().get('records', [])
    else:
        print(f"Fehler bei der Anfrage an Sonarr: {response.status_code}")
        return []

def get_sabnzbd_queue():
    sabnzbd_queue_url = f"{SABNZBD_URL}/api?mode=queue&output=json&apikey={SABNZBD_API_KEY}"
    response = requests.get(sabnzbd_queue_url)
    if response.status_code == 200:
        return response.json().get('queue', {}).get('slots', [])
    else:
        print(f"Fehler bei der Anfrage an Sabnzbd: {response.status_code}")
        return []

def remove_from_sabnzbd(nzb_id, title):
    sabnzbd_remove_url = f"{SABNZBD_URL}/api?mode=queue&name=delete&value={nzb_id}&apikey={SABNZBD_API_KEY}"
    response = requests.get(sabnzbd_remove_url)
    if response.status_code == 200:
        print(f"Removed '{title}' from Sabnzbd queue.")
    else:
        print(f"Failed to remove '{title}' from Sabnzbd queue.")

def pause_in_sabnzbd(nzb_id, title):
    sabnzbd_pause_url = f"{SABNZBD_URL}/api?mode=queue&name=pause&value={nzb_id}&apikey={SABNZBD_API_KEY}"
    response = requests.get(sabnzbd_pause_url)
    if response.status_code == 200:
        print(f"Paused '{title}' in Sabnzbd queue.")
    else:
        print(f"Failed to pause '{title}' in Sabnzbd queue.")

def is_season_pack(title):
    return not re.search(r'E\d{2}', title)

def check_for_upgrades(dry_run):
    sonarr_queue = get_queue()
    sabnzbd_queue = get_sabnzbd_queue()

    tracked_episodes = {}
    season_packs = set()

    for sonarr_item in sonarr_queue:
        if not isinstance(sonarr_item, dict):
            print("Unerwartete API-Antwort von Sonarr.")
            continue

        title = sonarr_item['title']
        series_id = sonarr_item['seriesId']
        episode_id = sonarr_item['episodeId']
        sonarr_quality_name = sonarr_item['quality']['quality']['name']
        sonarr_quality_rank = quality_rank.get(sonarr_quality_name, 0)
        download_id = sonarr_item['downloadId']

        if is_season_pack(title):
            if title in season_packs:
                continue
            season_packs.add(title)

        if (series_id, episode_id) in tracked_episodes:
            existing_item = tracked_episodes[(series_id, episode_id)]
            
            if sonarr_quality_rank > existing_item['quality_rank']:
                print(f"Found better quality '{sonarr_quality_name}' for '{title}' compared to '{existing_item['quality']}'")
                if better_quality_action == 'delete':
                    remove_from_sabnzbd(existing_item['download_id'], existing_item['title'])
                elif better_quality_action == 'pause':
                    pause_in_sabnzbd(existing_item['download_id'], existing_item['title'])

                tracked_episodes[(series_id, episode_id)] = {
                    'title': title,
                    'quality': sonarr_quality_name,
                    'quality_rank': sonarr_quality_rank,
                    'download_id': download_id
                }
            elif sonarr_quality_rank < existing_item['quality_rank']:
                print(f"Retaining higher quality '{existing_item['quality']}' and handling lower quality '{sonarr_quality_name}'")
                if better_quality_action == 'delete':
                    remove_from_sabnzbd(download_id, title)
                elif better_quality_action == 'pause':
                    pause_in_sabnzbd(download_id, title)
            else:
                print(f"Duplicate entry for '{title}' with same quality '{sonarr_quality_name}' found.")
                if duplicate_entry_action == 'delete':
                    remove_from_sabnzbd(download_id, title)
                elif duplicate_entry_action == 'pause':
                    pause_in_sabnzbd(download_id, title)
        else:
            tracked_episodes[(series_id, episode_id)] = {
                'title': title,
                'quality': sonarr_quality_name,
                'quality_rank': sonarr_quality_rank,
                'download_id': download_id
            }

    print("Completed checking for upgrades.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Remove or pause lower quality releases from Sabnzbd queue if a better quality is found in Sonarr.")
    parser.add_argument('--dry-run', action='store_true', help="Enable dry-run mode to test without removing or pausing anything.")
    args = parser.parse_args()

    check_for_upgrades(dry_run=args.dry_run)
