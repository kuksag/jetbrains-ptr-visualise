void bar(int *a, int *b) {
    int C;
    int *c = &C;
} // Set a breakpoint here

void foo(int *a) {
    int B;
    bar(a, &B);
}

int main() {
    int A;
    foo(&A);
    return 0;
}
