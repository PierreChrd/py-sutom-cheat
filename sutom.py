def input_word():
    word = input("Entrez votre mot:\n>")
    word_letters = list(word)
    dict = {}

    for index, letter in enumerate(word_letters):
        dict[index] = (letter, '')
        print(f"{index+1} - {letter}")

    def get_letters_color(color):
        while True:
            letter_color = input(f"Choisissez les lettres {color} (tapez \"ok\" pour terminer)\n>")
            if letter_color == "ok":
                break
            letter_color= int(letter_color) - 1
            if color == "orange":
                dict[letter_color] = ( dict[letter_color][0], color)
            elif color == "red":
                dict[letter_color] = ( dict[letter_color][0], color, letter_color)

    get_letters_color('red')
    get_letters_color('orange')

    return dict

def dict_to_conditions(dict):

    red_dict = {}
    orange_dict = {}
    for element in dict:
        letter = dict[element][0]
        color = dict[element][1]
        if color == "red":
            position = dict[element][2]
            red_dict[position] = ( letter )

        elif color == "orange":
            if letter in orange_dict:
                orange_dict[letter] = ( orange_dict[letter][0] + 1, 'orange' )
            else:
                orange_dict[letter] = ( 1, 'orange' )

    return (orange_dict, red_dict)


def dict_to_words(dict):
    count = 0
    word_array = []
    with open("dictionnaire.txt") as fp:
        while True:
            count += 1
            line = fp.readline()
            word = line.strip().lower()

            word_len = len(dict)
            slen = len(list(str(word)))
            if word_len == slen:
                conditions = dict_to_conditions(dict)
                if verify_condition(word ,conditions):
                    word_array.append(word)

            if not line:
                break

    return word_array

def dict_to_words_with_array(dict, dictionary_array):
    count = 0
    word_array = []
    for word in dictionary_array:

        word_len = len(dict)
        slen = len(list(str(word)))
        if word_len == slen:
            conditions = dict_to_conditions(dict)
            if verify_condition(word ,conditions):
                word_array.append(word)

    return word_array

def orange_verification(letter_list, letter, effectif, conditions):
    print(conditions)
    print(letter_list)

    for c in conditions:
        letter_list[c] = '@'

    new_arr = []
    for t in letter_list:
        if t != '@':
            new_arr.append(t)
    print(letter_list)
    print(new_arr)
    letter_list = new_arr

    count = 0
    for specific_letter in letter_list:
        if specific_letter == letter:
            count += 1
    if count == effectif:
        return True
    else:
        print(letter_list)
        print("erreur orange")
        return False

def verify_condition(word ,condition_dict):

    letter_list = list(word)
    orange_condition = condition_dict[0]
    red_condition = condition_dict[1]
    for position in red_condition:
        if letter_list[position] != red_condition[position]:
            print(word)
            print('Erreur rouge')
            return False

    for c_orange in orange_condition:

        if orange_verification(letter_list, c_orange ,orange_condition[c_orange][0], red_condition) == False:
            print(word)
            return False

    return True

def get_first_word(size, first_letter):
    count = 0
    with open("dictionnaire.txt") as fp:
        while True:
            count += 1
            line = fp.readline()
            word = line.strip().lower()
            word_list = list(str(word))
            slen = len(word_list)
            if slen == size and word_list[0] == first_letter.lower():
                return word
            if not line:
                break
def get_random_word(list):
    size = len(list)


if __name__ == "__main__":
    dict = input_word()
    print(dict)
    result = dict_to_words(dict)

    print(result)
    print(len(result))
    while(True):
        dict = input_word()
        result = dict_to_words_with_array(dict ,result)
        print(result)
