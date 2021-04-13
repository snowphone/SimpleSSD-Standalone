folder=results/overprovisioning
parallel --eta --tmuxpane \
	./simplessd-standalone {1} {2} "$folder"/{1/.}/{2/.} \
	::: config/alibaba_50.cfg \
		config/msnfs_50.cfg \
		config/exchange_50.cfg \
		config/systor17_50.cfg \
	::: simplessd/config/op14.cfg simplessd/config/op28.cfg simplessd/config/op7.cfg
