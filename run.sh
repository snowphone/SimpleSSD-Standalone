folder=results/miniature
parallel --sshdelay 0.1 --sshlogin n0006,n0010 --shuf --eta \
	cd simplessd-standalone \&\& time ./simplessd-standalone {1} {2} "$folder"/{1/.}/{2/.} \
	::: config/msnfs_sampled.cfg config/msnfs_writeonly_sampled.cfg config/exchange_sampled.cfg config/exchange_writeonly_sampled.cfg config/ycsb_sampled.cfg config/ycsb_writeonly_sampled.cfg config/randwrite.cfg \
	::: simplessd/config/small.cfg simplessd/config/small_optimized.cfg
	#::: config/msnfs.cfg config/msnfs_writeonly.cfg config/exchange.cfg config/exchange_writeonly.cfg config/ycsb.cfg config/ycsb_writeonly.cfg config/randwrite.cfg \
	#::: simplessd/config/mine.cfg simplessd/config/mine_optimized.cfg
