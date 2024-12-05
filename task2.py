import string

from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

import requests

import matplotlib.pyplot as plt

def get_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Перевірка на помилки HTTP
        return response.text
    except requests.RequestException as e:
        return None

# Функція для видалення знаків пунктуації
def remove_punctuation(text) -> str:
    return text.translate(str.maketrans("", "", string.punctuation))

def map_function(word):
    return remove_punctuation(word).lower(), 1

def shuffle_function(mapped_values):
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        if key: # Бо split може лишити порожні рядки, якщо там були лише знаки пунктуації
            shuffled[key].append(value)
    return shuffled.items()

def reduce_function(key_values):
    key, values = key_values
    return key, sum(values)

# Виконання MapReduce
def map_reduce(text, search_words=None):
    # Видалення знаків пунктуації ПЕРЕНЕСЕНО В MAP
    words = text.split()

    # Якщо задано список слів для пошуку, враховувати тільки ці слова
    # (БЛОК ПРИБРАНО через те що пунктуація і Lower перенесені в мапінг)
    # if search_words:
    #     words = [word for word in words if word in search_words]

    # Паралельний Мапінг
    with ThreadPoolExecutor() as executor:
        mapped_values = list(executor.map(map_function, words))

    # Крок 2: Shuffle
    shuffled_values = shuffle_function(mapped_values)

    # Паралельна Редукція
    with ThreadPoolExecutor() as executor:
        reduced_values = list(executor.map(reduce_function, shuffled_values))

    reduced_values.sort(key=lambda x: x[1], reverse=True)

    return dict(reduced_values)

if __name__ == '__main__':
    # Вхідний текст для обробки
    url = "https://raw.githubusercontent.com/pull-ups/ybigta_21winter/refs/heads/master/2021.%202.%204%20(%EB%AA%A9)%20wordcloud-konlpy/The%20Hunger%20Games.txt"
    text = get_text(url)
    if text:
        # Виконання MapReduce на вхідному тексті
        search_words = ['war', 'peace', 'love']
        result = map_reduce(text, search_words)
        top_ten = list(result.items())[:10]
        top_ten.reverse()
        y, x = zip(*top_ten)
        plt.barh(y, x)
 
        plt.ylabel("Word")
        
        plt.xlabel("Occurences") 
        plt.title("Top words in the book")
        plt.show()
    else:
        print("Помилка: Не вдалося отримати вхідний текст.")
