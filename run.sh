folder=results/withoutHotcold
parallel --eta --tmuxpane \
	time ./simplessd-standalone {1} {2} "$folder"/{1/.}/{2/.} \
	::: config/alibaba_sampled.cfg \
		config/exchange_sampled.cfg \
		config/msnfs_sampled.cfg \
		config/systor17_sampled.cfg \
	::: simplessd/config/1e-12.cfg simplessd/config/1e-12_optimized.cfg \
		simplessd/config/5e-12.cfg simplessd/config/5e-12_optimized.cfg \
		simplessd/config/1e-11.cfg simplessd/config/1e-11_optimized.cfg \
		simplessd/config/5e-11.cfg simplessd/config/5e-11_optimized.cfg \
		simplessd/config/1e-10.cfg simplessd/config/1e-10_optimized.cfg \
		simplessd/config/3.32e-11.cfg simplessd/config/3.32e-11_optimized.cfg

