from parameters import Parameters

scenarios = {
    # "baseline": {}

    "extreme renewables material intensity": {"recMaterialProductivity": 0.75},
    "higher renewables material intensity": {"recMaterialProductivity": 1.25},
    "baseline renewables material intensity": {"recMaterialProductivity": 2},
    # "lower renewables material intensity": {"recMaterialProductivity": 3},

    # "miningSiteExplorationProbability_0": {"miningSiteExplorationProbability": 0},
    # "miningSiteExplorationProbability_0.1": {"miningSiteExplorationProbability": 0.1},
    # "base_miningSiteExplorationProbability_0.5": {"miningSiteExplorationProbability": 0.5},

    # "logitCompetitionParamMining_0.01": {"logitCompetitionParamMining": 0.01},
    # "logitCompetitionParamMining_1": {"logitCompetitionParamMining": 1},
    # "base_logitCompetitionParamMining_10": {"logitCompetitionParamMining": 10},

    # "adaptiveExpectationMaterialPrice_0.2": {"adaptiveExpectationMaterialPrice": 0.2},
    # "base_adaptiveExpectationMaterialPrice_0.5": {"adaptiveExpectationMaterialPrice": 0.5},
    # "adaptiveExpectationMaterialPrice_0.8": {"adaptiveExpectationMaterialPrice": 0.8},

    # "recMaterialProductivity_5": {"recMaterialProductivity": 5},
    # "base_recMaterialProductivity_2": {"recMaterialProductivity": 2},
    # "recMaterialProductivity_1": {"recMaterialProductivity": 1},

    # "fuelPriceVolatility_0.00000001": {"fuelPriceVolatility": 0.00000001},
    # "base_fuelPriceVolatility_0.00003": {"fuelPriceVolatility": 0.00003},
    # "fuelPriceVolatility_0.0005": {"fuelPriceVolatility": 0.0005},

    # "fuelPriceDrift_0.0002": {"fuelPriceDrift": 0.0002},
    # "base_fuelPriceDrift_0.002": {"fuelPriceDrift": 0.002},
    # "fuelPriceDrift_0.02": {"fuelPriceDrift": 0.02},

    # "oreCostParamOne_0.1": {"oreCostParamOne": 0.1},
    # "base_oreCostParamOne_0.3": {"oreCostParamOne": 0.3},
    # "oreCostParamOne_0.5": {"oreCostParamOne": 0.5},

    # "sigmaOreCostParamOne 0.001": {"sigmaOreCostParamOne": 0.001},
    # "base_sigmaOreCostParamOne 0.1": {"sigmaOreCostParamOne": 0.1},
    # "sigmaOreCostParamOne 0.2": {"sigmaOreCostParamOne": 0.2},

    # "oreCostParamTwo_0.1": {"oreCostParamTwo": 0.1},
    # "base_oreCostParamTwo_0.5": {"oreCostParamTwo": 0.5},
    # "oreCostParamTwo_0.9": {"oreCostParamTwo": 0.9},

    # "muOreDeposit_100": {"muOreDeposit": 100},
    # "base_muOreDeposit_150": {"muOreDeposit": 150},
    # "muOreDeposit_200": {"muOreDeposit": 200},

    # "sigmaSqOreDeposit_40": {"sigmaSqOreDeposit": 40},
    # "base_sigmaSqOreDeposit_400": {"sigmaSqOreDeposit": 400},
    # "sigmaSqOreDeposit_4000": {"sigmaSqOreDeposit": 4000},

    # "oreProductivity_0.5": {"oreProductivity": 0.5},
    # "base_oreProductivity_1": {"oreProductivity": 1},
    # "oreProductivity_2": {"oreProductivity": 2},

}

def generate_scenarios(scenarios=scenarios):
    for scenario_name, new_params in scenarios.items():
        params = Parameters()
        # params.name = scenario_name
        for param_name, param_val in new_params.items():
            getattr(params, param_name)["val"] = param_val
        scenarios[scenario_name] = params#["params"] = params
    return scenarios