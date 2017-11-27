# Code to smoothly interface with taxcalc
records_url = 'puf.csv'
def make_calculator(reform_dict, start_year):
    policy1 = Policy()
    behavior1 = Behavior()
    records1 = Records(records_url)
    if reform_dict != {}:
        policy1.implement_reform(reform_dict)
    calc1 = Calculator(records = records1, policy = policy1, behavior = behavior1)
    calc1.advance_to_year(start_year)
    calc1.calc_all()
    return(calc1)

def calc_MTRs_nc(param_dict, startyear):
    alpha_nc_ft = 0.763 # fully taxable share of noncorporate equity
    alpha_nc_td = 0.101 # share of noncorporate equity held in tax-deferred accounts
    alpha_nc_nt = 0.136 # nontaxable share of noncorporate equity
    calc_base = make_calculator({}, startyear)
    calc_ref = make_calculator(param_dict, startyear)
    mtr_soleprop_base = calc_base.mtr('e00900p')[2]
    mtr_soleprop_ref = calc_ref.mtr('e00900p')[2]
    mtr_partner_base = calc_base.mtr('e26270')[2]
    mtr_partner_ref = calc_ref.mtr('e26270')[2]
    mtr_otherSchE_base = calc_base.mtr('e02000')[2]
    mtr_otherSchE_ref = calc_ref.mtr('e02000')[2]
    mtr_taxdef_base = calc_base.mtr('e01700')[2]
    mtr_taxdef_ref = calc_ref.mtr('e01700')[2]
    posti_base = (calc_base.records.c04800 > 0.)
    posti_ref = (calc_ref.records.c04800 > 0.)
    tau_nc_taxable_base = ((((mtr_soleprop_base * np.abs(calc_base.records.e00900p)) +
                             (mtr_otherSchE_base * np.abs(calc_base.records.e02000 - calc_base.records.e26270)) +
                             (mtr_partner_base * np.abs(calc_base.records.e26270))) * calc_base.records.s006 * posti_base).sum() /
                           ((np.abs(calc_base.records.e00900p) + np.abs(calc_base.records.e02000-calc_base.records.e26270) +
                             np.abs(calc_base.records.e26270)) * calc_base.records.s006 * posti_base).sum())
    tau_nc_taxable_ref = ((((mtr_soleprop_base * np.abs(calc_base.records.e00900p)) +
                            (mtr_otherSchE_base * np.abs(calc_base.records.e02000 - calc_base.records.e26270)) +
                            (mtr_partner_base * np.abs(calc_base.records.e26270))) * calc_base.records.s006 * posti_ref).sum() /
                          ((np.abs(calc_base.records.e00900p) + np.abs(calc_base.records.e02000-calc_base.records.e26270) +
                            np.abs(calc_base.records.e26270)) * calc_base.records.s006 * posti_ref).sum())
    tau_td_base = ((mtr_taxdef_base * calc_base.records.e01700 * calc_base.records.s006).sum() /
                   (calc_base.records.e01700 * calc_base.records.s006).sum())
    tau_td_ref = ((mtr_taxdef_ref * calc_ref.records.e01700 * calc_ref.records.s006).sum() /
                  (calc_ref.records.e01700 * calc_ref.records.s006).sum())
    tau_base = tau_nc_taxable_base * alpha_nc_ft + tau_td_base * alpha_nc_td
    tau_ref = tau_nc_taxable_ref * alpha_nc_ft + tau_td_ref * alpha_nc_td
    return (tau_base, tau_ref)

def distribute_results(reformdict):
    calc_base = make_calculator({}, 2014)
    calc_ref = make_calculator(reformdict, 2014)
    indiv_rev_impact = np.zeros(14)
    for i in range(2014,2028):
        calc_ref2 = copy.deepcopy(calc_ref)
        calc_ref2.records.e00900p = np.where(calc_ref2.records.e00900p >= 0, 
                                             calc_ref2.records.e00900p * indiv_gfactors['SchC_pos'][i-2014], 
                                             calc_ref2.records.e00900p * indiv_gfactors['SchC_neg'][i-2014])
        calc_ref2.records.e00900s = np.where(calc_ref2.records.e00900s >= 0, 
                                             calc_ref2.records.e00900s * indiv_gfactors['SchC_pos'][i-2014], 
                                             calc_ref2.records.e00900s * indiv_gfactors['SchC_neg'][i-2014])
        calc_ref2.records.e00900 = np.where(calc_ref2.records.e00900 >= 0, 
                                            calc_ref2.records.e00900 * indiv_gfactors['SchC_pos'][i-2014], 
                                            calc_ref2.records.e00900 * indiv_gfactors['SchC_neg'][i-2014])
        change_e26270 = np.where(calc_ref2.records.e26270 >= 0, 
                                 calc_ref2.records.e26270 * (indiv_gfactors['e26270_pos'][i-2014] - 1), 
                                 calc_ref2.records.e26270 * (indiv_gfactors['e26270_neg'][i-2014] - 1))
        calc_ref2.records.e26270 = calc_ref2.records.e26270 + change_e26270
        calc_ref2.records.e02000 = calc_ref2.records.e02000 + change_e26270
        # Change investment income
        calc_ref2.records.e00600 = calc_ref2.records.e00600 * indiv_gfactors['equity'][i-2014]
        calc_ref2.records.e00650 = calc_ref2.records.e00650 * indiv_gfactors['equity'][i-2014]
        calc_ref2.records.p22250 = calc_ref2.records.p22250 * indiv_gfactors['equity'][i-2014]
        calc_ref2.records.p23250 = calc_ref2.records.p23250 * indiv_gfactors['equity'][i-2014]
        calc_base.calc_all()
        calc_ref2.calc_all()
        indiv_rev_impact[i-2014] = sum((calc_ref2.records.combined -
                                        calc_base.records.combined) * calc_base.records.s006) / 10**9
        if i < 2027:
            calc_base.increment_year()
            calc_ref.increment_year()
    return(indiv_rev_impact)

            




    
