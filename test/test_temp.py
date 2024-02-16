import pytest


@pytest.mark.django_db  # TODO: тест для проверки пре коммита | удалить как будут тесты
def test_testings():
    assert 1 == 1
