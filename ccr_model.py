# construct base dataset
def ccr_data_v1():
    ModelDiffs = run_btax(False, True, 2017)
    btax_data = ModelDiffs[0]
    btax_data.drop(['ADS Life', 'Asset Type', 'GDS Life', 'System', 'asset_category',
                    'b', 'bea_asset_code', 'bonus', 'major_asset_group', 'metr_c',
                    'metr_c_d', 'metr_c_e', 'metr_nc', 'metr_nc_d', 'metr_nc_e',
                    'mettr_c', 'mettr_c_d', 'mettr_c_e', 'mettr_nc', 'mettr_nc_d',
                    'mettr_nc_e', 'rho_c', 'rho_c_d', 'rho_c_e', 
                    'rho_nc', 'rho_nc_d', 'rho_nc_e',
                    'z_c_d', 'z_c_e', 'z_nc_d', 'z_nc_e'], axis=1, inplace=True)
    btax_data.rename(columns={'GDS Class Life': 'L'}, inplace=True)
    btax_data.drop([3, 21, 32, 91], axis=0, inplace=True)
    ccrdata = btax_data.merge(right=df_econdepr, how='outer', on='Asset')
    ccrdata.drop([96,97,98], axis=0, inplace=True)
    return ccrdata
base_data = ccr_data_v1()


"""
CCR data version 2
"""
btax_defaults = pd.read_csv('mini_params_btax.csv')

def get_taxdep_info():
    taxdep = pd.read_csv('btax/data/depreciation_rates/tax_depreciation_rates.csv')
    taxdep.drop(['System'], axis=1, inplace=True)
    taxdep.rename(columns={'GDS Life': 'L_gds', 'ADS Life': 'L_ads', 'Asset Type': 'Asset'}, inplace=True)
    taxdep['Asset'][81] = 'Motor vehicles and parts manufacturing'
    taxdep['Method'][taxdep['Asset'] == 'Land'] = 'None'
    taxdep['Method'][taxdep['Asset'] == 'Inventories'] = 'None'
    econdep = pd.read_csv('btax/data/depreciation_rates/Economic Depreciation Rates.csv')
    econdep['Asset'][78] = 'Communications equipment manufacturing'
    econdep['Asset'][81] = 'Motor vehicles and parts manufacturing'
    econdep.drop('Code', axis=1, inplace=True)
    econdep.rename(columns={'Economic Depreciation Rate': 'delta'}, inplace=True)
    depinfo = taxdep.merge(right=econdep, how='outer', on='Asset')
    return depinfo

taxdep_info_gross = get_taxdep_info()

def taxdep_final(depr_3yr_method, depr_3yr_bonus,
                 depr_5yr_method, depr_5yr_bonus,
                 depr_7yr_method, depr_7yr_bonus,
                 depr_10yr_method, depr_10yr_bonus,
                 depr_15yr_method, depr_15yr_bonus,
                 depr_20yr_method, depr_20yr_bonus,
                 depr_25yr_method, depr_25yr_bonus,
                 depr_275yr_method, depr_275yr_bonus,
                 depr_39yr_method, depr_39yr_bonus):
    taxdep = copy.deepcopy(taxdep_info_gross)
    taxdep['System'] = ''
    # Determine depreciation systems for each asset type
    taxdep['System'][taxdep['GDS Class Life'] == 3] = depr_3yr_method
    taxdep['System'][taxdep['GDS Class Life'] == 5] = depr_5yr_method
    taxdep['System'][taxdep['GDS Class Life'] == 7] = depr_7yr_method
    taxdep['System'][taxdep['GDS Class Life'] == 10] = depr_10yr_method
    taxdep['System'][taxdep['GDS Class Life'] == 15] = depr_15yr_method
    taxdep['System'][taxdep['GDS Class Life'] == 20] = depr_20yr_method
    taxdep['System'][taxdep['GDS Class Life'] == 25] = depr_25yr_method
    taxdep['System'][taxdep['GDS Class Life'] == 27.5] = depr_275yr_method
    taxdep['System'][taxdep['GDS Class Life'] == 39] = depr_39yr_method
    # Determine asset lives to use
    taxdep['L'] = taxdep['L_gds']
    taxdep['L'][taxdep['System'] == 'ADS'] = taxdep['L_ads']
    taxdep['L'][taxdep['System'] == 'None'] = 100
    # Determine depreciation method
    taxdep['Method'][taxdep['System'] == 'ADS'] = 'SL'
    taxdep['Method'][taxdep['System'] == 'Economic'] = 'Economic'
    taxdep['Method'][taxdep['System'] == 'None'] = 'None'
    # Detemine bonus depreciation
    taxdep['bonus'] = 0
    taxdep['bonus'][taxdep['GDS Class Life'] == 3] = depr_3yr_bonus
    taxdep['bonus'][taxdep['GDS Class Life'] == 5] = depr_5yr_bonus
    taxdep['bonus'][taxdep['GDS Class Life'] == 7] = depr_7yr_bonus
    taxdep['bonus'][taxdep['GDS Class Life'] == 10] = depr_10yr_bonus
    taxdep['bonus'][taxdep['GDS Class Life'] == 15] = depr_15yr_bonus
    taxdep['bonus'][taxdep['GDS Class Life'] == 20] = depr_20yr_bonus
    taxdep['bonus'][taxdep['GDS Class Life'] == 25] = depr_25yr_bonus
    taxdep['bonus'][taxdep['GDS Class Life'] == 27.5] = depr_275yr_bonus
    taxdep['bonus'][taxdep['GDS Class Life'] == 39] = depr_39yr_bonus
    taxdep.drop(['System', 'L_gds', 'L_ads', 'GDS Class Life'], axis=1, inplace=True)
    return taxdep

def taxdep_pre2017(year):
    bonusinfo = pd.read_csv('aggregates_data/bonus_data.csv')
    taxdep = copy.deepcopy(taxdep_info_gross)
    taxdep['L'] = taxdep['L_gds']
    taxdep['bonus'] = 0
    taxdep['bonus'][taxdep['GDS Class Life'] == 3] = bonusinfo['bonus3'][year-1960]
    taxdep['bonus'][taxdep['GDS Class Life'] == 5] = bonusinfo['bonus5'][year-1960]
    taxdep['bonus'][taxdep['GDS Class Life'] == 7] = bonusinfo['bonus7'][year-1960]
    taxdep['bonus'][taxdep['GDS Class Life'] == 10] = bonusinfo['bonus10'][year-1960]
    taxdep['bonus'][taxdep['GDS Class Life'] == 15] = bonusinfo['bonus15'][year-1960]
    taxdep['bonus'][taxdep['GDS Class Life'] == 20] = bonusinfo['bonus20'][year-1960]
    taxdep['bonus'][taxdep['GDS Class Life'] == 25] = bonusinfo['bonus25'][year-1960]
    taxdep['bonus'][taxdep['GDS Class Life'] == 27.5] = bonusinfo['bonus27'][year-1960]
    taxdep['bonus'][taxdep['GDS Class Life'] == 39] = bonusinfo['bonus39'][year-1960]
    taxdep.drop(['L_gds', 'L_ads', 'GDS Class Life'], axis=1, inplace=True)
    return taxdep

def test_btax_reform(paramdict):
    assert type(paramdict) == dict
    paramnames = list(btax_defaults)
    paramnames.remove('year')
    keylist = []
    for key in paramdict:
        key2 = int(key)
        assert key2 in range(2017, 2027)
        keylist.append(key2)
        #for mod in paramdict[key]:
        for param in paramdict[key]:
            assert param in paramnames

def update_btax_params(param_dict):
    """
    param_dict is a year: mod dictionary. Acceptable years are 2017-2027. Ex:
        {'2018': {'tau_c': 0.3}}
    """
    test_btax_reform(param_dict)
    params_df = copy.deepcopy(btax_defaults)
    yearlist = []
    for key in param_dict:
        yearlist.append(int(key))
    yearlist.sort()
    for year in yearlist:
        for param in param_dict[str(year)]:
            params_df[param][params_df['year'] >= year] = param_dict[str(year)][param]
    return params_df

def get_btax_params_oneyear(btax_params, year):
    if year >= 2017:
        year = min(year, 2027)
        method_3yr = btax_params['depr_3yr_method'][year-2017]
        method_5yr = btax_params['depr_5yr_method'][year-2017]
        method_7yr = btax_params['depr_7yr_method'][year-2017]
        method_10yr = btax_params['depr_10yr_method'][year-2017]
        method_15yr = btax_params['depr_15yr_method'][year-2017]
        method_20yr = btax_params['depr_20yr_method'][year-2017]
        method_25yr = btax_params['depr_25yr_method'][year-2017]
        method_275yr = btax_params['depr_275yr_method'][year-2017]
        method_39yr = btax_params['depr_39yr_method'][year-2017]
        bonus_3yr = btax_params['depr_3yr_bonus'][year-2017]
        bonus_5yr = btax_params['depr_5yr_bonus'][year-2017]
        bonus_7yr = btax_params['depr_7yr_bonus'][year-2017]
        bonus_10yr = btax_params['depr_10yr_bonus'][year-2017]
        bonus_15yr = btax_params['depr_15yr_bonus'][year-2017]
        bonus_20yr = btax_params['depr_20yr_bonus'][year-2017]
        bonus_25yr = btax_params['depr_25yr_bonus'][year-2017]
        bonus_275yr = btax_params['depr_275yr_bonus'][year-2017]
        bonus_39yr = btax_params['depr_39yr_bonus'][year-2017]
        taxdep = taxdep_final(method_3yr, bonus_3yr, method_5yr, bonus_5yr,
                              method_7yr, bonus_7yr, method_10yr, bonus_10yr,
                              method_15yr, bonus_15yr, method_20yr, bonus_20yr,
                              method_25yr, bonus_25yr, method_275yr, bonus_275yr,
                              method_39yr, bonus_39yr)
    else:
        taxdep = taxdep_pre2017(year)
    return taxdep



# longer functions to use
def depreciationDeduction(year_investment, year_deduction, method, L,
                          delta, bonus):
    # year_investment: year the investment is made
    # year_deduction: year the CCR deduction is taken
    # Method: Method of CCR (DB 200%, DB 150%, SL, Expensing)
    # L: class life for DB or SL depreciation (MACRS)
    # bonus: bonus depreciation rate
    assert method in ['DB 200%', 'DB 150%', 'SL', 'Expensing', 'Economic', 'None']
    # No depreciation
    if method == 'None':
    	deduction = 0
    # Expensing
    elif method == 'Expensing':
        if year_deduction == year_investment:
            deduction = 1.0
        else:
            deduction = 0
    # Economic depreciation
    elif method == 'Economic':
        pi_temp = (investmentGfactors_data['pce'][year_deduction + 1] /
                   investmentGfactors_data['pce'][year_deduction])
        if pi_temp == np.exp(delta):
            annual_change = 1.0
        else:
            annual_change = ((pi_temp * np.exp(delta) - 1) /
                             (np.log(pi_temp) - delta))
        if year_deduction < year_investment:
            deduction = 0
        elif year_deduction == year_investment:
            deduction = bonus + (1 - bonus) * delta * annual_change
        else:
            deduction = (investmentGfactors_data['pce'][year_deduction] /
                         investmentGfactors_data['pce'][year_investment] *
                         np.exp(-delta * (year_deduction - year_investment)) *
                         delta * annual_change) * (1 - bonus)
    else:
        if method == 'DB 200%':
            N = 2
        elif method == 'DB 150%':
            N = 1.5
        elif method == 'SL':
            N = 1
    # DB or SL depreciation, half-year convention
        t0 = year_investment + 0.5
        t1 = t0 + L * (1 - 1 / N)
        s1 = year_deduction
        s2 = s1 + 1
        if year_deduction < year_investment:
            deduction = 0
        elif year_deduction > year_investment + L:
            deduction = 0
        elif year_deduction == year_investment:
            deduction = bonus + (1 - bonus) * (1 - np.exp(-N / L * 0.5))
        elif s2 <= t1:
            deduction = ((1 - bonus) * (np.exp(-N / L * (s1 - t0)) -
                                        np.exp(-N / L * (s2 - t0))))
        elif s1 >= t1 and s1 <= t0 + L and s2 > t0 + L:
            deduction = (1 - bonus) * (N / L * np.exp(1 - N) * (s2 - s1) * 0.5)
        elif s1 >= t1 and s2 <= t0 + L:
            deduction = (1 - bonus) * (N / L * np.exp(1 - N) * (s2 - s1))
        elif s1 < t1 and s2 > t1:
            deduction = ((1 - bonus) * (np.exp(-N / L * (s1 - t0)) -
                                        np.exp(-N / L * (t1 - t0)) +
                                        N / L * np.exp(1 - N) * (s2 - t1)))
    return(deduction)

def build_inv_matrix(corp_noncorp=True):
    # Function builds a matrix of investment by asset type by year
    # corp_noncorp: indicator for corporate or noncorporate investment
    # Returns 96x75 invesment matrix (96 assets, years 1960-2034)
    inv_mat1 = np.zeros((96,75))
    # build historical portion
    for j in range(57):
        if corp_noncorp:
            inv_mat1[:,j] = (investmentrate_data['i' + str(j + 1960)] *
                             investmentshare_data['c_share'][j])
        else:
            inv_mat1[:,j] = (investmentrate_data['i' + str(j + 1960)] *
                             (1 - investmentshare_data['c_share'][j]))
    # Extend investment using NGDP (growth factors from CBO forecast)
    for j in range(57,75):
        inv_mat1[:,j] = (inv_mat1[:,56] * investmentGfactors_data['ngdp'][j] /
                         investmentGfactors_data['ngdp'][56])
    # Rescale investment to match investment based on B-Tax for 2017
    if corp_noncorp:
        inv2017 = np.asarray(base_data['assets_c'] *
                             (investmentGfactors_data['ngdp'][57] /
                              investmentGfactors_data['ngdp'][56] - 1 +
                              base_data['delta']))
    else:
        inv2017 = np.asarray(base_data['assets_nc'] *
                             (investmentGfactors_data['ngdp'][57] /
                              investmentGfactors_data['ngdp'][56] - 1 +
                              base_data['delta']))
    inv_mat2 = np.zeros((96,75))
    l1 = range(96)
    l1.remove(32) # exclude land
    for j in range(75):
        for i in l1:
            inv_mat2[i,j] = inv_mat1[i,j] * inv2017[i] / inv_mat1[i, 57]
    return(inv_mat2)

def calcDepAdjustment(corp_noncorp=True):
    # corp_noncorp: indicator for whether corporate or noncorporate data
    investment_matrix = build_inv_matrix(corp_noncorp)
    Dep_arr = np.zeros((96,75,75))
    #methodlist = np.asarray(base_data['Method'])
    #Llist = np.asarray(base_data['L'])
    #deltalist = np.asarray(base_data['delta'])
    for j in range(75):
        taxdepinfo = get_btax_params_oneyear(btax_defaults, j+1960)
        print 'params' + str(j+1960)
        for i in range(96):
            for k in range(75):
                Dep_arr[i,j,k] = (depreciationDeduction(j, k, 
                										taxdepinfo['Method'][i],
                                                        taxdepinfo['L'][i],
                                                        taxdepinfo['delta'][i],
                                                        taxdepinfo['bonus'][i]) *
                                  investment_matrix[i,j])
    totalAnnualDepreciation = np.zeros(75)
    for k in range(75):
        totalAnnualDepreciation[k] = Dep_arr[:,:,k].sum().sum()
    depreciation_data = copy.deepcopy(depreciationIRS_data)
    depreciation_data['dep_model'] = totalAnnualDepreciation[40:54]
    if corp_noncorp:
        depreciation_data['scale'] = (depreciation_data['dep_Ccorp'] /
                                      depreciation_data['dep_model'])
    else:
        depreciation_data['scale'] = ((depreciation_data['dep_Scorp'] +
                                       depreciation_data['dep_sp'] +
                                       depreciation_data['dep_partner']) /
                                      depreciation_data['dep_model'])
    adj_factor = (sum(depreciation_data['scale']) /
                  len(depreciation_data['scale']))
    return(adj_factor)
adjfactor_dep_corp = calcDepAdjustment()
adjfactor_dep_noncorp = calcDepAdjustment(False)


def annualCCRdeduction(investment_matrix, btax_params, adj_factor,
                       hc_undep=0., hc_undep_year=0):
    # investment_matrix: the matrix of investment (by asset and year)
    # bonusdata: bonus depreciation data (by asset and year)
    # hc_undep: haircut on depreciation deductions taken
    #           after hc_under_year on investments made before hc_undep_year
    Dep_arr = np.zeros((96,75,75))
    #methodlist =np.asarray(base_data['Method'])
    #Llist = np.asarray(base_data['L'])
    #deltalist = np.asarray(base_data['delta'])
    for j in range(75):
        taxdepinfo = get_btax_params_oneyear(btax_params, j+1960)
        print 'params' + str(j+1960)
        for i in range(96):
            for k in range(75):
                Dep_arr[i,j,k] = (depreciationDeduction(j, k, 
                                                        taxdepinfo['Method'][i],
                                                        taxdepinfo['L'][i], 
                                                        taxdepinfo['delta'][i],
                                                        taxdepinfo['bonus'][i]) *
                                  investment_matrix[i,j])
    for j in range(75):
        for k in range(75):
            if j + 1960 < hc_undep_year and k + 1960 >= hc_undep_year:
                Dep_arr[:,j,k] = Dep_arr[:,j,k] * (1 - hc_undep)
    totalAnnualDeduction = np.zeros(75)
    for k in range(75):
        totalAnnualDeduction[k] = (Dep_arr[:,:,k].sum().sum() *
                                   adjfactor_dep_corp)
    return totalAnnualDeduction

def capitalPath(investment_mat, depDeduction_vec, 
                corp_noncorp=True, economic=False):
    if corp_noncorp:
        adj_factor = adjfactor_dep_corp
    else:
        adj_factor = adjfactor_dep_noncorp
    Kstock = np.zeros((96,15))
    trueDep = np.zeros((96,14))
    pcelist = np.asarray(investmentGfactors_data['pce'])
    deltalist = np.asarray(base_data['delta'])
    for i in range(96):
        if corp_noncorp:
            Kstock[i,3] = np.asarray(base_data['assets_c'])[i]
        else:
            Kstock[i,3] = np.asarray(base_data['assets_nc'])[i]
        for j in [56,55,54]:
            Kstock[i,j-54] = ((Kstock[i,j-53] * pcelist[j] / pcelist[j+1] -
                               investment_mat[i,j]) / (1 - deltalist[i]))
            trueDep[i,j-54] = Kstock[i,j-54] * deltalist[i]
        for j in range(57,68):
            trueDep[i,j-54] = Kstock[i,j-54] * deltalist[i]
            Kstock[i,j-53] = ((Kstock[i,j-54] + investment_mat[i,j] -
                               trueDep[i,j-54]) *
                              pcelist[j+1] / pcelist[j])
    # Sum across assets and put into new dataset
    Kstock_total = np.zeros(14)
    fixedK_total = np.zeros(14)
    trueDep_total = np.zeros(14)
    inv_total = np.zeros(14)
    fixedInv_total = np.zeros(14)
    Mdep_total = np.zeros(14)
    for j in range(14):
        Kstock_total[j] = sum(Kstock[:,j]) * adj_factor
        fixedK_total[j] = ((sum(Kstock[:,j]) - Kstock[31,j] - Kstock[32,j]) *
                           adj_factor)
        trueDep_total[j] = sum(trueDep[:,j]) * adj_factor
        inv_total[j] = sum(investment_mat[:,j+54]) * adj_factor
        fixedInv_total[j] = (sum(investment_mat[:,j+54]) -
                             investment_mat[31,j+54]) * adj_factor
        Mdep_total[j] = depDeduction_vec[j+54]
    cap_result = pd.DataFrame({'year': range(2014,2028),
                               'Kstock': Kstock_total,
                               'Investment': inv_total,
                               'FixedInv': fixedInv_total,
                               'TrueDep': trueDep_total,
                               'taxDep': Mdep_total,
                               'FixedK': fixedK_total})
    if economic:
        taxDep_results = cap_result.drop(['Kstock', 'FixedK', 'Investment',
                                          'FixedInv', 'taxDep'], axis=1)
        taxDep_results.rename(columns={'TrueDep': 'taxDep'}, inplace=True)
    else:
        taxDep_results = cap_result.drop(['Kstock', 'FixedK', 'Investment',
                                          'FixedInv', 'TrueDep'], axis=1)
    return (cap_result, taxDep_results)

