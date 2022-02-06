from .models import *
from .services import *


def add_argument_networks():
    """
    Calls the adding methods in the right order
    :return:
    """
    argument_networks = receive_argument_networks()
    print('data received')
    add_issues_positions_statements(argument_networks)
    print('positions_and_statements added')
    add_premises(argument_networks)
    print('premises added')
    add_conclusions(argument_networks)
    print('conclusion added')
    add_arguments(argument_networks)
    print('argument added')


def add_issues_positions_statements(argument_networks):
    """
    Add issue to database and gather all positions concerning and the
    statements below them
    :param argument_networks: json with the relevant Information
    :return:
    """
    for i in argument_networks['issues']:
        current_issue = Issue(id=int(i['uid']),
                              issue_title=i['title'],
                              issue_info=i['info'],
                              lang=i['lang'])
        current_issue.save()
        add_positions_and_statements(i, current_issue)


def add_positions_and_statements(issue, current_issue):
    """
    Adding all positions and the statements below them to the database.
    :param issue: json with all positions and statements below
    :param current_issue: Issue object which relates to the positions
    :return:
    """
    for pos in issue['positions']:
        current_statement, created = Statement.objects.get_or_create(id=int(pos['textversionUid']),
                                                                     statement_text=pos['text'],
                                                                     isPosition=True,
                                                                     lang=issue['lang'])
        current_position, created = Position.objects.get_or_create(id=int(pos['uid']),
                                                                   statement=current_statement)
        current_position.issue.add(current_issue)
        current_position.statement_below.add(current_statement)
        for stat in pos['flatStatementsBelow']:
            current_statement, created = Statement.objects.get_or_create(id=stat['textversionUid'],
                                                                         statement_text=stat['text'],
                                                                         isPosition=False,
                                                                         lang=issue['lang'])
            current_position.statement_below.add(current_statement)


def add_premises(argument_networks):
    """
    All premises and premise groups build with the statements
    :param argument_networks: json with all information about the argument networks
    :return:
    """
    for ps in argument_networks['arguments']:
        if Issue.objects.filter(pk=int(ps['issueUid'])).exists():  # sometimes Arguments are not in relevant Issues
            for p in ps['premises']:
                current_premise_group, created = PremiseGroup.objects.get_or_create(id=int(p['premisegroupUid']))
                current_premise = Premise(id=int(p['uid']),
                                          premiseGroup=current_premise_group,
                                          statement=Statement.objects.get(id=int(p['statement']['textversionUid'])))
                current_premise.save()


def add_conclusions(argument_networks):
    """
    All Conclusion build with the statements
    :param argument_networks: json with all information about the argument networks
    :return:
    """
    for cs in argument_networks['arguments']:
        if Issue.objects.filter(pk=int(cs['issueUid'])).exists():
            if cs['conclusion'] is not None:
                current_conclusion = Conclusion(id=int(cs['conclusion']['uid']),
                                                statement=Statement.objects.get(id=int(cs['conclusion']['textversionUid'])),
                                                rebuts=len(cs['conclusion']['rebuts']),
                                                supports=len(cs['conclusion']['supports']),
                                                undercuts=len(cs['conclusion']['undercuts']))
                current_conclusion.save()


def add_arguments(argument_networks):
    """
    Complete argument saving process
    :param argument_networks: json with all information about the argument networks
    :return:
    """
    for argument in argument_networks['arguments']:
        if Issue.objects.filter(pk=int(argument['issueUid'])).exists():
            current_conclusion = None
            current_up_vote_count, current_down_vote_count = count_votes(argument)
            if argument['conclusionUid']:
                current_conclusion = Conclusion.objects.get(id=argument['conclusionUid'])
            current_premise_group = PremiseGroup.objects.get(id=argument['premisegroupUid'])
            current_argument = Argument(
                id=int(argument['uid']),
                conclusion=current_conclusion,
                premise_group=current_premise_group,
                attacked_argument=None,
                downVotes=current_down_vote_count,
                upVotes=current_up_vote_count,
                date=argument['timestamp'],
                isSupportive=argument['isSupportive'],
                type=None,
                context_assessment=False,
                lang=argument['lang'])
            current_argument.save()
    add_argument_attacks(argument_networks)  # attacked arguments can only be added when every argument is saved
    assign_arguments_to_positions()


def count_votes(argument):
    up_votes = 0
    down_votes = 0
    if argument['clicks']:
        for click in argument['clicks']:
            if click['isValid'] is True:
                if click['isUpVote'] is True:
                    up_votes += 1
                else:
                    down_votes += 1
    return up_votes, down_votes


def add_argument_attacks(argument_networks):
    for a in argument_networks['arguments']:
        if Issue.objects.filter(pk=int(a['issueUid'])).exists():
            argument = Argument.objects.get(id=a['uid'])
            if a['argumentUid'] is not None:
                argument.attacked_argument = Argument.objects.get(id=a['argumentUid'])
            argument.save()


def assign_arguments_to_positions():
    # Premise statements cant be used here because the direction of an argument is accessed through its conclusion
    for argument in Argument.objects.all():
        nearest_conclusion = argument.conclusion
        attacked_argument = argument.attacked_argument
        while nearest_conclusion is None:               # find first argument which is not an undercut
            if attacked_argument.conclusion is not None:
                nearest_conclusion = attacked_argument.conclusion
            else:
                attacked_argument = attacked_argument.attacked_argument
                nearest_conclusion = attacked_argument.conclusion
        for position in nearest_conclusion.statement.statementsBelow.all().iterator():
            argument.under_position.add(position)
        argument.save()

