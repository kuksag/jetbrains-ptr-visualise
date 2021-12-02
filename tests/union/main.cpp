union Union1 {
    int A;
    double B;
};

union Union2 {
    struct {
        float x;
        int y;
    } A;
    struct {
        int w;
        int z;
    } B;
};

int main() {
//  ====================================
    Union1 foo;
    foo.A = static_cast<int>(0);
    int *pointer_foo_a = &foo.A;
//  ====================================
    Union1 bar;
    bar.B = static_cast<double>(2.0);
    double *pointer_bar_b = &bar.B;
//  ====================================
    Union2 baz;
    baz.A = {2.0, 3};
    float *pointer_baz_x = &baz.A.x;
    int *pointer_baz_y = &baz.A.y;
    void *void_pointer_baz_x = &baz.A.x;
    void *void_pointer_baz_y = &baz.A.y;
//  ====================================
    Union2 qux;
    qux.B = {4, 5};
    int *pointer_qux_w = &qux.B.w;
    int *pointer_qux_z = &qux.B.z;
    void *void_qux_w = &qux.B.w;
    void *void_qux_z = &qux.B.z;
//  ====================================
    return 0; // Set a breakpoint here
}
