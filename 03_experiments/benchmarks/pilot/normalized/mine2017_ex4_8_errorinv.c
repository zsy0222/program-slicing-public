/*
 * Normalized input for the Error Invariants prototype.
 *
 * Provenance: SV-COMP loop-lit/mine2017-ex4.8.c.
 * The verifier wrapper is removed.  A fresh nondeterministic Boolean guard is
 * modeled by assigning b from the prototype's interval syntax before the loop
 * and after each iteration, which preserves the original loop-choice model.
 */
int main() {
  int v = 0;
  int b;
  b = [0, 1];

  while (b == 0) {
    assert(0 <= v);
    assert(v <= 1);
    if (v == 0) {
      v = 1;
    }
    b = [0, 1];
  }
}
