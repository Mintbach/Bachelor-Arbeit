from .models import Keyword, News, Argument
from .services import receive_news, receive_news_object


def add_news():
    er = receive_news_object()
    i = 0
    if er is not None:
        try:
            for argument in Argument.objects.all().filter(lang='en'):
                clean_category_list = []
                if i < 5:
                    for category in argument.categories.all():
                        for text in category.categorylabel.label.split('/'):
                            clean_category_list.append(text)
                    # Categories are '/law, govt and politics/politics' in this format so we have to split them on the backslash
                    # Many times arguments have Categories like this,
                    #     /art and entertainment/music/music genres/pop music
                    #     /art and entertainment/music/music genres/rock music
                    # We dont want to search for 'art and entertainment' twice.
                    non_redundant_category_list = list(set(clean_category_list))
                    for keyword in argument.keywords.all():
                        keyword_text = keyword.keywordtext
                        for a in receive_news(keyword_text.text, non_redundant_category_list, er):
                            current_news, created = News.objects.get_or_create(source=a['source']['title'],
                                                                               title=a['title'],
                                                                               date=a['date'],
                                                                               type=a['dataType'],
                                                                               description=a['body'],
                                                                               url=a['url'])
                            keyword_text.news.add(current_news)
                            keyword_text.save()
                        i += 1
        except Exception as e:
            print(e)
    else:
        print('No Connection')
