import os
import pandas as pd
from bs4 import BeautifulSoup
import requests

with open('phrases_for_suggest.txt', 'r', encoding='utf-8') as file:
    phrases = file.read().split('\n')

file_1 = 'suggest.csv'
file_2 = 'suggest.txt'

if os.path.exists(file_1):
    os.remove(file_1)

if os.path.exists(file_2):
    os.remove(file_2)

passes = input(
    'Укажите максимальное количество проходов нажмите enter если не хотите устанавливать этот параметр): ')

pd.DataFrame(columns=['PHRASE', 'SUGGESTION']).to_csv(file_1, index=False, sep=';')
new_phrases = []
all_phrases = []
i = 1
while True:
    if phrases == new_phrases:
        break

    elif passes != '' and i > int(passes):
        break

    else:
        print(f'\rПроход № {i}', end='')
        i += 1

        new_phrases = phrases
        suggestion_list = []

        for phrase in phrases:
            if phrase in all_phrases:
                continue

            else:
                url = f'http://clients1.google.com/complete/search?output=toolbar&num=100&hl=en&pq=suggestqueries.google.com&cp=1&q={phrase}'
                page = requests.get(url)
                soup = BeautifulSoup(page.text, 'html.parser')

                for tag in soup.find_all('suggestion'):
                    suggestion_list.append({'PHRASE': phrase, 'SUGGESTION': tag['data']})
        else:
            df = pd.DataFrame(suggestion_list)
            df = df.loc[df['PHRASE'] != df['SUGGESTION']]
            df.to_csv(file_1, index=False, header=False, mode='a', sep=';')

            all_phrases.extend(phrases)
            phrases = df['SUGGESTION'].to_list()

df = pd.read_csv(file_1, sep=';')
df.drop_duplicates(keep='last').to_csv(file_1, index=False, sep=';')  # удаление дубликатов

with open(file_2, 'w') as f:
    f.write('\n'.join(df['SUGGESTION'].to_list()))

print('\nDONE!')
