from .services import csv_dict_list, generate_color
from .models import Information, AcadScore
import os


def add_academic_domains():
    """
    The Wikipedia Titles and the Words are searched in the ACAD Corpus the relevant values are saved.
    :return:
    """
    word_list = csv_dict_list(os.path.abspath("acadCore.csv"))
    for information in Information.objects.all():
        for row in word_list:
            if (information.word or information.title) in row['word']:
                current_score = AcadScore(his=row['HIS'].replace(",", "."),
                                          edu=row['EDU'].replace(",", "."),
                                          soc=row['SOC'].replace(",", "."),
                                          bus=row['BUS'].replace(",", "."),
                                          med=row['MED'].replace(",", "."),
                                          hum=row['HUM'].replace(",", "."),
                                          sci=row['SCI'].replace(",", "."),
                                          law=row['LAW'].replace(",", "."),
                                          phil=row['PHIL'].replace(",", "."),
                                          linecol=generate_color(),
                                          background=generate_color())
                current_score.save()
                information.acad_score = current_score
                information.save()
                for argument in information.argument_set.all():
                    argument.context_assessment = True
                    argument.save()
