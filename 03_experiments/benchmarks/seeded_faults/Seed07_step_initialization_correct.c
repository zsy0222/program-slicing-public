int main() {
  int x = 0;
  int z = 10;
  int step = 2;
  while (x < 20) {
    if (x >= 10) {
      z = z - step;
    }
    x = x + 1;
  }
  assert(z != 0);
}
