def reliability(x, y):
    return 2 * x + y - 2 * x * y - 1 / 2


def acceptability(x, y):
    return 2 * x + 2 * y - 2 * x * y - 1


def rebuts(a_is_supportive, a, b, b_is_supportive):
    if a_is_supportive is False and b_is_supportive and 1-a > b:
        return True
    if a_is_supportive and b_is_supportive is False and 1-a < b:
        return True
    return False


def undercut(a_of_premise, a_of_premise_under_u):
    if a_of_premise * a_of_premise_under_u < 0.5:
        return True
    else:
        return False

