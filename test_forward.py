import torch
from clebsch_gordan import get_real_clebsch_gordan, ClebschGordan
from sparse_accumulation_plain_torch import sparse_accumulation_loops
import sparse_accumulation


def test_forward(epsilon = 1e-10):
    L_MAX = 5
    clebsch = ClebschGordan(L_MAX).precomputed_
    indices = get_real_clebsch_gordan(clebsch[L_MAX, L_MAX, L_MAX], L_MAX, L_MAX, L_MAX)
    
    m1_aligned, m2_aligned = [], []
    multipliers, mu_aligned = [], []
    for mu in range(0, 2 * L_MAX + 1):
        for el in indices[mu]:
            m1, m2, multiplier = el
            m1_aligned.append(m1)
            m2_aligned.append(m2)
            multipliers.append(multiplier)
            mu_aligned.append(mu)
    m1_aligned = torch.LongTensor(m1_aligned)
    m2_aligned = torch.LongTensor(m2_aligned)
    mu_aligned = torch.LongTensor(mu_aligned)
    multipliers = torch.FloatTensor(multipliers)
    
    
    BATCH_SIZE = 1000
    N_FEATURES = 100
    X1 = torch.randn(BATCH_SIZE, N_FEATURES, 2 * L_MAX + 1)
    X2 = torch.randn(BATCH_SIZE, N_FEATURES, 2 * L_MAX + 1)

    
    python_loops_output = sparse_accumulation_loops(X1, X2, mu_aligned, 2 * L_MAX + 1, m1_aligned, m2_aligned, multipliers)
    cpp_output = sparse_accumulation.SparseAccumulation.apply(X1, X2, mu_aligned,
                                                          2 * L_MAX + 1, m1_aligned, m2_aligned, multipliers)
    delta = python_loops_output - cpp_output
    
    relative_error = torch.mean(torch.abs(delta)) / torch.mean(torch.abs(python_loops_output))
    assert  relative_error < epsilon
    