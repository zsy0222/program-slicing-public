int main() {
  int x = 0;
  int z = 10;
  while (x < 30) {
    if (x > 20) {
      z = z - 1;
    }
    x = x + 1;
  }
  assert(z != 0);
}
