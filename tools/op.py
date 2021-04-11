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
	analyze(argv[1:])


def analyze(paths: List[str]):
	fn = lambda x: (x.traceConfig, float(x.ssdConfig.replace("op", "")))
	stats = sorted( readRecords(paths), key=fn)

	lst = map(str, ["Trace", "Over-provisioning ratio", "Average valid pages", "Reclaimed blocks", "GC", "Throughput"])
	print(",".join(lst))

	for stat in stats:
		valid = max(stat.statistics, key=lambda x: x["host_time"])
		vVal = valid["ftl.page_mapping.valid_pages"]
		vRclm = valid["ftl.page_mapping.gc.reclaimed_blocks"]
		gc = valid["ftl.page_mapping.gc.count"]
		bndwth = valid["cum_bandwidth"]
		lst = map(str, [stat.traceConfig.replace("_50", ""), stat.ssdConfig.replace("op", ""), vVal, vRclm, gc, bndwth])
		print(",".join(lst))


def readRecords(paths: List[str]) -> List[Record]:
	stats: List[Record] = []
	for path in paths:
		pathList = glob(f"{path}/**/log.json", recursive=True)
		stats.extend([
		    Record(**it) for it in map(lambda x: load(open(x, "rt")), pathList)
		])
	return stats


if __name__ == "__main__":
	main(argv)
