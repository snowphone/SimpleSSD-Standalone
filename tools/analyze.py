#!/usr/bin/env python3.8

from dataclasses import asdict, dataclass
from json import dump
import os
from pathlib import Path
import re
from sys import argv
from typing import Dict, IO, List, Union

@dataclass(order=True)
class Record:
	name: str
	traceConfig: str
	ssdConfig: str
	statistics: List[Dict[str, float]]

def main(argv: List[str]):
	for arg in argv[1:]:
		analyze(arg)
		print(arg)

def analyze(path: str):
	f = open(path, "rt")

	p = Path(path)
	ssdConfig = p.parents[0].name
	traceConfig = p.parents[1].name
	name = p.parents[2].name

	stat = Record(name, traceConfig, ssdConfig, [])
	while token := tokenize(f):
		stat.statistics.append(token)
	f.close()


	saveJson(stat, path.replace(".txt", ".json"))
	saveCsv(stat, path.replace(".txt", ".csv"))

def saveJson(stat: Record, dstPath: str):
	with open(dstPath, "wt") as dst:
		dump(asdict(stat), dst, indent=2)

def saveCsv(stat: Record, dstPath: str, saveHeader=True):
	if saveHeader:
		data = [",".join(["name", "trace", "SSD", *stat.statistics[0].keys()]) + '\n'] + \
			[",".join([stat.name, stat.traceConfig, stat.ssdConfig, *map(str, i.values())]) + '\n' for i in stat.statistics]
	else:
		data = [",".join([stat.name, stat.traceConfig, stat.ssdConfig, *map(str, i.values())]) + '\n' for i in stat.statistics]
	with open(dstPath, "wt") as dst:
		dst.writelines(data)

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
