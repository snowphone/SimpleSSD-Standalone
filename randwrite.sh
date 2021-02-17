folder=results/faster
parallel --sshdelay 0.1 --sshlogin 1/n0001,1/n0002,1/n0003,1/n0004,1/n0005,1/n0006  --shuf --eta --tmuxpane \
	cd simplessd-standalone \&\& time ./simplessd-standalone {1} {2} "$folder"/{1/.}/{2/.} \
	::: config/randwrite.cfg \
	::: simplessd/config/small.cfg simplessd/config/small_optimized.cfg simplessd/config/worse.cfg simplessd/config/worse_optimized.cfg simplessd/config/worst.cfg simplessd/config/worst_optimized.cfg
	#::: config/msnfs.cfg config/msnfs_writeonly.cfg config/exchange.cfg config/exchange_writeonly.cfg config/ycsb.cfg config/ycsb_writeonly.cfg config/randwrite.cfg \
	#::: simplessd/config/mine.cfg simplessd/config/mine_optimized.cfg
