from parameters import Parameters

scenario_groups = {
    "Material intensity of renewable energy capital": {
        "Low R material intensity": {"recMaterialProductivity": 2, "color": "green"},
        "Base R material intensity": {"recMaterialProductivity": 1.25, "color": "orange"},
        "High R material intensity": {"recMaterialProductivity": 0.75, "color": "blue"}
    },

    # "The impact of the rising cost of fossil fuels": {
    #     "Low fuel price growth": {"fuelPriceDrift": 0.0003, "color": "blue"},
    #     "Base fuel price growth": {"fuelPriceDrift": 0.002, "color": "orange"},
    #     "High fuel price growth": {"fuelPriceDrift": 0.006, "color": "green"}
    # },

    # "A declining metal ore extraction costs": {
    #     "Baseline": {"color": "blue"},
    #     "Slow decline of ore cost": {"oreCostShocks": 400, "color": "orange"},
    #     "Fast decline of ore cost": {"oreCostShocks": 200, "color": "green"}
    # },

    # "The impact of carbon pricing on the energy transition pathways": {
    #     # "baseline": {},
    #     "high tax / low expectations": {"materialBufferReactionToCarbonTax": 0.1, 
    #                                                  "targetFinalCarbonTax": 0.6},
    #     "high tax / high expectations": {"materialBufferReactionToCarbonTax": 2, 
    #                                                "targetFinalCarbonTax": 0.6},
    #     "low tax / low expectations": {"materialBufferReactionToCarbonTax": 0.1, 
    #                                                  "targetFinalCarbonTax": 0.15},
    #     "low tax / high expectations": {"materialBufferReactionToCarbonTax": 2, 
    #                                                "targetFinalCarbonTax": 0.15},
    #     "baseline": {"constantMaterialBuffer": 1}
    #     },

        # "0.1x reaction and 60pct target carbon tax": {"materialBufferReactionToCarbonTax": 0.1, 
        #                                              "targetFinalCarbonTax": 0.6},
        # "2x reaction and 60pct target carbon tax": {"materialBufferReactionToCarbonTax": 2, 
        #                                            "targetFinalCarbonTax": 0.6},
        # "0.1x reaction and 15pct target carbon tax": {"materialBufferReactionToCarbonTax": 0.1, 
        #                                              "targetFinalCarbonTax": 0.15},
        # "2x reaction and 15pct target carbon tax": {"materialBufferReactionToCarbonTax": 2, 
        #                                            "targetFinalCarbonTax": 0.15},
        # "baseline": {"constantMaterialBuffer": 1},

        # "0.3 reaction and 40pct target carbon tax": {"materialBufferReactionToCarbonTax": 0.3, 
        #                                              "targetFinalCarbonTax": 0.4},
        # "3 reaction and 40pct target carbon tax": {"materialBufferReactionToCarbonTax": 3, 
        #                                            "targetFinalCarbonTax": 0.4},
        # "0.3 reaction and 20pct target carbon tax": {"materialBufferReactionToCarbonTax": 0.3, 
        #                                              "targetFinalCarbonTax": 0.2},
        # "3 reaction and 20pct target carbon tax": {"materialBufferReactionToCarbonTax": 3, 
        #                                            "targetFinalCarbonTax": 0.2},
        # "constant 0.3 m. buffer and 0.01pct target carbon tax": {"constantMaterialBuffer": 1, 
        #                                              "targetFinalCarbonTax": 0.0001},
        
        # 'Near-zero target carbon tax': {"targetFinalCarbonTax": 0.0001},
        # '30pct target carbon tax': {"targetFinalCarbonTax": 0.3},
        # '70pct target carbon tax': {"targetFinalCarbonTax": 0.7},
        # '200pct carbon tax': {"carbonTax": 2},
        # '500pct carbon tax': {"carbonTax": 5},
        # '1000pct carbon tax': {"carbonTax": 10},


        # "Fast decline of ore cost and 30pct target carbon tax": {"oreCostShocks": 200,
        #                                                       "targetFinalCarbonTax": 0.3},
        # "Fast decline of ore cost and 1pct target carbon tax": {"oreCostShocks": 200,
        #                                                         "targetFinalCarbonTax": 0.01},
        # "No decline of ore cost and 30pct target carbon tax": {"targetFinalCarbonTax": 0.3},
        # "No decline of ore cost and 1pct target carbon tax": {"targetFinalCarbonTax": 0.01},

        # "Fast decline of ore cost and 0.3 material buffer": {"oreCostShocks": 200,
        #                                                       "materialBuffer": 0.3},
        # "Fast decline of ore cost and 0.01 material buffer": {"oreCostShocks": 200,
        #                                                         "materialBuffer": 0.01},
        # "No decline of ore cost and 0.3 material buffer": {"materialBuffer": 0.3},
        # "No decline of ore cost and 0.01 material buffer": {"materialBuffer": 0.01},

        # "Fast decline of ore cost and 0.3 entry material buffer": {"oreCostShocks": 200,
        #                                                       "entrantMaterialBuffer": 0.3},
        # "Fast decline of ore cost and 0.01 entry material buffer": {"oreCostShocks": 200,
        #                                                         "entrantMaterialBuffer": 0.01},
        # "No decline of ore cost and 0.3 entry material buffer": {"entrantMaterialBuffer": 0.3},
        # "No decline of ore cost and 0.01 entry material buffer": {"entrantMaterialBuffer": 0.01},

        # "Stable ore cost": {"oreCostShocks": 0},
        # "Declining ore cost": {"oreCostShocks": 400},
        # "Sharply declining ore cost": {"oreCostShocks": 200},

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

    # "Material buffer configurations": {
        # "Zero material buffer": {"materialBuffer": 0},
        # "Baseline material buffer (0.3)": {"materialBuffer": 0.3},
        # "High material buffer (0.6)": {"materialBuffer": 0.6},
    # },

    # "Ore deposit exploration probability": {
        # "No ore deposit exploration": {"miningSiteExplorationProbability": 0,
        #                                "miningSiteShocks": 1,
        #                                "oreCostShocks": 200},
        # "Infrequent ore deposit exploration": {"miningSiteExplorationProbability": 0.1,
        #                                        "miningSiteShocks": 1,
        #                                        "oreCostShocks": 200},
        # "Frequent ore deposit exploration": {"miningSiteExplorationProbability": 0.5,
        #                                      "miningSiteShocks": 1,
        #                                      "oreCostShocks": 200},
        
        # "miningSiteExplorationProbability_0.1": {"miningSiteExplorationProbability": 0.1},
        # # "base_miningSiteExplorationProbability_0.5": {"miningSiteExplorationProbability": 0.5},
        # "miningSiteExplorationProbability_0.25": {"miningSiteExplorationProbability": 0.25},
        # "miningSiteExplorationProbability_0.9": {"miningSiteExplorationProbability": 0.9},
    # },

        # "extreme renewables material intensity": {"recMaterialProductivity": 0.75},
        # "higher renewables material intensity": {"recMaterialProductivity": 1.25},
        # "baseline renewables material intensity": {"recMaterialProductivity": 2},
        # "lower renewables material intensity": {"recMaterialProductivity": 3},

        # "recMaterialProductivity_0.9": {"recMaterialProductivity": 0.9},
        # # "base_recMaterialProductivity_1.25": {"recMaterialProductivity": 1.25},
        # "recMaterialProductivity_2": {"recMaterialProductivity": 2},
    
    # "Number of mining sites variations": {
    #     "nrMiningSites_5": {"nrMiningSites": 5, "color": "blue"},
    #     "nrMiningSites_20": {"nrMiningSites": 20, "color": "orange"},
    #     "nrMiningSites_100": {"nrMiningSites": 100, "color": "green"},

        # "logitCompetitionParamMining_1": {"logitCompetitionParamMining": 1},
        # # "base_logitCompetitionParamMining_10": {"logitCompetitionParamMining": 10},
        # "logitCompetitionParamMining_50": {"logitCompetitionParamMining": 50},
    # },

        # "fuelPriceDrift_0.0003": {"fuelPriceDrift": 0.0003},
        # # "base_fuelPriceDrift": {"fuelPriceDrift": 0.002},
        # "fuelPriceDrift_0.006": {"fuelPriceDrift": 0.006},

        # "fuelPriceVolatility_0.00000001": {"fuelPriceVolatility": 0.00000001},
        # # "base_fuelPriceVolatility_0.00003": {"fuelPriceVolatility": 0.00003},
        # "fuelPriceVolatility_0.0009": {"fuelPriceVolatility": 0.0009},

    # "Other Material Productivity Variations": {
        # "fgcMaterialProductivity_0.9": {"fgcMaterialProductivity": 0.9},
        # # "base_fgcMaterialProductivity_1": {"fgcMaterialProductivity": 1},
        # "fgcMaterialProductivity_2": {"fgcMaterialProductivity": 2},

        # "fecMaterialProductivity_10": {"fecMaterialProductivity": 10},
        # # "base_fecMaterialProductivity_15": {"fecMaterialProductivity": 15},
        # "fecMaterialProductivity_20": {"fecMaterialProductivity": 20},

        # "mcMaterialProductivity_5": {"mcMaterialProductivity": 5},
        # # "base_mcMaterialProductivity_7": {"mcMaterialProductivity": 7},
        # "mcMaterialProductivity_10": {"mcMaterialProductivity": 10},
    # },

    # "Other parameters": {
        # "reCapitalLifeSpan_15": {"reCapitalLifeSpan": 15},
        # # "base_reCapitalLifeSpan_20" : {"reCapitalLifeSpan": 20},
        # "reCapitalLifeSpan_25": {"reCapitalLifeSpan": 25},

        # "loanInterestRate_0.00001": {"loanInterestRate": 0.00001},
        # # "base_loanInterestRate_0.001": {"loanInterestRate": 0.0001},
        # "loanInterestRate_0.05": {"loanInterestRate": 0.05},
    # }
}

scenarios = {}
for group_name, group_scenarios in scenario_groups.items():
    for scen_name, scen_params in group_scenarios.items():
        if isinstance(scen_params, dict):
            scen_params["group"] = group_name
        scenarios[scen_name] = scen_params

def generate_scenarios(scenarios=scenarios):
    for scenario_name, new_params in scenarios.items():
        params = Parameters()
        for param_name, param_val in new_params.items():
            if param_name == "color":
                params.color = param_val
            elif param_name == "group":
                params.group = param_val
            else:
                getattr(params, param_name)["val"] = param_val
        scenarios[scenario_name] = params
    return scenarios