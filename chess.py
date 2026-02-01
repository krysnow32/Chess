import pygame
from pygame.locals import *
import sys
from chess_egine import ChessEngine


def main():
    pygame.init()
    surface = pygame.display.set_mode((1024, 1024))
    FPS = pygame.time.Clock()
    FPS.tick(60)
    game = ChessEngine(surface)
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONUP:
                x, y = pygame.mouse.get_pos()
                x = x // 128
                y = y // 128
                game.move(x, y)
                game.select_piece(x, y)
                game.check_attack()
                game.check_possible_moves()

        game.draw_chessboard()
        game.draw_pieces()
        game.draw_selection()
        game.draw_possible_moves()
        # game.draw_attack_fields()
        pygame.display.update()


if __name__ == '__main__':
    main()