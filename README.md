# JetBrains: Pointer Visualise 
Describe pointee location during debug session: specify thread, frame and possible object-candidates

# Use
```
(lldb) command script import script.py
(lldb) tp <pointer> # Get info about <pointer>
(lldb) vp # tp for all pointers in the current frame
```

# Tests
1) Fork [LLVM repo](https://github.com/llvm/llvm-project)
2) Run tests from `lldb/test/API`
