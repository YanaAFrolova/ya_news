from datetime import datetime, timedelta

import pytest

from django.conf import settings
from django.test.client import Client
from django.utils import timezone
from django.urls import reverse

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):  
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):  
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author): 
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки'
    )
    return news


@pytest.fixture
def news_list():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)
    return News


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        text='Текст коментария',
        author=author,
        news=news
    )
    return comment


@pytest.fixture
def comment_list(comment, news, author):
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return Comment


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст',
    }


@pytest.fixture
def id_for_args(comment):
    return (comment.id,)


@pytest.fixture
def url_detail(news):
    url = reverse('news:detail', args=(news.id,))
    return url


@pytest.fixture
def url_to_comments(url_detail):
    url = url_detail + '#comments'
    return url


@pytest.fixture
def url_delete_comment(comment):
    url = reverse('news:delete', args=(comment.id,))
    return url

@pytest.fixture
def url_edit_comment(comment):
    url = reverse('news:edit', args=(comment.id,))
    return url
