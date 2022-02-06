from .models import *
from .services import *
import os


def add_wiki_data():
    """
    This method runs over all Statements and searches for every word and his successor
    a Wikipedia information, as long as the word is not commonly used
    :return:
    """
    easy_words = csv_dict_list(os.path.abspath("english-word-list-total.csv"))
    for s in Statement.objects.all().filter(lang='en'):
        word_list = s.statement_text.split()
        for cw in range(len(word_list)):
            term_with_two_words = ""
            if cw+1 < len(word_list):
                term_with_two_words = "_".join([word_list[cw], word_list[cw+1]])
            if Information.objects.all().filter(word=word_list[cw]) is None:
                if worthy_searching(word_list[cw], easy_words):
                    create_information(word_list[cw], s)
                    if term_with_two_words:
                        if Information.objects.all().filter(word=term_with_two_words) is None:
                            create_information(term_with_two_words, s)


def create_information(term, statement):
    """
    This method creates Information objects with the data fetched from Wikipedia.
    Further the created Object gets connected to the relevant premises, conclusions and
    arguments.
    :param term:
    :param statement:
    :return:
    """
    data = receive_wiki_data(term)
    if data is None:
        return
    info, created = Information.objects.get_or_create(id=data['pageid'])
    info.word = term
    info.title = data['titles']['display']
    info.link = data['content_urls']['desktop']['page']
    if data['type'] != 'disambiguation':
        try:
            info.description = data['description']   # Sometimes there is no description
        except KeyError:
            pass
        info.summary = data['extract']
    info.save()
    for conclusion in Conclusion.objects.filter(statement=statement):
        conclusion.information.add(info)
        for argument in Argument.objects.filter(conclusion=conclusion):
            argument.information.add(info)
    for premise in Premise.objects.filter(statement=statement):
        premise.premiseGroup.information.add(info)
        for argument in Argument.objects.filter(premise_group=premise.premiseGroup):
            argument.information.add(info)


def worthy_searching(word, easy_words):
    """
    Compares the word to the 500 most commonly used words in the english language.
    :param word:
    :param easy_words:
    :return:
    """
    for row in easy_words:
        if word.lower() in row['word'].split(';')[1]:
            return False
    return True


