#!/usr/bin/env python
"""Aspect solver program. Uses functional flow, with the intent of being
easily translatable into purely functional languages like Haskell or Racket
"""
from sys import argv
from itertools import chain


def invalid_value():
    raise ValueError('how HIGH do you have to even BE???')


def map_aspects(index):
    """Maps each of the twelve homestuck aspects to a priority index;
    aspects of lower index values win ties over higher indices.
    """
    return (
        'Time', 'Space',   #  0,  1
        'Heart', 'Mind',   #  2,  3
        'Hope', 'Rage',    #  4,  5
        'Light', 'Void',   #  6,  7 
        'Breath', 'Blood', #  8,  9
        'Life', 'Doom',    # 10, 11
        )[index]


def map_adjacents(aspect):
    """Obtains the minor aspects of any given aspect, based on
    the adjacent aspects in the canon aspect wheel.
    """
    return (
        (2,  6), # Time   (Heart, Light)
        (3,  7), # Space  (Mind, Void)
        (0,  5), # Heart  (Time, Rage)
        (1,  4), # Mind   (Space, Hope)
        (3,  8), # Hope   (Mind, Breath)
        (2,  9), # Rage   (Heart, Blood)
        (0, 10), # Light  (Time, Life)
        (1, 11), # Void   (Space, Doom)
        (4, 10), # Breath (Hope, Life)
        (5, 11), # Blood  (Rage, Doom)
        (6,  8), # Life   (Light, Breath)
        (7,  9), # Doom   (Void, Blood)
        )[aspect]


def map_answers(answer):
    """Maps point values to each question answer, in the following order:
    (major aspect, minor "adjacent" aspect)
    """
    return (
        (8, 4) if answer in 'AE' else # Extreme
        (4, 2) if answer in 'BD' else # Leaning
        (3, 1) if answer == 'C'  else # Neutral
        invalid_value() # Invalid value, cause exception
        )


def arrange_answers(answerlist):
    """Rearranges answers in aspect priority list order."""
    return (
        answerlist[4:10] # Time - Rage
        + answerlist[2:4] # Light - Void
        + answerlist[0:2] # Breath - Blood
        + answerlist[10:12] # Life - Doom
        )


def distribute_points(answer, qpair):
    """Distributes the point effect of an answer to each question.

    Each answer grants points to each aspect based on value:

    If the answer is neutral, the major aspect pair gets deducted,
    the minor aspect pair receives a small boost, and all other
    aspects receive a significant boost.

    If the answer is not neutral, the major aspect pair gains
    points based on whether it's extreme (A/E) or leaning (B/D).
    If the answer is A or B, the first aspect in the pair gains
    the points, otherwise the second aspect gains points.
    When a major aspect gains points this way, its two minor
    or adjacent aspects will receive half the points.
    """
    as_offset = int(answer in 'DE') # 1 if D or E, otherwise 0
    adjacents = map_adjacents(qpair * 2 + as_offset)
    compladjs = map_adjacents(qpair * 2 + 1 - as_offset)
    major_point, minor_point = map_answers(answer)
    return (
        [
            major_point if indx == qpair * 2 + as_offset else
            minor_point if indx in adjacents else
            0
            for indx in range(12)
            ]
        if answer != 'C' else
        [
            -minor_point if indx // 2 == qpair else
            +minor_point if indx in adjacents + compladjs else
            +major_point
            for indx in range(12)
            ]
        )


def accumulate_points(answerlist):
    """Accumulates the points awarded per question answered into a list."""
    answergen = (
        distribute_points(answer, idx // 2)
        for idx, answer in enumerate(answerlist)
        )
    # Flip the list of lists and sum every item in the same sublist.
    return [sum(points) for points in zip(*answergen)]


def break_ties(point_list, maxima):
    """If more than one aspect holds a maximum value, consider only all
    aspects with the maximum value. If any tied aspects are a paired
    complement, discard them.

    If any aspects remain from this procedure, the first aspect in the
    priority chain among the remaining aspects win.
    Otherwise, the first aspect in the priority chain among the tied
    aspects wins.
    """
    culled_list = [point if point == maxima else 0 for point in point_list]
    paired_list = [
        [0, 0] if culled_list[i] == culled_list[i+1] else
        culled_list[i:i+2] for i in range(0, 12, 2)
        ]
    return [idx for idx, value in enumerate(chain(*paired_list)) if value]


def solve_aspect(answer):
    """Determines what aspect the user is based on the point system,
    priority chain, and tiebreaker rules stated above.
    """
    point_list = accumulate_points(arrange_answers(answer))
    maxima = max(point_list)
    max_indices = [
        idx for idx, value in enumerate(point_list)
        if value == maxima
        ]
    if len(max_indices) > 1:
        culled_indices = break_ties(point_list, maxima)
        return (
            map_aspects(culled_indices[0])
            if culled_indices else 
            map_aspects(max_indices[0])
            )
    return map_aspects(max_indices[0])


# def test_file():
#     """Used to test against a data set. Non-functional."""
#     with open(argv[1], 'r') as casefile:
#         caselines = casefile.readlines()
#     answerset = [line[:12] for line in caselines]
#     trueset = [line[15:-1] for line in caselines]
#     aspectset = [solve_aspect(answer) for answer in answerset]
#     with open('testresults.txt', 'w') as resultfile:
#         for aspect, trueaspect in zip(aspectset, trueset):
#             if aspect.lower() == trueaspect.lower():
#                 resultstr = aspect
#             else:
#                 resultstr = '{} ({})'.format(aspect, trueaspect)
#             resultfile.write(resultstr + '\n')


def main():
    answer = input('What are the answers you got in the aspect quiz, in order?\n')
    aspect = solve_aspect(answer)
    print('You are one of the '+aspect+'-bound.', sep='')


if __name__ == '__main__':
    main()
