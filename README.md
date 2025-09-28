# Docs Hub (Raspberry Pi)

Docs Hub is a lightweight web app for Raspberry Pi that lets you **store, tag, search, preview, and download** document files. It supports **PDF**, **Markdown (.md)**, and **plain text (.txt)**, and comes with a simple **tag system**, **tag filters**, and **backup/restore** utilities.

> Optimized for mobile, tablet, and desktop. Works great in local networks (LAN) on your Raspberry Pi.

---

## Features

- **Drag & Drop upload** (auto-upload as soon as files are dropped)
- **In-browser preview** for PDF/MD/TXT (viewer page includes a **Download** button at the bottom)
- **Tags** for categorizing files + **tag filter chips** above the list
- **✏️ Change Tag** button per file (opens a popup to select tags from an existing list)
- **Backup/Restore** the entire database and file storage
- **Reindex** to quickly rebuild the search/index if things get out of sync
- Responsive UI for **mobile / tablet / desktop**
- Supported file types: `.pdf`, `.md`, `.txt`

---

## Quick Start (Manual Install)

```bash
# 1) Unzip and enter the project directory
unzip DocsHub.zip -d ~
cd ~/DocsHub

# 2) Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3) Install dependencies
python -m pip install --upgrade pip wheel
pip install -r requirements.txt

# 4) Run the development server
python -m uvicorn main:app --host 0.0.0.0 --port 8088

# 5) Open from another device on the same LAN:
# http://<RPi_IP>:8088
```
> On Raspberry Pi OS/Debian, you may need to install `python3-venv` if it's missing:
> ```bash
> sudo apt update && sudo apt install -y python3-venv
> ```

---

## Quick Start (Using `scripts/install.sh`)

```bash
cd ~/DocsHub
chmod +x scripts/install.sh
./scripts/install.sh

# Then run the server
source .venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8088
```
The script installs `python3-venv` if needed and then installs dependencies from `requirements.txt`.

---

## Usage

- **Upload:** Drag files into the upload area. Upload starts automatically.
- **Preview:** Click a file to open the viewer. For PDF/MD/TXT, preview is shown in-browser.
- **Download:** Use the **Download** button at the bottom of the viewer page.
- **Tags:** Click **✏️ Change Tag** on a file to open the tag picker popup.
- **Filter by tags:** Use the tag chips at the top of the list to narrow results.
- **Reindex:** If you move files or restore from backup, run **Reindex** to rebuild the index.

---
