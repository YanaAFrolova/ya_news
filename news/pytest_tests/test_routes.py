from http import HTTPStatus

import pytest

from pytest_django.asserts import assertRedirects

from django.urls import reverse

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None)
    ),
)
def test_home_availability_for_anonymous_user(client, name, args):
    """
    Главная страница, страница отдельной новости,
    страницы регистрации пользователей, входа и выхода из учётной записи
    доступны анонимному пользователю.
    """
    if args is not None:
        url = reverse(name, args=(args.id,))
    else:
        url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('id_for_args')),
        ('news:delete', pytest.lazy_fixture('id_for_args')),
    )
)
def test_pages_availability_for_different_users(
        parametrized_client, name, args, expected_status
):
    """
    Страницы удаления и редактирования комментария
    доступны автору комментария и
    не доступны авторизованному пользователю(возвращается ошибка 404).
    """
    url = reverse(name, args=args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('id_for_args')),
        ('news:delete', pytest.lazy_fixture('id_for_args')),
    ),
)
def test_redirects(client, name, args):
    """
    Анонимный пользователь перенаправляется на страницу авторизации
    при попытке перейти на страницу редактирования
    или удаления комментария.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
