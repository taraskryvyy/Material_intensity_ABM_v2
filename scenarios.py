from parameters import Parameters

scenarios = {
    # "baseline": {},

    # "No ore deposit exploration": {"miningSiteExplorationProbability": 0,
    #                                "miningSiteShocks": 1,
    #                                "oreCostShocks": 200},
    # "Infrequent ore deposit exploration": {"miningSiteExplorationProbability": 0.1,
    #                                        "miningSiteShocks": 1,
    #                                        "oreCostShocks": 200},
    # "Frequent ore deposit exploration": {"miningSiteExplorationProbability": 0.5,
    #                                      "miningSiteShocks": 1,
    #                                      "oreCostShocks": 200},

    # "Low R material intensity": {"recMaterialProductivity": 2},
    # "Base R material intensity": {"recMaterialProductivity": 1.25},
    # "High R material intensity": {"recMaterialProductivity": 0.75},

    # "extreme renewables material intensity": {"recMaterialProductivity": 0.75},
    # "higher renewables material intensity": {"recMaterialProductivity": 1.25},
    # "baseline renewables material intensity": {"recMaterialProductivity": 2},
    ##### "lower renewables material intensity": {"recMaterialProductivity": 3},"

    # "Stable ore cost": {"oreCostShocks": 0},
    # "Declining ore cost": {"oreCostShocks": 400},
    # "Sharply declining ore cost": {"oreCostShocks": 200},

    # "Slow decline of ore cost": {"oreCostShocks": 400},
    # "Fast decline of ore cost": {"oreCostShocks": 200},

    # "Low fuel price growth": {"fuelPriceDrift": 0.0003},
    # "Base fuel price growth": {"fuelPriceDrift": 0.002},
    # "High fuel price growth": {"fuelPriceDrift": 0.006},

    "miningSiteExplorationProbability_0.1": {"miningSiteExplorationProbability": 0.1},
    # # "base_miningSiteExplorationProbability_0.5": {"miningSiteExplorationProbability": 0.5},
    # "miningSiteExplorationProbability_0.25": {"miningSiteExplorationProbability": 0.25},
    # "miningSiteExplorationProbability_0.9": {"miningSiteExplorationProbability": 0.9},

    # "oreCostParamOne_0.1": {"oreCostParamOne": 0.1},
    # # "base_oreCostParamOne_0.3": {"oreCostParamOne": 0.3},
    # "oreCostParamOne_0.5": {"oreCostParamOne": 0.5},

    # "sigmaOreCostParamOne 0.005": {"sigmaOreCostParamOne": 0.005},
    # "sigmaOreCostParamOne_0.01": {"sigmaOreCostParamOne": 0.01},
    # "sigmaOreCostParamOne_0.03": {"sigmaOreCostParamOne": 0.03},
    # # "base_sigmaOreCostParamOne 0.05": {"sigmaOreCostParamOne": 0.05},
    # "sigmaOreCostParamOne 0.1": {"sigmaOreCostParamOne": 0.1},
    # "sigmaOreCostParamOne_0.2": {"sigmaOreCostParamOne": 0.2},

    # "oreCostParamTwo_0.1": {"oreCostParamTwo": 0.1},
    # # "base_oreCostParamTwo_0.5": {"oreCostParamTwo": 0.5},
    # "oreCostParamTwo_0.9": {"oreCostParamTwo": 0.9},

    # "recMaterialProductivity_0.9": {"recMaterialProductivity": 0.9},
    # # "base_recMaterialProductivity_1.25": {"recMaterialProductivity": 1.25},
    # "recMaterialProductivity_2": {"recMaterialProductivity": 2},

    # "fgcMaterialProductivity_0.9": {"fgcMaterialProductivity": 0.9},
    # # "base_fgcMaterialProductivity_1": {"fgcMaterialProductivity": 1},
    # "fgcMaterialProductivity_2": {"fgcMaterialProductivity": 2},

    # "fecMaterialProductivity_10": {"fecMaterialProductivity": 10},
    # # "base_fecMaterialProductivity_15": {"fecMaterialProductivity": 15},
    # "fecMaterialProductivity_20": {"fecMaterialProductivity": 20},

    # "mcMaterialProductivity_5": {"mcMaterialProductivity": 5},
    # # "base_mcMaterialProductivity_7": {"mcMaterialProductivity": 7},
    # "mcMaterialProductivity_10": {"mcMaterialProductivity": 10},

    # "reCapitalLifeSpan_15": {"reCapitalLifeSpan": 15},
    # # "base_reCapitalLifeSpan_20" : {"reCapitalLifeSpan": 20},
    # "reCapitalLifeSpan_25": {"reCapitalLifeSpan": 25},

    # "oreProductivity_0.75": {"oreProductivity": 0.75},
    # # "base_oreProductivity_1": {"oreProductivity": 1},
    # "oreProductivity_1.25": {"oreProductivity": 1.25},

    # "muOreDeposit_100": {"muOreDeposit": 100},
    # # "base_muOreDeposit_150": {"muOreDeposit": 150},
    # "muOreDeposit_200": {"muOreDeposit": 200},

    # # "base_sigmaSqOreDeposit_400": {"sigmaSqOreDeposit": 400},
    # "sigmaSqOreDeposit_8000": {"sigmaSqOreDeposit": 8000},
    # "sigmaSqOreDeposit_16000": {"sigmaSqOreDeposit": 16000},

    # "adaptiveExpectationMaterialPrice_0.1": {"adaptiveExpectationMaterialPrice": 0.1},
    # # "base_adaptiveExpectationMaterialPrice_0.5": {"adaptiveExpectationMaterialPrice": 0.5},
    # "adaptiveExpectationMaterialPrice_0.9": {"adaptiveExpectationMaterialPrice": 0.9},

    # "logitCompetitionParamMining_1": {"logitCompetitionParamMining": 1},
    # # "base_logitCompetitionParamMining_10": {"logitCompetitionParamMining": 10},
    # "logitCompetitionParamMining_50": {"logitCompetitionParamMining": 50},

    # "fuelPriceDrift_0.0003": {"fuelPriceDrift": 0.0003},
    # # "base_fuelPriceDrift": {"fuelPriceDrift": 0.002},
    # "fuelPriceDrift_0.006": {"fuelPriceDrift": 0.006},

    # "fuelPriceVolatility_0.00000001": {"fuelPriceVolatility": 0.00000001},
    # # "base_fuelPriceVolatility_0.00003": {"fuelPriceVolatility": 0.00003},
    # "fuelPriceVolatility_0.0009": {"fuelPriceVolatility": 0.0009},

    # "loanInterestRate_0.00001": {"loanInterestRate": 0.00001},
    # # "base_loanInterestRate_0.001": {"loanInterestRate": 0.0001},
    # "loanInterestRate_0.05": {"loanInterestRate": 0.05},

}

def generate_scenarios(scenarios=scenarios):
    for scenario_name, new_params in scenarios.items():
        params = Parameters()
        # params.name = scenario_name
        for param_name, param_val in new_params.items():
            getattr(params, param_name)["val"] = param_val
        scenarios[scenario_name] = params#["params"] = params
    return scenarios