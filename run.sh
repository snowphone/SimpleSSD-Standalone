folder=results/512MiB
parallel --sshdelay 0.1 --sshlogin 8/localhost,4/n0001,8/n0002,4/n0003,4/n0004,4/n0005,4/n0006,4/n0007,4/n0008,4/n0009,4/n0010,8/n0011,8/n0012,4/n0013,8/n0014,8/n0015 --shuf --eta --tmuxpane \
	cd simplessd-standalone \&\& time ./simplessd-standalone {1} {2} "$folder"/{1/.}/{2/.} \
	::: config/bs_sampled.cfg config/dap_sampled.cfg \
		config/ddr_sampled.cfg config/exchange_sampled.cfg \
		config/lmbe_sampled.cfg config/msnfs_sampled.cfg \
		config/ycsb_sampled.cfg \
	::: simplessd/config/full_0.12_30.cfg simplessd/config/full_0.12_optimized_30.cfg \
		simplessd/config/full_0.25_30.cfg simplessd/config/full_0.25_optimized_30.cfg \
		simplessd/config/full_0.47_30.cfg simplessd/config/full_0.47_optimized_30.cfg
