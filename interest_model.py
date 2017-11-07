def calcNIDscale(capital_path, eta=0.4):
    # capital_path: growth path of the capital stock
    # eta: retirement rate of existing debt
    Kstock2016 = capital_path['Kstock'][2]
    K_fa = debt_data_corp['Kfa'][:57].tolist()
    A = debt_data_corp['A'][:57].tolist()
    L = debt_data_corp['L'][:57].tolist()
    D = [L[i] - A[i] for i in range(len(L))]
    i_t = debt_data_corp['i_t'].tolist()
    i_pr = debt_data_corp['i_pr'].tolist()
    for i in range(57,68):
        K_fa.append(K_fa[56] * capital_path['Kstock'][i-54] / Kstock2016)
        A.append(A[56] * K_fa[i] / K_fa[56])
        D.append(D[56] * K_fa[i] / K_fa[56])
        L.append(D[i] - A[i])
    R = np.zeros(68)
    O = np.zeros(68)
    for i in range(1,68):
        R[i] = L[i-1] * eta
        O[i] = L[i] - L[i-1] + R[i]
    i_a = [x / 100. for x in i_t]
    i_l = [(i_t[i] + i_pr[i]) / 100. for i in range(len(i_t))]
    int_income = [A[i] * i_a[i] for i in range(len(A))]
    int_expense = np.zeros(68)
    for i in range(1,68):
        for j in range(i+1):
            int_expense[i] += O[j] * (1 - eta)**(i - j - 1) * i_l[j]
    NID_gross = int_expense - int_income
    NID_scale = sum((debt_data_corp['NID_IRS'][38:54] / NID_gross[38:54])) / 16.
    return NID_scale
adjfactor_nid_corp = calcNIDscale(capPath_base_corp)

def calcIDscale_noncorp(capital_path, eta=0.4):
    # capital_path: growth path of the capital stock
    # eta: retirement rate of existing debt
    Kstock2016 = capital_path['Kstock'][2]
    K_fa = debt_data_noncorp['Kfa'][:57].tolist()
    L = debt_data_noncorp['L'][:57].tolist()
    i_t = debt_data_noncorp['i_t'].tolist()
    i_pr = debt_data_noncorp['i_pr'].tolist()
    for i in range(57,68):
        K_fa.append(K_fa[56] * capital_path['Kstock'][i-54] / Kstock2016)
        L.append(L[56] * K_fa[i] / K_fa[56])
    R = np.zeros(68)
    O = np.zeros(68)
    for i in range(1,68):
        R[i] = L[i-1] * eta
        O[i] = L[i] - L[i-1] + R[i]
    i_l = [(i_t[i] + i_pr[i]) / 100. for i in range(len(i_t))]
    int_expense = np.zeros(68)
    for i in range(1,68):
        for j in range(i+1):
            int_expense[i] += O[j] * (1 - eta)**(i - j - 1) * i_l[j]
    ID_scale = sum(((debt_data_noncorp['ID_Scorp'][38:54] + debt_data_noncorp['ID_sp'][38:54] + 
                     debt_data_noncorp['ID_partner'][38:54]) / int_expense[38:54])) / 16.
    return ID_scale
adjfactor_id_noncorp = calcIDscale_noncorp(capPath_base_noncorp)


def netInterestDeduction(capital_path, eta=0.4, id_hc_year=0, nid_hc_year=0, id_hc_old=0, id_hc_new=0, nid_hc_old=0, nid_hc=0):
    # capital_path: growth path of the capital stock
    # eta: retirement rate of existing debt
    # nid_hc: haircut on the net interest deduction, beginning in nid_hc_year
    # id_hc_old, id_hc_new: haircuts on the deduction of interest paid on debt originated before id_hc_year and on debt originated beginning in id_hc_year
    Kstock2016 = capital_path['Kstock'][2]
    K_fa = debt_data_corp['Kfa'][:57].tolist()
    A = debt_data_corp['A'][:57].tolist()
    L = debt_data_corp['L'][:57].tolist()
    D = [L[i] - A[i] for i in range(len(L))]
    i_t = debt_data_corp['i_t'].tolist()
    i_pr = debt_data_corp['i_pr'].tolist()
    for i in range(57,68):
        K_fa.append(K_fa[56] * capital_path['Kstock'][i-54] / Kstock2016)
        A.append(A[56] * K_fa[i] / K_fa[56])
        D.append(D[56] * K_fa[i] / K_fa[56])
        L.append(D[i] + A[i])
    R = np.zeros(68)
    O = np.zeros(68)
    for i in range(1,68):
        R[i] = L[i-1] * eta
        O[i] = L[i] - L[i-1] + R[i]
    i_a = [x / 100. for x in i_t]
    i_l = [(i_t[i] + i_pr[i]) / 100. for i in range(len(i_t))]
    int_income = [A[i] * i_a[i] for i in range(len(A))]
    int_expense = np.zeros(68)
    for i in range(1,68):
        for j in range(i+1):
            if j + 1960 < id_hc_year and i + 1960 >= id_hc_year:
                int_expense[i] += O[j] * (1 - eta)**(i - j - 1) * i_l[j] * (1 - id_hc_old)
            elif j + 1960 >= id_hc_year:
                int_expense[i] += O[j] * (1 - eta)**(i - j - 1) * i_l[j] * (1 - id_hc_new)
            else:
                int_expense[i] += O[j] * (1 - eta)**(i - j - 1) * i_l[j]
    NID_gross = int_expense - int_income
    NID = np.zeros(len(NID_gross))
    NIP = NID_gross * adjfactor_nid_corp
    for i in range(len(NID)):
        if i + 1960 < nid_hc_year:
            NID[i] = NID_gross[i] * adjfactor_nid_corp
        else:
            NID[i] = NID_gross[i] * adjfactor_nid_corp * (1 - nid_hc)
    NID_results = pd.DataFrame({'year': range(2014,2028), 'nid': NID[54:68]})
    NIP_results = pd.DataFrame({'year': range(2014,2028), 'nip': NIP[54:68]})
    #NID_results = pd.DataFrame({'year': range(1998,2014), 'nid': NID[38:54]}) #for printing historical results
    return (NID_results, NIP_results)

def noncorpIntDeduction(capital_path, eta=0.4):
    Kstock2016 = capital_path['Kstock'][2]
    K_fa = debt_data_noncorp['Kfa'][:57].tolist()
    L = debt_data_noncorp['L'][:57].tolist()
    i_t = debt_data_noncorp['i_t'].tolist()
    i_pr = debt_data_noncorp['i_pr'].tolist()
    for i in range(57,68):
        K_fa.append(K_fa[56] * capital_path['Kstock'][i-54] / Kstock2016)
        L.append(L[56] * K_fa[i] / K_fa[56])
    R = np.zeros(68)
    O = np.zeros(68)
    for i in range(1,68):
        R[i] = L[i-1] * eta
        O[i] = L[i] - L[i-1] + R[i]
    i_l = [(i_t[i] + i_pr[i]) / 100. for i in range(len(i_t))]
    int_expense = np.zeros(68)
    for i in range(1,68):
        for j in range(i+1):
            int_expense[i] += O[j] * (1 - eta)**(i - j - 1) * i_l[j]
    int_total = int_expense * adjfactor_id_noncorp
    ID_results = pd.DataFrame({'year': range(2014,2028), 'intpaid': int_total[54:68]})
    #ID_results = pd.DataFrame({'year': range(1998,2014), 'intpaid': int_total[38:54]})
    return ID_results
