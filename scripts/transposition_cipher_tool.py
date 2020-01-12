import sys
from math import ceil
from typing import List, Tuple
from constants import ALPHABET, NULL_CHAR


class BaseError(Exception):
    pass


class InvalidSecretKey(BaseError):
    pass


class InvalidOption(BaseError):
    pass


def insert_letters_into_grid(grid: List[List[str]], number_of_rows: int, plain_text: str, keyword: str) -> List[List[str]]:
    current_letter_index = 0
    additional_grid_spaces = int((number_of_rows * len(keyword)) - len(plain_text))
    plain_text += (NULL_CHAR * additional_grid_spaces)

    for row in range(number_of_rows):
        for column in range(len(keyword)):
            if current_letter_index == len(plain_text):
                break

            grid[row][column] = plain_text[current_letter_index]
            current_letter_index += 1

    return grid


def generate_cipher_text(grid: List[List[str]], order_of_columns: List[int], number_of_rows: int) -> str:
    # take the first column letters starting from column 1 specified in the ordered_columns
    # which maps to keyword letter index and order in alphabet
    cipher_text = ''

    for i in range(len(order_of_columns)):
        column = order_of_columns[i]
        for row in range(number_of_rows):
            cipher_text += grid[row][column]

    return cipher_text


def analyze_order_of_columns(keyword: str) -> List[int]:
    keyword_length = len(keyword)

    # get the order of columns based on which letter in the keyword occurs first
    keyword_letter_index = get_letter_position_in_alphabet(keyword)

    order_of_columns = []
    for i in range(keyword_length + 1):
        for j in range(keyword_length):
            if keyword_letter_index[j] == i:
                order_of_columns.append(j)

    return order_of_columns


def initialize_grid(keyword: str, number_of_rows: int) -> List[List[str]]:
    return [
        [''] * len(keyword)
        for _
        in range(number_of_rows)
    ]


def encrypt(keyword: str, plain_text: str) -> Tuple[str, List[int]]:
    validate_keyword(keyword)
    # size of grid
    number_of_rows = int(ceil(len(plain_text) / len(keyword)))
    grid = initialize_grid(keyword, number_of_rows)

    # place the text into the rows letter by letter starting from left to right
    filled_grid = insert_letters_into_grid(grid, number_of_rows, plain_text, keyword)

    order_of_columns = analyze_order_of_columns(keyword)
    cipher_text = generate_cipher_text(filled_grid, order_of_columns, number_of_rows)

    return cipher_text, order_of_columns


def get_letter_position_in_alphabet(keyword: str):
    # assign numbers to each letter in the keyword based on which occurs first in the alphabet
    # e.g. A is 1 and B is 2 whereas another occurrence of B will be 3
    # this will later determine the order of columns when encrypting or decrypting
    assigned_numbers = [0] * len(keyword)
    letter_count = 0

    for alphabet_letter in ALPHABET:
        for i in range(len(keyword)):
            if alphabet_letter == keyword[i]:
                letter_count += 1
                assigned_numbers[i] = letter_count

    return assigned_numbers


def generate_plain_text(
        grid: List[List[str]],
        order_of_columns: List[int],
        number_of_rows: int) -> str:

    # read the plain text across the rows
    plain_text = ''
    for row in range(number_of_rows):
        for column in range(len(order_of_columns)):
            plain_text += grid[row][column]

    additional_grid_spaces = plain_text.count(NULL_CHAR)
    return plain_text[: -additional_grid_spaces] if additional_grid_spaces > 0 else plain_text


def insert_cipher_into_grid(grid: List[List[str]], order_of_columns: List[int], number_of_rows: int, cipher_text: str, keyword: str) -> List[List[str]]:
    current_column = 0
    cipher_letter_index = 0

    for i in range(len(cipher_text)):
        # reset column to start again from first column since this row is now filled
        if current_column == len(keyword):
            current_column = 0

        column = order_of_columns[current_column]
        for row in range(number_of_rows):
            if cipher_letter_index == len(cipher_text):
                break

            grid[row][column] = cipher_text[cipher_letter_index]
            cipher_letter_index += 1

        if cipher_letter_index == len(cipher_text):
            break

        current_column += 1

    return grid


def validate_keyword(keyword: str):
    if not keyword:
        raise InvalidSecretKey('A valid secret key is required')

    if not all(x.isalpha() or x.isspace() or x.isupper() for x in keyword):
        raise InvalidSecretKey(f'Secret key must comprise of capital English letters: {keyword}')


def decrypt(keyword: str, cipher_text: str) -> Tuple[str, List[int]]:
    validate_keyword(keyword)
    # first determine the size of the grid
    number_of_rows = int(ceil(len(cipher_text) / len(keyword)))
    grid = initialize_grid(keyword, number_of_rows)

    # getting the order of columns based on keyword
    order_of_columns = analyze_order_of_columns(keyword)

    # now place the cipher text in these columns
    filled_grid = insert_cipher_into_grid(
        grid,
        order_of_columns,
        number_of_rows,
        cipher_text,
        keyword,
    )

    plain_text = generate_plain_text(filled_grid, order_of_columns, number_of_rows)
    return plain_text, order_of_columns


if __name__ == '__main__':
    print('*********** Transposition Cipher ***********\n')

    dispatcher = {
        1: encrypt,
        2: decrypt,
    }

    operation_prompt = {
        1: 'Plain Text',
        2: 'Cipher Text',
        3: 'Thank you for using transposition cipher.',
    }

    while True:
        try:
            if(input_mode := int(input('1. Encrypt \n'
                                       '2. Decrypt \n'
                                       '3. Exit    \n'
                                       'Option: '))) in operation_prompt.keys():

                if input_mode == 3:
                    print(f'{operation_prompt[input_mode]} \n')
                    sys.exit(0)

                text_input = input(f'* {operation_prompt[input_mode]}: ').upper()
                keyword_input = input('* Secret: ').upper()

                text_result, columns_order = dispatcher[input_mode](keyword_input, text_input)

                formatter = f'{operation_prompt[input_mode]}: <<{text_result}>> \n'
                formatter += f'Columns Order: {columns_order} \n'
                formatter += '**************** \n\n'

                print(formatter)

            else:
                raise InvalidOption('Choose from available options. \n')

        except ValueError as e:
            print('Option must be a number (integer). \n')

        except InvalidSecretKey as e:
            print(f'{str(e)} \n')

        except InvalidOption as e:
            print(f'{str(e)} \n')

