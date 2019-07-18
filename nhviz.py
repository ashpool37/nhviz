import os
import argparse
import matplotlib.pyplot as plt
from collections import deque
from urllib.request import urlopen
from bs4 import BeautifulSoup


def is_scum(pairs):
    points = int(pairs[1].split("=")[1])
    reason = pairs[16].split("=")[1]
    return reason in ("escaped", "quit") and points < 1000


def get_val(field, fname, count_scum):
    col = -1
    with open(fname) as file:
        for line in file:
            pairs = line.split(":")
            if not count_scum and is_scum(pairs):
                continue
            if col == -1:
                while True:
                    col += 1
                    pair = pairs[col].split("=")
                    if pair[0] == field:
                        val = pair[1]
                        break
            else:
                val = pairs[col].split("=")[1]
            yield val


def total_avg(field, fname):
    acc_sum = 0
    n = 0
    for val in get_val(field, fname):
        n += 1
        acc_sum += int(val)
        yield acc_sum / n


def mov_avg(field, fname, n, count_scum):
    acc = deque()
    acc_sum = 0
    for val in get_val(field, fname, count_scum):
        acc.append(int(val))
        acc_sum += int(val)
        if len(acc) == n:
            yield acc_sum / len(acc)
            acc_sum -= acc.popleft()


def fname(nickname):
    return nickname + ".xlogfile"


def slurp_data(nickname):
    soup = BeautifulSoup(urlopen("https://alt.org/nethack/player-all-xlog.php?player=" + nickname).read(),
                         'html.parser')
    with open(fname(nickname), "w") as file:
        file.write(soup.pre.get_text())


def main():
    aparse = argparse.ArgumentParser(description='Visualize and compare game log data from nethack.alt.org')
    aparse.add_argument('-f', dest='field', metavar='field', type=str, default='maxlvl',
                        help='the field to visualize (default: maxlvl)')
    aparse.add_argument('players', metavar='nickname', type=str, nargs='+',
                        help='a NAO user\'s nickname')
    aparse.add_argument('--ma', dest='ma_period', metavar='period', type=int, default=200,
                        help='period of the moving average (default: 200)')
    aparse.add_argument('--scum', dest='count_scum', action='store_true',
                        help='count the start-scummed games')
    aparse.add_argument('-u', dest='force_update', action='store_true',
                        help='force updating logfiles from the server')
    args = aparse.parse_args()

    plt.figure()
    for plr in args.players:
        if args.force_update or not os.path.isfile(fname(plr)):
            slurp_data(plr)
        plt.plot(list(mov_avg(args.field, fname(plr), args.ma_period, args.count_scum)), label=plr)
    plt.grid()
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
