
def determine_column_fire_period_method_A(G_k, Q_k, section, column, alpha_cc=0.85, f_cd = 20):
    
    # determine design actions in the fire scenario
    N_Ed_fi = 1.0 * G_k + 0.5*Q_k # Quasi-permanent combination factors for fire load case combos
    N_Rd_y, N_Rd_z = compute_R_d_normal() # kN, to be determined by calculatin
    mu_fi_y = N_Ed_fi / N_Rd_y # utilisation in fire scenario
    mu_fi_z = N_Ed_fi / N_Rd_z # utilisation in fire scenario
    mu_fi = max(mu_fi_y, mu_fi_z)
    omega = section.A_s*section.f_yd / (section.A_c*f_cd) #mechanical reinforcement ratio
    e_max = 0.15*section.h # mm
    a = section.cover + section.link_dia + section.bar_diameter/2 # Compute axis distance to reinforcement

    if section.num_bars <= 4:
        R_n = 0
    else:
        R_n = 12
    
    if column.condition == "upper floor":
        L_ofi_y = 0.5*column.L_actual_y
        L_ofi_z = 0.5*column.L_actual_z
    elif column.condition == "intermediate floor":
        L_ofi_y = 0.7*column.L_actual_y
        L_ofi_z = 0.7*column.L_actual_z
    
    if section.shape == 'rectangular':
        b_dash = 2*section.A_c / (section.b + section.h)
    elif section.shape == 'circular':
        b_dash = section.diameter 
    
    error_flag = False
    error_message = None
    ## Preliminary checks to validate method used
    if L_ofi_y > 3.0 or e_y > e_max:
        error_flag = True
        error_message = "Method A not valid for this column. Design outside of scope of tool"

    R_mu_fi = 83 * (1.00 - mu_fi*((1+omega) / (0.85/alpha_cc) + omega))
    R_a = 1.60 * (a-30)
    R_l = 9.60 * (5-L_ofi_y)
    R_b = 0.09*b_dash

    R = 120*((R_mu_fi + R_a + R_l + R_b + R_n)/120)**(1/8) 

    return error_flag, R, error_message

def compute_R_d_normal(N_Rd_normal = 2000):
    pass





    
