from django.conf import settings
from datetime import timedelta
import pytest


@pytest.fixture
def alternative_throttling_settings():
	settings.ACCESS_RESTORE_CODE_THROTTLING = {
		"duration": timedelta(milliseconds=1),
		"num_requests": 3,
		"cooldown": timedelta(milliseconds=1),
	}


def test_request_code_after_last_try_returns_error(alternative_throttling_settings):
	pass
