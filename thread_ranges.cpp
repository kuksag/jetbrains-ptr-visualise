#include <iostream>
#include <windows.h>
#include <intrin.h>
#include <processthreadsapi.h>
#include <winternl.h>
#include <cassert>
#include <string>

typedef struct _THREAD_BASIC_INFORMATION {
    NTSTATUS ExitStatus;
    PVOID TebBaseAddress;
    CLIENT_ID ClientId;
    KAFFINITY AffinityMask;
    KPRIORITY Priority;
    KPRIORITY BasePriority;
} THREAD_BASIC_INFORMATION, *PTHREAD_BASIC_INFORMATION;

std::pair<void *, void *> GetThreadStackRange(HANDLE hProcess, HANDLE hThread) {
    bool loadedManually = false;
    HMODULE module = GetModuleHandle("ntdll.dll");

    if (!module) {
        module = LoadLibrary("ntdll.dll");
        loadedManually = true;
    }

    NTSTATUS (__stdcall *NtQueryInformationThread)(HANDLE ThreadHandle, THREADINFOCLASS ThreadInformationClass,
                                                   PVOID ThreadInformation, ULONG ThreadInformationLength,
                                                   PULONG ReturnLength);
    NtQueryInformationThread = reinterpret_cast<decltype(NtQueryInformationThread)>(GetProcAddress(module,
                                                                                                   "NtQueryInformationThread"));

    if (NtQueryInformationThread) {
        NT_TIB tib = {nullptr};
        THREAD_BASIC_INFORMATION tbi = {0};

        const auto ThreadBasicInformation = static_cast<THREADINFOCLASS>(0);
        NTSTATUS status = NtQueryInformationThread(hThread, ThreadBasicInformation, &tbi, sizeof(tbi), nullptr);
        if (status >= 0) {
            // todo: only 2 values + bitwise check; dealloc stack instead of stack limit
            ReadProcessMemory(hProcess, tbi.TebBaseAddress, &tib, sizeof(tbi), nullptr);

            if (loadedManually) {
                FreeLibrary(module);
            }
            return {tib.StackBase, tib.StackLimit};
        }
    }
    if (loadedManually) {
        FreeLibrary(module);
    }
    return {nullptr, nullptr};
}


int main(int argc, char *argv[]) {
    assert(argc == 3);

    DWORD process_id = std::stoi(argv[1]);
    HANDLE process_handle = OpenProcess(PROCESS_VM_READ,
                                        false,
                                        process_id);

    DWORD thread_id = std::stoi(argv[2]);
    HANDLE thread_handle = OpenThread(THREAD_QUERY_INFORMATION,
                                      false,
                                      thread_id);
    auto result = GetThreadStackRange(process_handle, thread_handle);
    assert(result.first > result.second);
    std::cout << result.second << " " << result.first << '\n';
    CloseHandle(thread_handle);
    CloseHandle(process_handle);
    return 0;
}
