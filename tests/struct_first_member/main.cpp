struct Foo {
  int A = 0;
};

int main() {
  Foo F{};
  Foo *f = &F;
  int *a = &F.A;
  return 0; // Set a breakpoint here
}
