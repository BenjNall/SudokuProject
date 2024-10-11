from django.contrib import admin
from .models import Puzzle

@admin.register(Puzzle)
class PuzzleAdmin(admin.ModelAdmin):
    list_display = ('name', 'difficulty', 'completed', 'puzzle_time')
