from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Users, Puzzle, Tile  # Import your models
from django.urls import reverse

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

    def is_valid_completion(self):
        # Check if the Sudoku grid is fully complete and valid
        for row in range(9):
            seen = set()
            for col in range(9):
                num = self.grid[row][col]['value']
                if num == 0:  # Check for unfilled cell
                    return False  # The puzzle is not complete
                if num < 1 or num > 9:  # Ensure the number is within valid range
                    return False
                seen.add(num)
            
            if len(seen) != 9:
                return False  # The row does not have exactly 9 unique digits

        return True  # If all checks passed, the puzzle is complete and valid

#hardcoded puzzles used for dev and testing purposes
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
    ],
    "test": [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 0]
    ]
    }


def puzzle_selection(request):
    """View to display the predefined puzzles and handle user selection."""
    puzzles = Puzzle.objects.all()  # Get puzzle names
    users = Users.objects.all()  # Get all users
    
    selected_user = None  # Initialize selected_user as None

    # Check if there's a username in the query parameters
    username = request.GET.get('username')
    if username:
        try:
            selected_user = Users.objects.get(username=username)  # Get the user by username
        except Users.DoesNotExist:
            selected_user = None  # If the user doesn't exist, keep it None

    return render(request, 'solver/puzzle_selection.html', {
        'puzzles': puzzles,
        'users': users,
        'selected_user': selected_user,  # Pass the selected user to the template
    })

def load_puzzle(request, puzzle_name):
    """Load either a predefined or database puzzle based on the puzzle name."""
    if puzzle_name in PREDEFINED_PUZZLES:
        # Handle predefined puzzles
        puzzle_grid = PREDEFINED_PUZZLES[puzzle_name]
    else:
        # Try to load a puzzle from the database
        try:
            puzzle_instance = Puzzle.objects.get(name=puzzle_name)  # Get puzzle by name
            puzzle_grid = puzzle_instance.grids  # Assuming grids is a JSON or list format
        except Puzzle.DoesNotExist:
            return redirect('puzzle_selection')  # Redirect if puzzle doesn't exist

    # Create the Sudoku object from the fetched puzzle grid
    sudoku_data = {
        'name': puzzle_name,
        'grid': [[{'value': cell, 'locked': cell != 0} for cell in row] for row in puzzle_grid]
    }
    
    request.session['custom_puzzle'] = sudoku_data  # Store puzzle in session
    return redirect('sudoku_grid')  # Redirect to sudoku_grid


def sudoku_grid(request):
    # Retrieve the current user or create a default user for demo purposes
    user_id = request.session.get('user_id')
    user = Users.objects.get(id=user_id) if user_id else Users.objects.create(username='demo_user') #python's ternary operator is different

    # Initialize the Sudoku object
    sudoku = Sudoku(name='Custom Puzzle', grid=[[{'value': 0, 'locked': False} for _ in range(9)] for _ in range(9)])

    # Check if there's a custom puzzle in the session
    if 'custom_puzzle' in request.session:
        sudoku_data = request.session['custom_puzzle']
        sudoku = Sudoku(name=sudoku_data['name'], grid=sudoku_data['grid'])


    if request.method == 'POST':
        #populates the grid with the values entered by the user
        for row in range(9):
            for col in range(9):
                cell_name = f'cell_{row}_{col}'
                value = request.POST.get(cell_name)
                # Maybe unnecessary input validation
                if value and value.isdigit() and 1 <= int(value) <= 9:
                    num = int(value)
                    # Update the grid with the new value
                    sudoku.grid[row][col]['value'] = num

        elapsed_time = request.POST.get('elapsed_time', 0)
        # bind the elapsed time to the object
        sudoku.elapsed_time = float(elapsed_time)

        # Check if the puzzle is fully completed and valid
        if sudoku.is_valid_completion():
            # adds the elapsed time to the session
            request.session['elapsed_time'] = sudoku.elapsed_time 
            messages.success(request, f'Puzzle submitted successfully! Time taken: {sudoku.elapsed_time} seconds.') 

            # Update the user's solved puzzle times
            user.solved_time = sudoku.elapsed_time
            user.puzzle_count += 1
            user.total_time += sudoku.elapsed_time
            user.average_time = user.total_time / user.puzzle_count
            user.save() # Save the user instance

            # used to redirect to puzzle select but now it breaks if I remove it
            return render(request, 'solver/sudoku.html', {'sudoku': sudoku, 'elapsed_time': elapsed_time})

        # If not valid, show a general error message
        messages.error(request, 'The puzzle is not complete or contains errors. Please check your entries.')

    elapsed_time = request.session.get('elapsed_time', 0) # Get the elapsed time from the session
    return render(request, 'solver/sudoku.html', {'sudoku': sudoku, 'elapsed_time': elapsed_time}) # Pass the elapsed time to the template (most of the elapsed time logic is in the template)


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

def user_selection(request):
    """View to handle user selection or creation."""
    users = Users.objects.all()  # Get all existing users
    
    if request.method == 'POST':
        username = request.POST.get('username') # Get the username from the form
        if username:
            # Create or get the user
            user = Users.objects.get_or_create(username=username)
            request.session['user_id'] = user.id  # Store the user in session
            return redirect(f'{reverse("puzzle_selection")}?username={user.username}')  # Redirect with username as a query parameter

    return render(request, 'solver/user_select.html', {'users': users})