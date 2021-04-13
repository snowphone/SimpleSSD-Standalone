#!/usr/bin/env python3

from random import random
from typing import Tuple
import re
import argparse
import multiprocessing as mp

BITS_PER_BYTE = 8
PAGES_IN_BLOCK = 768

# timestamp, 0, slba, nlba, op
pattern = re.compile(r"\d+ 0 (\d+) (\d+) (\w+)")


def to_per(ber: float) -> float:
	return ber * BITS_PER_BYTE * PAGES_IN_BLOCK


def parseLine(line: str) -> Tuple[int, int, str]:
	match = pattern.search(line)
	slba = int(match.group(1))
	nlba = int(match.group(2))
	op = match.group(3)

	return (slba, nlba, op)


def prob(p: float):
	return random() < p


CONV_FACTOR = 16384 // 512


def simulate(tracePath: str, ber: float):
	per = to_per(ber)

	accessCnt = 0
	insertCnt = 0
	for _ in range(50):
		f = open(tracePath, "rt")
		for line in f:
			slba, nlba, op = parseLine(line)

			lpn = slba // CONV_FACTOR
			for _ in range(lpn, lpn + nlba // CONV_FACTOR):
				if op[0] == 'R':
					continue

				accessCnt += 1
				if prob(per):
					insertCnt += 1
		f.close()
	return accessCnt, insertCnt


def main(args: argparse.Namespace):
	inputs = [(trace, ber) for ber in args.bers for trace in args.traces]
	with mp.Pool() as p:
		results = p.starmap(simulate, inputs)
		print(",".join(map(str, ["ber", "trace", "access", "insert"])))
		for ((trace, ber), (access, insert)) in zip(inputs, results):
			print(",".join(map(str, [ber, trace, access, insert])))


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--traces", '-t', required=True, nargs='+')
	parser.add_argument("--bers", '-b', type=float, required=True, nargs='+')
	args = parser.parse_args()

	main(args)
