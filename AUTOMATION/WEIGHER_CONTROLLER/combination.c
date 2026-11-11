#include "combination.h"

static uint8_t popcount16(uint16_t v) { uint8_t c = 0; while (v) { v &= (uint16_t)(v - 1); c++; } return c; }

cw_result_t cw_select(const int32_t *w, uint8_t n, uint16_t avail, int32_t target,
                      int32_t max_over, uint8_t max_heads)
{
    cw_result_t best = {0, 0, 0};
    if (n == 0 || n > CW_MAX_HEADS) return best;
    const uint32_t full = (n == 16) ? 0xFFFFu : ((1u << n) - 1u);
    avail &= (uint16_t)full;
    /* Gray-code walk: each step toggles one head, so the running sum needs one add/sub.
     * 2^10 = 1024 subsets for 10 heads - microseconds on a Cortex-M. */
    int32_t sum = 0;
    uint16_t gray = 0;
    for (uint32_t i = 1; i <= full; i++) {
        uint16_t g = (uint16_t)(i ^ (i >> 1));
        uint16_t diff = (uint16_t)(g ^ gray);
        uint8_t bit = 0;
        while (!(diff & 1u)) { diff >>= 1; bit++; }
        if (g & (1u << bit)) sum += w[bit]; else sum -= w[bit];
        gray = g;
        if (g & (uint16_t)~avail) continue;                 /* uses an unavailable head */
        if (sum < target || sum > target + max_over) continue;
        if (max_heads && popcount16(g) > max_heads) continue;
        if (best.heads == 0 || sum < best.sum) {
            best.mask = g; best.sum = sum; best.heads = popcount16(g);
        }
    }
    return best;
}

uint8_t cw_worst_head(const int32_t *w, uint8_t n, uint16_t avail, int32_t target, uint8_t nominal)
{
    uint8_t worst = 0xFF;
    int32_t worst_err = -1;
    if (nominal == 0) nominal = 1;
    const int32_t ideal = target / nominal;
    for (uint8_t i = 0; i < n && i < CW_MAX_HEADS; i++) {
        if (!(avail & (1u << i))) continue;
        int32_t e = w[i] > ideal ? w[i] - ideal : ideal - w[i];
        if (e > worst_err) { worst_err = e; worst = i; }
    }
    return worst;
}
