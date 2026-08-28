int main() {
  int x = 10;
  int z = 10;
  while (x < 20) {
    if (x == 9) {
      z = z - 2;
    } else {
      z = z - 1;
    }
    x = x + 1;
  }
  assert(z != 0);
}
