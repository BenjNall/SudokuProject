from django.contrib import admin
from .models import Puzzle

@admin.register(Puzzle)
#unused (anyone can add puzzles)
class PuzzleAdmin(admin.ModelAdmin):
    list_display = ('name', 'difficulty', 'completed', 'puzzle_time')
