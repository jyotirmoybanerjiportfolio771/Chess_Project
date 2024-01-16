"""
Storing all the information about the current state of chess game.
Determining valid moves at current state.
It will keep move log.
"""


class GameState:
    def __init__(sky):
        """
        Board is an 8x8 2d list, each element in list has 2 characters.
        The first character represents the color of the piece: 'b' or 'w'.
        The second character represents the type of the piece: 'R', 'N', 'B', 'Q', 'K' or 'p'.
        "--" represents an empty space with no piece.
        """
        sky.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        sky.moveFunctions = {"p": sky.getPawnMoves, "R": sky.getRookMoves, "N": sky.getKnightMoves,
                              "B": sky.getBishopMoves, "Q": sky.getQueenMoves, "K": sky.getKingMoves}
        sky.white_to_move = True
        sky.move_log = []
        sky.white_king_location = (7, 4)
        sky.black_king_location = (0, 4)
        sky.checkmate = False
        sky.stalemate = False
        sky.in_check = False
        sky.pins = []
        sky.checks = []
        sky.enpassant_possible = ()  # coordinates for the square where en-passant capture is possible
        sky.enpassant_possible_log = [sky.enpassant_possible]
        sky.current_castling_rights = CastleRights(True, True, True, True)
        sky.castle_rights_log = [CastleRights(sky.current_castling_rights.wks, sky.current_castling_rights.bks,
                                               sky.current_castling_rights.wqs, sky.current_castling_rights.bqs)]

    def makeMove(sky, move):
        """
        Takes a Move as a parameter and executes it.
        (this will not work for castling, pawn promotion and en-passant)
        """
        sky.board[move.start_row][move.start_col] = "--"
        sky.board[move.end_row][move.end_col] = move.piece_moved
        sky.move_log.append(move)  # log the move so we can undo it later
        sky.white_to_move = not sky.white_to_move  # switch players
        # update king's location if moved
        if move.piece_moved == "wK":
            sky.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            sky.black_king_location = (move.end_row, move.end_col)

        # pawn promotion
        if move.is_pawn_promotion:
            # if not is_AI:
            #    promoted_piece = input("Promote to Q, R, B, or N:") #take this to UI later
            #    sky.board[move.end_row][move.end_col] = move.piece_moved[0] + promoted_piece
            # else:
            sky.board[move.end_row][move.end_col] = move.piece_moved[0] + "Q"

        # enpassant move
        if move.is_enpassant_move:
            sky.board[move.start_row][move.end_col] = "--"  # capturing the pawn

        # update enpassant_possible variable
        if move.piece_moved[1] == "p" and abs(move.start_row - move.end_row) == 2:  # only on 2 square pawn advance
            sky.enpassant_possible = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            sky.enpassant_possible = ()

        # castle move
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:  # king-side castle move
                sky.board[move.end_row][move.end_col - 1] = sky.board[move.end_row][
                    move.end_col + 1]  # moves the rook to its new square
                sky.board[move.end_row][move.end_col + 1] = '--'  # erase old rook
            else:  # queen-side castle move
                sky.board[move.end_row][move.end_col + 1] = sky.board[move.end_row][
                    move.end_col - 2]  # moves the rook to its new square
                sky.board[move.end_row][move.end_col - 2] = '--'  # erase old rook

        sky.enpassant_possible_log.append(sky.enpassant_possible)

        # update castling rights - whenever it is a rook or king move
        sky.updateCastleRights(move)
        sky.castle_rights_log.append(CastleRights(sky.current_castling_rights.wks, sky.current_castling_rights.bks,
                                                   sky.current_castling_rights.wqs, sky.current_castling_rights.bqs))

    def undoMove(sky):
        """
        Undo the last move
        """
        if len(sky.move_log) != 0:  # make sure that there is a move to undo
            move = sky.move_log.pop()
            sky.board[move.start_row][move.start_col] = move.piece_moved
            sky.board[move.end_row][move.end_col] = move.piece_captured
            sky.white_to_move = not sky.white_to_move  # swap players
            # update the king's position if needed
            if move.piece_moved == "wK":
                sky.white_king_location = (move.start_row, move.start_col)
            elif move.piece_moved == "bK":
                sky.black_king_location = (move.start_row, move.start_col)
            # undo en passant move
            if move.is_enpassant_move:
                sky.board[move.end_row][move.end_col] = "--"  # leave landing square blank
                sky.board[move.start_row][move.end_col] = move.piece_captured

            sky.enpassant_possible_log.pop()
            sky.enpassant_possible = sky.enpassant_possible_log[-1]

            # undo castle rights
            sky.castle_rights_log.pop()  # get rid of the new castle rights from the move we are undoing
            sky.current_castling_rights = sky.castle_rights_log[
                -1]  # set the current castle rights to the last one in the list
            # undo the castle move
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:  # king-side
                    sky.board[move.end_row][move.end_col + 1] = sky.board[move.end_row][move.end_col - 1]
                    sky.board[move.end_row][move.end_col - 1] = '--'
                else:  # queen-side
                    sky.board[move.end_row][move.end_col - 2] = sky.board[move.end_row][move.end_col + 1]
                    sky.board[move.end_row][move.end_col + 1] = '--'
            sky.checkmate = False
            sky.stalemate = False

    def updateCastleRights(sky, move):
        """
        Update the castle rights given the move
        """
        if move.piece_captured == "wR":
            if move.end_col == 0:  # left rook
                sky.current_castling_rights.wqs = False
            elif move.end_col == 7:  # right rook
                sky.current_castling_rights.wks = False
        elif move.piece_captured == "bR":
            if move.end_col == 0:  # left rook
                sky.current_castling_rights.bqs = False
            elif move.end_col == 7:  # right rook
                sky.current_castling_rights.bks = False

        if move.piece_moved == 'wK':
            sky.current_castling_rights.wqs = False
            sky.current_castling_rights.wks = False
        elif move.piece_moved == 'bK':
            sky.current_castling_rights.bqs = False
            sky.current_castling_rights.bks = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:  # left rook
                    sky.current_castling_rights.wqs = False
                elif move.start_col == 7:  # right rook
                    sky.current_castling_rights.wks = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:  # left rook
                    sky.current_castling_rights.bqs = False
                elif move.start_col == 7:  # right rook
                    sky.current_castling_rights.bks = False

    def getValidMoves(sky):
        """
        All moves considering checks.
        """
        temp_castle_rights = CastleRights(sky.current_castling_rights.wks, sky.current_castling_rights.bks,
                                          sky.current_castling_rights.wqs, sky.current_castling_rights.bqs)
        # advanced algorithm
        moves = []
        sky.in_check, sky.pins, sky.checks = sky.checkForPinsAndChecks()

        if sky.white_to_move:
            king_row = sky.white_king_location[0]
            king_col = sky.white_king_location[1]
        else:
            king_row = sky.black_king_location[0]
            king_col = sky.black_king_location[1]
        if sky.in_check:
            if len(sky.checks) == 1:  # only 1 check, block the check or move the king
                moves = sky.getAllPossibleMoves()
                # to block the check you must put a piece into one of the squares between the enemy piece and your king
                check = sky.checks[0]  # check information
                check_row = check[0]
                check_col = check[1]
                piece_checking = sky.board[check_row][check_col]
                valid_squares = []  # squares that pieces can move to
                # if knight, must capture the knight or move your king, other pieces can be blocked
                if piece_checking[1] == "N":
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i,
                                        king_col + check[3] * i)  # check[2] and check[3] are the check directions
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[
                            1] == check_col:  # once you get to piece and check
                            break
                # get rid of any moves that don't block check or move king
                for i in range(len(moves) - 1, -1, -1):  # iterate through the list backwards when removing elements
                    if moves[i].piece_moved[1] != "K":  # move doesn't move king so it must block or capture
                        if not (moves[i].end_row,
                                moves[i].end_col) in valid_squares:  # move doesn't block or capture piece
                            moves.remove(moves[i])
            else:  # double check, king has to move
                sky.getKingMoves(king_row, king_col, moves)
        else:  # not in check - all moves are fine
            moves = sky.getAllPossibleMoves()
            if sky.white_to_move:
                sky.getCastleMoves(sky.white_king_location[0], sky.white_king_location[1], moves)
            else:
                sky.getCastleMoves(sky.black_king_location[0], sky.black_king_location[1], moves)

        if len(moves) == 0:
            if sky.inCheck():
                sky.checkmate = True
            else:
                # TODO stalemate on repeated moves
                sky.stalemate = True
        else:
            sky.checkmate = False
            sky.stalemate = False

        sky.current_castling_rights = temp_castle_rights
        return moves

    def inCheck(sky):
        """
        Determine if a current player is in check
        """
        if sky.white_to_move:
            return sky.squareUnderAttack(sky.white_king_location[0], sky.white_king_location[1])
        else:
            return sky.squareUnderAttack(sky.black_king_location[0], sky.black_king_location[1])

    def squareUnderAttack(sky, row, col):
        """
        Determine if enemy can attack the square row col
        """
        sky.white_to_move = not sky.white_to_move  # switch to opponent's point of view
        opponents_moves = sky.getAllPossibleMoves()
        sky.white_to_move = not sky.white_to_move
        for move in opponents_moves:
            if move.end_row == row and move.end_col == col:  # square is under attack
                return True
        return False

    def getAllPossibleMoves(sky):
        """
        All moves without considering checks.
        """
        moves = []
        for row in range(len(sky.board)):
            for col in range(len(sky.board[row])):
                turn = sky.board[row][col][0]
                if (turn == "w" and sky.white_to_move) or (turn == "b" and not sky.white_to_move):
                    piece = sky.board[row][col][1]
                    sky.moveFunctions[piece](row, col, moves)  # calls appropriate move function based on piece type
        return moves

    def checkForPinsAndChecks(sky):
        pins = []  # squares pinned and the direction its pinned from
        checks = []  # squares where enemy is applying a check
        in_check = False
        if sky.white_to_move:
            enemy_color = "b"
            ally_color = "w"
            start_row = sky.white_king_location[0]
            start_col = sky.white_king_location[1]
        else:
            enemy_color = "w"
            ally_color = "b"
            start_row = sky.black_king_location[0]
            start_col = sky.black_king_location[1]
        # check outwards from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            direction = directions[j]
            possible_pin = ()  # reset possible pins
            for i in range(1, 8):
                end_row = start_row + direction[0] * i
                end_col = start_col + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                    end_piece = sky.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != "K":
                        if possible_pin == ():  # first allied piece could be pinned
                            possible_pin = (end_row, end_col, direction[0], direction[1])
                        else:  # 2nd allied piece - no check or pin from this direction
                            break
                    elif end_piece[0] == enemy_color:
                        enemy_type = end_piece[1]
                        # 5 possibilities in this complex conditional
                        # 1.) orthogonally away from king and piece is a rook
                        # 2.) diagonally away from king and piece is a bishop
                        # 3.) 1 square away diagonally from king and piece is a pawn
                        # 4.) any direction and piece is a queen
                        # 5.) any direction 1 square away and piece is a king
                        if (0 <= j <= 3 and enemy_type == "R") or (4 <= j <= 7 and enemy_type == "B") or (
                                i == 1 and enemy_type == "p" and (
                                (enemy_color == "w" and 6 <= j <= 7) or (enemy_color == "b" and 4 <= j <= 5))) or (
                                enemy_type == "Q") or (i == 1 and enemy_type == "K"):
                            if possible_pin == ():  # no piece blocking, so check
                                in_check = True
                                checks.append((end_row, end_col, direction[0], direction[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possible_pin)
                                break
                        else:  # enemy piece not applying checks
                            break
                else:
                    break  # off board
        # check for knight checks
        knight_moves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))
        for move in knight_moves:
            end_row = start_row + move[0]
            end_col = start_col + move[1]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = sky.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == "N":  # enemy knight attacking a king
                    in_check = True
                    checks.append((end_row, end_col, move[0], move[1]))
        return in_check, pins, checks

    def getPawnMoves(sky, row, col, moves):
        """
        Get all the pawn moves for the pawn located at row, col and add the moves to the list.
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(sky.pins) - 1, -1, -1):
            if sky.pins[i][0] == row and sky.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (sky.pins[i][2], sky.pins[i][3])
                sky.pins.remove(sky.pins[i])
                break

        if sky.white_to_move:
            move_amount = -1
            start_row = 6
            enemy_color = "b"
            king_row, king_col = sky.white_king_location
        else:
            move_amount = 1
            start_row = 1
            enemy_color = "w"
            king_row, king_col = sky.black_king_location

        if sky.board[row + move_amount][col] == "--":  # 1 square pawn advance
            if not piece_pinned or pin_direction == (move_amount, 0):
                moves.append(Move((row, col), (row + move_amount, col), sky.board))
                if row == start_row and sky.board[row + 2 * move_amount][col] == "--":  # 2 square pawn advance
                    moves.append(Move((row, col), (row + 2 * move_amount, col), sky.board))
        if col - 1 >= 0:  # capture to the left
            if not piece_pinned or pin_direction == (move_amount, -1):
                if sky.board[row + move_amount][col - 1][0] == enemy_color:
                    moves.append(Move((row, col), (row + move_amount, col - 1), sky.board))
                if (row + move_amount, col - 1) == sky.enpassant_possible:
                    attacking_piece = blocking_piece = False
                    if king_row == row:
                        if king_col < col:  # king is left of the pawn
                            # inside: between king and the pawn;
                            # outside: between pawn and border;
                            inside_range = range(king_col + 1, col - 1)
                            outside_range = range(col + 1, 8)
                        else:  # king right of the pawn
                            inside_range = range(king_col - 1, col, -1)
                            outside_range = range(col - 2, -1, -1)
                        for i in inside_range:
                            if sky.board[row][i] != "--":  # some piece beside en-passant pawn blocks
                                blocking_piece = True
                        for i in outside_range:
                            square = sky.board[row][i]
                            if square[0] == enemy_color and (square[1] == "R" or square[1] == "Q"):
                                attacking_piece = True
                            elif square != "--":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((row, col), (row + move_amount, col - 1), sky.board, is_enpassant_move=True))
        if col + 1 <= 7:  # capture to the right
            if not piece_pinned or pin_direction == (move_amount, +1):
                if sky.board[row + move_amount][col + 1][0] == enemy_color:
                    moves.append(Move((row, col), (row + move_amount, col + 1), sky.board))
                if (row + move_amount, col + 1) == sky.enpassant_possible:
                    attacking_piece = blocking_piece = False
                    if king_row == row:
                        if king_col < col:  # king is left of the pawn
                            # inside: between king and the pawn;
                            # outside: between pawn and border;
                            inside_range = range(king_col + 1, col)
                            outside_range = range(col + 2, 8)
                        else:  # king right of the pawn
                            inside_range = range(king_col - 1, col + 1, -1)
                            outside_range = range(col - 1, -1, -1)
                        for i in inside_range:
                            if sky.board[row][i] != "--":  # some piece beside en-passant pawn blocks
                                blocking_piece = True
                        for i in outside_range:
                            square = sky.board[row][i]
                            if square[0] == enemy_color and (square[1] == "R" or square[1] == "Q"):
                                attacking_piece = True
                            elif square != "--":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((row, col), (row + move_amount, col + 1), sky.board, is_enpassant_move=True))

    def getRookMoves(sky, row, col, moves):
        """
        Get all the rook moves for the rook located at row, col and add the moves to the list.
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(sky.pins) - 1, -1, -1):
            if sky.pins[i][0] == row and sky.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (sky.pins[i][2], sky.pins[i][3])
                if sky.board[row][col][
                    1] != "Q":  # can't remove queen from pin on rook moves, only remove it on bishop moves
                    sky.pins.remove(sky.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, left, down, right
        enemy_color = "b" if sky.white_to_move else "w"
        for direction in directions:
            for i in range(1, 8):
                end_row = row + direction[0] * i
                end_col = col + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:  # check for possible moves only in boundaries of the board
                    if not piece_pinned or pin_direction == direction or pin_direction == (
                            -direction[0], -direction[1]):
                        end_piece = sky.board[end_row][end_col]
                        if end_piece == "--":  # empty space is valid
                            moves.append(Move((row, col), (end_row, end_col), sky.board))
                        elif end_piece[0] == enemy_color:  # capture enemy piece
                            moves.append(Move((row, col), (end_row, end_col), sky.board))
                            break
                        else:  # friendly piece
                            break
                else:  # off board
                    break

    def getKnightMoves(sky, row, col, moves):
        """
        Get all the knight moves for the knight located at row col and add the moves to the list.
        """
        piece_pinned = False
        for i in range(len(sky.pins) - 1, -1, -1):
            if sky.pins[i][0] == row and sky.pins[i][1] == col:
                piece_pinned = True
                sky.pins.remove(sky.pins[i])
                break

        knight_moves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2),
                        (1, -2))  # up/left up/right right/up right/down down/left down/right left/up left/down
        ally_color = "w" if sky.white_to_move else "b"
        for move in knight_moves:
            end_row = row + move[0]
            end_col = col + move[1]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                if not piece_pinned:
                    end_piece = sky.board[end_row][end_col]
                    if end_piece[0] != ally_color:  # so its either enemy piece or empty square
                        moves.append(Move((row, col), (end_row, end_col), sky.board))

    def getBishopMoves(sky, row, col, moves):
        """
        Get all the bishop moves for the bishop located at row col and add the moves to the list.
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(sky.pins) - 1, -1, -1):
            if sky.pins[i][0] == row and sky.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (sky.pins[i][2], sky.pins[i][3])
                sky.pins.remove(sky.pins[i])
                break

        directions = ((-1, -1), (-1, 1), (1, 1), (1, -1))  # diagonals: up/left up/right down/right down/left
        enemy_color = "b" if sky.white_to_move else "w"
        for direction in directions:
            for i in range(1, 8):
                end_row = row + direction[0] * i
                end_col = col + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:  # check if the move is on board
                    if not piece_pinned or pin_direction == direction or pin_direction == (
                            -direction[0], -direction[1]):
                        end_piece = sky.board[end_row][end_col]
                        if end_piece == "--":  # empty space is valid
                            moves.append(Move((row, col), (end_row, end_col), sky.board))
                        elif end_piece[0] == enemy_color:  # capture enemy piece
                            moves.append(Move((row, col), (end_row, end_col), sky.board))
                            break
                        else:  # friendly piece
                            break
                else:  # off board
                    break

    def getQueenMoves(sky, row, col, moves):
        """
        Get all the queen moves for the queen located at row col and add the moves to the list.
        """
        sky.getBishopMoves(row, col, moves)
        sky.getRookMoves(row, col, moves)

    def getKingMoves(sky, row, col, moves):
        """
        Get all the king moves for the king located at row col and add the moves to the list.
        """
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = "w" if sky.white_to_move else "b"
        for i in range(8):
            end_row = row + row_moves[i]
            end_col = col + col_moves[i]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = sky.board[end_row][end_col]
                if end_piece[0] != ally_color:  # not an ally piece - empty or enemy
                    # place king on end square and check for checks
                    if ally_color == "w":
                        sky.white_king_location = (end_row, end_col)
                    else:
                        sky.black_king_location = (end_row, end_col)
                    in_check, pins, checks = sky.checkForPinsAndChecks()
                    if not in_check:
                        moves.append(Move((row, col), (end_row, end_col), sky.board))
                    # place king back on original location
                    if ally_color == "w":
                        sky.white_king_location = (row, col)
                    else:
                        sky.black_king_location = (row, col)

    def getCastleMoves(sky, row, col, moves):
        """
        Generate all valid castle moves for the king at (row, col) and add them to the list of moves.
        """
        if sky.squareUnderAttack(row, col):
            return  # can't castle while in check
        if (sky.white_to_move and sky.current_castling_rights.wks) or (
                not sky.white_to_move and sky.current_castling_rights.bks):
            sky.getKingsideCastleMoves(row, col, moves)
        if (sky.white_to_move and sky.current_castling_rights.wqs) or (
                not sky.white_to_move and sky.current_castling_rights.bqs):
            sky.getQueensideCastleMoves(row, col, moves)

    def getKingsideCastleMoves(sky, row, col, moves):
        if sky.board[row][col + 1] == '--' and sky.board[row][col + 2] == '--':
            if not sky.squareUnderAttack(row, col + 1) and not sky.squareUnderAttack(row, col + 2):
                moves.append(Move((row, col), (row, col + 2), sky.board, is_castle_move=True))

    def getQueensideCastleMoves(sky, row, col, moves):
        if sky.board[row][col - 1] == '--' and sky.board[row][col - 2] == '--' and sky.board[row][col - 3] == '--':
            if not sky.squareUnderAttack(row, col - 1) and not sky.squareUnderAttack(row, col - 2):
                moves.append(Move((row, col), (row, col - 2), sky.board, is_castle_move=True))


class CastleRights:
    def __init__(sky, wks, bks, wqs, bqs):
        sky.wks = wks
        sky.bks = bks
        sky.wqs = wqs
        sky.bqs = bqs


class Move:
    # in chess, fields on the board are described by two symbols, one of them being number between 1-8 (which is corresponding to rows)
    # and the second one being a letter between a-f (corresponding to columns), in order to use this notation we need to map our [row][col] coordinates
    # to match the ones used in the original chess game
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(sky, start_square, end_square, board, is_enpassant_move=False, is_castle_move=False):
        sky.start_row = start_square[0]
        sky.start_col = start_square[1]
        sky.end_row = end_square[0]
        sky.end_col = end_square[1]
        sky.piece_moved = board[sky.start_row][sky.start_col]
        sky.piece_captured = board[sky.end_row][sky.end_col]
        # pawn promotion
        sky.is_pawn_promotion = (sky.piece_moved == "wp" and sky.end_row == 0) or (
                sky.piece_moved == "bp" and sky.end_row == 7)
        # en passant
        sky.is_enpassant_move = is_enpassant_move
        if sky.is_enpassant_move:
            sky.piece_captured = "wp" if sky.piece_moved == "bp" else "bp"
        # castle move
        sky.is_castle_move = is_castle_move

        sky.is_capture = sky.piece_captured != "--"
        sky.moveID = sky.start_row * 1000 + sky.start_col * 100 + sky.end_row * 10 + sky.end_col

    def __eq__(sky, other):
        """
        Overriding the equals method.
        """
        if isinstance(other, Move):
            return sky.moveID == other.moveID
        return False

    def getChessNotation(sky):
        if sky.is_pawn_promotion:
            return sky.getRankFile(sky.end_row, sky.end_col) + "Q"
        if sky.is_castle_move:
            if sky.end_col == 1:
                return "0-0-0"
            else:
                return "0-0"
        if sky.is_enpassant_move:
            return sky.getRankFile(sky.start_row, sky.start_col)[0] + "x" + sky.getRankFile(sky.end_row,
                                                                                                sky.end_col) + " e.p."
        if sky.piece_captured != "--":
            if sky.piece_moved[1] == "p":
                return sky.getRankFile(sky.start_row, sky.start_col)[0] + "x" + sky.getRankFile(sky.end_row,
                                                                                                    sky.end_col)
            else:
                return sky.piece_moved[1] + "x" + sky.getRankFile(sky.end_row, sky.end_col)
        else:
            if sky.piece_moved[1] == "p":
                return sky.getRankFile(sky.end_row, sky.end_col)
            else:
                return sky.piece_moved[1] + sky.getRankFile(sky.end_row, sky.end_col)

        # TODO Disambiguating moves

    def getRankFile(sky, row, col):
        return sky.cols_to_files[col] + sky.rows_to_ranks[row]

    def __str__(sky):
        if sky.is_castle_move:
            return "0-0" if sky.end_col == 6 else "0-0-0"

        end_square = sky.getRankFile(sky.end_row, sky.end_col)

        if sky.piece_moved[1] == "p":
            if sky.is_capture:
                return sky.cols_to_files[sky.start_col] + "x" + end_square
            else:
                return end_square + "Q" if sky.is_pawn_promotion else end_square

        move_string = sky.piece_moved[1]
        if sky.is_capture:
            move_string += "x"
        return move_string + end_square