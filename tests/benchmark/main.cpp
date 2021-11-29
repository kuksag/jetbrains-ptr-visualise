#include <thread>
#include <vector>

const int RECURSION_LEVEL = 1000;
const int THREAD_COUNT = 300;

void foo(int level = 0) {
    int A = 0;
    int *a = &A;
    int *b = &A;
    int *c = &A;
    int *d = &A;
    int *e = &A;
    int *f = &A;
    int *g = &A;
    int *j = &A;
    if (level >= RECURSION_LEVEL) {
        return; // Set a breakpoint here
    }
    foo(level + 1);
}

int main() {
    std::vector<std::thread> threads;
    for (int i = 0; i < THREAD_COUNT; i++) {
        threads.emplace_back([&]() {
            foo();
        });
    }
    for (int i = 0; i < THREAD_COUNT; i++) {
        threads[i].join();
    }
    return 0;
}
