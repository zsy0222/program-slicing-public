/*
 * Normalized input for the Error Invariants prototype.
 *
 * Provenance: SV-COMP loop-invgen/down.c.
 * The original nondeterministic integer is represented as a main parameter;
 * the loop structure and the assertion are unchanged.
 */
int main(int n) {
  int k = 0;
  int i = 0;

  while (i < n) {
    i = i + 1;
    k = k + 1;
  }

  int j = n;
  while (j > 0) {
    assert(k > 0);
    j = j - 1;
    k = k - 1;
  }
}
