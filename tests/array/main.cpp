#pragma pack(push, 1)
struct Foo {
    int bar[4];
    int baz;
};
#pragma pack(pop)


int main() {
    int array[4];
    int *a = &array[0];
    int *b = &array[1];
    int *c = &array[2];
    int *d = &array[3];

    Foo foo;
    int *qux = &foo.baz;
    void *waldo = &foo.baz;
    return 0; // Set a breakpoint here
}
