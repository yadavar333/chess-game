# Chess Game

A real-time multiplayer chess game. Two players can register, create a game, share a code, and play live with instant move synchronization.

## Why This Project?

I built this to explore real-time features in FastAPI without overcomplicating things. The core idea: keep WebSocket communication simple, validate everything on the server, and let the browser handle just rendering.

Most chess apps either over-engineer (tons of features you don't need) or under-deliver on the real-time experience. This one tries to sit in the middle — good enough to actually play with someone, lightweight enough to understand in an afternoon.

## What Works

- **Real-time Multiplayer**: Open two browser windows or send a link to a friend. Moves sync instantly.
- **Proper Chess Rules**: Uses `python-chess` library for move validation. No weird illegal moves sneaking through.
- **User Accounts**: Simple registration and login. Nothing fancy, just works.
- **Game Codes**: Create a game, get a 4-letter code, share it. Your opponent joins with that code.
- **Server-side Validation**: All move logic runs on the server. The browser can't cheat.

## Tech Stack

- **Backend**: FastAPI with Uvicorn
- **Real-time**: WebSockets (no Redis, just in-process management)
- **Database**: PostgreSQL in production, SQLite for local dev
- **Frontend**: Plain HTML, CSS, JavaScript (no React, no build step)
- **Move Validation**: `python-chess` library

## Getting Started Locally

```bash
git clone <this-repo>
cd chess-game
pip install -r requirements.txt
python main.py
```

Open `http://localhost:8000` in your browser. Register, create a game, open another browser/incognito window, register again, join the game.

## How It's Structured

```
main.py           # FastAPI app, WebSocket handlers, routes
database.py       # User, Game, GameMove models (SQLAlchemy)
requirements.txt  # Dependencies
templates/
  ├── index.html  # Login, registration, game lobby
  └── game.html   # Chess board and move interface
```

## Deploying (Free)

I'm using Render (free tier) + Neon (free PostgreSQL) because:
- Zero credit card cost
- WebSocket support works perfectly
- Database persists across redeploys
- Git push = instant deploy

**Quick setup:**
1. Create a Neon account, get a PostgreSQL connection string
2. Create a Render account, connect your GitHub repo
3. Set environment variables: `DATABASE_URL`, `PYTHONUNBUFFERED=1`, `PYTHON_VERSION=3.12.0`
4. Deploy and test in two browser tabs

See the [deployment notes](#deployment) below for details.

## What Happens When You Play

1. Player A registers, creates a game (white)
2. Game sends back a code like `ABCD`
3. Player A shares the code
4. Player B registers, joins with code `ABCD`
5. Second player connected → game becomes "active"
6. Both players see the board, Player A moves first
7. Move is validated server-side, broadcast to both via WebSocket
8. Board updates instantly in both browsers

Invalid moves are rejected. Check, checkmate, and stalemate are detected automatically.

## Known Limitations

**Single server only.** The game state (active boards, whose turn it is) lives in process memory. Don't run multiple instances or use multiple workers — each one would have its own copy and players wouldn't see each other's moves.

For a hobby project, this is fine. If you wanted to scale horizontally, you'd need to move game state to Redis or similar.

**Render free tier spins down.** After 15 minutes of inactivity, the service sleeps. First request takes ~1 minute to wake up. For a real product, you'd upgrade to a paid plan (~$7/month) or use a different host.

**Active games reset on redeploy.** If someone's mid-game when you push new code, their game gets corrupted. The database survives (all moves are logged), but the in-memory board state is lost. For a real app, you'd want to persist and restore that state gracefully.

## For Developers

If you want to extend this:

- **Add an API**: The game logic is in FastAPI routes. You could expose JSON endpoints for a mobile app or different frontend.
- **Better UI**: Replace `game.html` with a React component. The WebSocket messages stay the same.
- **Leaderboard**: Add a `user_stats` table, track wins/losses, show rankings.
- **Different time controls**: Blitz, rapid, classical. Just track move timestamps and validate.
- **AI opponent**: Plug in a chess engine (Stockfish) for single-player games.

The code is straightforward enough to fork and modify. Main entry point is `main.py`. Database models are in `database.py`.

## Running Tests

No automated tests yet. For now:
1. Start the server locally
2. Open two browser windows (or private windows)
3. Register two users
4. Create and join a game
5. Try various moves: normal moves, captures, castling, promotion, checks
6. Try illegal moves — they should be rejected
7. Try disconnecting and reconnecting — the game should recover

## Deployment

### Local

```bash
python main.py
# Runs on http://127.0.0.1:8000 with auto-reload
```

### Production (Render + Neon)

**Setup Neon PostgreSQL:**
1. Sign up at [neon.com](https://neon.com) (free tier, no credit card)
2. Create a project
3. Copy your connection string (looks like `postgresql://user:pass@host/neondb`)

**Setup Render:**
1. Sign up at [render.com](https://render.com) with GitHub
2. Create a new web service from this repo
3. Set environment variables:
   - `DATABASE_URL`: your Neon connection string
   - `PYTHONUNBUFFERED`: `1` (for real-time logs)
   - `PYTHON_VERSION`: `3.12.0` (important — Render defaults to 3.14, which breaks sqlalchemy)
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Click deploy, wait 3–5 minutes

**Test it:**
- Get the Render URL from the dashboard
- Open in two browser tabs
- Register two users, create a game, join, play
- Check Render logs if something breaks

**Re-deploy:** Just push to GitHub. Render auto-detects the change and redeploys.

**Cost:** $0 for both Render and Neon free tiers. Render can handle hobby traffic fine. Neon gives you 512 MB database storage.

## Troubleshooting

**WebSocket connection fails:**
- Make sure you're using HTTPS (Render enforces this)
- Check browser console (F12) for actual error
- Check Render logs for server errors

**Moves aren't syncing:**
- Probably a WebSocket disconnect. Refresh the page.
- Check Render logs for errors
- Make sure both players are actually connected

**Database connection error:**
- Verify `DATABASE_URL` is set correctly in Render
- Verify the Neon connection string is complete (includes password)
- Neon might be rate-limiting if the database is overloaded (unlikely on free tier)

**App takes forever to load after sitting idle:**
- Render's free tier spins down services after 15 minutes. First request wakes it. Takes ~1 minute.
- This is expected. Upgrade to paid if you need instant responses.

## License

MIT. Use it, modify it, learn from it.

## Random Notes

- The chess piece rendering uses Unicode symbols (♟ ♞ ♗ etc). Simple and works everywhere.
- Passwords are hashed with SHA-256 + salt. Not super hardened, but reasonable for a hobby project.
- Game codes are random 8-character strings. Collision risk is negligible for small deployments.
- The database keeps only the last 10 games. Old games are deleted to save space. You can change this in `main.py` if needed.

---

If you fork this or use it as a reference, I'd love to hear what you build with it.
