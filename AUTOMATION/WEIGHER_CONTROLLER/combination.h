/* Combination selection for an N-head weigher (N <= 16). Portable C99, no heap,
 * no floating point: weights are in 0.01 g counts (int32).
 * Intended for the self-built weigher controller of the educational / semi-industrial
 * configurations (e.g. STM32 + one 24-bit ADC per load cell). Host-tested only. */
#ifndef COMBINATION_H
#define COMBINATION_H
#include <stdint.h>

#define CW_MAX_HEADS 16

typedef struct {
    uint16_t mask;      /* bit i set = head i discharges */
    int32_t  sum;       /* measured sum of selected heads, 0.01 g */
    uint8_t  heads;     /* number of heads selected, 0 = no valid combination */
} cw_result_t;

/* weights[i]  : stable net weight of head i, 0.01 g
 * avail_mask  : heads that are stable and not locked out
 * target      : target weight, 0.01 g
 * max_over    : largest accepted positive error, 0.01 g
 * max_heads   : upper limit of heads in one dump (0 = no limit)
 * Returns the combination with the smallest sum >= target; heads == 0 if none
 * lies within [target, target + max_over]. */
cw_result_t cw_select(const int32_t *weights, uint8_t n_heads, uint16_t avail_mask,
                      int32_t target, int32_t max_over, uint8_t max_heads);

/* Head to recharge when no combination exists: the available head whose weight
 * is furthest from target / nominal_heads. Returns 0xFF if none available. */
uint8_t cw_worst_head(const int32_t *weights, uint8_t n_heads, uint16_t avail_mask,
                      int32_t target, uint8_t nominal_heads);
#endif
