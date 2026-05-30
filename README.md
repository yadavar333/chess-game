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

