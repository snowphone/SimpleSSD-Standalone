#!/usr/bin/env python3


from tqdm import tqdm
from sys import argv

q = tqdm()
with open(argv[1], "rt") as f:
		current = int(f.readline().split()[0])
		while True:
			q.update()
			prev = current
			line = f.readline()
			if not line:
				break
			current = int(line.split()[0])
			if not (prev <= current):
				#raise Exception(f"Problem tick: {current}")
				print(f"Problem tick: {current}")
