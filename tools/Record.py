#!/usr/bin/env python3.8

from dataclasses import asdict, dataclass
from typing import Dict, List
from json import dump


@dataclass(order=True)
class Record:
	name: str
	traceConfig: str
	ssdConfig: str
	latency: float
	statistics: List[Dict[str, float]]

	def __hash__(self) -> int:
		return "".join([self.name, self.traceConfig,
		                self.ssdConfig]).__hash__()


def saveJson(stat: Record, dstPath: str):
	with open(dstPath, "wt") as dst:
		dump(asdict(stat), dst, indent=2)


def saveCsv(stat: Record, dstPath: str, saveHeader=True):
	if saveHeader:
		data = [",".join(["name", "trace", "SSD", "latency", *stat.statistics[0].keys()]) + '\n'] + \
				[",".join([stat.name, stat.traceConfig, stat.ssdConfig, str(stat.latency), *map(str, i.values())]) + '\n' for i in stat.statistics]
	else:
		data = [
		    ",".join([
		        stat.name, stat.traceConfig, stat.ssdConfig,
		        str(stat.latency), *map(str, i.values())
		    ]) + '\n' for i in stat.statistics
		]
	with open(dstPath, "wt") as dst:
		dst.writelines(data)
