# Chess Game Database Features

## Overview
The chess game now uses SQLite database for persistent storage of:
- User accounts and authentication
- Game history and move records
- User sessions
- Online presence tracking

## Database Schema

### Users Table
- `id`: Unique user identifier
- `username`: Unique username
- `password_hash`: Hashed password with salt
- `salt`: Random salt for password hashing
- `created_at`: Account creation timestamp

### Games Table
- `id`: Unique game identifier
- `creator_id`: User who created the game
- `creator_color`: Color chosen by creator (white/black)
- `status`: Game status (waiting/active/completed)
- `current_fen`: Current board position in FEN notation
- `current_turn`: Whose turn it is (white/black)
- `created_at`: Game creation timestamp
- `completed_at`: Game completion timestamp (if finished)

### Game Players Table
- `id`: Unique player-game relationship ID
- `game_id`: Reference to game
- `user_id`: Reference to user
- `color`: Player's color (white/black)
- `joined_at`: When player joined the game

### Game Moves Table
- `id`: Unique move ID
- `game_id`: Reference to game
- `move_number`: Sequential move number
- `move_uci`: Move in UCI format (e.g., "e2e4")
- `move_san`: Move in SAN format (e.g., "e4")
- `player_color`: Color of player who made the move
- `fen_after`: Board position after this move
- `created_at`: When move was made

### User Sessions Table
- `id`: Unique session identifier
- `user_id`: Reference to user
- `created_at`: Session creation timestamp
- `expires_at`: Session expiration timestamp
- `is_active`: Whether session is still valid

## Features

### Persistent User Accounts
- User registration and login with secure password hashing
- Session management with automatic expiration
- User data persists across server restarts

### Game History
- All games are stored permanently
- Complete move history for each game
- Game status tracking (waiting, active, completed)
- Board state preservation in FEN notation

### Move Validation and Recording
- Server-side move validation using python-chess
- All moves recorded with timestamps
- Move history available for replay
- Game completion detection (checkmate, stalemate, draw)

### Online Presence
- Real-time online user tracking via WebSockets
- Persistent session management
- User activity monitoring

## Database Location
The SQLite database is stored at: `./data/chess_game.db`

## Database Viewer
Run the database viewer to inspect stored data:
```bash
python view_db.py
```

This will show:
- All registered users
- All games and their status
- Game players and their colors
- Complete move history
- Active user sessions
- Summary statistics

## Testing the Database Features

### 1. User Registration and Login
1. Register a new user
2. Log out and log back in
3. Verify session persistence across browser restarts

### 2. Game Creation and Joining
1. Create a game with a specific color
2. Join the game from another browser/incognito window
3. Verify game state is preserved

### 3. Move History
1. Make several moves in a game
2. Refresh the page
3. Verify the board state and move history are restored

### 4. Game Completion
1. Play a game to completion (checkmate, stalemate, or draw)
2. Verify the game status is marked as completed
3. Check that all moves are recorded

### 5. Server Restart Persistence
1. Play a game and make some moves
2. Stop the server (Ctrl+C)
3. Restart the server
4. Verify all data is preserved (users, games, moves)

### 6. Database Inspection
1. After playing some games, run the database viewer:
   ```bash
   python view_db.py
   ```
2. Verify that all data is properly stored

## Benefits of Database Integration

### Data Persistence
- No data loss on server restart
- User accounts and game history preserved
- Session management across restarts

### Scalability
- SQLite provides ACID compliance
- Efficient querying and indexing
- Easy to migrate to PostgreSQL/MySQL for production

### Analytics and Features
- Complete game history for analysis
- User statistics and rankings (future feature)
- Game replay functionality (future feature)
- Tournament support (future feature)

### Security
- Secure password hashing with salt
- Session management with expiration
- User authentication validation

## Future Enhancements
- User profiles and statistics
- Game replay functionality
- Tournament system
- Rating system (ELO)
- Game analysis tools
- Export game data (PGN format) 