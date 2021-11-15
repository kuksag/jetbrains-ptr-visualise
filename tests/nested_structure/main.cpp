struct Bar {
    double d;
    long e[5];
};

struct Foo {
    int a = 0;
    Bar b[5];
    bool c = 1;
};

int main() {
    Foo foo{};
    double *D = &foo.b[1].d;
    long *E = &foo.b[2].e[3];
    return 0; // Set a breakpoint here
}
