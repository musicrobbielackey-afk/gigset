# gigset

A FastAPI-based collaboration hub for bands to manage calendars, rehearsal matches, setlists, chat, and shared reference links for charts (e.g., Ultimate Guitar).

## Getting started
1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Run the API with Uvicorn:
   ```bash
   uvicorn app.main:app --reload
   ```
   The interactive docs will be available at `http://localhost:8000/docs`.

## Available endpoints
- `POST /users` – create a user.
- `POST /bands` – create a band.
- `POST /bands/{band_id}/members?user_id=` – add an existing user to a band.
- `POST /bands/{band_id}/availability?user_id=` – save a member's weekly availability window.
- `GET /bands/{band_id}/availability/matches` – compute overlapping rehearsal windows across all members.
- `POST /bands/{band_id}/events` / `GET /bands/{band_id}/events` – manage rehearsals and gig calendar entries (location, notes, setlist included).
- `POST /bands/{band_id}/messages` / `GET /bands/{band_id}/messages` – lightweight band messaging feed.
- `POST /bands/{band_id}/files` / `GET /bands/{band_id}/files` – share chart links or file references with notes.

## Matching logic
For each day of the week (0 = Monday), the API intersects every member's availability windows to find rehearsal-ready windows. If any member has no availability on that day, no match is produced for that day.

## Notes
- Data is persisted in a local SQLite database (`gigset.db`).
- To keep the example lightweight, file sharing is handled via URLs (e.g., links to charts or cloud storage) rather than binary uploads.
- Setlists are stored on events so gigs or rehearsals can capture songs and notes.
