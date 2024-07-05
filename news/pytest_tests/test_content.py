import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count(client, news_list):
    """Количество новостей на главной странице — не более 10."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, news_list):
    """
    Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    """
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, news, url_detail):
    """
    Комментарии на странице отдельной новости отсортированы
    от старых к новым: старые в начале списка, новые — в конце.
    """
    response = client.get(url_detail)
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(client, url_detail):
    """
    Анонимному пользователю недоступна форма 
    для отправки комментария на странице отдельной новости.
    """
    response = client.get(url_detail)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, url_detail):
    """
    Авторизованному пользователю доступна форма 
    для отправки комментария на странице отдельной новости.
    """
    response = author_client.get(url_detail)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
