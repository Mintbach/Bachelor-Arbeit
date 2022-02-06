from workers import task
from .getNews import add_news
from .acadDomains import add_academic_domains
from .getCurrentArgumentNetworks import add_argument_networks
from .calculateIndices import calc_indices
from .getSoundFiles import add_sounds
from .getWikiData import add_wiki_data
from .languageAnalysis import add_language_analysis
from .designArgument import design_argument


@task()
def gather_data():
    """
    All things to update
    :return:
    """
    #add_argument_networks()
    print("done argument networks")
    #design_argument()
    print('done categories')
    #calc_indices()
    print('done calc')
    #add_wiki_data()
    print('done wiki data')
    #add_academic_domains()
    print('done academic')
    add_sounds()
    print('done sounds')
    #add_language_analysis()
    print('done analyzing')
    #add_news()
    print('done gathering')



