import pytest

from backend.utils.utils import binary_search


@pytest.mark.parametrize(
	"sequence, find_element, index",
	(
		(
			[1, 2, 3, 4, 5, 6, 7, 8],
			1,
			0,
		),
		(
			[2, 3, 4, 6, 7, 8, 120],
			7,
			4,
		),
		(
			[1, 2, 3, 4, 5, 6, 7, 8],
			130,
			False,
		),
	),
)
def test_binary_search(sequence, find_element, index) -> None:
	assert index == binary_search(sequence, find_element)
