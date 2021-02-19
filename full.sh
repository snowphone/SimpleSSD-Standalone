folder=results/fullSSD
parallel --sshdelay 0.1 --sshlogin 6/localhost,6/n0002,6/n0011,6/n0012,6/n0014,6/n0015 --shuf --eta --tmuxpane \
	cd simplessd-standalone \&\& time ./simplessd-standalone {1} {2} "$folder"/{1/.}/{2/.} \
	::: config/ycsb_12GB.cfg config/msnfs_12GB.cfg config/exchange_12GB.cfg \
		config/ycsb_8GB.cfg config/msnfs_8GB.cfg config/exchange_8GB.cfg \
	::: simplessd/config/full_small_10.cfg simplessd/config/full_small_optimized_10.cfg \
		simplessd/config/full_worse_30.cfg simplessd/config/full_worse_optimized_30.cfg \
		simplessd/config/full_worst_30.cfg simplessd/config/full_worst_optimized_30.cfg 
	#::: config/msnfs.cfg config/msnfs_writeonly.cfg config/exchange.cfg config/exchange_writeonly.cfg config/ycsb.cfg config/ycsb_writeonly.cfg config/randwrite.cfg \
	#::: simplessd/config/mine.cfg simplessd/config/mine_optimized.cfg
