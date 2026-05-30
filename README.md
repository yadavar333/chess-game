# FastAPI Chess Game

A real-time multiplayer chess game built with FastAPI, WebSockets, and modern web technologies. This project provides a lightweight alternative to Django-based chess games with native WebSocket support and no external dependencies like Redis for local development.

## Features

- **Real-time Multiplayer**: Play chess games in real-time using WebSockets
- **User Authentication**: Simple user registration and login system
- **Game Management**: Create and join games with unique game IDs
- **Color Assignment**: Automatic color assignment (white/black) for players
- **Server-side Validation**: All moves are validated on the server using python-chess
- **Modern UI**: Clean, responsive interface with chess piece Unicode symbols
- **Turn Management**: Automatic turn switching and validation
- **No External Dependencies**: Works without Redis or other external services

## Technology Stack

- **Backend**: FastAPI (Python web framework)
- **WebSockets**: Native FastAPI WebSocket support
- **Chess Engine**: python-chess library for move validation
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Templates**: Jinja2 templating engine
- **Server**: Uvicorn ASGI server
- **Database**: PostgreSQL (via SQLAlchemy ORM) with SQLite fallback for local dev
- **Authentication**: SHA-256 password hashing with salt

## Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd chess_fastapi
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Access the application**:
   Open your browser and go to `http://localhost:8000`

## Usage

### Getting Started

1. **Register/Login**: Create an account or login with an existing username
2. **Create a Game**: Choose your preferred color (white or black) and create a new game
3. **Share Game ID**: Share the game ID with your opponent
4. **Join Game**: Your opponent can join by visiting `/game/[GAME_ID]`

### Game Rules

- White always moves first
- Standard chess rules apply
- All moves are validated server-side
- Games are played in real-time with automatic synchronization

### Game Flow

1. **Game Creation**: Player creates a game and chooses their color
2. **Player Joining**: Second player joins using the game ID
3. **Color Assignment**: Joining player gets the opposite color
4. **Real-time Play**: Players take turns making moves
5. **Automatic Sync**: All moves are synchronized between players

## Project Structure

```
chess-game/
├── main.py              # FastAPI application and WebSocket handlers
├── database.py          # SQLAlchemy models and database setup
├── requirements.txt     # Python dependencies (includes psycopg2-binary)
├── runtime.txt          # Python version (3.12)
├── Procfile             # Process declaration for deployment
├── .gitignore           # Git ignore rules
├── config.json          # App configuration (static/templates dirs)
├── README.md            # This file
├── templates/
│   ├── index.html       # Home page with registration/login/lobby
│   └── game.html        # Chess game interface
├── static/              # Static files placeholder
└── data/
    └── chess_game.db    # SQLite database (local dev only)
```

## API Endpoints

### HTTP Routes
- `GET /` - Home page with registration and game creation
- `POST /register` - User registration
- `POST /login` - User login
- `POST /logout` - User logout
- `POST /create-game` - Create a new chess game
- `GET /game/{game_id}` - Join or view a specific game

### WebSocket Routes
- `WS /ws/{game_id}` - Real-time game communication

## Key Features Explained

### 1. Persistent Database Storage
The application uses SQLAlchemy ORM with PostgreSQL for persistent storage (or SQLite for local development). User accounts, game history, and moves are all saved to the database and survive server restarts.

### 2. WebSocket Communication
Real-time communication is handled through FastAPI's native WebSocket support with in-memory `GameManager` for active games. No external message brokers (Redis) required.

### 3. Chess Move Validation
All moves are validated server-side using the `python-chess` library, ensuring game integrity and preventing illegal moves.

### 4. Automatic Color Assignment
When a player joins a game, they are automatically assigned the opposite color of the game creator.

### 5. Session Management
User sessions are stored in the database with expiry (7 days), providing secure authentication via HTTP-only cookies.

## Development

### Adding Features

1. **Database Integration**: Replace in-memory storage with SQLAlchemy or another ORM
2. **User Profiles**: Add user statistics and game history
3. **Game Variants**: Implement different chess variants
4. **AI Opponent**: Add computer player using chess engines
5. **Spectator Mode**: Allow users to watch games without playing

### Deployment

For production deployment:

1. **Use a production ASGI server** like Gunicorn with Uvicorn workers
2. **Add a database** (PostgreSQL, MySQL, etc.) for persistent storage
3. **Set up reverse proxy** (Nginx) for static file serving
4. **Configure environment variables** for sensitive data
5. **Add SSL/TLS** for secure WebSocket connections

Example deployment with Gunicorn:
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Free Deployment (Render + Neon)

Deploy this app **completely free** using Render (FastAPI hosting) + Neon (PostgreSQL database).

### Prerequisites
- GitHub account with this repo pushed
- Neon account (free tier, no credit card)
- Render account (free tier, no credit card)

### Step 1: Create Neon PostgreSQL Database
1. Sign up at [Neon](https://neon.com) (free tier, no credit card)
2. Create a new project
3. Copy your connection string: `postgresql://user:password@host/neondb`

### Step 2: Deploy to Render
1. Sign up at [Render](https://render.com) with GitHub
2. Click **New → Web Service**
3. Select your `chess-game` repo, branch `main`
4. Configure:
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free
5. **Add Environment Variables** (click Advanced):
   - `DATABASE_URL`: (paste your Neon connection string)
   - `PYTHONUNBUFFERED`: `1`
   - `PYTHON_VERSION`: `3.12.0` (⚠️ critical — forces Python 3.12)
6. Click **Create Web Service** and wait 3–5 minutes

### Step 3: Test
- Open the Render URL in two browser tabs
- Register two users, create a game, join, and verify moves sync in real-time

### Auto-Redeploy
Push to GitHub `main` branch anytime — Render auto-deploys:
```bash
git push origin main
```

### Limitations (Free Tier)
- **Render**: Spins down after 15 min inactivity (wakes in ~1 min). For 24/7, upgrade ($7+/month)
- **Neon**: 512 MB storage, 100 CU-hours/month. Adequate for demo/dev
- **Single worker**: GameManager is in-process. Never add `--workers N` or scale horizontally

**Cost: $0** — both platforms have no-credit-card free tiers.

## Troubleshooting

### Common Issues

1. **WebSocket Connection Failed**: Ensure the server is running and accessible
2. **Move Not Working**: Check browser console for JavaScript errors
3. **Game Not Loading**: Verify the game ID is correct and the game exists

### Debug Mode

Run the application in debug mode for detailed error messages:
```bash
uvicorn main:app --reload --log-level debug
```

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the chess game! 