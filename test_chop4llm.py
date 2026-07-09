"""
Test script for Chop4LLM.

Tests with examples that demonstrate the difference between
variable-name slicing (fake) and PDG-based logical slicing (real).
"""

import sys
sys.path.insert(0, '.')

from chop4llm import chop_method, compare_approaches


# ─── Test 1: Discount Bug (from your document) ─────────────────────────
# NOTE: Raw strings start with \n, so line numbers below are from
# the raw string content. The assert is on line 12 (0-based counting from \n).

JAVA_DISCOUNT_BUG = """
public class DiscountCalculator {
    public static double calculateDiscount(int userLevel, double price) {
        double discount = 0;
        if (userLevel > 0) {
            discount = userLevel * 5;
        }
        if (userLevel == 3) {
            discount = discount + 10;
        }
        double finalPrice = price - discount;
        assert discount <= 20 : "discount exceeds max";
        return finalPrice;
    }
}
"""

# ─── Test 2: Simple def-use chain ──────────────────────────────────────

JAVA_SIMPLE = """
public class Example {
    public int compute(int x) {
        int a = x + 1;
        int b = a * 2;
        int c = b - 3;
        return c;
    }
}
"""

# ─── Test 3: Control dependency example ─────────────────────────────────

JAVA_CONTROL = """
public class Controller {
    public int process(int x) {
        int result = 0;
        if (x > 0) {
            result = x * 2;
        } else {
            result = x + 10;
        }
        return result;
    }
}
"""

# ─── Test 4: No-bug case — backward should include y++, but chop filters ──

JAVA_NO_BUG = """
public class Example2 {
    public int check(int x) {
        int y = 0;
        y = y + 1;
        if (x > 0) {
            y = y * 2;
        }
        return y;
    }
}
"""


def run_test(name, source, sink_line, source_line=None):
    print("=" * 70)
    print(f"TEST: {name}")
    print("=" * 70)

    try:
        result = chop_method(
            source,
            sink_line=sink_line,
            source_line=source_line,
            auto_source=True,
            template="bug_find",
        )
        print(f"  Result: {result}")
        print()
        print("  Slice contents:")
        for node in result.slice_nodes:
            markers = []
            if node.id in result.source_ids: markers.append("SOURCE")
            if node.id in result.sink_ids: markers.append("SINK")
            m = f" [{'|'.join(markers)}]" if markers else ""
            print(f"    L{node.line}: {node.code[:60]}{m}")
        print()
        print(f"  Compression: {result.original_count} → {result.sliced_count} "
              f"({result.compression_pct:.1f}% reduction)")
        print()

        if source_line:
            comp = compare_approaches(source, sink_line, source_line)
            stats = comp['stats']
            print("  Backward vs Chop comparison:")
            print(f"    Backward: {stats['backward_lines']} stmts ({stats['backward_reduction_pct']:.1f}% reduction)")
            print(f"    Chop:     {stats['chop_lines']} stmts ({stats['chop_reduction_pct']:.1f}% reduction)")

    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()

    print()


if __name__ == "__main__":
    # Helper: count lines in raw string to find correct line numbers
    def find_line(source, keyword):
        for i, line in enumerate(source.split('\n'), 1):
            if keyword in line:
                return i
        return -1

    # Test 1: Backward slice from assert
    sink = find_line(JAVA_DISCOUNT_BUG, "assert")
    print(f"Assert is at line {sink}")
    run_test("Discount Bug (backward from assert)",
             JAVA_DISCOUNT_BUG, sink_line=sink)

    # Test 2: Backward from return c
    sink = find_line(JAVA_SIMPLE, "return c")
    run_test("Simple Def-Use (backward from return c)",
             JAVA_SIMPLE, sink_line=sink)

    # Test 3: Backward from return result
    sink = find_line(JAVA_CONTROL, "return result")
    run_test("Control Dependency (backward from return result)",
             JAVA_CONTROL, sink_line=sink)

    # Test 4: Backward from return y
    sink = find_line(JAVA_NO_BUG, "return y")
    run_test("No-Bug Case (backward from return y)",
             JAVA_NO_BUG, sink_line=sink)

    # Test 5: Chop (bidirectional) — source is userLevel, sink is assert
    print("=" * 70)
    print("TEST 5: Chop — userLevel source → assert sink")
    print("=" * 70)
    sink = find_line(JAVA_DISCOUNT_BUG, "assert")
    source = find_line(JAVA_DISCOUNT_BUG, "double discount = 0")
    try:
        result = chop_method(JAVA_DISCOUNT_BUG, sink_line=sink, source_line=source)
        print(f"  Result: {result}")
        print(f"  Slice contents ({len(result.slice_nodes)} stmts):")
        for node in result.slice_nodes:
            print(f"    L{node.line}: {node.code[:60]}")
        print()
        print("--- LLM Prompt (first 1200 chars) ---")
        print(result.llm_prompt[:1200])
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
