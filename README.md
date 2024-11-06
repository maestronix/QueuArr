# QueuArr

**QueuArr** ist ein Python-Skript, das die Queue von Sonarr und Sabnzbd überwacht und dabei hilft, unnötige und doppelte Downloads zu vermeiden. Es unterstützt das automatische Entfernen oder Pausieren von niedrigeren Qualitätsversionen und Duplikaten in der Sabnzbd-Queue, wenn eine bessere oder bereits vorhandene Datei entdeckt wird.

## Features

- Überwacht die Sabnzbd-Queue basierend auf den Sonarr-Episodeneinträgen.
- Prüft die Qualität der Downloads und entfernt oder pausiert niedrigere Qualitätsversionen.
- Bietet Optionen zur Konfiguration des Verhaltens für bessere Qualitätsversionen und Duplikate.
- Kann optional als "dry-run" ausgeführt werden, um alle Aktionen zu testen, ohne Änderungen vorzunehmen.

## Voraussetzungen

- **Python 3.6+**
- Installierte Pakete:
  - `requests` (kann mit `pip install requests` installiert werden)

## Installation

1. Klone das Repository:
   ```bash
   git clone <repository-url>
   cd QueuArr
   ```
   
2. Installiere die Abhängigkeiten:
   ```bash
   pip install -r requirements.txt
   ```

## Konfiguration

Die Konfiguration erfolgt direkt im Skript oder in einer separat bereitgestellten Konfigurationsdatei. Passe die folgenden Einstellungen an:

- `SONARR_URL`: Die URL deiner Sonarr-Instanz.
- `SONARR_API_KEY`: Dein Sonarr-API-Schlüssel.
- `SABNZBD_URL`: Die URL deiner Sabnzbd-Instanz.
- `SABNZBD_API_KEY`: Dein Sabnzbd-API-Schlüssel.
- `better_quality_action`: Legt fest, ob Downloads niedrigerer Qualität gelöscht (`delete`) oder pausiert (`pause`) werden sollen, wenn eine bessere Qualitätsversion vorhanden ist.
- `duplicate_entry_action`: Bestimmt, ob doppelte Einträge in gleicher Qualität gelöscht (`delete`) oder pausiert (`pause`) werden sollen.

## Verwendung

Führe das Skript mit folgenden Befehlen aus:

```bash
python queuarr.py --dry-run
```

Verwende `--dry-run` zum Testen der Aktionen ohne Änderungen. Ohne diesen Parameter werden die konfigurierten Aktionen (Löschen oder Pausieren) angewendet.

## Beispielausgabe

```plaintext
Sonarr Queue enthält folgende Einträge:
Title: Series.S01E01, Quality: WEBDL-720p
Title: Series.S01E01, Quality: WEBDL-1080p
...
Processed 20 releases in total.
```

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Weitere Informationen findest du in der [LICENSE-Datei](LICENSE).

--- 

Das Skript und die README sollten eine solide Grundlage für das Tool bieten.
