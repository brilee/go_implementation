import argparse
import itertools
import re
import textwrap
import timeit
import flamegraph
from go_naive import N, NN
import go_naive
import go_mutable
import go_sets

def load_board(string):
    return re.sub(r'[^XO\.]+', '', string)

translate_sg = 'abcdefghijklmnopqrs'.index

def get_moves(sgf_snippet):
    return [go_naive.flatten((translate_sg(x), translate_sg(y))) for _, _, _, y, x, _ in textwrap.wrap(sgf_snippet, 6)]

game = ";B[qd];W[dc];B[pq];W[dq];B[do];W[co];B[cn];W[cp];B[ce];W[dn];B[fd];W[ed];B[ee];W[fc];B[gd];W[gc];B[hd];W[hc];B[id];W[jc];B[cm];W[en];B[dk];W[qo];B[cc];W[de];B[df];W[dd];B[cd];W[db];B[ef];W[nq];B[op];W[np];B[pn];W[qm];B[qp];W[pm];B[on];W[jp];B[qn];W[rn];B[ro];W[qi];B[hq];W[jq];B[go];W[fp];B[gp];W[fq];B[gl];W[ci];B[cj];W[ei];B[fj];W[cg];B[cf];W[gh];B[ii];W[ih];B[jh];W[gj];B[fk];W[dj];B[bj];W[hk];B[fi];W[fh];B[ig];W[gi];B[im];W[ij];B[ir];W[jr];B[or];W[ck];B[bk];W[km];B[jl];W[ji];B[hh];W[hl];B[gm];W[hm];B[hn];W[in];B[kl];W[lk];B[eh];W[ll];B[fg];W[so];B[rp];W[ki];B[qg];W[oc];B[pc];W[od];B[pf];W[rl];B[lc];W[pb];B[qb];W[nb];B[pa];W[gg];B[ob];W[ff];B[eg];W[hf];B[le];W[of];B[og];W[nf];B[ng];W[mf];B[jd];W[kc];B[ld];W[mg];B[cb];W[if];B[eb];W[da];B[ic];W[ib];B[jb];W[ha];B[kb];W[kf];B[mn];W[ek];B[dl];W[el];B[ej];W[pe];B[qe];W[fn];B[gn];W[no];B[nn];W[ln];B[mo];W[nr];B[lp];W[lr];B[gr];W[io];B[ds];W[cs];B[ca];W[fa];B[rh];W[mb];B[fe];W[nh];B[oh];W[oi];B[ni];W[mh];B[pi];W[oj];B[pj];W[ph];B[pg];W[pk];B[qj];W[rj];B[qh];W[ok];B[bo];W[bp];B[es];W[fl];B[gk];W[fr];B[fs];W[cr];B[ri];W[bn];B[bm];W[ao];B[lf];W[ke];B[kd];W[lg];B[gf];W[hg];B[nl];W[sp];B[sq];W[sn];B[rr];W[rk];B[nk];W[nj];B[fo];W[eo];B[di];W[oq];B[pr];W[oo];B[po];W[lq];B[mm];W[lm];B[js];W[ks];B[is];W[gq];B[hp];W[iq];B[kp];W[mp];B[lo];W[ko];B[pd];W[oe];B[me];W[nc];B[kq];W[kr];B[am];W[er];B[hr];W[os];B[ps];W[ns];B[an];W[bo];B[mk];W[mj];B[je];W[jf];B[ol];W[om];B[pp];W[si];B[sh];W[sj];B[he];W[pl];B[qk];W[ql];B[ja];W[ia];B[la];W[lb];B[oa];W[ma];B[ka];W[na];B[mc];W[nd];B[md];W[ne];B[ie];W[nm];B[ml];W[fm];B[dm];W[dr];B[gs];W[ip];B[ho];W[dp];B[em];W[hi];B[cl];W[ih];B[ch];W[jg];B[bi];W[kh];B[bg];W[jm];B[dg];W[il];B[kk];W[kj];B[rq];W[jk];B[qq];W[mi];B[qr];W[fb];B[ec];W[ea]"
moves = get_moves(game)
result = 13 # B wins by +13 before komi
final = load_board('''
..XOOO.OOXXXOOXX...
..XO.O..OXXOOOX.X..
..XO.OOOX..XXOOX...
..XOOXXXXXXXXOOXX..
..XOXX.XXXOXXOOOX..
..XXX.XOOOOXOOOX...
.X.XXXOO.O.OOXXXX..
..X.XOO.O.O.OOX.XXX
.X.X.XOO.OO.O.OX.XO
.XX.XXO.O.O.OOOXXOO
.X.XOXXO.O.OXXOOXO.
..XXOOXOO..OXXXOOO.
XXXXXOXO.OOOXOOOO..
XOXOOOXXO..OXXXXXOO
OOO.OXXXO.OXXOOX.XO
.OOO.OXXOOXXOOXXXXO
...O.OOXOOXO.OOXXXX
..OOOOXXXOOO.OXXXX.
..OXXXX.XXO..OOX...
''')

final_liberties = [
0,  0,  13, 5,  5,  5,  0,  2,  2,  2,  2,  2,  8,  8,  2,  2,  0,  0,  0,
0,  0,  13, 5,  0,  5,  0,  0,  2,  2,  2,  8,  8,  8,  2,  0,  4,  0,  0,
0,  0,  13, 5,  0,  5,  5,  5,  13, 0,  0,  13, 13, 8,  8,  5,  0,  0,  0,
0,  0,  13, 5,  5,  13, 13, 13, 13, 13, 13, 13, 13, 8,  8,  5,  5,  0,  0,
0,  0,  13, 5,  13, 13, 0,  13, 13, 13, 6,  13, 13, 8,  8,  8,  5,  0,  0,
0,  0,  13, 13, 13, 0,  2,  6,  6,  6,  6,  13, 8,  8,  8,  5,  0,  0,  0,
0,  4,  0,  13, 13, 13, 6,  6,  0,  6,  0,  8,  8,  5,  5,  5,  5,  0,  0,
0,  0,  4,  0,  13, 6,  6,  0,  4,  0,  8,  0,  8,  8,  5,  0,  5,  5,  5,
0,  8,  0,  4,  0,  3,  6,  6,  0,  8,  8,  0,  8,  0,  8,  2,  0,  5,  8,
0,  8,  8,  0,  3,  3,  6,  0,  4,  0,  8,  0,  8,  8,  8,  2,  2,  8,  8,
0,  8,  0,  4,  2,  3,  3,  4,  0,  4,  0,  7,  4,  4,  8,  8,  2,  8,  0,
0,  0,  4,  4,  2,  2,  3,  4,  4,  0,  0,  7,  4,  4,  4,  8,  8,  8,  0,
4,  4,  4,  4,  4,  2,  3,  4,  0,  7,  7,  7,  4,  8,  8,  8,  8,  0,  0,
4,  8,  4,  2,  2,  2,  3,  3,  6,  0,  0,  7,  4,  4,  4,  4,  4,  2,  2,
8,  8,  8,  0,  2,  3,  3,  3,  6,  0,  2,  4,  4,  3,  3,  4,  0,  4,  2,
0,  8,  8,  8,  0,  8,  3,  3,  6,  6,  4,  4,  3,  3,  4,  4,  4,  4,  2,
0,  0,  0,  8,  0,  8,  8,  3,  6,  6,  4,  6,  0,  3,  3,  4,  4,  4,  4,
0,  0,  8,  8,  8,  8,  3,  3,  3,  6,  6,  6,  0,  3,  4,  4,  4,  4,  0,
0,  0,  8,  3,  3,  3,  3,  0,  3,  3,  6,  0,  0,  3,  3,  4,  0,  0,  0,
]

def measure_game_exec(initial_state, reps=1000, calc_libs=False):
    def snippet():
        pos = initial_state()
        for move, color in zip(moves, itertools.cycle('XO')):
            try:
                pos = pos.play_move(move, color)
                if calc_libs:
                    pos.get_liberties()
            except:
                print(pos)
                print(move, color)
                raise

        assert pos.get_board() == final
        assert pos.score() == result
        assert pos.get_liberties() == final_liberties
    time_taken = timeit.timeit(snippet, number=reps)
    return time_taken / reps

if __name__ == '__main__':
    implementations = ["naive", "mutable", "sets"]
    parser = argparse.ArgumentParser(description='Play and benchmark a game of go.')
    parser.add_argument('implementation', choices=implementations,
                        help='implementation to benchmark')
    parser.add_argument('runs', default=100, type=int,
                   help='number of repetitions of the game to play')
    parser.add_argument('--calc_libs', action='store_true')

    args = parser.parse_args()

    if args.implementation == 'naive':
      elapsed = measure_game_exec(go_naive.Position.initial_state, reps=args.runs, calc_libs=args.calc_libs)
      print("go_naive takes %.4f secs to play a game that's 288 moves long" % elapsed)
    elif args.implementation == 'mutable':
      elapsed = measure_game_exec(go_mutable.Position.initial_state, reps=args.runs, calc_libs=args.calc_libs)
      print("go_mutable takes %.4f secs to play a game that's 288 moves long" % elapsed)
    else:
      elapsed = measure_game_exec(go_sets.Position.initial_state, reps=args.runs, calc_libs=args.calc_libs)
      print("go_sets takes %.4f secs to play a game that's 288 moves long" % elapsed)


