from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Users, Puzzle, Tile  # Import your models

class Sudoku:
    def __init__(self, name, grid):
        self.name = name
        self.grid = grid
        self.start_time = None  # Initialize start time
        self.elapsed_time = 0  # Initialize elapsed time in seconds

    def start_timer(self):
        self.start_time = timezone.now()

    def stop_timer(self):
        if self.start_time:
            elapsed = timezone.now() - self.start_time
            self.elapsed_time = elapsed.total_seconds()  # Store elapsed time in seconds
            self.start_time = None  # Reset start time after stopping

    def is_valid_move(self, row, col, num):
        # Same validation logic as before but applied to the grid property
        if num in [cell['value'] for cell in self.grid[row]]:
            return False
        for i in range(9):
            if self.grid[i][col]['value'] == num:
                return False

        box_row_start = (row // 3) * 3
        box_col_start = (col // 3) * 3
        for i in range(box_row_start, box_row_start + 3):
            for j in range(box_col_start, box_col_start + 3):
                if self.grid[i][j]['value'] == num:
                    return False
        return True

PREDEFINED_PUZZLES = {
    "easy": [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ],
    "medium": [
        [0, 3, 0, 0, 7, 0, 8, 0, 5],
        [0, 0, 5, 0, 0, 9, 0, 3, 0],
        [0, 8, 0, 0, 0, 0, 4, 0, 0],
        [0, 5, 0, 0, 0, 4, 0, 0, 0],
        [7, 0, 0, 6, 0, 2, 0, 0, 4],
        [0, 0, 0, 7, 0, 0, 0, 6, 0],
        [0, 0, 3, 0, 0, 0, 0, 9, 0],
        [0, 1, 0, 5, 0, 0, 2, 0, 0],
        [9, 0, 7, 0, 2, 0, 0, 5, 0]
    ],
    "hard": [
        [0, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 6, 0, 0, 0],
        [4, 0, 1, 0, 0, 0, 0, 7, 2],
        [5, 0, 0, 7, 0, 0, 6, 0, 0],
        [0, 0, 0, 0, 3, 0, 0, 0, 0],
        [0, 0, 2, 0, 0, 8, 0, 0, 1],
        [8, 4, 0, 0, 0, 0, 7, 0, 9],
        [0, 0, 0, 2, 0, 0, 0, 0, 0],
        [0, 9, 0, 0, 0, 0, 0, 0, 0]
    ]
}

def puzzle_selection(request):
    """View to display the predefined puzzles."""
    puzzles = Puzzle.objects.all()  # Get the puzzle names
    return render(request, 'solver/puzzle_selection.html', {'puzzles': puzzles})

def load_puzzle(request, puzzle_name):
    """Load the selected predefined puzzle as a Sudoku object."""
    try:
        puzzle_instance = Puzzle.objects.get(name=puzzle_name)  # Get puzzle by name
        puzzle_grid = puzzle_instance.grids  # Assuming grids is a JSON or list format
        
        # Create the Sudoku object from the fetched puzzle instance
        sudoku = Sudoku(name=puzzle_instance.name, grid=[
            [{'value': cell, 'locked': cell != 0} for cell in row] for row in puzzle_grid
        ])
        
        return render(request, 'solver/sudoku.html', {'sudoku': sudoku})
    except Puzzle.DoesNotExist:
        return redirect('puzzle_selection')


def sudoku_grid(request):
    # Retrieve the current user or create a default user for demo purposes
    user, _ = Users.objects.get_or_create(username='demo_user')

    # Initialize the Sudoku object
    sudoku = Sudoku(name='Custom Puzzle', grid=[[{'value': 0, 'locked': False} for _ in range(9)] for _ in range(9)])

    if 'custom_puzzle' in request.session:
        sudoku_data = request.session['custom_puzzle']
        sudoku = Sudoku(name=sudoku_data['name'], grid=sudoku_data['grid'])

    if request.method == 'POST':
        for row in range(9):
            for col in range(9):
                cell_name = f'cell_{row}_{col}'
                value = request.POST.get(cell_name)
                if value and value.isdigit() and 1 <= int(value) <= 9:
                    num = int(value)
                    if sudoku.is_valid_move(row, col, num):
                        if not sudoku.grid[row][col]['locked']:
                            sudoku.grid[row][col]['value'] = num
                    else:
                        messages.error(request, f'Invalid move at cell ({row + 1}, {col + 1}).')

        elapsed_time = request.POST.get('elapsed_time', 0)
        sudoku.elapsed_time = float(elapsed_time)

        if all(cell['value'] != 0 for row in sudoku.grid for cell in row):
            request.session['elapsed_time'] = sudoku.elapsed_time
            messages.success(request, f'Puzzle submitted successfully! Time taken: {sudoku.elapsed_time} seconds.')

            # Update the user's solved puzzle times
            user.solved_time = sudoku.elapsed_time
            user.save()

            return render(request, 'solver/sudoku.html', {'sudoku': sudoku, 'elapsed_time': sudoku.elapsed_time})

    elapsed_time = request.session.get('elapsed_time', 0)
    return render(request, 'solver/sudoku.html', {'sudoku': sudoku, 'elapsed_time': elapsed_time})

def board_creator(request):
    if request.method == 'POST':
        # Initialize a 9x9 grid with zeros
        custom_grid = [[0 for _ in range(9)] for _ in range(9)]
        for i in range(9):
            for j in range(9):
                cell_name = f'cell_{i}_{j}'
                value = request.POST.get(cell_name)
                if value and value.isdigit() and 1 <= int(value) <= 9:
                    custom_grid[i][j] = int(value)  # Set value in the grid

        # Create a Sudoku instance (if needed)
        sudoku_instance = Sudoku(name=request.POST.get('puzzle_name'), grid=[
            [{'value': cell, 'locked': cell != 0} for cell in row] for row in custom_grid
        ])

        # Create a Puzzle instance in the database
        Puzzle.objects.create(
            name=request.POST.get('puzzle_name'),  # Save the puzzle name
            completed=False,
            puzzle_time="",  # Set to empty string, can be updated later
            difficulty="E",  # Default for custom puzzles; can adjust as needed
            grids=custom_grid  # Save the grid in the format expected by ArrayField
        )

        # Redirect to the solver page with the newly created puzzle
        return render(request, 'solver/sudoku.html', {'sudoku': sudoku_instance})

    return render(request, 'solver/board_creator.html', {'range_9': range(9)})