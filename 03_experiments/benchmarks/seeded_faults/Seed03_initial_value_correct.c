int main() {
  int x = 0;
  int z = 11;
  while (x < 10) {
    if (x >= 0) {
      z = z - 1;
    }
    x = x + 1;
  }
  assert(z != 0);
}
