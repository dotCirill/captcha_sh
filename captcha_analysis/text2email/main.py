#!/usr/bin/env python

from dataclasses import dataclass
from itertools import permutations
from tqdm import tqdm
from fuzzywuzzy import fuzz # python-Levenshtein

@dataclass
class Variant:
    email: str
    ratio: int
    perm: str

EMAIL_LIST = "emails.txt"
INPUT = "de qc ra hl7 @9m ail .c om"

if __name__ == "__main__":
    best = Variant(email="/dev/null", ratio=0, perm="")
    with open(EMAIL_LIST) as f:
        emails = f.read().splitlines()
        emails = [email.strip().lower() for email in emails if email.strip()]

    parts = INPUT.split()
    assert(len(parts) == 8)
    for perm in tqdm(list(permutations(list(range(8)))), colour="green"):
        email = ''.join([parts[i] for i in perm])
        for real_email in emails:
            ratio = fuzz.ratio(email, real_email)
            # if email == "captainjack@car.car":
            #     print(dist)
            if ratio > best.ratio:
                best.ratio = ratio
                best.email = email
                best.perm = " ".join([str(i) for i in perm])

    print(f'Email: {best.email}\nRatio: {best.ratio}%\nPermutation: {best.perm}')
