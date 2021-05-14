#!/usr/bin/env python

from itertools import product
from main import EMAIL_LIST
from tqdm import tqdm

N = 300
names = [
    'smirnov',
    'petrov',
    'ivanov',
    'egor',
    'sasha',
    'aleksandr',
    'semenov',
    'ivan',
    'grigoriy',
    'marina'
    'arina',
    'elizaveta',
    'nastya',
    'tatyana',
    'oleg',
    'vladislav',
    'ilya',
    'ulyana',
    'fedor',
    'michael',
    'alexey',
    'julia',
]

domains = [
    '@gmail.com',
    '@mail.ru',
    '@inbox.ru',
    '@yandex.ru',
    '@yahoo.com',
    '@edu.spbstu.ru'
]

if __name__ == "__main__":
    with open(EMAIL_LIST, 'w') as f:
        for pair in tqdm(product(names, domains)):
            # email, safe_email, free_email
            # safe_email = .*@example.com
            f.write(f'{"".join(pair)}\n')
