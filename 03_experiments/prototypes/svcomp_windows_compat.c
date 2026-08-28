/*
 * Minimal compatibility shim for executing unchanged SV-COMP C benchmarks
 * with MinGW on Windows.  The benchmarks were authored for glibc, which
 * exposes __assert_fail; MinGW does not provide that symbol.
 */

#include <stdio.h>
#include <stdlib.h>

void __assert_fail(const char *assertion, const char *file,
                   unsigned int line, const char *function) {
  fprintf(stderr, "SV-COMP assertion failure: %s at %s:%u (%s)\n",
          assertion, file, line, function);
  abort();
}
