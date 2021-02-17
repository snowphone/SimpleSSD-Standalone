#!/usr/bin/env zsh

isfirst=true
dst="$1"/full.csv

truncate -s 0 "$dst"
for p in "$1"/**/log.csv
do
	if [[ $isfirst = "true"  ]]; then
		cat "$p" >> "$dst"
		isfirst=false
	else
		cat "$p" | sed '1d' >> "$dst"
	fi
	echo $p
done
