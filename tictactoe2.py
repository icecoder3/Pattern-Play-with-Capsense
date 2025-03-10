import numpy as np
from read_coordinates import read_coordinates, get_serial_port
from new import identify_pattern  # Import function from new.py

# Tic Tac Toe board (1 to 9 indexing)
board = [" " for _ in range(9)]

def print_board():
    """Prints the current Tic Tac Toe board."""
    print("\n")
    for i in range(0, 9, 3):
        print(f" {board[i]} | {board[i+1]} | {board[i+2]} ")
        if i < 6:
            print("---+---+---")
    print("\n")

def check_winner():
    """Check if there's a winner in the game (1 to 9 positions)."""
    win_positions = [
        [1, 2, 3], [4, 5, 6], [7, 8, 9],  # Rows
        [1, 4, 7], [2, 5, 8], [3, 6, 9],  # Columns
        [1, 5, 9], [3, 5, 7]              # Diagonals
    ]

    for line in win_positions:
        a, b, c = line
        if board[a - 1] == board[b - 1] == board[c - 1] and board[a - 1] != " ":
            return board[a - 1]  # Return the winner ("O" or "X")

    return None  # No winner yet

def get_symbol_choice(serial_port):
    """Asks the user to draw 'X' or 'O' to choose their symbol."""
    while True:
        print("Draw 'X' or 'O' to choose your symbol:")
        coordinates = read_coordinates(serial_port=serial_port, timeout=5)

        if len(coordinates) == 0:
            print("Error: No coordinates received. Check if the sensor is connected properly.")
            continue

        new_shape = np.array(coordinates)
        symbol = identify_pattern(new_shape)  # Detect whether the user drew 'X' or 'O'

        if symbol not in ["X", "O"]:
            print("Invalid choice. Please draw 'X' or 'O' to continue.")
            continue

        print(f"You have chosen: {symbol}")
        return symbol

def get_valid_move(player, serial_port):
    """Ensures that the player provides a valid move by drawing numbers 1-9."""
    while True:
        print(f"Player {player}, draw a number (1-9) to place your move:")
        coordinates = read_coordinates(serial_port=serial_port, timeout=5)

        if len(coordinates) == 0:
            print("Error: No coordinates received. Check if the sensor is connected properly.")
            continue

        new_shape = np.array(coordinates)
        digit = identify_pattern(new_shape)  # Call function from new.py

        if digit is None:
            print("Invalid input. Please draw a valid number (1-9).")
            continue

        try:
            digit = int(digit)  # Ensure it's converted to an integer
        except ValueError:
            print("Invalid input. Please draw a valid number (1-9).")
            continue

        if not (1 <= digit <= 9):
            print("Invalid input. Please draw a valid number (1-9).")
            continue

        if board[digit - 1] != " ":
            print("That position is already taken. Try another.")
            continue

        return digit

if __name__ == "__main__":
    serial_port = get_serial_port()
    print("Welcome to Tic Tac Toe! First, choose your symbol.")

    player_symbol = get_symbol_choice(serial_port)  # User selects "X" or "O"
    opponent_symbol = "X" if player_symbol == "O" else "O"

    print(f"Starting Tic Tac Toe... You are {player_symbol}. Draw numbers (1-9) to place your move.")
    print_board()

    current_player = player_symbol

    while True:
        move = get_valid_move(current_player, serial_port)
        board[move - 1] = current_player  
        print_board()

        winner = check_winner()
        if winner:
            print(f"Player {winner} wins!")
            break

        if " " not in board:
            print("It's a draw!")
            break

        # Switch players
        current_player = "X" if current_player == "O" else "O"
