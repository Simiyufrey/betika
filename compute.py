
# sum of numbers
def compute_sum(arr):
    total = 0.0
    for num in arr:
        total += num
    return total

# Example usage:
numbers = [1.5, 2.5, 3.5, 4.5]
print("Sum of numbers:", compute_sum(numbers))



# average of numbers
def compute_average(arr):
    if len(arr) == 0:
        return 0.0  # Return 0 if the array is empty to avoid division by zero
    total = compute_sum(arr)
    return total / len(arr)


numbers = [20.0,30.4,33.0,32.8]
print("Average of numbers:", compute_average(numbers))
