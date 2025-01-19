import pygame
import transaction
from database import Database


SCREEN_WIDTH = 700
SCREEN_HEIGHT = 800
CELL_SIZE = 100
COLUMNS = 7
ROWS = 6
RADIUS = CELL_SIZE // 2 - 5
SCROLL_SPEED = 20  


BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
LIGHT_GRAY = (150, 150, 150)
GREEN = (1, 50, 32)


class ConnectFourUI:
    def __init__(self, db):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Connect Four")
        self.db = db
        self.game = None
        self.running = True
        self.font = pygame.font.SysFont("Roboto", 40)  
        self.title_font = pygame.font.SysFont("Roboto", 60, bold=True)  
        self.label_font = pygame.font.SysFont("Roboto", 30)  
        self.message = ""  
        self.player1 = None
        self.player2 = None

    #Crtanje ploče
    def draw_board(self):
        
        self.screen.fill(BLACK)

        #Ispis poruke iznad ploče
        if self.game:
            if self.game.winner:
                winner_text = f"Pobjednik: {self.game.winner.username}"
                winner_surface = self.font.render(winner_text, True, WHITE)
                self.screen.blit(winner_surface, (20, 20))
            else:
                player_text = f"Na redu: {self.game.current_player.username}"
                player_surface = self.font.render(player_text, True, WHITE)
                self.screen.blit(player_surface, (20, 20))

        if self.message:
            message_surface = self.font.render(self.message, True, WHITE)
            self.screen.blit(message_surface, (20, 60))

        # Crtanje ploče za igru
        for row in range(ROWS):
            for col in range(COLUMNS):
                pygame.draw.rect(self.screen, BLUE, (col * CELL_SIZE, row * CELL_SIZE + CELL_SIZE, CELL_SIZE, CELL_SIZE))
                pygame.draw.circle(self.screen, BLACK, (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE + CELL_SIZE // 2), RADIUS)
        if self.game:
            for row in range(ROWS):
                for col in range(COLUMNS):
                    if self.game.board[row][col] == 1:
                        pygame.draw.circle(self.screen, RED, (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE + CELL_SIZE // 2), RADIUS)
                    elif self.game.board[row][col] == 2:
                        pygame.draw.circle(self.screen, YELLOW, (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE + CELL_SIZE // 2), RADIUS)
        pygame.display.update()

    #Animiranje žetona
    def animate_token_drop(self, column, color, final_row):
        for row in range(final_row + 1):
            self.draw_board()  
            pygame.draw.circle(self.screen, color, (column * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2), RADIUS)
            pygame.display.update()
            pygame.time.wait(50) 
            if row < final_row:
                pygame.draw.circle(self.screen, BLACK, (column * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2), RADIUS)

    #Dohvati stupac
    def get_column_from_mouse(self, x):
        return x // CELL_SIZE

    #Scena igre
    def play_game(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return

                if event.type == pygame.MOUSEBUTTONDOWN and self.game and self.game.winner is None:
                    column = self.get_column_from_mouse(event.pos[0])
                    try:
                        row = self.game.add_move(column)

                        
                        color = RED if self.game.current_player == self.game.player1 else YELLOW
                        self.message = ""  
                        self.animate_token_drop(column, color, row)

                        self.draw_board()

                        if self.check_winner(row, column):
                            self.game.winner = self.game.current_player
                            # Ažuriranje statistike
                            self.game.winner.record_win()
                            loser = (
                                self.game.player1
                                if self.game.winner == self.game.player2
                                else self.game.player2
                            )
                            loser.record_loss()
                            transaction.commit()
                            print(f"Pobjednik: {self.game.winner.username}")
                            self.message = f"Pobjednik: {self.game.winner.username}"
                            self.draw_board()
                            
                            pygame.time.wait(3000)
                            
                            
                            self.show_statistics()
                            return
                        else:
                            self.game.switch_turn()
                        transaction.commit()
                    except ValueError:
                        self.message = "Odabrani stupac je pun!"  
                        print("Odabrani stupac je pun.")

           
            if self.running and self.game.winner is None:
                self.draw_board()


    #Startanje igre
    def start_game(self, player1_name, player2_name):

        self.message = ""
        self.db.add_player(player1_name)
        self.db.add_player(player2_name)

        self.player1 = self.db.get_player(player1_name)
        self.player2 = self.db.get_player(player2_name)

        self.game = self.db.add_game(self.player1, self.player2)

        self.play_game()


    #Provjeravanje pobjednika
    def check_winner(self, row, col):
        def check_line(delta_row, delta_col):
            count = 0
            player = self.game.board[row][col]
            r, c = row, col
            while 0 <= r < ROWS and 0 <= c < COLUMNS and self.game.board[r][c] == player:
                count += 1
                r += delta_row
                c += delta_col
            return count

        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for delta_row, delta_col in directions:
            total = check_line(delta_row, delta_col) + check_line(-delta_row, -delta_col) - 1
            if total >= 4:
                return True
        return False
    
    #učitaj nedovršenu igru
    def load_unfinished_game(self):
        for game in self.db.root.games:
            if game.is_active:
                return game
        return None
    

    #Prikaži scenu statistike
    def show_statistics(self):

        if not self.running:  
            return
    
        # Clear screen
        self.screen.fill(BLACK)

        # Prikaz gumba za daljnje scene
        buttons = [
            {"text": "Korisnici u bazi", "action": self.show_users},
            {"text": "Rang lista", "action": self.show_rankings},
            {"text": "Statistike po protivnicima", "action": self.show_opponent_stats},
            {"text": "Povijest igara", "action": self.show_game_history},
            {"text": "Brisanje korisnika iz baze", "action": self.show_delete_user},
            {"text": "Ponovi igru", "action": self.restart_game}
    
        ]

        y_offset = 200
        button_rects = []
        for i, button in enumerate(buttons):
            text_surface = self.font.render(button["text"], True, WHITE)
            rect = pygame.Rect(150, y_offset, 400, 50)
            
            if i == 5:
                color = GREEN  
            elif i == 4:
                color = RED  
            else:
                color = BLUE  

            pygame.draw.rect(self.screen, color, rect)
            self.screen.blit(text_surface, (rect.x + 10, rect.y + 10))
            button_rects.append((rect, button["action"]))
            y_offset += 75

        pygame.display.update()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for rect, action in button_rects:
                        if rect.collidepoint(event.pos):
                            action() 
                            return
                        
    #Gumb resetiraj igru 
    def restart_game(self):
        self.message = ""
        self.game = self.db.add_game(self.player1, self.player2)
        self.play_game()

    #Gumb rang liste
    def show_rankings(self):
        print("Prikaz Rang liste")
        self.screen.fill(BLACK)
        rankings = sorted(self.db.root.players.values(), key=lambda p: p.wins, reverse=True)
        y_offset = 100
        title = self.font.render("Rang lista", True, WHITE)
        self.screen.blit(title, (50, 50))

        for idx, player in enumerate(rankings, start=1):
            text = f"{idx}. {player.username} - Pobjede: {player.wins}, Porazi: {player.losses}"
            text_surface = self.font.render(text, True, WHITE)
            self.screen.blit(text_surface, (50, y_offset))
            y_offset += 50

        back_button = self.draw_back_button()
        pygame.display.update()
        self.wait_for_keypress(back_button)

    #Gumb statistike po protivnicima
    def show_opponent_stats(self):
        print("Prikaz Statistika po protivnicima")
        self.screen.fill(BLACK)
        y_offset = 100
        title = self.font.render("Statistike po protivnicima", True, WHITE)
        self.screen.blit(title, (50, 50))

        for username, player in self.db.root.players.items():
            text = f"Igrač: {username}"
            text_surface = self.font.render(text, True, WHITE)
            self.screen.blit(text_surface, (50, y_offset))
            y_offset += 30
            opponents = {}

            for game in self.db.root.games:
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
                stats_text = f"  Protiv {opponent}: {stats['wins']} pobjeda, {stats['losses']} poraza"
                stats_surface = self.font.render(stats_text, True, WHITE)
                self.screen.blit(stats_surface, (50, y_offset))
                y_offset += 30

        back_button = self.draw_back_button()
        pygame.display.update()
        self.wait_for_keypress(back_button)


    #Gumb prikaz povijesti igara
    def show_game_history(self):
        scroll_offset = 0
        running = True

        while running:
            self.screen.fill(BLACK)
            title = self.font.render("Povijest igara", True, WHITE)
            self.screen.blit(title, (50, 50))

            sorted_games = sorted(self.db.root.games, key=lambda g: g.date, reverse=True)

            y_offset = 100 + scroll_offset
            for game in sorted_games:
                text = f"Igra između {game.player1.username} i {game.player2.username} - Pobjednik: {game.winner.username if game.winner else 'Nema'}"
                text_surface = self.font.render(text, True, WHITE)
                self.screen.blit(text_surface, (50, y_offset))
                y_offset += 50

            back_button = self.draw_back_button()
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.running = False
                    pygame.quit()
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button.collidepoint(event.pos):
                        self.show_statistics()
                        return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:  
                        scroll_offset = min(scroll_offset + SCROLL_SPEED, 0)
                    if event.key == pygame.K_DOWN:  
                        scroll_offset -= SCROLL_SPEED

    #Gumb prikaz korisnika u bazi
    def show_users(self):
        self.screen.fill(BLACK)
        y_offset = 100
        title = self.font.render("Korisnici u bazi", True, WHITE)
        self.screen.blit(title, (50, 50))

        for username, player in self.db.root.players.items():
            text = f"{username} - Pobjede: {player.wins}, Porazi: {player.losses}"
            text_surface = self.font.render(text, True, WHITE)
            self.screen.blit(text_surface, (50, y_offset))
            y_offset += 50

        back_button = self.draw_back_button()
        pygame.display.update()
        self.wait_for_keypress(back_button)

    #Gumb nazad
    def draw_back_button(self):
        rect = pygame.Rect(50, SCREEN_HEIGHT - 100, 200, 50)
        pygame.draw.rect(self.screen, RED, rect)
        text_surface = self.font.render("Nazad", True, WHITE)
        self.screen.blit(text_surface, (rect.x + 10, rect.y + 10))
        return rect
    
    #Čekanje pritiska bilo kodjeg gumba
    def wait_for_keypress(self, back_button):
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    return  
                if event.type == pygame.KEYDOWN: 
                    waiting = False
                if event.type == pygame.MOUSEBUTTONDOWN:  
                    if back_button.collidepoint(event.pos):  
                        self.show_statistics()
                        waiting = False

    #Početni zaslon
    def input_player_names(self):
        
        self.screen.fill(BLACK)
        title = self.title_font.render("Connect Four", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))

        label1 = self.label_font.render("Unesite ime igrača 1:", True, LIGHT_GRAY)
        self.screen.blit(label1, (SCREEN_WIDTH // 2 - label1.get_width() // 2, 100))

        label2 = self.label_font.render("Unesite ime igrača 2:", True, LIGHT_GRAY)
        self.screen.blit(label2, (SCREEN_WIDTH // 2 - label2.get_width() // 2, 500))

        player1_text = ""
        player2_text = ""

        input_active = [False, False] 

        input_boxes = [
            pygame.Rect(SCREEN_WIDTH // 2 - 150, 130, 300, 50),
            pygame.Rect(SCREEN_WIDTH // 2 - 150, 230, 300, 50)
        ]

        colors = [GRAY, GRAY]

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_boxes[0].collidepoint(event.pos):
                        input_active = [True, False]
                    elif input_boxes[1].collidepoint(event.pos):
                        input_active = [False, True]
                    else:
                        input_active = [False, False]
                if event.type == pygame.KEYDOWN:
                    if input_active[0]:
                        if event.key == pygame.K_RETURN:
                            input_active = [False, True]
                        elif event.key == pygame.K_BACKSPACE:
                            player1_text = player1_text[:-1]
                        else:
                            player1_text += event.unicode
                    elif input_active[1]:
                        if event.key == pygame.K_RETURN:
                            running = False
                        elif event.key == pygame.K_BACKSPACE:
                            player2_text = player2_text[:-1]
                        else:
                            player2_text += event.unicode

            colors[0] = RED if input_active[0] else GRAY
            colors[1] = RED if input_active[1] else GRAY

            # Nacrtaj textbox
            self.screen.fill(BLACK)
            self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))
            self.screen.blit(label1, (SCREEN_WIDTH // 2 - label1.get_width() // 2, 100))
            self.screen.blit(label2, (SCREEN_WIDTH // 2 - label2.get_width() // 2, 200))

            for i, box in enumerate(input_boxes):
                pygame.draw.rect(self.screen, colors[i], box, 2)

            player1_surface = self.font.render(player1_text, True, WHITE)
            player2_surface = self.font.render(player2_text, True, WHITE)

            self.screen.blit(player1_surface, (input_boxes[0].x + 5, input_boxes[0].y + 5))
            self.screen.blit(player2_surface, (input_boxes[1].x + 5, input_boxes[1].y + 5))

            pygame.display.update()

        return player1_text, player2_text
    

    #Gumb brisanja korisnika
    def show_delete_user(self):
        running = True
        while running:
            self.screen.fill(BLACK)

            title_surface = self.title_font.render("Brisanje korisnika", True, WHITE)
            self.screen.blit(title_surface, (SCREEN_WIDTH // 2 - title_surface.get_width() // 2, 20))

            # Prikaži korisnike
            y_offset = 100
            users = list(self.db.root.players.keys())
            user_buttons = []
            for username in users:
                button = pygame.Rect(50, y_offset, 600, 50)
                pygame.draw.rect(self.screen, GRAY, button)
                text_surface = self.font.render(username, True, BLACK)
                self.screen.blit(text_surface, (button.x + 10, button.y + 10))
                user_buttons.append((button, username))
                y_offset += 60

            back_button = pygame.Rect(50, SCREEN_HEIGHT - 100, 200, 50)
            pygame.draw.rect(self.screen, GRAY, back_button)
            back_text = self.font.render("Nazad", True, BLACK)
            self.screen.blit(back_text, (back_button.x + 10, back_button.y + 10))

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.running = False
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button, username in user_buttons:
                        if button.collidepoint(event.pos):
                            self.db.delete_player(username)
                            self.show_message(f"Korisnik {username} obrisan.")
                            return
                    if back_button.collidepoint(event.pos):
                        return

    #Povratak na izbornik
    def show_main_menu(self):
            running = True
            while running:
                self.screen.fill(BLACK)

                title_surface = self.title_font.render("Connect Four - Izbornik", True, WHITE)
                self.screen.blit(title_surface, (SCREEN_WIDTH // 2 - title_surface.get_width() // 2, 20))

                delete_user_button = pygame.Rect(50, 200, 600, 50)
                pygame.draw.rect(self.screen, GRAY, delete_user_button)
                delete_user_text = self.font.render("Obriši korisnika", True, BLACK)
                self.screen.blit(delete_user_text, (delete_user_button.x + 10, delete_user_button.y + 10))

                pygame.display.update()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        self.running = False
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if delete_user_button.collidepoint(event.pos):
                            self.show_delete_user()


    #Pokaži poruku nakon brisanja
    def show_message(self, message):
        running = True
        while running:
            self.screen.fill(BLACK)

            message_surface = self.font.render(message, True, WHITE)
            self.screen.blit(message_surface, (SCREEN_WIDTH // 2 - message_surface.get_width() // 2, SCREEN_HEIGHT // 2 - 25))

            back_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 50)
            pygame.draw.rect(self.screen, GRAY, back_button)
            back_text = self.font.render("Nazad", True, BLACK)
            self.screen.blit(back_text, (back_button.x + 50, back_button.y + 10))

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button.collidepoint(event.pos):
                        self.show_statistics()
                        return


if __name__ == "__main__":
    db = Database()
    connect_four = ConnectFourUI(db)
    
    while connect_four.running:
        player1_name, player2_name = connect_four.input_player_names()
        connect_four.start_game(player1_name, player2_name)
    
    db.close()
    pygame.quit()

