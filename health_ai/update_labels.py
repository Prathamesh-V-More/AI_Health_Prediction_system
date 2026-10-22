"""
Run this AFTER training to update ml/predict.py with your actual class labels.
Usage: python update_labels.py
"""

print("=" * 60)
print("LABEL MAP UPDATER")
print("=" * 60)
print()
print("After training in Colab, you saw output like:")
print("  Index 0 = NORMAL")
print("  Index 1 = PNEUMONIA")
print()

# ── X-Ray labels ──────────────────────────────────────────────
print("Enter your X-RAY class indices (from Colab output).")
print("Press Enter when done.\n")

xray_labels = {}
while True:
    idx = input("  X-Ray Index number (or press Enter to finish): ").strip()
    if not idx:
        break
    name = input(f"  Class name for index {idx}: ").strip()
    xray_labels[int(idx)] = name

# ── Skin labels ───────────────────────────────────────────────
print()
print("Enter your SKIN DISEASE class indices (from Colab output).")
print("Press Enter when done.\n")

skin_labels = {}
while True:
    idx = input("  Skin Index number (or press Enter to finish): ").strip()
    if not idx:
        break
    name = input(f"  Class name for index {idx}: ").strip()
    skin_labels[int(idx)] = name

# ── Print result ──────────────────────────────────────────────
print()
print("=" * 60)
print("Copy these into health_ai/ml/predict.py")
print("=" * 60)
print()
print("XRAY_LABELS = {")
for k, v in sorted(xray_labels.items()):
    print(f'    {k}: "{v}",')
print("}")
print()
print("SKIN_LABELS = {")
for k, v in sorted(skin_labels.items()):
    print(f'    {k}: "{v}",')
print("}")
