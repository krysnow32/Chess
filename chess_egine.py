import pygame
import copy
from pprint import pprint

class ChessEngine():
    def __init__(self, surface: pygame.Surface):
        self.white = pygame.image.load(r'graphics\white.png')
        self.black = pygame.image.load(r'graphics\black.png')
        self.turn = 'W'
        self.pawn_double = False
        self.pawn_double_position = None
        self.chosen_piece = None
        self.piece_coords = None
        self.surface = surface
        self.white_short_castle = True
        self.white_long_castle = True
        self.black_short_castle = True
        self.black_long_castle = True

        self.white_pieces = [
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            # [None, None, None, None, None, None, None, None],
            # [None, None, None, None, None, None, None, None],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            ['r', 'k', 'b', 'Q', 'K', 'b', 'k', 'r']
        ]

        self.black_pieces = [
            ['r', 'k', 'b', 'Q', 'K', 'b', 'k', 'r'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            # [None, None, None, None, None, None, None, None],
            # [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None]
        ]

        # possible moves -> None - cant move, 1 -> can move, 2 -> can capture, 3 -> en passant capture (bicie w przelocie)
        # 4 -> white short castle, 5 -> white long castle, 6 -> black short castle, 7 -> black long castle
        self.possible_moves = [
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None]
        ]

        self.fields_attacked = [
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None]
        ]

        self.next_player_position = [
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None]
        ]

        self.next_enemy_attack = [
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None]
        ]

    def draw_pieces(self):
        image_path = ''
        for y, row in enumerate(self.black_pieces):
            for x, piece in enumerate(row):
                match piece:
                    case 'r':
                        image_path = r'graphics\b_Rook.png'
                    case 'k':
                        image_path = r'graphics\b_Knight.png'
                    case 'b':
                        image_path = r'graphics\b_Bishop.png'
                    case 'Q':
                        image_path = r'graphics\b_Queen.png'
                    case 'K':
                        image_path = r'graphics\b_King.png'
                    case 'p':
                        image_path = r'graphics\b_Pawn.png'
                    case _:
                        continue
                img = pygame.image.load(image_path)
                self.surface.blit(img, (x * 128, y * 128))
        for y, row in enumerate(self.white_pieces):
            for x, piece in enumerate(row):
                match piece:
                    case 'r':
                        image_path = r'graphics\w_Rook.png'
                    case 'k':
                        image_path = r'graphics\w_Knight.png'
                    case 'b':
                        image_path = r'graphics\w_Bishop.png'
                    case 'Q':
                        image_path = r'graphics\w_Queen.png'
                    case 'K':
                        image_path = r'graphics\w_King.png'
                    case 'p':
                        image_path = r'graphics\w_Pawn.png'
                    case _:
                        continue
                img = pygame.image.load(image_path)
                self.surface.blit(img, (x * 128, y * 128))


    def change_turn(self):
        if self.turn == 'W':
            self.turn = 'B'
        else:
            self.turn = 'W'
        self.chosen_piece = None
        self.piece_coords = None
        for i in range(64):
            self.fields_attacked[i // 8][i % 8] = None


    def check_possible_moves(self, piece = None, coords = None, attack = False, next_attack = False):
        for i in range(64):
            self.possible_moves[i // 8][i % 8] = None
        if self.chosen_piece is None and piece is None:
            return
        if coords is None:
            coords = self.piece_coords
        enemy_pieces = []
        player_pieces = []
        if self.turn == 'W':
            enemy_pieces = self.black_pieces
            if next_attack:
                player_pieces = self.next_player_position
            else:
                player_pieces = self.white_pieces
        else:
            enemy_pieces = self.white_pieces
            if next_attack:
                player_pieces = self.next_player_position
            else:
                player_pieces = self.black_pieces
        if piece is None and self.chosen_piece is not None:
            piece = self.chosen_piece
        elif piece is not None:
            # print(piece, coords, attack)
            pass
        else:
            return

        match piece:
            case 'b' | 'r' | 'Q':
                if piece == 'b':
                    directions = [
                    (1, 1),  # x += 1, y += 1
                    (1, -1),
                    (-1, 1),
                    (-1, -1)
                    ]
                elif piece == 'r':
                    directions = [
                        (1, 0),  # x += 1, y += 0
                        (-1, 0),
                        (0, 1),
                        (0, -1)
                    ]
                elif piece == 'Q':
                    directions = [
                        (1, 0),  # x += 1, y += 0
                        (-1, 0),
                        (0, 1),
                        (0, -1),
                        (1, 1),  # x += 1, y += 1
                        (1, -1),
                        (-1, 1),
                        (-1, -1)
                    ]
                for dx, dy in directions:
                    x, y = coords
                    while (True):
                        x += dx
                        y += dy
                        if x < 0 or x > 7 or y < 0 or y > 7:
                            break
                        if player_pieces[y][x] is not None:
                            self.possible_moves[y][x] = None
                            if attack:
                                self.fields_attacked[y][x] = 1
                            if next_attack:
                                self.next_enemy_attack[y][x] = 1
                            break
                        elif enemy_pieces[y][x] is not None:
                            self.possible_moves[y][x] = 2
                            if attack:
                                self.fields_attacked[y][x] = 1
                            if next_attack:
                                self.next_enemy_attack[y][x] = 1
                            break
                        else:
                            self.possible_moves[y][x] = 1
                            if attack:
                                self.fields_attacked[y][x] = 1
                            if next_attack:
                                self.next_enemy_attack[y][x] = 1
            case 'k':
                directions = [
                    (1, -2),
                    (2, -1),
                    (2, 1),
                    (1, 2),
                    (-1, 2),
                    (-2, 1),
                    (-2, -1),
                    (-1, -2)
                ]
                for dx, dy in directions:
                    x, y = coords
                    x += dx
                    y += dy
                    if x < 0 or x > 7 or y < 0 or y > 7:
                        continue
                    if player_pieces[y][x] is not None:
                        self.possible_moves[y][x] = None
                        if attack:
                            self.fields_attacked[y][x] = 1
                        if next_attack:
                            self.next_enemy_attack[y][x] = 1
                    elif enemy_pieces[y][x] is not None:
                        self.possible_moves[y][x] = 2
                        if attack:
                            self.fields_attacked[y][x] = 1
                        if next_attack:
                            self.next_enemy_attack[y][x] = 1
                    else:
                        self.possible_moves[y][x] = 1
                        if attack:
                            self.fields_attacked[y][x] = 1
                        if next_attack:
                            self.next_enemy_attack[y][x] = 1
            case 'K':
                directions = [
                    (0, -1),
                    (1, -1),
                    (1, 0),
                    (1, 1),
                    (0, 1),
                    (-1, 1),
                    (-1, 0),
                    (-1, -1)
                ]

                for dx, dy in directions:
                    x, y = coords
                    x += dx
                    y += dy
                    if x < 0 or x > 7 or y < 0 or y > 7:
                        continue
                    if player_pieces[y][x] is not None:
                        self.possible_moves[y][x] = None
                        if attack:
                            self.fields_attacked[y][x] = 1
                        if next_attack:
                            self.next_enemy_attack[y][x] = 1
                    elif enemy_pieces[y][x] is not None:
                        self.possible_moves[y][x] = 2
                        if attack:
                            self.fields_attacked[y][x] = 1
                        if next_attack:
                            self.next_enemy_attack[y][x] = 1
                    else:
                        self.possible_moves[y][x] = 1
                        if attack:
                            self.fields_attacked[y][x] = 1
                        if next_attack:
                            self.next_enemy_attack[y][x] = 1

                if self.turn == 'W':
                    if self.white_short_castle == True:
                        wsc = True  #wsc - white short castle (helper variable)
                        if (self.white_pieces[7][5] is not None or self.white_pieces[7][6] is not None
                        or self.black_pieces[7][5] is not None or self.black_pieces[7][6] is not None):
                            wsc = False
                        for i in range(4, 7, 1):
                            if self.fields_attacked[7][i] == 1:
                                wsc = False
                                break
                        if wsc == True:
                            self.possible_moves[7][6] = 4
                    if self.white_long_castle == True:
                        wlc = True
                        if (self.white_pieces[7][3] is not None or self.white_pieces[7][2] is not None or self.white_pieces[7][1] is not None
                        or self.black_pieces[7][3] is not None or self.black_pieces[7][2] is not None or self.black_pieces[7][1] is not None):
                            wlc = False
                        for i in range(1, 5, 1):
                            if self.fields_attacked[7][i] == 1:
                                wlc = False
                                break
                        if wlc == True:
                            self.possible_moves[7][2] = 5
                else:
                    if self.black_short_castle == True:
                        bsc = True
                        if (self.white_pieces[0][5] is not None or self.white_pieces[0][6] is not None
                        or self.black_pieces[0][5] is not None or self.black_pieces[0][6] is not None):
                            bsc = False
                        for i in range(4, 7, 1):
                            if self.fields_attacked[0][i] == 1:
                                bsc = False
                                break
                        if bsc == True:
                            self.possible_moves[0][6] = 6
                    if self.black_long_castle == True:
                        blc = True
                        if (self.white_pieces[0][3] is not None or self.white_pieces[0][2] is not None or self.white_pieces[0][1] is not None
                        or self.black_pieces[0][3] is not None or self.black_pieces[0][2] is not None or self.black_pieces[0][1] is not None):
                            blc = False
                        for i in range(1, 5, 1):
                            if self.fields_attacked[0][i] == 1:
                                blc = False
                                break
                        if blc == True:
                            self.possible_moves[0][2] = 7
            case 'p':
                if self.turn == 'W':
                    directions = [
                        (0, -1),    #ruch o jeden
                        (0, -2),    #ruch o dwa
                        (-1, -1),   #bicie w lewo (w przelocie i bez)
                        (1, -1),    #bicie w prawo (w przelocie i bez)
                    ]
                    starting_pose_y = 6
                    passant_pose_y = 3
                else:
                    directions = [
                        (0, 1),  # ruch o jeden
                        (0, 2),  # ruch o dwa
                        (-1, 1),  # bicie w lewo (w przelocie i bez)
                        (1, 1),  # bicie w prawo (w przelocie i bez)
                    ]
                    starting_pose_y = 1
                    passant_pose_y = 4

                x, y = coords
                if player_pieces[y + directions[0][1]][x + directions[0][0]] is None and enemy_pieces[y + directions[0][1]][x + directions[0][0]] is None:
                    self.possible_moves[y + directions[0][1]][x + directions[0][0]] = 1
                if y == starting_pose_y:
                    if (player_pieces[y + directions[1][1]][x + directions[1][0]] is None and enemy_pieces[y+ directions[1][1]][x + directions[1][0]] is None
                            and player_pieces[y + directions[0][1]][x + directions[0][0]] is None and enemy_pieces[y + directions[0][1]][x + directions[0][0]] is None):
                        self.possible_moves[y + directions[1][1]][x + directions[1][0]] = 1
                if not x == 0:
                    if enemy_pieces[y + directions[2][1]][x + directions[2][0]] is not None:
                        self.possible_moves[y + directions[2][1]][x + directions[2][0]] = 2
                if not x == 7:
                    if enemy_pieces[y + directions[3][1]][x + directions[3][0]] is not None:
                        self.possible_moves[y + directions[3][1]][x + directions[3][0]] = 2
                # bicie w przelocie
                if y == passant_pose_y and self.pawn_double:
                    if x - 1 == self.pawn_double_position[0]:
                        self.possible_moves[y + directions[2][1]][x + directions[2][0]] = 3
                    if x + 1 == self.pawn_double_position[0]:
                        self.possible_moves[y + directions[3][1]][x + directions[3][0]] = 3


    def move(self, x: int, y: int):
        self.reset_next_pos()
        if self.chosen_piece is None:
            return
        if self.turn == 'W':
            player_pieces = self.white_pieces
            enemy_pieces = self.black_pieces
        else:
            player_pieces = self.black_pieces
            enemy_pieces = self.white_pieces
        if self.fields_attacked[y][x] == 1 and self.chosen_piece == 'K':
            return
        if self.possible_moves[y][x] == 1:

            self.next_player_position = copy.deepcopy(player_pieces)
            self.next_player_position[self.piece_coords[1]][self.piece_coords[0]] = None
            self.next_player_position[y][x] = self.chosen_piece
            self.check_attack(next_position=True)
            if self.check_king_attack_next_position():
                return

            player_pieces[self.piece_coords[1]][self.piece_coords[0]] = None
            player_pieces[y][x] = self.chosen_piece
            if self.chosen_piece == 'p' and abs(self.piece_coords[1] - y) == 2:
                self.pawn_double = True
                self.pawn_double_position = (x, y)
            else:
                self.pawn_double = False
                self.pawn_double_position = None
            self.update_castle()
            self.change_turn()
        if self.possible_moves[y][x] == 2:

            self.next_player_position = copy.deepcopy(player_pieces)
            self.next_player_position[self.piece_coords[1]][self.piece_coords[0]] = None
            self.next_player_position[y][x] = self.chosen_piece
            self.check_attack(next_position=True)
            if self.check_king_attack_next_position():
                return

            player_pieces[self.piece_coords[1]][self.piece_coords[0]] = None
            player_pieces[y][x] = self.chosen_piece
            enemy_pieces[y][x] = None
            self.update_castle()
            self.change_turn()
        if self.possible_moves[y][x] == 3:

            self.next_player_position = copy.deepcopy(player_pieces)
            self.next_player_position[self.piece_coords[1]][self.piece_coords[0]] = None
            self.next_player_position[y][x] = self.chosen_piece
            self.check_attack(next_position=True)
            if self.check_king_attack_next_position():
                return

            player_pieces[self.piece_coords[1]][self.piece_coords[0]] = None
            player_pieces[y][x] = self.chosen_piece
            enemy_pieces[self.pawn_double_position[1]][self.pawn_double_position[0]] = None
            self.change_turn()
        if self.possible_moves[y][x] == 4:
            player_pieces[self.piece_coords[1]][self.piece_coords[0]] = None
            player_pieces[7][7] = None
            player_pieces[7][6] = 'K'
            player_pieces[7][5] = 'r'
            self.white_short_castle = False
            self.change_turn()
        if self.possible_moves[y][x] == 5:
            player_pieces[self.piece_coords[1]][self.piece_coords[0]] = None
            player_pieces[7][0] = None
            player_pieces[7][2] = 'K'
            player_pieces[7][3] = 'r'
            self.white_long_castle = False
            self.change_turn()
        if self.possible_moves[y][x] == 6:
            player_pieces[self.piece_coords[1]][self.piece_coords[0]] = None
            player_pieces[0][7] = None
            player_pieces[0][6] = 'K'
            player_pieces[0][5] = 'r'
            self.black_short_castle = False
            self.change_turn()
        if self.possible_moves[y][x] == 7:
            player_pieces[self.piece_coords[1]][self.piece_coords[0]] = None
            player_pieces[0][0] = None
            player_pieces[0][2] = 'K'
            player_pieces[0][3] = 'r'
            self.black_long_castle = False
            self.change_turn()


    def update_castle(self):
        if self.turn == 'W':
            if self.chosen_piece == 'K':
                self.white_short_castle = False
                self.white_long_castle = False
            if self.chosen_piece == 'r':
                # short castle
                if self.piece_coords == (7, 7):
                    self.white_short_castle = False
                if self.piece_coords == (0, 7):
                    self.white_long_castle = False
        else:
            if self.chosen_piece == 'K':
                self.black_short_castle = False
                self.black_long_castle = False
            if self.chosen_piece == 'r':
                # short castle
                if self.piece_coords == (7, 0):
                    self.black_short_castle = False
                if self.piece_coords == (0, 0):
                    self.black_long_castle = False


    def select_piece(self, x: int, y: int):
        self.chosen_piece = None
        self.piece_coords = None
        if self.white_pieces[y][x] is not None and self.turn == 'W':
            self.chosen_piece = self.white_pieces[y][x]
        elif self.black_pieces[y][x] is not None and self.turn == 'B':
            self.chosen_piece = self.black_pieces[y][x]
        if self.chosen_piece is None:
            return
        self.piece_coords = (x, y)


    def draw_selection(self):
        if self.piece_coords is None:
            return
        pygame.draw.rect(self.surface,
                         (0, 255, 0),
                         pygame.Rect(self.piece_coords[0] * 128,
                                     self.piece_coords[1] * 128, 128, 128),
                         width=3)


    def draw_possible_moves(self):
        for y, row in enumerate(self.possible_moves):
            for x, col in enumerate(row):
                if self.possible_moves[y][x] is not None:
                    pygame.draw.circle(self.surface, (0, 255, 100), (x * 128 + 64, y * 128 + 64), 10)


    def check_attack(self, next_position = False):
        if self.turn == 'W':
            if next_position:
                player_pieces = self.next_player_position
            else:
                player_pieces = self.white_pieces
            enemy_pieces = self.black_pieces

            directions = [
                (-1, 1),  # bicie w lewo (w przelocie i bez)
                (1, 1)  # bicie w prawo (w przelocie i bez)
            ]
        else:
            if next_position:
                player_pieces = self.next_player_position
            else:
                player_pieces = self.black_pieces
            enemy_pieces = self.white_pieces
            directions = [
                (-1, -1),   # bicie w lewo (w przelocie i bez)
                (1, -1)     # bicie w prawo (w przelocie i bez)
            ]
        for y, row in enumerate(enemy_pieces):
            for x, piece in enumerate(row):
                # print(x, y, piece)
                if piece is not None and piece != 'p':
                    if next_position:
                        self.check_possible_moves(piece=piece, coords= (x, y), attack = False, next_attack = True)
                    else:
                        self.check_possible_moves(piece = piece, coords = (x, y), attack = True)
                if piece == 'p':
                    if not x == 0:
                        if next_position:
                            self.next_enemy_attack[y + directions[0][1]][x + directions[0][0]] = 1
                        else:
                            self.fields_attacked[y + directions[0][1]][x + directions[0][0]] = 1
                    if not x == 7:
                        if next_position:
                            self.next_enemy_attack[y + directions[0][1]][x + directions[0][0]] = 1
                        else:
                            self.fields_attacked[y + directions[1][1]][x + directions[1][0]] = 1


    def draw_attack_fields(self):
        for y, row in enumerate(self.fields_attacked):
            for x, col in enumerate(row):
                if self.fields_attacked[y][x] == 1:
                    pygame.draw.circle(self.surface, (255, 0, 0), (x * 128 + 64, y * 128 + 64), 10)


    def check_king_attack_next_position(self) -> bool:
        """
        Method checks if player's king is under attack in next position. If yes returns True.
        """
        for y, row in enumerate(self.next_player_position):
            for x, piece in enumerate(row):
                if (self.next_player_position[y][x] == 'K'
                    and self.next_enemy_attack[y][x] == 1):
                    return True
        return False


    def reset_next_pos(self):
        for i in range(64):
            self.next_enemy_attack[i // 8][i % 8] = None
            self.next_player_position[i // 8][i % 8] = None


    def draw_chessboard(self):
        for i in range(64):
            x = (i * 128) % 1024
            y = (i // 8) * 128
            if (y // 128) % 2 == 0:
                if i % 2 == 0:
                    self.surface.blit(self.white, (x, y))
                else:
                    self.surface.blit(self.black, (x, y))
            else:
                if i % 2 == 0:
                    self.surface.blit(self.black, (x, y))
                else:
                    self.surface.blit(self.white, (x, y))