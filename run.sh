folder=results/renaming
parallel --sshdelay 0.1 --sshlogin 2/n0006,2/n0010 --shuf --eta \
	cd simplessd-standalone \&\& time ./simplessd-standalone {1} {2} "$folder"/{1/.}/{2/.} \
	::: config/msnfs.cfg config/msnfs_writeonly.cfg config/exchange.cfg config/exchange_writeonly.cfg config/ycsb.cfg config/ycsb_writeonly.cfg config/randwrite.cfg \
	::: simplessd/config/mine.cfg simplessd/config/mine_optimized.cfg
