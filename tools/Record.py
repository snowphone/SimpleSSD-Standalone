#!/usr/bin/env python3.8

from dataclasses import dataclass
from typing import Dict, List

@dataclass(order=True)
class Record:
	name: str
	traceConfig: str
	ssdConfig: str
	latency: float
	statistics: List[Dict[str, float]]

	def __hash__(self) -> int:
		return "".join([self.name, self.traceConfig, self.ssdConfig]).__hash__()

