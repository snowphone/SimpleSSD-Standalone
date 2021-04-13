#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <unordered_map>
#include <vector>

using namespace std;

typedef struct {
  const char *path;
  uint64_t lines;
  double size;
  double write_size;
  double intensity;
#ifdef HOTNESS
  double hotness; // The fraction of overall address space that 5% of top hot pages take up
#endif
} stat_t;

stat_t get_stat(const char *path) {
  stat_t stat = {
      path, 0, 0, 0, 0, 
#ifdef HOTNESS
	  0,
#endif
  };

  FILE *fp = fopen(path, "rt");
  char buf[256];
  uint64_t begin = 0, end;
  uint64_t size = 0, write_size = 0;
  unordered_map<uint64_t, uint64_t> lba_counter;

  while (fgets(buf, sizeof buf, fp)) {
    uint64_t timestamp, slba, nlba;
    char op;
    sscanf(buf, "%lu 0 %lu %lu %c", &timestamp, &slba, &nlba, &op);

    stat.lines++;
    if (begin == 0) {
      begin = timestamp;
    } else {
      end = timestamp;
    }
    size += nlba * 512;
    if (op == 'W') {
      write_size += nlba * 512;

#ifdef HOTNESS
	  for (uint64_t i = slba; i < slba + nlba; ++i) {
		  lba_counter[i]++;
	  }
#endif
    }
  }


  stat.size = size / 1000000000.;             // unit: GB
  stat.write_size = write_size / 1000000000.; // unit: GB

  stat.intensity = (double)size / (end - begin) * 1000.; // unit: MB/s

#ifdef HOTNESS
  vector<pair<uint64_t, uint64_t>> lba_list;
  copy(lba_counter.begin(), lba_counter.end(), back_inserter(lba_list));
  sort(lba_list.rbegin(), lba_list.rend(), [](auto& l, auto& r) {
		  return l.second < r.second;
		  });
  auto hotEnd = lba_list.begin() + lba_list.size() * 0.05;
  uint64_t hotRequests = 0;
  for(auto it = lba_list.begin(); it != hotEnd; ++it) {
	  hotRequests += it->second;
  }
  stat.hotness = hotRequests / (write_size / 512.);
#endif

  fclose(fp);
  return stat;
}

void print_stat(const stat_t stat) {
  static bool isFirst = true;
  if (isFirst) {
    puts("Path,# of lines,Size (GB),Write size (GB),Bandwidth (MB/s)"
#ifdef HOTNESS
			",Hotness of top 5%% hot pages"
#endif
			);
    isFirst = false;
  }
  printf("%s,%lu,%.3f,%.3f,%f"
#ifdef HOTNESS
		  ",%f"
#endif
		  "\n", stat.path, stat.lines, stat.size,
         stat.write_size, stat.intensity
#ifdef HOTNESS
		 , stat.hotness
#endif
		 );
}

int main(int argc, const char *argv[]) {
  for (int i = 1; i < argc; ++i) {
    const char *path = argv[i];
    stat_t stat = get_stat(path);
    print_stat(stat);
  }

  return 0;
}
