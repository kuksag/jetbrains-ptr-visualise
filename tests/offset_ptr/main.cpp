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
    void *ptr_a = static_cast<void *>(&foo) + 0;
    void *ptr_a_1 = static_cast<void *>(&foo) + 1;
    void *ptr_b = static_cast<void *>(&foo) + 2;
    void *ptr_c = static_cast<void *>(&foo) + 3;
    void *ptr_c_1 = static_cast<void *>(&foo) + 4;
    void *ptr_c_2 = static_cast<void *>(&foo) + 5;
    void *ptr_c_3 = static_cast<void *>(&foo) + 6;

    Bar bar{};
    void *ptr_bar_7 = static_cast<void *>(&bar) + 7;
    void *ptr_e = static_cast<void *>(&bar) + 8;
    return 0; // Set a breakpoint here
}
