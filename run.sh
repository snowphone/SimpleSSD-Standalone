folder=results/threeDifferentCases
parallel --sshdelay 0.1 --sshlogin 8/n0011,8/n0012,8/n0014,8/n0015 --shuf --eta --tmuxpane \
	cd simplessd-standalone \&\& time ./simplessd-standalone {1} {2} "$folder"/{1/.}/{2/.} \
	::: config/msnfs_sampled.cfg config/msnfs_writeonly_sampled.cfg config/exchange_sampled.cfg config/exchange_writeonly_sampled.cfg config/ycsb_sampled.cfg config/ycsb_writeonly_sampled.cfg \
	::: simplessd/config/small.cfg simplessd/config/small_optimized.cfg simplessd/config/worse.cfg simplessd/config/worse_optimized.cfg simplessd/config/worst.cfg simplessd/config/worst_optimized.cfg
	#::: config/msnfs.cfg config/msnfs_writeonly.cfg config/exchange.cfg config/exchange_writeonly.cfg config/ycsb.cfg config/ycsb_writeonly.cfg config/randwrite.cfg \
	#::: simplessd/config/mine.cfg simplessd/config/mine_optimized.cfg
