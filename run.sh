folder=results/compensated
parallel --sshdelay 0.1 --sshlogin 8/n0011 --sshlogin 8/n0012 --sshlogin 8/n0002 --eta \
	cd simplessd-standalone \&\& time ./simplessd-standalone {1} {2} "$folder"/{1/.}_{2/.} \; notify {1/.}_{2/.} " done" \
	::: config/msnfs.cfg config/msnfs_onlyWrites.cfg config/exchange.cfg config/exchange_onlyWrites.cfg config/ycsb.cfg config/ycsb_onlyWrites.cfg config/randwrite.cfg \
	::: simplessd/config/intel750_400gb.cfg simplessd/config/original_toshiba.cfg simplessd/config/toshiba_optimized.cfg
