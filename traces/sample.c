#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef unsigned int uint;

uint lineCount(const char *path);
void sample(const char *path, const char *dstPath);
const char *getDstPath(const char *src);

int main(int argc, const char *argv[]) {
  for (const char **pathIter = argv + 1; *pathIter; ++pathIter) {
    const char *dst = getDstPath(*pathIter);
    sample(*pathIter, dst);
    printf("%s ->  %s\n", *pathIter, dst);
  }

  return 0;
}

const char *getDstPath(const char *src) {
  // Example: temp.trace -> temp_sampled.trace
  static char buf[256];
  strcpy(buf, src);

  char *it = strstr(buf, ".trace");
  strcpy(it, "_sampled.trace");
  return buf;
}

uint lineCount(const char *path) {
  FILE *fp = fopen(path, "rt");
  char buf[256];
  uint lineNum = 0;

  while (fgets(buf, sizeof buf, fp)) {
    lineNum++;
  }

  fclose(fp);
  return lineNum;
}

void sample(const char *path, const char *dstPath) {
  float sampleRatio = 0.0234;
  uint lineNum = lineCount(path);
  uint beg = lineNum / 2;
  uint end = beg + lineNum * sampleRatio + 1;

  FILE *src = fopen(path, "rt");
  FILE *dst = fopen(dstPath, "wt");
  char buf[256];

  // Skip
  for (uint i = 1; i < beg; ++i) {
    fgets(buf, sizeof buf, src);
  }

  // Copy
  for (uint i = beg; i < end; ++i) {
    fgets(buf, sizeof buf, src);
    uint len = strlen(buf);
    fwrite(buf, 1, len, dst);
  }

  fclose(src);
  fclose(dst);
}
