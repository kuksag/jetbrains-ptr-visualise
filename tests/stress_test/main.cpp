#include <mutex>
#include <thread>
#include <vector>

std::mutex global;
std::mutex append;

const int RECURSION_LEVEL = 5;
const int THREADS = 5;
int* ptrs[2 * RECURSION_LEVEL * THREADS];
int counter = 0;

struct Foo {
    Foo() {
        bar();
    }
    void bar(int level = 0) {
        int a = 1;
        {
            std::unique_lock<std::mutex> ul(append);
            ptrs[counter] = &a;
            counter++;
        }
        if (level >= RECURSION_LEVEL) {
            return; // Set a breakpoint here
        } else {
            bar(level + 1);
        }
    }
};

int main() {
    std::unique_lock<std::mutex> ul(global);
    std::vector<std::thread> threads;
    for (int i = 0; i < THREADS; i++) {
        threads.emplace_back([&]() {
            Foo foo{};
        });
    }
    ul.unlock();
    for (int i = 0; i < THREADS; i++) {
        threads[i].join();
    }
    return 0;
}
