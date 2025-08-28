import pygame
import sys
import time
from .board import Board
from .utils import load_images, load_sounds, draw_text, load_scores, save_scores

class MemoryPuzzle:
    def __init__(self, rows=6, cols=7):
        pygame.init()
        try:
            pygame.mixer.init()
        except Exception:
            # in some environments mixer may fail; continue without sound
            pass

        # Window size (fits well for many grids)
        self.WIDTH, self.HEIGHT = 900, 700
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Memory Puzzle Game - By Rashmi Kori")

        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)

        self.clock = pygame.time.Clock()

        # Load assets
        images, back_image = load_images()
        self.sounds = load_sounds()

        # Selected difficulty
        self.rows = rows
        self.cols = cols

        # Initialize board
        self.board = Board(self.screen, rows, cols, images, back_image, self.sounds)

        # Game state
        self.moves = 0
        self.running = True
        self.win_played = False

        # Timer
        self.start_time = time.time()
        self.elapsed_time = 0

        # Load best scores
        self.scores = load_scores()  # dict with best_moves, best_time

    def reset_timer(self):
        self.start_time = time.time()
        self.elapsed_time = 0

    def run(self):
        while self.running:
            self.screen.fill(self.WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    sys.exit()

                # mouse click: board handles clicks and returns whether move was made
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    made_move = self.board.handle_click(event.pos)
                    if made_move:
                        self.moves += 1

                # keyboard: hint key
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_h:
                        self.board.reveal_all_temp()  # non-blocking

            # Update timer
            self.elapsed_time = int(time.time() - self.start_time)

            # Draw board and UI
            self.board.draw(self.screen)
            # Moves and timer
            draw_text(self.screen, f"Moves: {self.moves}", 24, self.BLACK, 20, 18)
            minutes = self.elapsed_time // 60
            seconds = self.elapsed_time % 60
            draw_text(self.screen, f"Time: {minutes:02}:{seconds:02}", 24, self.BLACK, 20, 46)

            # Hints left
            draw_text(self.screen, f"Hints left (H): {self.board.hints_left}", 22, (120, 60, 200), 20, 74)

            # Show best scores (if present)
            best_m = self.scores.get("best_moves")
            best_t = self.scores.get("best_time")
            if best_m is not None:
                draw_text(self.screen, f"Best Moves: {best_m}", 20, (0, 100, 0), self.WIDTH - 220, 18)
            if best_t is not None:
                bm, bs = divmod(best_t, 60)
                draw_text(self.screen, f"Best Time: {bm:02}:{bs:02}", 20, (0, 100, 0), self.WIDTH - 220, 46)

            # Win detection
            if self.board.is_finished():
                draw_text(self.screen, "🎉 You Win! 🎉", 48, (0, 150, 0), self.WIDTH // 2 - 140, 10)
                if not self.win_played:
                    # Update scores.json
                    # Compare and save only once
                    updated = False
                    # best moves
                    if self.scores.get("best_moves") is None or self.moves < self.scores.get("best_moves"):
                        self.scores["best_moves"] = self.moves
                        updated = True
                    # best time (in seconds)
                    if self.scores.get("best_time") is None or self.elapsed_time < self.scores.get("best_time"):
                        self.scores["best_time"] = self.elapsed_time
                        updated = True

                    if updated:
                        save_scores(self.scores)

                    # play win sound once
                    if 'win.wav' in self.sounds:
                        try:
                            self.sounds['win.wav'].play()
                        except Exception:
                            pass

                    self.win_played = True

            pygame.display.flip()
            self.clock.tick(60)
