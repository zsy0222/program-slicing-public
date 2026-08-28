/*
 * Normalized from SV-COMP loops-crafted-1/Mono4_1.c.
 * The original values are within signed-int range; verifier wrappers only are
 * removed and the failed property is expressed using native assert syntax.
 */
int main() {
  int x = 0;
  int y = 500000;
  while (x < 1000000) {
    if (x < 500000) {
      x = x + 1;
    } else {
      x = x + 1;
      y = y + 1;
    }
  }
  assert(y != x);
}
