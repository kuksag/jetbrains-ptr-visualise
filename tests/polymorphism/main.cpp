
struct Foo {
    int A;
};

struct Bar : Foo {
    double B;
};

struct Baz : Bar {
    long long C;
};

int main() {
    Baz baz{};

    Bar *bar = &baz;
    Foo *foo = &baz;

    int *a = &baz.A;
    double *b = &baz.B;
    long long *c = &baz.C;

    return 0; // Set a breakpoint here
}
