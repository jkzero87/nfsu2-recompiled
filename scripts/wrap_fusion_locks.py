"""Put Fusion Fix locks in front of four lifted SPEED2.EXE functions.

Renames each lifted body to orig_sub_<VA> and defines sub_<VA> as a wrapper
that holds nfs_fusion_lock(<index>) around it, so direct calls and the
dispatch table both go through the lock. Index 0 is the "bf:" file device,
1 the bWare allocator (see guest_runtime.cpp). Run after run_lift.py lift;
running it again changes nothing.

Usage: python wrap_fusion_locks.py <src/recomp/gen>
"""
import os
import sys

TARGETS = {0x006F69E6: 0, 0x006F69B2: 0, 0x00440390: 1, 0x00440540: 1}


def main(gen):
    found = set()
    for name in sorted(os.listdir(gen)):
        if not (name.startswith("recomp_") and name.endswith(".c")):
            continue
        path = os.path.join(gen, name)
        text = open(path, encoding="utf-8", newline="").read()
        wrappers = []
        for va, index in TARGETS.items():
            definition = f"\nvoid sub_{va:08X}(void) {{"
            if f"orig_sub_{va:08X}" in text:
                found.add(va)
                continue
            if definition not in text:
                continue
            text = text.replace(definition, f"\nvoid orig_sub_{va:08X}(void) {{", 1)
            wrappers.append(
                f"void orig_sub_{va:08X}(void);\n"
                f"void sub_{va:08X}(void) {{ nfs_fusion_lock({index}); orig_sub_{va:08X}(); nfs_fusion_unlock({index}); }}\n")
            found.add(va)
        if wrappers:
            marker = "#include <string.h>\n"
            head, sep, tail = text.partition(marker)
            if not sep:
                sys.exit(f"{path}: include marker missing")
            text = head + sep + "\nvoid nfs_fusion_lock(int which);\nvoid nfs_fusion_unlock(int which);\n" + "".join(wrappers) + tail
            open(path, "w", encoding="utf-8", newline="").write(text)
            print(f"{name}: wrapped {len(wrappers)}")
    missing = [f"0x{va:08X}" for va in TARGETS if va not in found]
    if missing:
        sys.exit("lifted functions not found: " + ", ".join(missing))
    print("FUSION_LOCKS_OK")


if __name__ == "__main__":
    main(sys.argv[1])
