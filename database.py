from datetime import datetime
import ZODB, ZODB.FileStorage, transaction
from persistent import Persistent
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping

import transaction


class Player(Persistent):
    def __init__(self, username):
        self.username = username
        self.wins = 0
        self.losses = 0
        self.moves = PersistentList()
        self.longest_win_streak = 0
        self.total_moves = 0
        


    def record_win(self):
        self.wins += 1

    def record_loss(self):
        self.losses += 1

    def add_move(self, column):
        self.moves.append(column)

class Game(Persistent):
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.board = [[0] * 7 for _ in range(6)]
        self.current_player = player1
        self.winner = None
        self.date = datetime.now() 
        self.is_active = True

    def switch_turn(self):
        self.current_player = self.player2 if self.current_player == self.player1 else self.player1

    def add_move(self, column):
        for row in range(5, -1, -1):
            if self.board[row][column] == 0:
                self.board[row][column] = 1 if self.current_player == self.player1 else 2
                self.current_player.add_move(column)
                return row
        raise ValueError("Column is full")

class Database:
    def __init__(self, db_file="connect_four.fs"):
        self.storage = ZODB.FileStorage.FileStorage(db_file)
        self.db = ZODB.DB(self.storage)
        self.connection = self.db.open()
        self.root = self.connection.root
        self.initialize_database()

    def initialize_database(self):
        if not hasattr(self.root, 'players'):
            self.root.players = PersistentMapping()
        if not hasattr(self.root, 'games'):
            self.root.games = PersistentList()
        transaction.commit()

    def add_player(self, username):
        if username not in self.root.players:
            self.root.players[username] = Player(username)
            transaction.commit()
            print(f"Korisnik {username} uspješno dodan u bazu.")
            print(f"Trenutni korisnici u bazi: {list(self.root.players.keys())}")
        else:
            print(f"Korisnik {username} već postoji u bazi.")

    def get_player(self, username):
        return self.root.players.get(username)

    def add_game(self, player1, player2):
        print(f"Kreiranje igre između: {player1.username} i {player2.username}")
        game = Game(player1, player2)
        self.root.games.append(game)
        transaction.commit()
        return game
    
    def delete_player(self, username):
        if username in self.root.players:
            del self.root.players[username]

            self.root.games = [
                game for game in self.root.games
                if game.player1.username != username and game.player2.username != username
            ]

            print(f"Korisnik {username} uspješno obrisan iz baze.")
            transaction.commit()
        else:
            print(f"Korisnik {username} ne postoji u bazi.")

    def close(self):
        self.connection.close()
        self.db.close()

if __name__ == "__main__":
    db = Database()
    db.add_player("Player1")
    db.add_player("Player2")
    player1 = db.get_player("Player1")
    player2 = db.get_player("Player2")
    game = db.add_game(player1, player2)
    print("Database initialized and players added.")
    db.close()
