#!/usr/bin/env python3
from dataclasses import dataclass, field
from collections import deque

#--

class Cache:
    def __init__(self):
        self.cache = set()
    def __call__(self, vs: tuple[int, ...]) -> bool:
        if vs in self.cache:
            return True
        self.cache.add(vs)
        return False
is_cached = Cache()

####
# alternate approach to placate mypy is kind of gross
#
# def is_cached(vs: tuple[int, ...]) -> bool:
#     if not (hasattr(is_cached,'cache')):
#         setattr(is_cached,'cache', set())
#     if vs in getattr(is_cached,'cache'):
#         return True
#     getattr(is_cached,'cache').add(vs)
#     return False

#--

@dataclass
class Candidate:
    vs:    tuple[int, ...]
    op:    str = 'begin'
    parents: tuple['Candidate', ...] = field(default_factory=tuple)

    def __str__(self) -> str:
        fields = [self.op, str(self.vs)]
        return " ===> ".join([f"{s:18}" for s in fields])

    def is_valid(self, vmax: int) -> bool:
        # check cache
        if (is_cached(self.vs)):
            return False

        # check for duplicates
        dedup = set(self.vs)
        if len(dedup) != len(self.vs):
            return False

        # check for any gt vmax
        if (any(((x > vmax) for x in self.vs))):
            return False

        return True

    def split_cand(self, ndx: int, keep: int) -> 'Candidate':
        """split index ndx into two values (keep, vs[ndx]-keep), and return a new Candidate"""
        vnew = self.vs[:ndx] + (keep, self.vs[ndx]-keep) + self.vs[ndx+1:]
        return Candidate(vnew, f"split {self.vs[ndx]}   -> {keep},{self.vs[ndx]-keep}", self.parents + (self,))

    def join_cand(self, ndx: int) -> 'Candidate':
        """join indexes ndx and (ndx+1), and return a new Candidate"""
        vnew = self.vs[:ndx] + (self.vs[ndx]+self.vs[ndx+1],) + self.vs[ndx+2:]
        return Candidate(vnew, f"join  {self.vs[ndx]},{self.vs[ndx+1]} -> {vnew[ndx]}", self.parents + (self,))

#--

def solve(puzzle: tuple[int, ...]) -> None:
    vmax       = max(puzzle)
    candidates = deque((Candidate(puzzle, "begin"),))
    soln       = tuple(reversed(puzzle))
    print(f"Start: {puzzle}")
    print(f"Goal:  {soln}")

    # spin while candidates list is non-empty, until/unless solution is found
    while candidates:
        this_cand = candidates.popleft()

        # check for solution
        if this_cand.vs == soln:
            print("Solution found!")
            print("\n".join([str(p) for p in this_cand.parents + (this_cand,)]))
            return

        # if no solution, then iterate over every posn; for each posn P, append new candidate for all legal joins/splits at P to the candidates deque
        for n in range(len(this_cand.vs)):
            # append the join case at this index as long as we aren't the final index (and it is valid)
            if n < len(this_cand.vs)-1:
                next_cand = this_cand.join_cand(n)
                if next_cand.is_valid(vmax):
                    candidates.append(next_cand)

            # extend by all legal splits on this index 
            candidates.extend((next_cand for k in range(1,this_cand.vs[n]) if (next_cand := this_cand.split_cand(n,k)).is_valid(vmax)))

    print("No solutions found :-(")

    return None

#--

if __name__=='__main__':
    puzzle = (3,5,7)
    solve(puzzle)
