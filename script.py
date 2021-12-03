#!/usr/bin/env python

import lldb
import json
from time_logger import log_time

PATH_TO_MAPS = '/proc/{}/maps'
OUTPUT_PATTERN = '"{ptr_name}" points to "{obj_name}", that located in "{func_name}", frame #{frame_id}, ' \
                 'of thread #{thread_id} '


def get_threads_with_ranges(process: lldb.SBProcess):
    """
    Gets range of stack for every thread in the process.
    """
    threads = sorted(process.threads, key=lambda x: x.GetFrameAtIndex(0).sp)
    ranges = []
    with open(PATH_TO_MAPS.format(process.id), 'r') as maps:
        for thread in threads:
            for line in maps:

                # Parse '0x12-0x34 56 78' to (0x12, 0x34) and cast to base 10
                left, right = list(map(lambda x: int(x, 16), line.split()[0].split('-')))
                assert left <= right

                if left <= thread.GetFrameAtIndex(0).sp <= right:
                    ranges.append((left, right))
                    break
    return threads, ranges


class PointerMatch:
    def __init__(self):
        self.matches = [[], [], []]
        self.thread = None
        self.frame = None
        self.pointer = None

    def extend(self, other):
        self.matches[0].extend(other.matches[0])
        self.matches[1].extend(other.matches[1])
        self.matches[2].extend(other.matches[2])

    def _get_info_from_matches(self):
        return [list(map(lambda var: var.path, self.matches[0])),
                list(map(lambda var: var.path, self.matches[1])),
                list(map(lambda var: (var.path, self.pointer - int(var.location, 16)), self.matches[2]))]

    def to_json(self, ptr_name=None):
        payload = {
            'frame_id': self.frame.idx,
            'frame_name': self.frame.name,
            'matches': self._get_info_from_matches(),
            'ptr_name': ptr_name,
            'thread_id': self.thread.idx,
        }
        return json.dumps(payload, sort_keys=True, indent=4)

    def to_plain(self, ptr_name=None):
        plain_matches = self._get_info_from_matches()
        plain_matches[2].sort(key=lambda x: x[1])
        match = plain_matches[0] or plain_matches[1] or list(
            map(lambda x: f'{x[0]} + {hex(x[1])}', plain_matches[2][:1]))
        if not match:
            return 'Not found'
        if len(match) == 1:
            match = match[0]
        return OUTPUT_PATTERN.format(ptr_name=ptr_name or hex(self.pointer),
                                     obj_name=match,
                                     func_name=self.frame.name,
                                     frame_id=self.frame.idx,
                                     thread_id=self.thread.idx)


def traverse_var_tree(pointer, var: lldb.SBValue, pointee_type: lldb.SBType = None):
    """
    If var is not a struct or array, then return it.
    Otherwise, look through all members of var and go inside at which pointer points.
    """
    result = PointerMatch()
    if pointee_type == var.type and pointer == int(var.location, 16):
        result.matches[0].append(var)
    elif pointer == int(var.location, 16):
        result.matches[1].append(var)
    else:
        result.matches[2].append(var)

    for i in range(var.num_children):
        child = var.GetChildAtIndex(i)
        location = int(child.location, 16)
        if location <= pointer < location + child.size:
            result.extend(traverse_var_tree(pointer, child, pointee_type))

    return result


def get_thread_for_pointer(pointer, threads, ranges):
    left = -1
    right = len(threads) - 1
    while right - left > 1:
        middle = (left + right) // 2
        if pointer <= ranges[middle][1]:
            right = middle
        else:
            left = middle
    return threads[right] if ranges[right][0] <= pointer <= ranges[right][1] else None


def get_frame_for_pointer(pointer, thread: lldb.SBThread):
    """
    Find the frame that contains pointer or None.
    It works on the assumption that thread.GetFrames() returns frames in increasing CanonicalFrameAddress order
    """
    left = -1
    right = thread.GetNumFrames() - 1
    while right - left > 1:
        middle = (left + right) // 2
        if pointer < thread.GetFrameAtIndex(middle).GetCFA():
            right = middle
        else:
            left = middle
    return thread.GetFrameAtIndex(right) if pointer < thread.GetFrameAtIndex(right).GetCFA() else None


@log_time
def trace_pointer(pointer, process: lldb.SBProcess, pointee_type: lldb.SBType = None):
    """
    Finding thread, stack, function, object to which the pointer points
    """
    thread = get_thread_for_pointer(pointer, *get_threads_with_ranges(process))
    if thread:
        frame = get_frame_for_pointer(pointer, thread)
        if frame:
            for var in frame.GetVariables(True, True, False, True):
                location = int(var.location, 16)
                if location <= pointer < location + var.size:
                    trace = traverse_var_tree(pointer, var, pointee_type)
                    trace.thread = thread
                    trace.frame = frame
                    trace.pointer = pointer
                    return trace
    return None


def visualise_pointer(debugger, command, exe_ctx, result, internal_dict):
    """
    Alias for call from debugger
    """
    # TODO: handle hex
    pointer_match = trace_pointer(int(command), exe_ctx.GetProcess())
    if pointer_match:
        print(pointer_match.to_plain(), file=result)
    else:
        print('Not found', file=result)


@log_time
def visualise_pointers(debugger, command, exe_ctx, result, internal_dict):
    """
    Take all pointers from current frame and find their target
    """
    pointers = list(filter(lambda x: x.type.is_pointer, exe_ctx.GetFrame().GetVariables(True, True, False, True)))
    pointers = list(map(lambda x: (x.data.uint64s[0], x.GetName(), x.type.GetPointeeType()), pointers))
    for pointer, ptr_name, pointee_type in pointers:
        pointer_match = trace_pointer(pointer, exe_ctx.GetProcess(), pointee_type)
        print(pointer_match.to_plain(ptr_name=ptr_name), file=result)


def __lldb_init_module(debugger, internal_dict):
    """
    Code below runs with 'command script import script.py'
    """
    debugger.HandleCommand('command script add -f script.visualise_pointers vp')
    debugger.HandleCommand('command script add -f script.visualise_pointer tp')
