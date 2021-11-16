union U {
    int A;
    double B;
};

int main() {
    U a;
    a.A = static_cast<int>(0);
    int *pa = &a.A;

    U b;
    b.B = static_cast<double>(2.0);
    double *pb = &b.B;

    return 0; // Set a breakpoint here
}
