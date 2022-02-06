from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.generic import ListView, DetailView
from .models import *
from .tasks import gather_data
from .forms import ArgumentSearchForm
from search_views.search import SearchListView
from search_views.filters import BaseFilter


class ArgumentFilter(BaseFilter):
    search_fields = {
        'search_text' : ['text'],
        'search_date_start' : { 'operator' : '__gte', 'fields' : ['date'] },
        'search_date_end' : { 'operator' : '__lte', 'fields' : ['date'] },
        'search_isSupportive' : { 'operator' : '__exact', 'fields' : ['isSupportive'],
                                  'value_mapper': lambda x: True if x in 'on' else False},
        'search_isAttacking' : { 'operator' : '__exact', 'fields' : ['isSupportive'],
                                  'value_mapper': lambda x: False if x in 'on' else True},
        'search_language' : { 'operator' : '__exact', 'fields' : ['lang'] },
        'search_acceptance_min': {'operator': '__gte', 'fields': ['argument_acceptance']},
        'search_acceptance_max': {'operator' : '__lte', 'fields' : ['argument_acceptance']}
    }


class ArgumentSearchList(SearchListView):
    model = Argument
    template_name = "wiki/searchField.html"
    paginate_by = 33
    form_class = ArgumentSearchForm
    filter_class = ArgumentFilter


@login_required(login_url='/admin/login/')
def update(request):
    gather_data()
    return redirect('/w')


class IndexView(ListView):
    template_name = 'wiki/index.html'
    context_object_name = 'discussion_topics'

    def get_queryset(self):
        return Issue.objects.all()


class DetailViewDiscussion(DetailView):
    model = Issue
    template_name = 'wiki/detailDiscussion.html'


class DetailViewArgument(DetailView):
    model = Argument
    template_name = 'wiki/detailArgument.html'


class DetailViewPremises(DetailView):
    model = PremiseGroup
    template_name = 'wiki/detailPremises.html'


class DetailViewConclusion(DetailView):
    model = Conclusion
    template_name = 'wiki/detailConclusion.html'


class DetailViewCategory(DetailView):
    model = CategoryLabel
    template_name = 'wiki/detailCategory.html'


class DetailViewKeyword(DetailView):
    model = KeywordText
    template_name = 'wiki/detailKeywordText.html'

