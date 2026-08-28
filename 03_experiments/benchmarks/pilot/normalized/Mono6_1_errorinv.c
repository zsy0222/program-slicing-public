/*
 * Normalized from SV-COMP loops-crafted-1/Mono6_1.c.
 * All original unsigned values stay in signed-int range along this path.
 * Verifier wrappers are removed and the failed property is preserved.
 */
int main() {
  int x = 0;
  int y = 10000000;
  int z = 5000000;
  while (x < y) {
    if (x >= 5000000) {
      z = z + 1;
    }
    x = x + 1;
  }
  assert(z != x);
}
