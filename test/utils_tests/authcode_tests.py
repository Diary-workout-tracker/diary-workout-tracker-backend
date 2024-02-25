from backend.utils.authcode import AuthCode
from backend.utils.mailsender import MailSender
from rest_framework.exceptions import ValidationError
import pytest


class DummyMailSend(MailSender):
    def __init__(self):
        self.mail_sent = False
        self.code = None
        self.mail_address = None

    def send_code(self, mail_address, code):
        self.mail_sent = True
        self.code = code
        self.mail_address = mail_address


@pytest.fixture
def authcode(user):
    sender = DummyMailSend()
    code = AuthCode(user)
    code.set_sender(sender)
    code.create_code()
    return code


@pytest.mark.parametrize(
    ("incorrect_user_class"),
    ("hi", 123, True, {"a": 5}, 3.141592653589793, ("a", "b", "c"), [1, 2, 3]),
)
def test_incorrect_init_raises_validationerror(incorrect_user_class):
    with pytest.raises(ValidationError):
        AuthCode(incorrect_user_class)


@pytest.mark.django_db
def test_authcode_tries_to_send_mail_code_upon_generation(user):
    sender = DummyMailSend()
    code = AuthCode(user)
    code.set_sender(sender)
    code.create_code()
    assert sender.mail_sent is True


@pytest.mark.django_db
def test_code_is_str_with_four_digits(authcode):
    assert all(
        (
            isinstance(authcode.code, str),
            len(authcode.code) == 4,
            authcode.code.isnumeric,
        )
    )


@pytest.mark.django_db
def test_correct_code_is_valid(authcode):
    assert authcode.code_is_valid(authcode.code)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "invalid_code", (None, "00000", "0000", "0", False, 123, 3.15, {"a": "b"})
)
def test_incorrect_code_after_generation_is_invalid(authcode, invalid_code):
    assert not authcode.code_is_valid(invalid_code)


# def test_code_generation_is_determined_by_the_settings():
#     pass
