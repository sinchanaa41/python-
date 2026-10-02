

import math

# ---------------- CONFIGURABLE SETTINGS ----------------
INTERNAL_MAX = 60        # internal marks maximum
ENDSEM_WEIGHT = 40       # end-sem is reduced to this (out of 40)
ENDSEM_RAW_MAX = 100     # end-sem paper is written out of this
MIN_ENDSEM_RAW = 40      # minimum raw end-sem marks (out of 100) needed to pass
                         # (set to 0 if your college has no such rule)

# (minimum total out of 100, grade point) -- edit to match your college
GRADE_SCALE = [
    (90, 10),
    (80, 9),
    (70, 8),
    (60, 7),
    (50, 6),
    (40, 5),
]
# -------------------------------------------------------


def read_int(prompt, low, high):
    while True:
        try:
            value = int(input(prompt))
            if low <= value <= high:
                return value
            print(f"  Enter a whole number between {low} and {high}.")
        except ValueError:
            print("  Invalid input. Enter a whole number.")


def read_float(prompt, low, high):
    while True:
        try:
            value = float(input(prompt))
            if low < value <= high:
                return value
            print(f"  Enter a value greater than {low} and up to {high}.")
        except ValueError:
            print("  Invalid input. Enter a number.")


def read_marks(prompt, low, high):
    while True:
        try:
            value = float(input(prompt))
            if low <= value <= high:
                return value
            print(f"  Marks must be between {low} and {high}.")
        except ValueError:
            print("  Invalid input. Enter a number.")


def grade_options(internal):
    """Return the list of grades this subject can still reach (lowest first).

    Each option holds: grade point, end-sem marks out of 100, out of 40,
    and the resulting total out of 100.
    """
    options = []
    for min_total, gp in sorted(GRADE_SCALE, key=lambda x: x[1]):
        needed_scaled = max(0.0, min_total - internal)                 # out of 40
        raw = math.ceil(round(needed_scaled * ENDSEM_RAW_MAX / ENDSEM_WEIGHT, 6))
        raw = max(raw, MIN_ENDSEM_RAW)                                 # pass rule
        if raw <= ENDSEM_RAW_MAX:
            scaled = raw * ENDSEM_WEIGHT / ENDSEM_RAW_MAX
            options.append({
                "gp": gp,
                "raw": raw,
                "scaled": scaled,
                "total": internal + scaled,
            })
    return options


def main():
    print("=" * 60)
    print("   TARGET SGPA CALCULATOR  (Internals 60 + End-Sem 40)")
    print("=" * 60)

    n = read_int("\nNumber of subjects: ", 1, 20)

    subjects = []
    for i in range(1, n + 1):
        print(f"\n--- Subject {i} ---")
        name = input("  Subject name: ").strip() or f"Subject {i}"
        credits = read_float("  Credits: ", 0, 10)
        internal = read_marks(f"  Internal marks (out of {INTERNAL_MAX}): ", 0, INTERNAL_MAX)
        subjects.append({"name": name, "credits": credits, "internal": internal})

    desired = read_float("\nDesired CGPA for this semester (out of 10): ", 0, 10)

    total_credits = sum(s["credits"] for s in subjects)
    target_points = desired * total_credits

    # Work out which grades are reachable for each subject
    for s in subjects:
        s["options"] = grade_options(s["internal"])
        if not s["options"]:
            print(f"\n'{s['name']}' cannot be passed with {s['internal']} internal marks "
                  f"(end-sem alone cannot cover the gap).")
            return
        s["level"] = 0   # start every subject at the lowest passing grade

    min_points = sum(s["credits"] * s["options"][0]["gp"] for s in subjects)
    max_points = sum(s["credits"] * s["options"][-1]["gp"] for s in subjects)
    achievable = max_points + 1e-9 >= target_points

    if not achievable:
        print(f"\nDesired CGPA {desired} is NOT achievable with your internal marks.")
        print(f"Best possible CGPA: {max_points / total_credits:.2f} "
              f"(scoring full marks needed in the end-sems below).")
        for s in subjects:
            s["level"] = len(s["options"]) - 1
    else:
        points = min_points
        # Raise grades evenly: always lift the subject with the lowest current
        # grade point; ties go to the one needing the fewest extra marks.
        while points < target_points - 1e-9:
            candidates = [s for s in subjects if s["level"] < len(s["options"]) - 1]
            best = min(
                candidates,
                key=lambda s: (
                    s["options"][s["level"]]["gp"],
                    s["options"][s["level"] + 1]["raw"] - s["options"][s["level"]]["raw"],
                ),
            )
            cur = best["options"][best["level"]]
            nxt = best["options"][best["level"] + 1]
            points += best["credits"] * (nxt["gp"] - cur["gp"])
            best["level"] += 1

    # ---------------- OUTPUT ----------------
    header = (f"{'Subject':<22}{'Cr':>4}{'Int/60':>8}{'Grade Pt':>10}"
              f"{'Total/100':>11}{'EndSem/40':>11}{'EndSem/100':>12}")
    print("\n" + "=" * len(header))
    print(header)
    print("-" * len(header))

    final_points = 0
    for s in subjects:
        opt = s["options"][s["level"]]
        final_points += s["credits"] * opt["gp"]
        print(f"{s['name'][:21]:<22}{s['credits']:>4g}{s['internal']:>8g}{opt['gp']:>10}"
              f"{opt['total']:>11.1f}{opt['scaled']:>11.1f}{opt['raw']:>12}")

    print("=" * len(header))
    print(f"Total credits          : {total_credits:g}")
    print(f"Desired CGPA           : {desired:.2f}")
    print(f"CGPA with these marks  : {final_points / total_credits:.2f}")
    print("\nNote: 'EndSem/100' is what you must score in the actual exam paper;")
    print("      'EndSem/40' is the reduced value added to your internals.")


if __name__ == "__main__":
    main()
