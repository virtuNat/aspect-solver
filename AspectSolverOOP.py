#!/usr/bin/env python
"""
Testing bullshit. It looks like it works but needs more testing.
Also it kinda looks fugly???
"""

class AspectSolver:
    """"""
    __slots__ = ()

    class AspectList(list):
        """"""
        __slots__ = ()

        class Aspect:
            """"""
            __slots__ = ('name', 'adjacents', 'score', 'pair')

            def __init__(self, name, adjacents):
                self.name = name
                self.adjacents = adjacents
                self.reset()

            def reset(self):
                self.score = 0

            def __str__(self):
                return 'You are bound to the {} Aspect.'.format(self.name)

            def __repr__(self):
                return '{} Aspect: {} points.'.format(self.name, self.score)

            def __and__(self, other):
                try:
                    return self.adjacents + other.adjacents
                except AttributeError:
                    raise TypeError('{} is not an aspect!'.format(other))

            def __iadd__(self, point):
                self.score += point
                return self

            def __gt__(self, other):
                try:
                    return self.score > other.score
                except AttributeError:
                    raise TypeError('{} is not an aspect!'.format(other))

        def __init__(self):
            super().__init__((
                self.Aspect('Time'  , (2,  6)), # (Heart, Light)
                self.Aspect('Space' , (3,  7)), # (Mind, Void)
                self.Aspect('Heart' , (0,  5)), # (Time, Rage)
                self.Aspect('Mind'  , (1,  4)), # (Space, Hope)
                self.Aspect('Hope'  , (3,  8)), # (Mind, Breath)
                self.Aspect('Rage'  , (2,  9)), # (Heart, Blood)
                self.Aspect('Light' , (0, 10)), # (Time, Life)
                self.Aspect('Void'  , (1, 11)), # (Space, Doom)
                self.Aspect('Breath', (4, 10)), # (Hope, Life)
                self.Aspect('Blood' , (5, 11)), # (Rage, Doom)
                self.Aspect('Life'  , (6,  8)), # (Light, Breath)
                self.Aspect('Doom'  , (7,  9)), # (Void, Blood)
                ))
            for i in range(0, 12, 2):
                self[i].pair = self[i+1]
                self[i+1].pair = self[i]

        def get_adjacents(self, aspect):
            return (self[adj_index] for adj_index in aspect.adjacents)

        def get_adj_pairs(self, aspect):
            return (self[adj_index] for adj_index in aspect & aspect.pair)

        def spread_points(self, pair_idx, offset, points):
            if offset < 2:
                aspect = self[pair_idx * 2 + offset]
                aspect += points[0]
                for adjacent in self.get_adjacents(aspect):
                    adjacent += points[1]
                return
            target = self[pair_idx * 2]
            adj_pairs = list(self.get_adj_pairs(target))
            for aspect in self:
                if aspect is target or aspect is target.pair:
                    aspect -= points[1]
                elif aspect in adj_pairs:
                    aspect += points[1]
                else:
                    aspect += points[0]

        def get_max(self):
            maxima = max(self)
            max_indices = [idx for idx, asp in enumerate(self) if asp is maxima]
            if len(max_indices) > 1:
                new_indices = []
                for idx in max_indices:
                    if not(idx % 2) and idx+1 in max_indices:
                        continue
                    elif idx % 2 and idx-1 in max_indices:
                        continue
                    new_indices.append(idx)
                if new_indices:
                    return self[new_indices[0]]
            return self[max_indices[0]]

        def reset(self):
            for aspect in self:
                aspect.reset()

    ASPECTS = AspectList()
    ANSWERKEY = {
        'A': (0, (8, 4)),
        'B': (0, (4, 2)),
        'C': (2, (3, 1)),
        'D': (1, (4, 2)),
        'E': (1, (8, 4)),
        }

    def __call__(self, answerlist):
        answerlist = (
            answerlist[4:10] # Time - Rage
            + answerlist[2:4] # Light - Void
            + answerlist[0:2] # Breath - Blood
            + answerlist[10:12] # Life - Doom
            )
        for qnum, answer in enumerate(answerlist):
            self.ASPECTS.spread_points(qnum // 2, *self.ANSWERKEY[answer])
        result = self.ASPECTS.get_max()
        self.ASPECTS.reset()
        return result

    def __iter__(self, answersets):
        for answer in answersets:
            yield self(answer)

if __name__ == '__main__':
    solver = AspectSolver()
    answer = input('What are the answers you got in the aspect quiz, in order?\n')
    print(solver(answer))
