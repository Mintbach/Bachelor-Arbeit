from .models import *


def design_argument():
    """
    Saves for every argument the type of the argument, the text that fits the type the best
    and the text of the argument.
    :return:
    """
    for argument in Argument.objects.all():
        argument.type = which_type(argument)
        argument.type_text = which_text(argument)
        argument.save_text


def which_text(argument):
    """
    Determines the text fitting the best for type
    :param argument: treated argument
    :return type text: is a phrase that displays the way the argument interferes
    """
    if argument.type in 'support':
        return ' strengthens the claim that '
    elif argument.type in 'undercut':
        return ' doubts the inference from '
    elif argument.type in 'rebut':
        return ' questions the validity of '
    else:
        return ' weakens the claim that '


def which_type(argument):
    """
    Returns the type of the Argument.
    :param argument: treated argument
    :return type: is the type of the interference of the argument
    """
    if argument.isSupportive:
        return 'support'
    elif argument.attacked_argument is not None:
        return 'undercut'
    elif Premise.objects.filter(statement=argument.conclusion.statement):
        if Argument.objects.filter(conclusion=argument.conclusion).count() > 1:
            return 'undermine/rebut'
        return 'undermine'
    else:
        return 'rebut'
