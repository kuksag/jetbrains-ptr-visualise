void bar(int *a, int *b, int D) {
    int C;
    int *c = &C;
    int *d = &D;
} // Set a breakpoint here

void foo(int *a) {
    int B;
    bar(a, &B, B);
}

int main() {
    int A;
    foo(&A);
    return 0;
}
