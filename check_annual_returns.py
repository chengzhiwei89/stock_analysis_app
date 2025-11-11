strikes = [215, 220, 225, 240, 245]
bids = [0.70, 0.92, 1.21, 2.93, 3.90]
days = 31

print("Checking if options pass 15% annual return requirement:")
print("="*60)

for s, b in zip(strikes, bids):
    annual_ret = (b / s) * (365 / days) * 100
    status = "PASS" if annual_ret >= 15 else "FAIL (too low)"
    print(f"${s} PUT @ ${b:.2f}: Annual Return = {annual_ret:.1f}% - {status}")

print("\nConclusion:")
print("If all fail, the min_annual_return=15% filter is removing them!")
