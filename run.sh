folder=results/withAlibaba_12GB
parallel --eta --tmuxpane \
	time ./simplessd-standalone {1} {2} "$folder"/{1/.}/{2/.} \
	::: config/alibaba_sampled.cfg \
		config/exchange_sampled.cfg \
		config/msnfs_sampled.cfg \
		config/ycsb_sampled.cfg \
	::: simplessd/config/full_0.12_30.cfg simplessd/config/full_0.12_optimized_30.cfg \
		simplessd/config/full_0.25_30.cfg simplessd/config/full_0.25_optimized_30.cfg \
		simplessd/config/full_0.47_30.cfg simplessd/config/full_0.47_optimized_30.cfg
