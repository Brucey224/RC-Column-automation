b = 300
h = 500
N_Ed_fi = 1.0 * G_k + 0.5*Q_k
mu_fi = N_Ed_fi / N_Rd

def determine_column_fire_period_method_A(length):
    if column.condition == "upper floor":
        l_ofi = 0.5*length
    elif column.condition == "intermediate floor":
        l_ofi = 0.7*length
    validity_flag = True
    ## Preliminary checks to validate method used
    if l_ofi > 3.0 or lambd :
        validity_flag = False


if section.shape == 'rectangular':
    b_dash = 2*A_c / (b+h)
elif section.shape == 'circular':
    b_dash = diameter 

def compute_R_d_normal(N_Rd_normal = 2000):
    return N_Rd_normal


omega = A_s*f_yd / (A_cc*f_cd)
N_Rd = compute_R_d_normal() #kN, to be determined by calculatin
R_mu_fi = 83 * (1.00 - mu_fi*((1+omega) / (0.85/alpha_cc) + omega))
R_a = 1.60 * (a-30)
R_l = 9.60 * (5-L_ofi)
R_b = 0.09*b_dash

if num_bars <= 4:
    R_n = 0
else:
    R_n = 12

R = 120*((R_mu_fi + R_a + R_l + R_b + R_n)/120)**(1/8) 


    
