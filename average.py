def compute_average(arr):
    if len(arr) == 0:
        return 0.0  # Return 0 if the array is empty to avoid division by zero
    total = compute_sum(arr)
    return total / len(arr)

# Example usage:
numbers = [1.5, 2.5, 3.5, 4.5]
print("Average of numbers:", compute_average(numbers))
