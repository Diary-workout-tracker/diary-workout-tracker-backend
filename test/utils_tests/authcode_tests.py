from backend.utils.authcode import AuthCode
from rest_framework.exceptions import ValidationError
import pytest


@pytest.mark.parametrize(
    ("incorrect_user_class"),
    ("hi", 123, True, {"a": 5}, 3.141592653589793, ("a", "b", "c"), [1, 2, 3]),
)
def test_incorrect_init_raises_validationerror(incorrect_user_class):
    with pytest.raises(ValidationError):
        AuthCode(incorrect_user_class)
