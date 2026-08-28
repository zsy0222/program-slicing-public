/*
 * Normalized from SV-COMP loops-crafted-1/Mono3_1.c.
 * Verifier wrappers and unsigned declarations are removed. All values remain
 * within signed-int range on the relevant path; the loop and failed property
 * are preserved.
 */
int main() {
  int x = 0;
  int y = 0;
  while (x < 1000000) {
    if (x < 500000) {
      y = y + 1;
    } else {
      y = y - 1;
    }
    x = x + 1;
  }
  assert(y != 0);
}
