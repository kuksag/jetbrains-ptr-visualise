#include <thread>

int main() {
    int A;
    std::thread thread1([&]() {
        int B;
        std::thread thread2([&]() {
            int C;
            std::thread thread3([&]() {
                int *a = &A;
                int *b = &B;
                int *c = &C;
                return; // Set a breakpoint here
            });
            thread3.join();
        });
        thread2.join();
    });
    thread1.join();
    return 0;
}
