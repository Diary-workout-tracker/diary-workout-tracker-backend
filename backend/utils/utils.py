from collections.abc import Iterable


def binary_search(sequence: Iterable, find_element: any) -> int | bool:
	"""Бинарный поиск."""
	start_element = 0
	end_element = len(sequence) - 1
	while start_element <= end_element:
		middle_element = start_element + (end_element - start_element) // 2
		if sequence[middle_element] == find_element:
			return middle_element
		elif sequence[middle_element] < find_element:
			start_element = middle_element + 1
		else:
			end_element = middle_element - 1
	return False
