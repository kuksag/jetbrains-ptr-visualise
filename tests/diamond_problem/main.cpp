struct Top {
    int A;
};

struct Left : virtual Top {
    long long B;
};

struct Right : virtual Top {
    double C;
};

struct Bottom : Left, Right {
    bool D;
};


int main() {
    Bottom bottom{};

    Top *top = &bottom;
    Left *left = &bottom;
    Right *right = &bottom;

    int *a = &bottom.A;
    long long *b = &bottom.B;
    double *c = &bottom.C;
    bool *d = &bottom.D;

    return 0; // Set a breakpoint here
}
