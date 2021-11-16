#include <cstdint>

#pragma pack(push, 1)
struct Foo {
    std::int16_t a;
    std::int8_t b;
    std::int32_t c;
};
#pragma pack(pop)

#pragma pack(push, 8)
struct Bar {
    std::int8_t d;
    std::int64_t e;
};
#pragma pack(pop)

int main() {
    Foo foo{};
    void *pa1 = static_cast<void *>(&foo) + 0;
    void *pa2 = static_cast<void *>(&foo) + 1;
    void *pb1 = static_cast<void *>(&foo) + 2;
    void *pc1 = static_cast<void *>(&foo) + 3;
    void *pc2 = static_cast<void *>(&foo) + 4;
    void *pc3 = static_cast<void *>(&foo) + 5;
    void *pc4 = static_cast<void *>(&foo) + 6;

    Bar bar{};
    void *pd1 = static_cast<void *>(&bar) + 7;
    void *pd2 = static_cast<void *>(&bar) + 8;
    return 0; // Set a breakpoint here
}
