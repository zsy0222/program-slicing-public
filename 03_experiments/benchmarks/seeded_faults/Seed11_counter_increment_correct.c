int main() {
  int x = 0;
  int z = 10;
  while (x < 20) {
    if (x >= 10) {
      z = z - 1;
    }
    x = x + 2;
  }
  assert(z != 0);
}
