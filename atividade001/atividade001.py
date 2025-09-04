# Dawkin's Weasel Algorithm:
#   1. Create a random sequence of 28 characters (phrase)
#   2. Make 100 copies of initial sequence (reproduction)
#   3. For each character, in every one of 100 copies, change it for a new random one with a 5% chance (mutation)
#   4. Compare each new sequence with target phrase "METHINKS IT IS LIKE A WEASEL", and give to each generated copy
#      a punctuation (quantity of characters in correct sequence and position).
#   5. If any of new characters sequence (phrases) has a perfect punctuation (28, all characters in correct sequence
#     and position), stop. Otherwise, take the highest punctuation phrase and restart from step 2.
#
import random
import time
import sys

# Start timer
start_time = time.perf_counter()
MAXINT = sys.maxsize
# 28 possible characters
POSSIBLE_CHARACTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ "

# Target phrase
TARGET_PHRASE = "METHINKS IT IS LIKE A WEASEL"

# Quantity of copies
QUANTITY_OF_COPIES = 100

# Chance of mutation
CHANCE_OF_MUTATION = 0.05

# Generate a random number between 0 and length of POSSIBLE_CHARACTERS minus 1
def generate_random_character():
    # Define a real random seed to improve random number generator
    random.seed(time.time_ns())

    # Return a random letter from possible characters
    return POSSIBLE_CHARACTERS[random.randint(0, len(POSSIBLE_CHARACTERS) - 1)]

# Get a random number from 1 to 1.000.000 and verify if it is in a percentage chance
def is_gonna_mutate():
    # Define a real random seed to improve random number generator
    random.seed(time.time_ns())

    # Get a random int number from 1 to MAXINT
    random_number = random.randint(1, MAXINT)

    # Number threshold for mutation rate
    number_threshold = CHANCE_OF_MUTATION * MAXINT

    # If random_number is below or equal to number_threshold, then return true and mutate
    if random_number <= number_threshold:
        return True
    else:
        return False

# Return an int number that is the punctuation of a sequence
def calculate_points(string_list):
    # Variable to count letter in correct position
    points = 0

    # Count every time a letter is in the correct position
    for index, character in enumerate(string_list):
        if character == TARGET_PHRASE[index]:
            points += 1

    return points

# Create a list with random uppercase characters
def create_random_list():
    random_sequence_list = []

    for _ in range(0, len(TARGET_PHRASE)):
        # Put the random generated character into string
        random_sequence_list.append(generate_random_character())

    return random_sequence_list

#   1. Create a random sequence of characters (phrase)
random_initial_sequence_list = create_random_list()

# Create a copy of initial list to preserve it
actual_sequence_list = random_initial_sequence_list.copy()

# Calculate punctuation for the initial sequence
max_points = calculate_points(actual_sequence_list)

# Generation counter
generation = 0

# Repeat until a correct sequence is found (max_points == len(TARGET_PHRASE))
while max_points < len(TARGET_PHRASE):
    # Increase generation
    generation += 1

    #   2. Make copies of actual sequence (reproduction)
    sequence_copies = []
    for i in range(0, QUANTITY_OF_COPIES):
        sequence_copies.append(actual_sequence_list.copy())

    #   3. For each character, in every one of its copies, change it for a new random one  with a chance of mutation
    for i, sequence in enumerate(sequence_copies):
        for j, letter in enumerate(sequence):
            if is_gonna_mutate():
                sequence_copies[i][j] = generate_random_character()

    #   4. Compare each new sequence with target phrase, and give to each generated copy a punctuation (quantity of
    #   characters in correct sequence and position).

    # Create a list to count points for each sequence
    sequence_points_list = [0] * QUANTITY_OF_COPIES

    # Calculate points for each sequence
    for i, sequence in enumerate(sequence_copies):
        sequence_points_list[i] = calculate_points(sequence)

    # 5. If any of new characters sequence (phrases) has a perfect punctuation (28, all characters in correct sequence
    #     and position), stop. Otherwise, take the highest punctuation phrase and restart from step 2.

    # Find max point sequence and its index
    max_points = max(sequence_points_list)
    max_index = sequence_points_list.index(max_points)

    # Copy the max point sequence to use it as the basis of next generation
    actual_sequence_list = sequence_copies[max_index]

    # Print generation, chosen sequence and its points
    print(f"Generation: {generation} - {actual_sequence_list} - Points: {max_points}")

# Stop timer
stop_time = time.perf_counter()

# Elapsed time
elapsed_time = stop_time - start_time

# Print elapsed time
print(f"Target sequence acquired in {elapsed_time:.4f} seconds!!!")
