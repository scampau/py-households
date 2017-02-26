# Demography Data
This folder exists to store birth, marriage, and death statistics to be used to run simulations for a Mediterranean, and especially a Classical to Hellenistic Greek, demographic regime.

Generally these data need to be adapted and loaded into an agetable python class, as documented in the ABMDemography.py module.

##Death statistics
Death tables need to be deconstructed from the aggregate values for 5 year windwos as given in Coale and Demeny 1983 and turned into annualized rates. This can be most easily done by taking the rate of death rate_agg in an n year period and converting it to an annual rate by:

'''
rate_annual = 1-(1-rate_agg)^(1/n)
'''