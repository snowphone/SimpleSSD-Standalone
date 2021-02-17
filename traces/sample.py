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


def sample(srcPath: str, dstPath: str, size=200 * MB):
	size //= 512 # unit: byte -> LBA
	src = tqdm(open(srcPath, "rt"))
	dst = open(dstPath, "wt")

	lines = getLineCount(path)

	acc = 0
	beg = lines // 2

	for line in islice(src, beg):
		dst.write(line)
		if line.find("W") != -1:
			acc += int(line.split()[3])
		if acc >= size:
			break

	src.close()
	dst.close()


for path in tqdm(argv[1:]):
	sample(path, path.replace(".trace", "_sampled.trace"))
