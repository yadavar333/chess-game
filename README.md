# Chess Game

A real-time multiplayer chess app I built to see if I could get WebSockets working smoothly in FastAPI without overthinking it.

## The Idea

I wanted to build something you could actually *play* — not just a demo. Two people register, one creates a game and gets a code, the other joins with that code, and they're playing live. Moves show up instantly on both screens.

Most of the chess apps I looked at felt either way too engineered or kinda sluggish on the real-time side. So I thought: what if I just made something minimal that actually feels responsive?

## How It Works

The game logic lives on the server. Browser sends a move, server validates it (using `python-chess`), logs it to the database, and broadcasts it to both players via WebSocket. Pretty straightforward.

I kept the frontend simple — just HTML, CSS, and vanilla JavaScript. No build step, no framework overhead. The hardest part was actually getting the WebSocket reconnection smooth, which honestly I'm still not 100% happy with.

## What's in Here

```
main.py           # All the FastAPI routes and WebSocket stuff
database.py       # User and game models (using SQLAlchemy)
requirements.txt  # Dependencies
templates/
  ├── index.html  # Login, game creation, lobby
  └── game.html   # The actual chessboard
```

Nothing fancy. I could've added a testing framework, but I just play test it instead — open two windows, try some moves, try to break it. Seems to work.

## Running It Locally

```bash
pip install -r requirements.txt
python main.py
```

Opens on `http://localhost:8000`. Create an account, make a game, open another window (incognito works), join it. That's it.

The first time you run it, it creates a SQLite database locally. Fine for development.

## The Tech Choices

**FastAPI:** I like how clean the code is. WebSocket support is native, no weird hacks needed.

**WebSockets:** Could've used polling, but WebSockets feel right for a real-time game. Latency matters.

**SQLAlchemy:** I wanted something that'd scale from local SQLite to a real database without rewriting everything. SQLAlchemy lets you do that.

**Vanilla JavaScript:** Honestly just because I didn't want to deal with a build step. If this got bigger, I'd probably switch to something like React, but for now it's nice having a single HTML file that works.

**`python-chess`:** Great library. I didn't want to reimplement chess rules. Too many edge cases (castling, en passant, promotion).

## Deploying This Thing

I got it running on Render with Neon PostgreSQL because they have a free tier and I didn't want to pay anything. The setup was annoying because Render kept trying to use Python 3.14 (which breaks SQLAlchemy), but once I pinned it to 3.12, it just worked.

**The flow:**
- Code lives on GitHub
- Render watches the repo. Push to `main`, it auto-deploys
- Database runs on Neon (free tier gives 512 MB)
- Takes about 3 minutes to deploy

It's obviously not production-grade (free tier Render spins down after 15 minutes of inactivity, active games get corrupted if you redeploy mid-game), but for showing the idea to people, it's perfect.

## What I'd Do Differently

**Graceful reconnects:** Right now if you disconnect and reconnect, the game state can get weird. I'd want to store more board state on the server and rebuild it on reconnect.

**More than one worker:** The game state (whose turn, what's on the board) lives in Python's memory. You can't run multiple instances without everything breaking. For a real app, you'd move that to Redis and be done in an afternoon.

**Testing:** I should've written tests from the start instead of just clicking around. Would've caught some of the edge cases earlier.

**Frontend polish:** The UI works but it's bare-bones. Drag-and-drop would be nicer than clicking. Mobile support is nonexistent.

But honestly? It does what it's supposed to do. Two people can play a real game of chess together in real-time. That's the bar I set, and it clears it.

## If You Want to Fork This

The code's pretty readable. Main entry point is `main.py`. Game logic is there, WebSocket handlers are there. Database models are in `database.py` if you want to add stuff like game statistics or user profiles.

Ideas I thought about but didn't build:
- Leaderboard / game history
- Time controls (blitz, rapid, etc)
- Playing against the computer (would need Stockfish or similar)
- Spectator mode
- Elo ratings

Any of those would be fun to add. The architecture doesn't make it hard.

## Actually Running It (Locally & Deployed)

**Locally:**
```bash
python main.py
# http://localhost:8000
```

**Deployed:**
- Code: GitHub repo
- App: Render (free tier)
- Database: Neon PostgreSQL (free tier)
- Environment variables on Render: `DATABASE_URL`, `PYTHONUNBUFFERED=1`, `PYTHON_VERSION=3.12.0`

The `PYTHON_VERSION` thing was important — Render defaults to whatever latest is, and that broke things. Pinning it solved it.

## The Honest Bits

**Render's free tier is slow at startup.** After sitting idle for 15 minutes, the first request takes forever (like 1 minute). You can upgrade to like $7/month if you want it instant, but for a side project, it doesn't really matter.

**Can't scale horizontally.** The game state is in-process. Two instances = two separate games = broken. You'd need to refactor that to work at scale, but honestly most of what I built doesn't need to scale. It's a fun project, not a business.

**Passwords aren't Fort Knox.** SHA-256 with salt. Not the most hardened thing ever, but way better than plaintext and good enough for a hobby project where the worst that happens is someone plays as someone else.

**Database only keeps 10 games.** Old ones get deleted. You can change that in the code if you want to keep history. Decided it wasn't worth the storage cost on the free tier.

## Misc

Unicode chess pieces (♟ ♞ ♗ ♕) work great. Simple, works everywhere, looks decent.

Game codes are 8 random characters. Collision risk is basically zero for small deployments.

If I'm being real, the part I'm least happy with is the reconnection logic. It's not broken, but it's a bit fragile. That's where I'd focus if I were going to keep working on it.

---

It was fun building this. If you use it, build on it, or steal ideas from it, that's cool. Happy to answer questions if you have them.
