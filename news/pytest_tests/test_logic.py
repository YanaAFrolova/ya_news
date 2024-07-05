from http import HTTPStatus

import pytest

from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, url_detail):
    """Анонимный пользователь не может отправить комментарий."""
    response = client.post(url_detail, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url_detail}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
        author_client,
        form_data,
        news,
        url_detail,
        url_to_comments
):
    """Авторизованный пользователь может отправить комментарий."""
    response = author_client.post(url_detail, data=form_data)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.news == news
    assert new_comment.author == new_comment.author


def test_user_cant_use_bad_words(author_client, url_detail):
    """
    Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url_detail, data=bad_words_data)
    assertFormError(
        response, 'form', 'text', errors=WARNING
    )
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(
        author_client,
        url_to_comments,
        url_delete_comment
):
    """Авторизованный пользователь может удалять свои комментарии."""
    response = author_client.delete(url_delete_comment)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(
        not_author_client,
        url_delete_comment
):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    response = not_author_client.delete(url_delete_comment)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
        author_client,
        form_data,
        comment,
        url_edit_comment,
        url_to_comments
):
    """Авторизованный пользователь может редактировать свои комментарии."""
    response = author_client.post(url_edit_comment, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
        not_author_client,
        news,
        comment,
        form_data,
        url_edit_comment,
):
    """
    Авторизованный пользователь не может редактировать
    чужие комментарии.
    """
    response = not_author_client.post(url_edit_comment, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_new = Comment.objects.get(id=news.id)
    assert comment.text == comment_new.text
