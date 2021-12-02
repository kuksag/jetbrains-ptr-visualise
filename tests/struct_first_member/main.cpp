struct Foo {
  int A = 0;
};

int main() {
  Foo foo{};
  Foo *ptr_foo = &foo;
  int *ptr_foo_a = &foo.A;
  void *void_foo = &foo;
  return 0; // Set a breakpoint here
}
