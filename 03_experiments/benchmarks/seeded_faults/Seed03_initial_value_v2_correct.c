int main() {
  int x = 0;
  int z = 12;
  while (x < 21) {
    if (x >= 10) {
      z = z - 1;
    }
    x = x + 1;
  }
  assert(z != 0);
}
