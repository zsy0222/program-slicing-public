/*
 * Normalized input for the Error Invariants prototype.
 *
 * Provenance: SV-COMP loops-crafted-1/Mono5_1.c.
 * The original verifier wrapper (GCC attributes, abort, and
 * __VERIFIER_assert) is replaced by the prototype's native assert syntax.
 * The numerical loop and its assertion are otherwise preserved.  The three
 * unsigned values all remain within the signed-int range on this execution
 * path, so this normalization preserves the relevant arithmetic behaviour.
 */
int main() {
  int x = 0;
  int y = 10000000;
  int z = 5000000;

  while (x < y) {
    if (x >= 5000000) {
      z = z - 1;
    }
    x = x + 1;
  }

  assert(z != 0);
}
