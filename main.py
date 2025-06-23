from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Dict, List, Optional
import json
import uuid
import chess
from datetime import datetime, timedelta
import os
import hashlib
import secrets
from sqlalchemy.orm import Session

# Import database models
from database import get_db, User, Game, GamePlayer, GameMove, UserSession, SessionLocal

app = FastAPI(title="Chess Game", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# In-memory storage for real-time features (online users, active connections)
online_users: Dict[str, Dict] = {}  # user_id -> {username, last_seen}
user_sessions: Dict[str, str] = {}  # session_id -> user_id (for quick lookup)
presence_connections: List[WebSocket] = []  # All presence WebSocket connections

# Game management with in-memory board state
class GameManager:
    def __init__(self):
        self.connections: Dict[str, List[WebSocket]] = {}
        self.game_boards: Dict[str, chess.Board] = {}  # game_id -> chess.Board
        self.game_turns: Dict[str, str] = {}  # game_id -> current turn
    
    def create_game(self, creator_id: str, creator_color: str, db: Session) -> str:
        game_id = str(uuid.uuid4())[:8]
        
        # Create game in database
        game = Game(
            id=game_id,
            creator_id=creator_id,
            creator_color=creator_color,
            status="waiting"
        )
        db.add(game)
        
        # Add creator as player
        creator_player = GamePlayer(
            game_id=game_id,
            user_id=creator_id,
            color=creator_color
        )
        db.add(creator_player)
        
        db.commit()
        
        # Initialize in-memory game state
        self.connections[game_id] = []
        self.game_boards[game_id] = chess.Board()
        self.game_turns[game_id] = "white"
        
        return game_id
    
    def join_game(self, game_id: str, joiner_id: str, db: Session) -> bool:
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            return False
        
        # Check if game is full
        player_count = db.query(GamePlayer).filter(GamePlayer.game_id == game_id).count()
        if player_count >= 2:
            return False
        
        # Assign opposite color
        creator_color = game.creator_color
        joiner_color = "black" if creator_color == "white" else "white"
        
        # Add joiner as player
        joiner_player = GamePlayer(
            game_id=game_id,
            user_id=joiner_id,
            color=joiner_color
        )
        db.add(joiner_player)
        
        # Update game status
        game.status = "active"
        game.joiner_id = joiner_id
        db.commit()
        return True
    
    def get_game(self, game_id: str, db: Session) -> Optional[Game]:
        return db.query(Game).filter(Game.id == game_id).first()
    
    def get_game_board(self, game_id: str) -> chess.Board:
        if game_id not in self.game_boards:
            self.game_boards[game_id] = chess.Board()
        return self.game_boards[game_id]
    
    def get_game_turn(self, game_id: str) -> str:
        return self.game_turns.get(game_id, "white")
    
    def add_connection(self, game_id: str, websocket: WebSocket):
        if game_id not in self.connections:
            self.connections[game_id] = []
        self.connections[game_id].append(websocket)
    
    def remove_connection(self, game_id: str, websocket: WebSocket):
        if game_id in self.connections:
            self.connections[game_id] = [ws for ws in self.connections[game_id] if ws != websocket]
    
    async def broadcast_to_game(self, game_id: str, message: dict):
        if game_id in self.connections:
            for connection in self.connections[game_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    pass

game_manager = GameManager()

# User management
def create_user(username: str, password: str, db: Session) -> str:
    user_id = str(uuid.uuid4())
    # Hash password
    salt = secrets.token_hex(16)
    hashed_password = hashlib.sha256((password + salt).encode()).hexdigest()
    
    user = User(
        id=user_id,
        username=username,
        password_hash=hashed_password,
        salt=salt
    )
    db.add(user)
    db.commit()
    return user_id

def verify_user(username: str, password: str, db: Session) -> Optional[str]:
    user = db.query(User).filter(User.username == username).first()
    if user:
        hashed_password = hashlib.sha256((password + user.salt).encode()).hexdigest()
        if hashed_password == user.password_hash:
            return user.id
    return None

def get_user(user_id: str, db: Session) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def create_session(user_id: str, db: Session) -> str:
    session_id = secrets.token_hex(32)
    expires_at = datetime.now() + timedelta(days=7)  # 7 days expiry
    
    # Store in database
    session = UserSession(
        id=session_id,
        user_id=user_id,
        expires_at=expires_at
    )
    db.add(session)
    db.commit()
    
    # Also store in memory for quick lookup
    user_sessions[session_id] = user_id
    return session_id

def get_user_from_session(session_id: str, db: Session) -> Optional[str]:
    # Check memory first
    if session_id in user_sessions:
        return user_sessions[session_id]
    
    # Check database
    session = db.query(UserSession).filter(
        UserSession.id == session_id,
        UserSession.is_active == True,
        UserSession.expires_at > datetime.now()
    ).first()
    
    if session:
        user_sessions[session_id] = session.user_id
        return session.user_id
    return None

def remove_session(session_id: str, db: Session):
    # Remove from database
    session = db.query(UserSession).filter(UserSession.id == session_id).first()
    if session:
        session.is_active = False
        db.commit()
    
    # Remove from memory
    if session_id in user_sessions:
        del user_sessions[session_id]

# Online user management
def add_online_user(user_id: str, username: str):
    online_users[user_id] = {
        "username": username,
        "last_seen": datetime.now()
    }

def remove_online_user(user_id: str):
    if user_id in online_users:
        del online_users[user_id]

def get_online_users() -> List[str]:
    return [user["username"] for user in online_users.values()]

async def broadcast_online_users():
    online_list = get_online_users()
    message = {
        "type": "online_users",
        "users": online_list
    }
    
    # Broadcast to all presence connections
    for connection in presence_connections[:]:  # Copy list to avoid modification during iteration
        try:
            await connection.send_text(json.dumps(message))
        except:
            # Remove dead connections
            if connection in presence_connections:
                presence_connections.remove(connection)

# Authentication dependency
def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    session_id = request.cookies.get("session_id")
    if session_id:
        user_id = get_user_from_session(session_id, db)
        if user_id:
            return get_user(user_id, db)
    return None

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    online_list = get_online_users()
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "online_users": online_list,
        "current_user": current_user
    })

@app.post("/register")
async def register(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    user_id = create_user(username, password, db)
    session_id = create_session(user_id, db)
    
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="session_id", value=session_id, httponly=True)
    return response

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user_id = verify_user(username, password, db)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    session_id = create_session(user_id, db)
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="session_id", value=session_id, httponly=True)
    return response

@app.post("/logout")
async def logout(request: Request, db: Session = Depends(get_db)):
    session_id = request.cookies.get("session_id")
    if session_id:
        user_id = get_user_from_session(session_id, db)
        if user_id:
            remove_online_user(user_id)
            await broadcast_online_users()
        remove_session(session_id, db)
    
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="session_id")
    return response

@app.post("/create-game")
async def create_game(request: Request, color: str = Form(...), db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if not current_user:
        raise HTTPException(status_code=401, detail="Not logged in")
    
    game_id = game_manager.create_game(current_user.id, color, db)
    return RedirectResponse(url=f"/game/{game_id}", status_code=303)

@app.get("/game/{game_id}", response_class=HTMLResponse)
async def game_page(request: Request, game_id: str, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if not current_user:
        return RedirectResponse(url="/", status_code=303)
    
    game = game_manager.get_game(game_id, db)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Check if user is already a player
    existing_player = db.query(GamePlayer).filter(
        GamePlayer.game_id == game_id,
        GamePlayer.user_id == current_user.id
    ).first()
    
    # If user is not in the game, join them
    if not existing_player:
        if not game_manager.join_game(game_id, current_user.id, db):
            raise HTTPException(status_code=400, detail="Game is full")
    
    # Get user's color
    player = db.query(GamePlayer).filter(
        GamePlayer.game_id == game_id,
        GamePlayer.user_id == current_user.id
    ).first()
    
    if not player:
        raise HTTPException(status_code=400, detail="Player not found in game")
    
    user_color = player.color
    fen = game_manager.get_game_board(game_id).fen()
    turn = game_manager.get_game_turn(game_id)
    
    return templates.TemplateResponse("game.html", {
        "request": request,
        "game_id": game_id,
        "user_color": user_color,
        "fen": fen,
        "turn": turn,
        "current_user": current_user
    })

@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    await websocket.accept()
    
    # Get database session
    db = SessionLocal()
    
    try:
        game = game_manager.get_game(game_id, db)
        if not game:
            await websocket.close()
            return
        
        game_manager.add_connection(game_id, websocket)
        
        # Get current user from game players
        current_user = None
        for player in game.players:
            user = get_user(player.user_id, db)
            if user:
                current_user = user
                break
        
        if current_user:
            add_online_user(current_user.id, current_user.username)
            await broadcast_online_users()
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "move":
                # Handle move
                try:
                    move = chess.Move.from_uci(message["move"])
                    chess_board = game_manager.get_game_board(game_id)
                    
                    if chess_board.is_legal(move):
                        # Record move in database
                        move_number = len(game.moves) + 1
                        move_san = chess_board.san(move)
                        player_color = game_manager.get_game_turn(game_id)
                        
                        # Create move record
                        game_move = GameMove(
                            game_id=game_id,
                            player_id=current_user.id if current_user else "",
                            move_number=move_number,
                            move_uci=message["move"],
                            move_san=move_san,
                            fen_after=chess_board.fen(),
                            is_check=chess_board.is_check(),
                            is_checkmate=chess_board.is_checkmate(),
                            is_stalemate=chess_board.is_stalemate(),
                            is_draw=chess_board.is_insufficient_material()
                        )
                        db.add(game_move)
                        
                        # Update board
                        chess_board.push(move)
                        game_manager.game_turns[game_id] = "black" if game_manager.game_turns[game_id] == "white" else "white"
                        
                        # Check game status
                        game_status = "ongoing"
                        if chess_board.is_checkmate():
                            game_status = "checkmate"
                            game.status = "completed"
                            game.result = "checkmate"
                            game.winner_id = current_user.id if current_user else None
                            game.completed_at = datetime.now()
                        elif chess_board.is_stalemate():
                            game_status = "stalemate"
                            game.status = "completed"
                            game.result = "stalemate"
                            game.completed_at = datetime.now()
                        elif chess_board.is_insufficient_material():
                            game_status = "draw"
                            game.status = "completed"
                            game.result = "draw"
                            game.completed_at = datetime.now()
                        
                        db.commit()
                        
                        # Get move history
                        moves = [move.move_san for move in game.moves]
                        
                        # Broadcast updated game state
                        await game_manager.broadcast_to_game(game_id, {
                            "type": "move",
                            "fen": chess_board.fen(),
                            "turn": game_manager.game_turns[game_id],
                            "move_history": moves,
                            "game_status": game_status
                        })
                except Exception as e:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": str(e)
                    }))
    
    except WebSocketDisconnect:
        game_manager.remove_connection(game_id, websocket)
        if current_user:
            remove_online_user(current_user.id)
            await broadcast_online_users()
    finally:
        db.close()

@app.websocket("/ws/presence")
async def presence_websocket(websocket: WebSocket):
    await websocket.accept()
    presence_connections.append(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "ping":
                # Update last seen for user
                user_id = message.get("user_id")
                if user_id and user_id in online_users:
                    online_users[user_id]["last_seen"] = datetime.now()
                
                # Send online users list
                await websocket.send_text(json.dumps({
                    "type": "online_users",
                    "users": get_online_users()
                }))
    
    except WebSocketDisconnect:
        if websocket in presence_connections:
            presence_connections.remove(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True) 