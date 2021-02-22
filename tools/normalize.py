#!/usr/bin/env python3.8

from glob import glob
from itertools import groupby
from json import load
from statistics import mean
from sys import argv
from typing import List, Tuple

try:
	from .Record import Record
except:
	from Record import Record


def main(argv: List[str]):
	results: List[Record] = []
	for traceLevelPath in argv[1:]:
		results.extend(normalize(traceLevelPath))
	results = calculateAverages(results)
	printRecords(results)


def normalize(path: str):
	stats = readRecords(path)
	pairList = sorted(makeThemPair(stats))

	results = []

	for base, opt in pairList:
		rec = Record(base.name, base.traceConfig, base.ssdConfig, 0, [{}])

		rec.latency = opt.latency / base.latency

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
				normalized = optValue / baseValue
			except:
				normalized = float("nan")
			rec.statistics[0][key] = normalized
		results.append(rec)

	return results


def calculateAverages(records: List[Record]):
	keyFunc = lambda x: (x.name, x.ssdConfig)
	avgs = []
	for (name, ssd), group in groupby(sorted(records, key=keyFunc),
	                                  key=keyFunc):
		group = list(group)
		avg = Record(name, f"average", ssd, 0, [{}])
		avg.latency = mean(i.latency for i in group)
		for key in records[0].statistics[0].keys():
			avg.statistics[0][key] = mean(i.statistics[0][key] for i in group)

		avgs.append(avg)
	return sorted(records + avgs)


def printRecords(records: List[Record]):
	keys = [
	    "Characteristics", "trace", "SSD", "latency", "GC", "reclaimed blocks",
	    "page copies"
	]
	print(",".join(keys))
	for rec in records:
		values = [rec.name, rec.traceConfig, rec.ssdConfig, rec.latency]
		for v in rec.statistics[0].values():
			values.append(v)
		print(",".join(
		    [v if isinstance(v, str) else f"{v:.3f}" for v in values]))


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
