#!/usr/bin/env python

from faker import Faker
from main import EMAIL_LIST
from tqdm import tqdm

N = 100
SEED = 0xdeadbeef

if __name__ == "__main__":
    faker = Faker()
    Faker.seed(SEED)

    with open(EMAIL_LIST, 'w') as f:
        for _ in tqdm(range(N), colour="yellow"):
            # email, safe_email, free_email
            # safe_email = .*@example.com
            f.write(f'{faker.email()}\n')
