#include <thread>
#include <vector>

const int RECURSION_LEVEL = 300;
const int THREAD_COUNT = 10;

void foo(int level = 0) {
    if (level >= RECURSION_LEVEL) {
        return; // Set a breakpoint here
    }
    int A = 0;
    int *a = &A;
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