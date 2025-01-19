from database import Database


# Otvori bazu
db = Database(db_file="connect_four.fs")


# Provjeri sve korisnike
print("Korisnici u bazi:")
for username, player in db.root.players.items():
    print(f"Korisničko ime: {username}, Pobjede: {player.wins}, Porazi: {player.losses}, Potezi: {list(player.moves)}")

print("\nRang lista:")
sorted_players = sorted(db.root.players.values(), key=lambda p: p.wins, reverse=True)
for idx, player in enumerate(sorted_players, start=1):
    print(f"{idx}. {player.username} - Pobjede: {player.wins}, Porazi: {player.losses}")

print("\nStatistike po protivnicima:")
for username, player in db.root.players.items():
    print(f"Igrač: {username}")
    opponents = {}
    for game in db.root.games:
        if game.player1.username == username:
            opponent = game.player2.username
        elif game.player2.username == username:
            opponent = game.player1.username
        else:
            continue
        if opponent not in opponents:
            opponents[opponent] = {"wins": 0, "losses": 0}
        if game.winner and game.winner.username == username:
            opponents[opponent]["wins"] += 1
        else:
            opponents[opponent]["losses"] += 1
    for opponent, stats in opponents.items():
        print(f"  Protiv {opponent}: {stats['wins']} pobjeda, {stats['losses']} poraza")


# Provjeri sve igre
print("\nPovijest igara:")
for game in db.root.games:
    print(f"Igra između {game.player1.username} i {game.player2.username}")
    print(f"Datum: {game.date}")
    print(f"Pobjednik: {game.winner.username if game.winner else 'Nema pobjednika'}")
    print(f"Ploča:\n{game.board}")

# Provjeri ključeve u bazi
print("\nPostoji li 'players':", hasattr(db.root, 'players'))
print("Postoji li 'games':", hasattr(db.root, 'games'))

# Zatvori bazu
db.close()
