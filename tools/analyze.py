#!/usr/bin/env python3.8

from dataclasses import asdict
from json import dump
from pathlib import Path
import re
from sys import argv
from typing import IO, List, Union

try:
	from .Record import Record
except:
	from Record import Record

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
	latency = getLatency(path)

	stat = Record(name, traceConfig, ssdConfig, latency, [])
	while token := tokenize(f):
		stat.statistics.append(token)
	f.close()


	saveJson(stat, path.replace(".txt", ".json"))
	saveCsv(stat, path.replace(".txt", ".csv"))

def getLatency(path: str) -> float:
	path = path.replace("log.txt", "stats.txt")
	pattern = re.compile(r"Latency \((\w+)\): .*avg=(\d+\.\d+)")
	toMilli = {
			"ms": 1,
			"us": 0.001,
			"ns": 0.001 * 0.001,
			"ps": 0.001 * 0.001 * 0.001,
			}
	with open(path, "rt") as f:
		text = f.read()
		match = pattern.search(text)
		unit = match.group(1)
		time = float(match.group(2))
	return time * toMilli[unit] # final unit: milliseconds



def saveJson(stat: Record, dstPath: str):
	with open(dstPath, "wt") as dst:
		dump(asdict(stat), dst, indent=2)

def saveCsv(stat: Record, dstPath: str, saveHeader=True):
	if saveHeader:
		data = [",".join(["name", "trace", "SSD", "latency", *stat.statistics[0].keys()]) + '\n'] + \
			[",".join([stat.name, stat.traceConfig, stat.ssdConfig, str(stat.latency), *map(str, i.values())]) + '\n' for i in stat.statistics]
	else:
		data = [",".join([stat.name, stat.traceConfig, stat.ssdConfig, str(stat.latency), *map(str, i.values())]) + '\n' for i in stat.statistics]
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
