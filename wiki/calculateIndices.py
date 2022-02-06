from .models import *
from textstat import *


def calc_indices():
    for position in Position.objects.all():   # all argument acceptances get calculated with that
        position.position_acceptance()
    for statement in Statement.objects.all():  # reset recursion value
        statement.new_calculation = 0
        statement.save()
    for argument in Argument.objects.all().filter(lang='en'):  # calculate readability
        if textstat.automated_readability_index(argument.plain_string()) < 14:
            argument.ari = textstat.automated_readability_index(argument.plain_string())
        else:
            argument.ari = 14
        fr_ease = textstat.flesch_reading_ease(argument.plain_string())
        if 100 > fr_ease > 0:
            argument.f_r_ease = fr_ease
        elif fr_ease < 0:
            argument.f_r_ease = 0
        else:
            argument.f_r_ease = 100
        argument.save()
