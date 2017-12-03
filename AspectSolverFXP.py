#!/usr/bin/env python
from sys import argv
from itertools import chain


def map_aspects(index):
    """Maps each of the twelve homestuck aspects to a priority index;
    aspects of lower index values win ties over higher indices.
    """
    return (
        'Time'   if index ==  0 else
        'Space'  if index ==  1 else
        'Heart'  if index ==  2 else
        'Mind'   if index ==  3 else
        'Hope'   if index ==  4 else
        'Rage'   if index ==  5 else
        'Light'  if index ==  6 else
        'Void'   if index ==  7 else
        'Breath' if index ==  8 else
        'Blood'  if index ==  9 else
        'Life'   if index == 10 else
        'Doom' # if index == 11
        )


def map_adjacents(aspect):
    """Obtains the minor aspects of any given aspect, based on
    the adjacent aspects in the canon aspect wheel.
    """
    return (
        (2,  6) if aspect ==  0 else # Time   (Heart, Light)
        (3,  7) if aspect ==  1 else # Space  (Mind, Void)
        (0,  5) if aspect ==  2 else # Heart  (Time, Rage)
        (1,  4) if aspect ==  3 else # Mind   (Space, Hope)
        (3,  8) if aspect ==  4 else # Hope   (Mind, Breath)
        (2,  9) if aspect ==  5 else # Rage   (Heart, Blood)
        (0, 10) if aspect ==  6 else # Light  (Time, Life)
        (1, 11) if aspect ==  7 else # Void   (Space, Doom)
        (4, 10) if aspect ==  8 else # Breath (Hope, Life)
        (5, 11) if aspect ==  9 else # Blood  (Rage, Doom)
        (6,  8) if aspect == 10 else # Life   (Light, Breath)
        (7,  9)#if aspect == 11        Doom   (Void, Blood)
        )


def map_answers(answer):
    """Maps point values to each question answer, in the following order:
    (major aspect, minor "adjacent" aspect)
    """
    return (
        (8, 4) if answer == 'A' else
        (4, 2) if answer == 'B' else
        (3, 1) if answer == 'C' else
        (4, 2) if answer == 'D' else
        (8, 4)#if answer == 'E'
        )


def arrange_answers(answerlist):
    """Rearranges answers in aspect priority list order."""
    return (
        answerlist[4:10] # Time - Rage
        + answerlist[2:4] # Light - Void
        + answerlist[0:2] # Breath - Blood
        + answerlist[10:12] # Life - Doom
        )


def distribute_points(answer, qnum):
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
    pair_item = (1, 0) if answer in 'DE' else (0, 1)
    adjacents = map_adjacents(qnum // 2 * 2 + pair_item[0])
    compladjs = map_adjacents(qnum // 2 * 2 + pair_item[1])
    major_point, minor_point = map_answers(answer)
    return (
        [
            major_point if indx == qnum // 2 * 2 + pair_item[0] else
            minor_point if indx in adjacents else
            0
            for indx in range(12)
            ]
        if answer != 'C' else
        [
            -minor_point if indx // 2 == qnum // 2 else
            +minor_point if indx in adjacents + compladjs else
            +major_point
            for indx in range(12)
            ]
        )


def accumulate_points(answerlist, listidx):
    """Accumulates the points awarded per question answered into a list."""
    if listidx < 0:
        return [0] * 12
    drop_list = accumulate_points(answerlist[:-1], listidx-1)
    dist_list = distribute_points(answerlist[-1], listidx)
    return [drop_list[index] + dist_list[index] for index in range(12)]


def break_ties(point_list, maxima):
    """If more than one aspect holds a maximum value, consider only all
    aspects with the maximum value. If any tied aspects are a paired
    complement, discard them.
    If any aspects remain from this procedure, the first aspect in the
    priority chain among the remaining aspects win.
    Otherwise, the first aspect in the priority chain among the tied
    aspects wins.
    """
    paired_list = [[point_list[i], point_list[i+1]] for i in range(0, 12, 2)]
    culled_list = [
        [0, 0] if maxima not in item or item[0] == item[1] else
        [0 if subitem != maxima else subitem for subitem in item]
        for item in paired_list
        ]
    return [
        idx for idx, value in enumerate(chain(*culled_list))
        if value == maxima
        ]



def solve_aspect(answer):
    """Determines what aspect the user is based on the point system,
    priority chain, and tiebreaker rules stated above.
    """
    point_list = accumulate_points(arrange_answers(answer), 11)
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
    print('Your aspect is:', aspect+',', 'making you', aspect+'-bound.')


if __name__ == '__main__':
    main()
