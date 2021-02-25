#!/usr/bin/python3

from itertools import islice
import subprocess
from sys import argv

from tqdm import tqdm

GiB = 1024 ** 3
MiB = 1024 ** 2
KiB = 1024

GB = 1000 ** 3
MB = 1000 ** 2
KB = 1000

def getLineCount(path: str) -> int:
	return int(subprocess.getoutput(f"wc -l {path}").split()[0])


whitelist = ["ycsb"]

def sample(srcPath: str, dstPath: str, size=8 * GB, minLine=1000, acceleration=10):
	size //= 512 # unit: byte -> LBA
	src = tqdm(open(srcPath, "rt"))
	dst = open(dstPath, "wt")

	lines = getLineCount(srcPath)

	lineCnt = 0
	acc = 0
	beg = lines // 2

	# If current item is in whitelist, then disable acceleration
	if next((it for it in whitelist if srcPath.find(it) != -1), False):
		acceleration = 1

	for line in islice(src, beg):
		lineCnt += 1
		time, _, slba, nlb, op = line.split()
		time = str(int(time) // acceleration)
		dst.write(" ".join([time, "0", slba, nlb, op]) + '\n')
		if op.find("W") != -1:
			acc += int(line.split()[3])
		if acc >= size and lineCnt >= minLine:
			break

	src.close()
	dst.close()


for path in tqdm(argv[1:]):
	sample(path, path.replace(".trace", "_sampled.trace"))
