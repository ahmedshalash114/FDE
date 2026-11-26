"""What caching saves on Claude Haiku 4.5 (Nov 2026 prices, per million tokens):
input $1 · cache write (5 min) $1.25 · cache read $0.10."""
PRICE_IN, PRICE_WRITE, PRICE_READ = 1.00, 1.25, 0.10
def per_day(prefix_tokens=10_000, questions=1_000, writes=12):
    no_cache = questions * prefix_tokens * PRICE_IN / 1e6
    cached = (writes * prefix_tokens * PRICE_WRITE + (questions - writes) * prefix_tokens * PRICE_READ) / 1e6
    return no_cache, cached
if __name__ == "__main__":
    a, b = per_day()
    print(f"10K-token handbook, 1,000 questions/day: no cache ${a:.2f}  cached ${b:.2f}  -> {100*(1-b/a):.0f}% less on the prefix")
