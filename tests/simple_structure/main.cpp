struct Foo {
    int A = 1;
    double B = 2;
    bool C = 0;
};

int main() {
    Foo foo{};
    int *a = &foo.A;
    double *b = &foo.B;
    bool *c = &foo.C;
    return 0; // Set a breakpoint here
}
