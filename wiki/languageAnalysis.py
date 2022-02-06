from .models import Argument, Concept, Category, Keyword, KeywordText, ConceptText, CategoryLabel, Emotion
from .services import receive_analysis, generate_color, receive_natural_language_analyzer


def add_language_analysis():
    """
    All information from Ibm Natural language analysis is processed here
    :return:
    """
    text_analysis = receive_natural_language_analyzer()
    for argument in Argument.objects.all().filter(lang='en'):
        analysis = receive_analysis(text=argument.plain_string(), text_analysis=text_analysis)
        if analysis is not None:
            argument.sentiment_accuracy = analysis['sentiment']['document']['score']
            for concept in analysis['concepts']:
                current_concept_text, created = ConceptText.objects.get_or_create(text=concept['text'],
                                                                                  explanation=concept['dbpedia_resource'])
                current_concept, created = Concept.objects.get_or_create(conceptname=current_concept_text,
                                                                         relevance=concept['relevance'])
                argument.concepts.add(current_concept)
            for category in analysis['categories']:
                current_category_label, created = CategoryLabel.objects.get_or_create(label=category['label'])
                current_category, created = Category.objects.get_or_create(categorylabel=current_category_label,
                                                                           relevance=category['score'])
                argument.categories.add(current_category)
            for keyword in analysis['keywords']:
                current_keywords_text, created = KeywordText.objects.get_or_create(text=keyword['text'])
                current_keywords, created = Keyword.objects.get_or_create(keywordtext=current_keywords_text,
                                                                          relevance=keyword['relevance'])
                argument.keywords.add(current_keywords)
            emotions = analysis['emotion']['document']['emotion']
            current_emotions = Emotion(sadness=emotions['sadness'],
                                       joy=emotions['joy'],
                                       fear=emotions['fear'],
                                       disgust=emotions['disgust'],
                                       anger=emotions['anger'],
                                       background=generate_color(),
                                       linecol=generate_color())
            current_emotions.save()
            argument.emotion = current_emotions
            argument.save()
