folder=results/extension
parallel --sshdelay 0.1 --sshlogin 8/localhost,4/n0001,8/n0002,4/n0003,4/n0004,4/n0005,4/n0006,4/n0007,4/n0008,4/n0009,4/n0010,8/n0011,8/n0012,4/n0013,8/n0014,8/n0015 --shuf --eta --tmuxpane \
	cd simplessd-standalone \&\& time ./simplessd-standalone {1} {2} "$folder"/{1/.}/{2/.} \
	::: config/msnfs_sampled.cfg config/msnfs_writeonly_sampled.cfg config/exchange_sampled.cfg config/exchange_writeonly_sampled.cfg config/ycsb_sampled.cfg config/ycsb_writeonly_sampled.cfg config/randwrite.cfg \
	::: simplessd/config/small.cfg simplessd/config/small_optimized.cfg simplessd/config/worse.cfg simplessd/config/worse_optimized.cfg simplessd/config/worst.cfg simplessd/config/worst_optimized.cfg simplessd/config/small_10.cfg simplessd/config/small_optimized_10.cfg simplessd/config/worse_10.cfg simplessd/config/worse_optimized_10.cfg simplessd/config/worst_10.cfg simplessd/config/worst_optimized_10.cfg simplessd/config/small_30.cfg simplessd/config/small_optimized_30.cfg simplessd/config/worse_30.cfg simplessd/config/worse_optimized_30.cfg simplessd/config/worst_30.cfg simplessd/config/worst_optimized_30.cfg
	#::: config/msnfs.cfg config/msnfs_writeonly.cfg config/exchange.cfg config/exchange_writeonly.cfg config/ycsb.cfg config/ycsb_writeonly.cfg config/randwrite.cfg \
	#::: simplessd/config/mine.cfg simplessd/config/mine_optimized.cfg
