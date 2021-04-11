folder=results/overprovisioning
parallel --eta --tmuxpane \
	./simplessd-standalone {1} {2} "$folder"/{1/.}/{2/.} \
	::: config/ycsb_70.cfg \
	::: simplessd/config/op14.cfg simplessd/config/op28.cfg simplessd/config/op7.cfg
