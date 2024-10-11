from django.db import models
from django.contrib.postgres.fields import ArrayField

#This class will be for the Users
class Users(models.Model):
    #primary key would just be integers will already have a defaulted id as a primary key
    username = models.CharField(max_length=100, unique=False, null=False, blank=True)
    solved_time = models.FloatField(default=0)
    prev_10 = models.JSONField(default=list)
    size=10
    #Might have to change this for later!!!
    average_time = models.FloatField(default=0)

    def __str(self):
        return self.username

    

#This class will be for the Puzzle class
class Puzzle(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False, unique=True)
    completed = models.BooleanField(null=False, blank=False)
    puzzle_time = models.CharField(max_length=100, blank=True, null=False) #Use puzzle_time instead of current_time as current_time is a reserved word
    
    difficulty_Choices = [
        ("E", "Easy"),
        ("M", "Medium"),
        ("H", "Hard"),
    ]
    difficulty = models.CharField(max_length=1, choices=difficulty_Choices)

    # Allow blank cells (0's) in the grid
    grids = ArrayField(
        ArrayField(
            models.IntegerField(null=True, blank=True),  # Allow null/blank integers
            size=9
        ),
        size=9
    )


#This class will be for the Tile class
class Tile(models.Model):
    #primary key would just be integers will already have a defaulted id as a primary key
    held = models.IntegerField()
    invalid = models.IntegerField()
