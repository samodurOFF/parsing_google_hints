import os
import sys
import pandas as pd

from bs4 import BeautifulSoup
import requests


def filtration(phrases: list, base_word: str, index: int = 0) -> list:
    assert len(base_word.split(' ')) != 1  # проверка на короткую фразу

    if index == len(phrases):  # услование выхода из рекурсии
        return phrases

    phrase = phrases[index]  # ьекущая фраза по рекурсии

    if base_word == phrase:  # если базовая фраза равна текущей фразе или не содержиться в ней
        phrases.remove(phrase)  # то удаляем текущую фразу из списка
        return filtration(phrases, base_word)  # и вызываем функцию снова без изменения индекса
    else:  # если базовая фраза не содержиться в текущей фразе, то нужно вызвать функцию перейдя к следующей фразе
        return filtration(phrases, base_word, index + 1)


def find_suggestions(phrases, final_dict: dict):
    """
    The function for looking for and record Google search suggestion

    :param phrases: object with phrases that are needed to look for
    :return:
    """

    if len(phrases) == 0:  # условие выхода из первой рекурсии
        return final_dict

    else:
        phrase = phrases.pop(0)
        url = f'http://clients1.google.com/complete/search?output=toolbar&num=100&hl=en&pq=suggestqueries.google.com&cp=1&q={phrase}'
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        suggestion_list = []
        for i in soup.find_all('suggestion'):
            suggestion_list.append(i['data'])

        else:
            final_dict[phrase] = ', '.join(filtration(suggestion_list, phrase))
            return find_suggestions(phrases, final_dict)


if __name__ == '__main__':
    with open('phrases_for_suggest.txt', 'r', encoding='utf-8') as file:
        phrases = file.read().split('\n')

    file_1 = 'suggest.csv'
    file_2 = 'suggest.txt'

    if os.path.exists(file_1):
        os.remove(file_1)

    if os.path.exists(file_2):
        os.remove(file_2)

    pd.DataFrame(columns=['PHRASE', 'SUGGESTION']).to_csv(file_1, index=False, sep=';')

    depth = input('Укажите грубину рекурсии (нажмите enter для установки значения по умолчанию): ')
    if depth != '':
        sys.setrecursionlimit(int(depth))

    passes = input('Укажите количество проходов рекурсии (нажмите enter если хотите ждать завершения рекурсии): ')
    print('Обратите внимание, что стек рекурсии может переполниться раньше, чем произойдет последний проход!\n')

    i = 1
    while True:
        final_dict = {}

        if passes != '':
            if i > int(passes):
                break

        print(f'\rПроход № {i}', end='')
        i += 1

        try:
            answer = find_suggestions(phrases, final_dict)
        except RuntimeError:
            print('\nГлубина рекурсии превышена!')
            break

        answer = {key: value for key, value in answer.items() if bool(value)}

        df = pd.DataFrame({'PHRASE': answer.keys(), 'SUGGESTION': answer.values()})
        values = [x for l in [i.split(', ') for i in answer.values()] for x in l]

        if values == phrases:
            break
        else:
            phrases = values

        df.to_csv(file_1, index=False, header=False, mode='a', sep=';')
        with open(file_2, 'a') as f:
            f.write('\n'.join(values))

    df = pd.read_csv(file_1, sep=';')
    list_of_values = [i.split(', ') for i in df['SUGGESTION'].to_list()]

    values = [x for l in list_of_values for x in l]
    df.drop_duplicates(subset='PHRASE', keep='last').to_csv(file_1, index=False, sep=';')  # удаление дубликатов

    with open(file_2, 'w') as f:
        f.write('\n'.join(set(values)))

    print('\nDONE!')
