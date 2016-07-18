import pygame
from pygame.locals import *
import time
from pieces.Queen import Queen

from ChessBoard import ChessBoard


class Game:
    def __init__(self):
        pygame.init()
        self.game_display = pygame.display.set_mode((1000, 650))
        pygame.display.set_caption('Chess')

        self.settings = {'board_image': 'images/orange_board.png'}
        self.board_image = pygame.image.load(self.settings['board_image'])

        self.clock = pygame.time.Clock()
        self.chess_board = ChessBoard()

        self.curr_selected_piece = None
        self.curr_poss_moves = []
        self.all_poss_moves = self.get_all_poss_moves()

        self.play_game()

    def play_game(self):

        while True:

            # Draw whole window (and draw board)
            self.draw_window()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()

                if event.type == pygame.MOUSEBUTTONUP:
                    # Get user click
                    self.get_user_click()

            # pygame.display.flip()
            self.clock.tick(60)

    def draw_window(self):
        """Draws everything in the window"""
        self.game_display.fill(white)
        # Draw side menus
        # Draw bottom menu
        # Draw board
        self.draw_board()
        pygame.display.update()

    def draw_board(self):
        """Draw chess board and all pieces on the board"""
        # Draw chess board
        self.game_display.blit(self.board_image, (200, 0))

        # Draw pieces on board
        for piece in self.chess_board.get_all_pieces():
            image_position = piece.position
            image_position = 200 + image_position[0] * 75, (7 - image_position[1]) * 75
            piece_image = pygame.image.load(piece.image)
            self.game_display.blit(piece_image, image_position)

        # Determine if piece is currently selected
        # If yes:
        if self.curr_selected_piece:
            # Highlight that piece
            box_x, box_y = self.convert_space_to_coordinates(self.curr_selected_piece.position)
            pygame.draw.rect(self.game_display, blue, Rect((box_x, box_y), (75, 75)), 5)
            # Display possible moves for that piece
            for move in self.curr_poss_moves:
                box1_x, box1_y = self.convert_space_to_coordinates(move)
                pygame.draw.rect(self.game_display, red, Rect((box1_x, box1_y), (75, 75)), 5)

    def get_user_click(self):
        """Analyze the position clicked by the user."""
        x, y = pygame.mouse.get_pos()
        # Determine if click is:
        # On bottom menu
        if y > 600:
            pass
        # On left side menu
        elif x < 200:
            pass
        # On right side menu
        elif x > 800:
            pass
        # If on board:
        else:
            # Convert coordinates into space
            selected_space = self.convert_coordinates_to_space(x, y)
            # If piece is not already selected:
            if not self.curr_selected_piece:

                # Validate and set curr_selected_piece to this piece
                if self.is_piece_of_curr_player(selected_space):
                    self.new_piece_selected(selected_space)

            # Else if piece already selected:
            else:
                # Determine if selected space is in possible moves

                # If space is current selected space
                if selected_space == self.curr_selected_piece.position:
                    self.deselect_piece()

                # Else if space in possible moves:
                elif selected_space in self.curr_poss_moves:
                    #### Check if piece is a king!!! ###
                    # Check if selected space is king and in poss_castle_move
                    if self.curr_selected_piece.name == 'King' and selected_space in self.chess_board.get_castle_moves_for_curr_player():
                            # Castle that king
                            self.chess_board.castle_king(self.curr_selected_piece, selected_space)

                    else:
                        # Move selected piece to this spot
                        self.move_piece(self.curr_selected_piece, selected_space)
                        if self.curr_selected_piece.name == 'Pawn' and selected_space[1] == 0 or selected_space[1] == 7:
                            self.chess_board.board[selected_space[0]][selected_space[1]] = None
                            self.chess_board.board[selected_space[0]][selected_space[1]] = Queen(self.chess_board.curr_player, selected_space)

                    # Deselect current piece and remove poss moves
                    self.deselect_piece()
                    # Change current player
                    self.change_curr_player()

                    # Check for checkmate and get new list of all possible moves
                    self.all_poss_moves = self.get_all_poss_moves()
                    checkmate = True
                    for piece_pos in self.all_poss_moves:
                        if len(self.all_poss_moves[piece_pos]) != 0:
                            checkmate = False
                    if checkmate:
                        self.draw_window()
                        self.message_display('Checkmate!', (500, 300))
                        winner = 'White' if self.chess_board.curr_player == 'b' else 'Black'
                        self.message_display('%s wins!' % winner, (500, 400))
                        pygame.display.update()
                        time.sleep(2)
                        quit()

                # Else if another piece of curr player:
                elif selected_space in [piece.position for piece in self.chess_board.get_curr_player_pieces()]:
                    # Make that piece current selected piece
                    self.new_piece_selected(selected_space)

                # Else (random non-selectable space):
                else:
                    # Deselect current move
                    self.deselect_piece()

    def convert_coordinates_to_space(self, x, y):
        """Converts (x, y) coordinates to corresponding space on board"""
        # NOTE: Board is drawn upside down, so y axis is flipped
        return (x - 200) // 75, 7 - y // 75

    def convert_space_to_coordinates(self, position):
        """Returns the top left corner coordinate corresponding to given chess spot"""
        return position[0] * 75 + 200, (7 - position[1]) * 75

    def is_piece_of_curr_player(self, space):
        """Returns if space holds a piece of current player"""
        for piece in self.chess_board.get_curr_player_pieces():
            if space == piece.position:
                return True

    def get_all_poss_moves(self):
        """Returns dictionary of all possible moves available. NOTE: will return empty list if checkmate"""
        # Creates dictionary of piece position to possible moves
        moves = {}
        pieces = self.chess_board.get_curr_player_pieces()
        for piece in pieces:
            p_moves = self.chess_board.get_poss_moves_for(piece)
            moves[piece.position] = self.chess_board.is_curr_player_in_check(piece, p_moves)
        return moves

    def get_curr_poss_moves(self):
        """Returns possible moves corresponding to cuurently selected piece"""
        return self.all_poss_moves[self.curr_selected_piece.position]

    def move_piece(self, piece, new_position):
        """Moves piece to new position"""
        # NOTE: This just moves piece, does not check if move is valid
        self.chess_board.move_piece(piece, new_position)

    def change_curr_player(self):
        """Change current player between 'w' and 'b'"""
        self.chess_board.curr_player = 'w' if self.chess_board.curr_player == 'b' else 'b'

    def new_piece_selected(self, new_space):
        """Sets new space to curr_selected_piece and gets new moves for that piece"""
        self.curr_selected_piece = self.chess_board.get_piece_at(new_space)
        self.curr_poss_moves = self.get_curr_poss_moves()

    def deselect_piece(self):
        """Deselects current piece"""
        self.curr_selected_piece = None
        self.curr_poss_moves = None

    def message_display(self, text, point, fontsize=90):
        """Displays message in window"""
        large_text = pygame.font.Font('freesansbold.ttf', fontsize)
        text_surface = large_text.render(text, True, black)
        text_rect = text_surface.get_rect()
        text_rect.center = (point)
        self.game_display.blit(text_surface, text_rect)

if __name__ == '__main__':

    white = (255,255,255)
    blue = (34, 0, 255)
    red = (209, 9, 9)
    black = (0, 0, 0)
    Game()