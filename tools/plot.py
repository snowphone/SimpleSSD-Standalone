#!/usr/bin/env python3.8

from itertools import count
from json import load
from sys import argv
from typing import List
import matplotlib

import matplotlib.pyplot as plt
from matplotlib.pyplot import axes
import pandas as pd


def main(argv: List[str]):
	for arg in argv[1:]:
		dstPath = arg.replace(".json", ".svg")
		plot(arg, dstPath)
		print(f"{arg} -> {dstPath}")


def plot(path: str, dstPath: str):
	with open(path, "rt") as f:
		stats: dict = load(f)
	x = [i["host_time"] for i in stats]
	x_label = "host time"
	y_list = [
	    ("gc count", [i["ftl.page_mapping.gc.count"] for i in stats]),
	    ("reclaimed blocks",
	     [i["ftl.page_mapping.gc.reclaimed_blocks"] for i in stats]),
	    ("page copies", [i["ftl.page_mapping.gc.page_copies"] for i in stats]),
	]

	colors = ['r', 'g', 'b']
	fig, ax = plt.subplots()
	fig.subplots_adjust(right=0.75)
	plots= []

	for (y_label, y), color, i in zip(y_list, colors, count(0)):
		if i >= 2:
			ax.spines["right"].set_position(("axes", 1 + 0.1 * i))
			ax.set_frame_on(True)
			ax.patch.set_visible(False)
			for sp in ax.spines.values():
				sp.set_visible(False)
			ax.spines["right"].set_visible(True)

		p, = ax.plot(x, y, color=color, label=y_label, linewidth=0.5 - 0.12 * i)
		#ax.set_xlim(min(x), max(x))
		#ax.set_ylim(min(y), max(y))
		ax.set_xlabel(x_label)
		ax.set_ylabel(y_label, color=color)
		#ax.set_yscale("log")
		plots.append(p)
		ax.tick_params(axis='y', labelcolor=color, size=4, width=1.5)
		if i + 1 != len(y_list):
			ax = ax.twinx()

	#fig.tight_layout()
	fig.legend(plots, [i.get_label() for i in plots])
	plt.savefig(dstPath)



if __name__ == "__main__":
	main(argv)
