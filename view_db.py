#!/usr/bin/env python3
"""
Simple database viewer for the chess game
Run this script to see the stored data
"""

import sqlite3
import os
from datetime import datetime

def view_database():
    db_path = "./data/chess_game.db"
    
    if not os.path.exists(db_path):
        print("Database file not found. Make sure the server has been run at least once.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("CHESS GAME DATABASE VIEWER")
    print("=" * 60)
    
    # First, let's see what tables exist
    print("\n📋 DATABASE TABLES:")
    print("-" * 30)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    for table in tables:
        print(f"Table: {table[0]}")
    
    # View Users
    print("\n📋 USERS:")
    print("-" * 30)
    cursor.execute("SELECT id, username, created_at FROM users")
    users = cursor.fetchall()
    if users:
        for user in users:
            print(f"ID: {user[0][:8]}... | Username: {user[1]} | Created: {user[2]}")
    else:
        print("No users found")
    
    # View Games - check schema first
    print("\n🎮 GAMES:")
    print("-" * 30)
    try:
        cursor.execute("PRAGMA table_info(games)")
        columns = cursor.fetchall()
        print("Games table columns:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Try to get games with available columns
        cursor.execute("SELECT id, status, creator_color, created_at FROM games")
        games = cursor.fetchall()
        if games:
            for game in games:
                print(f"Game ID: {game[0]} | Status: {game[1]} | Creator Color: {game[2]} | Created: {game[3]}")
        else:
            print("No games found")
    except Exception as e:
        print(f"Error reading games table: {e}")
    
    # View Game Players
    print("\n👥 GAME PLAYERS:")
    print("-" * 30)
    try:
        cursor.execute("""
            SELECT gp.game_id, u.username, gp.color, gp.joined_at
            FROM game_players gp
            JOIN users u ON gp.user_id = u.id
            ORDER BY gp.joined_at DESC
        """)
        players = cursor.fetchall()
        if players:
            for player in players:
                print(f"Game: {player[0]} | Player: {player[1]} | Color: {player[2]} | Joined: {player[3]}")
        else:
            print("No game players found")
    except Exception as e:
        print(f"Error reading game_players table: {e}")
    
    # View Game Moves - using correct schema
    print("\n♟️ GAME MOVES:")
    print("-" * 30)
    try:
        cursor.execute("""
            SELECT gm.game_id, gm.move_number, gm.move_san, u.username, gm.created_at
            FROM game_moves gm
            JOIN users u ON gm.player_id = u.id
            ORDER BY gm.game_id, gm.move_number
        """)
        moves = cursor.fetchall()
        if moves:
            for move in moves:
                print(f"Game: {move[0]} | Move {move[1]}: {move[2]} (by {move[3]}) | Time: {move[4]}")
        else:
            print("No moves found")
    except Exception as e:
        print(f"Error reading game_moves table: {e}")
    
    # View Active Sessions
    print("\n🔐 ACTIVE SESSIONS:")
    print("-" * 30)
    try:
        cursor.execute("""
            SELECT us.id, u.username, us.created_at, us.expires_at
            FROM user_sessions us
            JOIN users u ON us.user_id = u.id
            WHERE us.is_active = 1 AND us.expires_at > datetime('now')
            ORDER BY us.created_at DESC
        """)
        sessions = cursor.fetchall()
        if sessions:
            for session in sessions:
                print(f"Session: {session[0][:8]}... | User: {session[1]} | Created: {session[2]} | Expires: {session[3]}")
        else:
            print("No active sessions found")
    except Exception as e:
        print(f"Error reading user_sessions table: {e}")
    
    # Summary
    print("\n📊 SUMMARY:")
    print("-" * 30)
    try:
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"Total Users: {user_count}")
    except:
        print("Total Users: Error reading")
    
    try:
        cursor.execute("SELECT COUNT(*) FROM games")
        game_count = cursor.fetchone()[0]
        print(f"Total Games: {game_count}")
    except:
        print("Total Games: Error reading")
    
    try:
        cursor.execute("SELECT COUNT(*) FROM game_moves")
        move_count = cursor.fetchone()[0]
        print(f"Total Moves: {move_count}")
    except:
        print("Total Moves: Error reading")
    
    try:
        cursor.execute("SELECT COUNT(*) FROM user_sessions WHERE is_active = 1")
        session_count = cursor.fetchone()[0]
        print(f"Active Sessions: {session_count}")
    except:
        print("Active Sessions: Error reading")
    
    conn.close()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    view_database() 