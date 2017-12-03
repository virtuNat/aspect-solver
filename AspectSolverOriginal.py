#!/usr/bin/env python
from argparse import ArgumentParser
from itertools import product

cmdparser = ArgumentParser(
    description='A program made to replicate the Aspect Quiz.',
    )
cmdparser.add_argument(
    'casefname',
    help='The file containing the answer cases.',
    metavar='case_name',
    )
cmdargs = cmdparser.parse_args()

with open(cmdargs, 'r') as casefile:
    caselines = casefile.readlines()
    answerset = [
        line[4:6]
        + line[6:8]
        + line[8:10]
        + line[2:4]
        + line[0:2]
        + line[10:12]
        for line in caselines
        ]
    orglines = [line[0:12] for line in caselines]
    trueanswers = [
        line.split(' = ')[1][:-1]
        for line in caselines
        ]

ANSWER_KEYS = {
    'A': -3,
    'B': -2,
    'C': 0,
    'D': 2,
    'E': 3,
}
# List of aspects in priority index order.
ASPECTS = [
    'time',  #0
    'space', #1
    'heart', #2
    'mind',  #3
    'hope',  #4
    'rage',  #5
    'light', #6
    'void',  #7
    'breath',#8
    'blood', #9
    'life',  #10
    'doom',  #11
]
# Aspects that are adjacent to the indexed aspect on the wheel.
ADJACENTS = [
    (2, 6), # Time
    (3, 7), # Space
    (0, 5), # Heart
    (1, 4), # Mind
    (3, 8), # Hope
    (2, 9), # Rage
    (0, 10), # Light
    (1, 11), # Void
    (4, 10), # Breath
    (5, 11), # Blood
    (8, 6), # Life
    (9, 7), # Doom
]


failures = 0
resultlines = []
equation_lines = []
numset = [8, 4, 4, 2, 3, 1]
total_cases = len(answerset)

for ansind, (answers, trueanswer, orga) in enumerate(zip(answerset, trueanswers, orglines)):
    # Tally the total score per aspect pair.
    results = [0] * 12
    #if answers.find("C") != -1: continue
    for indx, answer in enumerate(answers):
        key = ANSWER_KEYS[answer]
        off, opoff = (1, 0) if key > 0 else (0, 1)
        adj1, adj2 = ADJACENTS[indx // 2 * 2 + off]
        opadj1, opadj2 = ADJACENTS[indx // 2 * 2 + opoff]
        

        base = abs(key)
        a = 0 if base == 3 else 1 if base == 2 else 4
        b = 2 if base == 3 else 3 if base == 2 else 5
        score1 = numset[a]
        score2 = numset[b]

        if base != 0:
            results[indx // 2 * 2 + off] += score1
            results[adj1] += score2
            results[adj2] += score2
        else:
            for no, val in enumerate(results):
                if no == indx // 2 * 2 or no == indx // 2 * 2 + 1:
                    results[no] -= score2
                elif no in (adj1,adj2,opadj1,opadj2):
                    results[no] += score2
                else:
                    results[no] += score1
        


    maxima = max(results)
    aspect_max = [idx for idx, val in enumerate(results) if val == maxima]
    if len(aspect_max) == 1:
        answer = ASPECTS[aspect_max[0]]
 
    else:
        culled_results = list(results)
        for i, val in enumerate(results):
            if val != maxima:
                culled_results[i] = 0
        for i in range(0, 12, 2):
            if culled_results[i] == culled_results[i+1]:
                culled_results[i] = culled_results[i+1] = 0
        aspect_max_culled = [idx for idx, val in enumerate(culled_results) if val == maxima]
        if len(aspect_max_culled) == 0:
            answer = ASPECTS[aspect_max[0]]
        else:
            answer = ASPECTS[aspect_max_culled[0]]
    
    if answer.lower() != trueanswer.lower():
        failures += 1
        resultlines.append(
            '{} {}: {!r} {} ({})'.format(
                str(ansind),
                orga[0:12],
                results,
                answer, trueanswer
                )
            )        
print(
'{} failed cases of {}, {:.2f}% failure rate.'.format(
    failures, total_cases, 100 * failures / total_cases
    )
)

with open('testresults.txt', 'w') as outfile:
    outfile.write('\n'.join(resultlines))
