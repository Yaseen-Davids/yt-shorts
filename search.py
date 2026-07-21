def binary_search_iterative(arr, target):
  low = 0
  high = len(arr) - 1

  while low <= high:
    mid = (low + high) // 2

    if arr[mid] == target:
      return mid
    elif arr[mid] > target:
      high = mid - 1
    else:
      low = mid + 1

  return -1

numbers = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
target_val = 2

result = binary_search_iterative(numbers, target_val)
print(f"Element found at index: {result}")  # Output: 5