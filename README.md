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
chess_fastapi/
├── main.py              # FastAPI application and WebSocket handlers
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── templates/          # HTML templates
│   ├── index.html      # Home page with registration/login
│   └── game.html       # Chess game interface
└── static/             # Static files (CSS, JS, images)
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

### 1. In-Memory Storage
The application uses in-memory storage for games and users, making it perfect for development and small-scale deployment. For production, you can easily replace this with a database.

### 2. WebSocket Communication
Real-time communication is handled through FastAPI's native WebSocket support, eliminating the need for external message brokers like Redis.

### 3. Chess Move Validation
All moves are validated using the `python-chess` library, ensuring game integrity and preventing illegal moves.

### 4. Automatic Color Assignment
When a player joins a game, they are automatically assigned the opposite color of the game creator.

### 5. Session Management
User sessions are managed through cookies, providing a simple authentication system.

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

## Railway Deployment

To deploy this app on Railway:

1. **Push your code and tag to GitHub:**
   ```sh
   git push origin main
   git push origin v1.0
   ```
2. **Create a new project on [Railway](https://railway.app/):**
   - Click 'New Project' > 'Deploy from GitHub repo'.
   - Select your chess-game repository.
3. **Configure the deployment:**
   - Railway will auto-detect Python from `requirements.txt`.
   - The `Procfile` should contain:
     ```
     web: uvicorn main:app --host 0.0.0.0 --port $PORT
     ```
   - No further configuration is needed for SQLite. For PostgreSQL, add the plugin and set the DB URL.
4. **Set environment variables (if needed):**
   - Add any secrets or DB URLs in the Railway dashboard under 'Variables'.
5. **Deploy the v1.0 tag:**
   - In Railway, select the `v1.0` tag for deployment.
6. **Access your app:**
   - Railway will provide a public URL after deployment.

**Required files:**
- `requirements.txt`
- `Procfile`
- `main.py`
- `templates/` and `static/` folders

If you encounter any issues, check the Railway build logs or ask for help!

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