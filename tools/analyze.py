#!/usr/bin/env python3.8

from glob import glob
from pathlib import Path
import re
from sys import argv
from typing import IO, List, Union

from tqdm import tqdm

from Record import Record, saveCsv, saveJson

def main(argv: List[str]):
	paths = []
	for path in argv[1:]:
		paths.extend(glob(f"{path}/**/log.txt", recursive=True))
	for arg in tqdm(paths):
		analyze(arg)

def analyze(path: str):
	f = open(path, "rt")

	p = Path(path)
	scheme = "baseline" if p.parents[0].name.find("optimized") == -1 else "proposal"
	ssdConfig = p.parents[0].name.replace("_optimized", "")
	traceConfig = p.parents[1].name
	name = p.parents[2].name
	latency = getLatency(path)

	stat = Record(name, traceConfig, ssdConfig, scheme, latency, [])
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



def tokenize(f: IO) -> Union[dict, None]: 
	beginPattern = re.compile(r"Periodic log printout @ tick (\d+)")
	statPattern = re.compile(r"([\w.]+)\s+(-?\d+[.]\d+)")
	endPattern = re.compile(r"End of log @ tick \d+")

	periodStats = dict()
	soFarBytes = 0
	soFarTime = 0
	while True:
		line = f.readline()
		if mat := beginPattern.search(line):
			periodStats["host_time"] = int(mat.group(1)) / 1_000_000_000_000 # unit: seconds
		elif mat:= statPattern.search(line):
			periodStats[mat.group(1)] = float(mat.group(2))
			if mat.group(1) == "bytes":
				# Calculate instantaneous bandwidth
				bytes = (periodStats["bytes"] - soFarBytes)
				time = float(periodStats["host_time"] - soFarTime)
				periodStats["bandwidth"] = bytes / time / 1000_000 # unit: MB/s
				periodStats["cum_bandwidth"] = periodStats["bytes"] / periodStats["host_time"] / 1000_000 # unit: MB/s

				soFarBytes = periodStats["bytes"]
				soFarTime = periodStats["host_time"]
		elif endPattern.search(line):
			break
		else:
			return None

	return periodStats



if __name__ == "__main__":
	main(argv)
