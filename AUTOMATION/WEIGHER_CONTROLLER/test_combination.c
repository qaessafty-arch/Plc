/* Host test: gcc -std=c99 -Wall -Wextra -O2 combination.c test_combination.c -o test_combination && ./test_combination */
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include "combination.h"

static cw_result_t brute(const int32_t *w, int n, uint16_t avail, int32_t target, int32_t over)
{
    cw_result_t b = {0, 0, 0};
    for (uint32_t m = 1; m < (1u << n); m++) {
        if (m & ~avail) continue;
        int32_t s = 0; uint8_t h = 0;
        for (int i = 0; i < n; i++) if (m & (1u << i)) { s += w[i]; h++; }
        if (s < target || s > target + over) continue;
        if (b.heads == 0 || s < b.sum) { b.mask = (uint16_t)m; b.sum = s; b.heads = h; }
    }
    return b;
}

int main(void)
{
    /* fixed case: target 40.00 g */
    int32_t w[10] = {1130, 1290, 980, 1410, 1020, 1175, 890, 1330, 1250, 1105};
    cw_result_t r = cw_select(w, 10, 0x3FF, 4000, 300, 0);
    assert(r.heads > 0 && r.sum >= 4000 && r.sum <= 4300);
    cw_result_t b = brute(w, 10, 0x3FF, 4000, 300);
    assert(r.sum == b.sum);
    printf("fixed case: mask 0x%03X sum %.2f g heads %u\n", r.mask, r.sum / 100.0, r.heads);

    /* unavailable heads are never used */
    r = cw_select(w, 10, 0x00F, 4000, 300, 0);
    assert((r.mask & ~0x00F) == 0);

    /* impossible target -> no combination */
    r = cw_select(w, 10, 0x3FF, 50000, 300, 0);
    assert(r.heads == 0);

    /* max_heads respected */
    r = cw_select(w, 10, 0x3FF, 4000, 300, 3);
    assert(r.heads == 0 || r.heads <= 3);

    /* randomised equivalence with brute force */
    srand(12345);
    int found = 0;
    for (int t = 0; t < 20000; t++) {
        int32_t x[10];
        for (int i = 0; i < 10; i++) x[i] = 400 + rand() % 1600;
        uint16_t avail = (uint16_t)(rand() & 0x3FF);
        int32_t target = 2000 + rand() % 6000;
        cw_result_t a = cw_select(x, 10, avail, target, 250, 0), c = brute(x, 10, avail, target, 250);
        assert(a.heads == c.heads || (a.heads && c.heads));
        assert(a.sum == c.sum);
        found += a.heads > 0;
    }
    printf("20000 random cases match brute force (%d with a valid combination)\n", found);
    assert(cw_worst_head(w, 10, 0x3FF, 4000, 4) == 3);      /* 14.10 g is furthest from 10.00 g */
    assert(cw_worst_head(w, 10, 0, 4000, 4) == 0xFF);
    puts("ALL TESTS PASSED");
    return 0;
}
