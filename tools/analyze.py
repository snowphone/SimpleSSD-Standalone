#!/usr/bin/env python3.8

from json import dump
import re
from sys import argv
from typing import IO, List, Union

def main(argv: List[str]):
	for arg in argv[1:]:
		analyze(arg)
		print(arg)

def analyze(path: str):
	f = open(path, "rt")
	logs = []
	while token := tokenize(f):
		logs.append(token)
	f.close()

	def saveJson():
		dstPath = path.replace(".txt", ".json")
		with open(dstPath, "wt") as dst:
			dump(logs, dst, indent=2)
	def saveCsv():
		dstPath = path.replace(".txt", ".csv")
		with open(dstPath, "wt") as dst:
			dst.writelines(
					[",".join(logs[0].keys()) + '\n'] + 
					[",".join(map(str, i.values())) + '\n' for i in logs]
					)

	saveJson()
	saveCsv()

def tokenize(f: IO) -> Union[dict, None]: 
	beginPattern = re.compile(r"Periodic log printout @ tick (\d+)")
	statPattern = re.compile(r"([\w.]+)\s+(-?\d+[.]\d+)")
	endPattern = re.compile(r"End of log @ tick \d+")

	periodStats = dict()
	while True:
		line = f.readline()
		if mat := beginPattern.search(line):
			periodStats["host_time"] = int(mat.group(1)) // 1_000_000_000_000 # unit: seconds
		elif mat:= statPattern.search(line):
			periodStats[mat.group(1)] = float(mat.group(2))
		elif endPattern.search(line):
			break
		else:
			return None

	return periodStats



if __name__ == "__main__":
	main(argv)
