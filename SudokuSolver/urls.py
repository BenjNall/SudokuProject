from django.contrib import admin
from django.urls import path
from solver import views
"""
URL configuration for SudokuSolver project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

urlpatterns = [
    path('admin/', admin.site.urls),

    # Display the Sudoku grid
    path('', views.sudoku_grid, name='sudoku_grid'),
    
    # Display the predefined puzzles
    path('puzzles/', views.puzzle_selection, name='puzzle_selection'),

    # Load a predefined puzzle
    path('load_puzzle/<str:puzzle_name>/', views.load_puzzle, name='load_puzzle'),
    
    # Enter path to start timer
    # integrated into solver page: obsolete
   # path('stopwatch/', views.stopwatch, name='stopwatch'),

    # Display a blank board to create a custom grid
    path('board-creator/', views.board_creator, name='board_creator'),
]
