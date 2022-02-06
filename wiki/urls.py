from django.urls import path
from . import views


app_name = 'wiki'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('issues/<int:pk>/', views.DetailViewDiscussion.as_view(), name='issue'),
    path('argument/<int:pk>/', views.DetailViewArgument.as_view(), name='argument'),
    path('premise/<int:pk>/', views.DetailViewPremises.as_view(), name='premises'),
    path('conclusion/<int:pk>/', views.DetailViewConclusion.as_view(), name='conclusion'),
    path('category/<int:pk>/', views.DetailViewCategory.as_view(), name='category'),
    path('news/<int:pk>/', views.DetailViewKeyword.as_view(), name='news'),
    path('update', views.update, name='update'),
    path('search', views.ArgumentSearchList.as_view(), name='search'),
]
