#!/usr/bin/env python3.8

from glob import glob
from itertools import groupby
from json import load
from math import isnan
from statistics import mean
from sys import argv
from typing import Dict, List, Tuple

from Record import Record


def main(argv: List[str]):
	results = normalize(argv[1:])
	results = calculateAverages(results)
	printRecords(results)


def normalize(paths: List[str]) -> List[Record]:
	stats = readRecords(paths)
	pairList = sorted(makeThemPair(stats))

	results = []

	for base, opt in pairList:
		rec = Record(base.name, base.traceConfig, base.ssdConfig, "normalized", 0, [{}])

		rec.latency = opt.latency / base.latency

		baseLastStat = max(base.statistics, key=lambda x: x["host_time"])
		optLastStat = max(opt.statistics, key=lambda x: x["host_time"])

		for key in [
			"cum_bandwidth",
			"ftl.page_mapping.gc.reclaimed_blocks",
			"ftl.page_mapping.valid_pages",
		]:
			baseValue, optValue = map(lambda x: x[key],
			                          [baseLastStat, optLastStat])
			try:
				normalized = optValue / baseValue
			except:
				normalized = float("nan")
			rec.statistics[0][key] = normalized
		
		rec.statistics[0]["WA"] = WA(optLastStat) / WA(baseLastStat)

		results.append(rec)

	return results

def WA(stat: Dict[str, float]) -> float:
	'''
	Actual writes / host writes
	'''
	sz = stat["write.bytes"]
	page_sz = 16384
	pages = stat["ftl.page_mapping.gc.page_copies"]
	return (sz + page_sz * pages) / sz


def calculateAverages(records: List[Record]):
	keyFunc = lambda x: (x.name, x.ssdConfig, x.scheme)
	avgs = []
	for (name, ssd, scheme), group in groupby(sorted(records, key=keyFunc),
	                                  key=keyFunc):
		group = list(group)
		avg = Record(name, f"average", ssd, scheme, 0, [{}])
		avg.latency = mean(i.latency for i in group)
		for key in records[0].statistics[0].keys():
			values = [i.statistics[0][key] for i in group if not isnan(i.statistics[0][key]) ]
			avg.statistics[0][key] = mean(values)

		avgs.append(avg)
	def k(x: Record):
		return (x.name, x.traceConfig, float(x.ssdConfig))
	return sorted(records, key=k) + sorted(avgs, key=k)


def printRecords(records: List[Record]):
	keys = [
	    "Characteristics", "Trace", "SSD", "Latency", "Bandwidth", "Reclaimed blocks", "Valid pages", "Write amplification"
	]
	print(",".join(keys))
	for rec in records:
		values = [rec.name, rec.traceConfig, rec.ssdConfig, rec.latency]
		for v in rec.statistics[0].values():
			values.append(v)
		print(",".join(
		    [v if isinstance(v, str) else f"{v:.3f}" for v in values]))


def makeThemPair(stats: List[Record]) -> List[Tuple[Record, Record]]:
	baselineList = {it for it in stats if it.scheme == "baseline"}
	optimizedList = set(stats) - baselineList

	return [(it, jt)
	  for it in baselineList
	  for jt in optimizedList
	            if it.name == jt.name and \
                    it.traceConfig == jt.traceConfig and \
                   it.ssdConfig == jt.ssdConfig]


def readRecords(paths: List[str]) -> List[Record]:
	stats = []
	for path in paths:
		pathList = glob(f"{path}/**/log.json", recursive=True)
		stats.extend([
	    Record(**it) for it in map(lambda x: load(open(x, "rt")), pathList)
	])
	return stats


if __name__ == "__main__":
	main(argv)
