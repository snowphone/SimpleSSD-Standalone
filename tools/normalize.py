#!/usr/bin/env python3.8

from glob import glob
from json import load
from sys import argv
from typing import List, Tuple

try:
	from .Record import Record
except:
	from Record import Record


def main(argv: List[str]):
	print(
	    "Characteristics,Trace,SSD config,Incr Thruput,Decr'd # GC,Decr'd Reclm'd blocks,Decr'd Pg copies"
	)
	for traceLevelPath in argv[1:]:
		normalize(traceLevelPath)


def normalize(path: str):
	stats = readRecords(path)
	pairList = sorted(makeThemPair(stats))

	for base, opt in pairList:
		values = [base.name, base.traceConfig, base.ssdConfig]

		normalizedThroughput = f"{(base.latency - opt.latency) / opt.latency * 100:.1f}%"
		values.append(normalizedThroughput)

		baseLastStat = max(base.statistics, key=lambda x: x["host_time"])
		optLastStat = max(opt.statistics, key=lambda x: x["host_time"])

		for key in [
		    "ftl.page_mapping.gc.count",
		    "ftl.page_mapping.gc.reclaimed_blocks",
		    "ftl.page_mapping.gc.page_copies"
		]:
			baseValue, optValue = map(lambda x: x[key],
			                          [baseLastStat, optLastStat])
			try:
				normalized = f"{(baseValue - optValue) / baseValue * 100:.1f}%"
			except:
				normalized = "NaN"
			values.append(normalized)

		print(",".join(values))


def makeThemPair(stats: List[Record]) -> List[Tuple[Record, Record]]:
	baselineList = {it for it in stats if it.ssdConfig.find("optimized") == -1}
	optimizedList = set(stats) - baselineList

	return [(it, jt)
	  for it in baselineList
	  for jt in optimizedList
	            if it.name == jt.name and \
              it.traceConfig == jt.traceConfig and \
             it.ssdConfig == jt.ssdConfig.replace("_optimized", "")]


def readRecords(path: str) -> List[Record]:
	pathList = glob(f"{path}/**/log.json", recursive=True)
	stats = [
	    Record(**it) for it in map(lambda x: load(open(x, "rt")), pathList)
	]
	return stats


if __name__ == "__main__":
	main(argv)
