from eventregistry import *
import requests
import json
import csv
from ibm_watson import TextToSpeechV1, NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, ConceptsOptions, CategoriesOptions, \
    KeywordsOptions, SentimentOptions, EmotionOptions
from ibm_cloud_sdk_core import api_exception
import os
import random


def receive_argument_networks():
    """
    Taking all Information about the Argumentnetworks
    """
    arguments = requests.get("https://dbas.cs.uni-duesseldorf.de/api/v2/query", params={'q': 'query{'
                                                                                             'issues{'
                                                                                             'uid,'
                                                                                             'lang,'
                                                                                             'title,'
                                                                                             'info,'
                                                                                             'lang,'
                                                                                             'positions{'
                                                                                             'uid,'
                                                                                             'textversionUid,'
                                                                                             'text,'
                                                                                             'flatStatementsBelow{'
                                                                                             'textversionUid,'
                                                                                             'text'
                                                                                             '}}}'
                                                                                             'arguments{'
                                                                                             'uid,'
                                                                                             'timestamp,'
                                                                                             'lang,'
                                                                                             'clicks{'
                                                                                             'isUpVote,'
                                                                                             'isValid'
                                                                                             '}'
                                                                                             'conclusionUid,'
                                                                                             'argumentUid,'
                                                                                             'issueUid,'
                                                                                             'isSupportive,'
                                                                                             'premisegroupUid,'
                                                                                             'premises{'
                                                                                             'uid,'
                                                                                             'premisegroupUid,'   
                                                                                             'statement{'
                                                                                             'textversionUid}'
                                                                                             '}'
                                                                                             'conclusion{'
                                                                                             'uid,'
                                                                                             'textversionUid,'
                                                                                             'rebuts{'
                                                                                             'uid}'
                                                                                             'supports{'
                                                                                             'uid}'
                                                                                             'undercuts{'
                                                                                             'uid}'   
                                                                                             '}}}'})
    if arguments.status_code < 300:
        return json.loads(arguments.content)
    else:
        return None


def receive_wiki_data(term):
    """
    Calls the wikipedia api for the term
    :param term: the term that should be searched
    :return:
    """
    summary = requests.get("https://en.wikipedia.org/api/rest_v1/page/summary/" + term)
    if summary.status_code < 300:
        try:
            data = json.loads(summary.content)
        except json.decoder.JSONDecodeError:
            return None
        return data
    return None


def receive_text_to_speech_token():
    try:
        text_to_speech = TextToSpeechV1()
        return text_to_speech
    except api_exception.ApiException as e:
        print(e)
        return None


def receive_sound(text, text_to_speech):
    try:
        response = text_to_speech.synthesize(text,
                                             voice='en-US_AllisonVoice',
                                             accept='audio/mp3'
                                             ).get_result()
    except api_exception.ApiException as e:
        print(e)
        return None
    return response.content


def receive_natural_language_analyzer():
    try:
        text_analysis = NaturalLanguageUnderstandingV1(version='2019-07-12')
        return text_analysis
    except api_exception.ApiException as e:
        print(e)
        return None


def receive_analysis(text, text_analysis):
    try:
        result = text_analysis.analyze(text=text,
                                       features=Features(concepts=ConceptsOptions(limit=3),
                                                         categories=CategoriesOptions(limit=3),
                                                         keywords=KeywordsOptions(limit=3),
                                                         emotion=EmotionOptions(),
                                                         sentiment=SentimentOptions()
                                                         )
                                       ).get_result()
    except api_exception.ApiException as e:
        print(e)
        return None
    return result


def receive_news_object():
    try:
        er = EventRegistry(apiKey=os.environ['EVEKEY'], repeatFailedRequestCount=1)
        return er
    except Exception as e:
        print(e)
        return None


def receive_news(keyword, category_list, er):
    q = QueryArticlesIter(keywords=keyword,
                          categoryUri=QueryItems.OR([er.getCategoryUri(category) for category in category_list]),
                          lang=QueryItems.OR(['eng', 'deu']),
                          sourceLocationUri=er.getLocationUri("Germany"),
                          isDuplicateFilter="skipDuplicates"
                          )
    try:
        content = q.execQuery(er, sortBy='rel', maxItems=2)
        return content
    except Exception as e:
        print(e)
        return None


def csv_dict_list(filename):
    reader = csv.DictReader(open(filename))
    dict_list = []
    for line in reader:
        dict_list.append(line)
    return dict_list


def generate_color():
    green = random.randint(1, 256)  # one special color for an information
    red = random.randint(1, 256)
    blue = random.randint(1, 256)
    return 'rgba('+str(red)+','+str(green)+','+str(blue)+',0.1)'
