import transaction
from database import Database
from datetime import datetime

db = Database()

for game in db.root.games:
    if not hasattr(game, 'date'):
        game.date = datetime.now()  
        print(f"Ažuriran datum za igru između {game.player1.username} i {game.player2.username}.")

transaction.commit()  
db.close()
