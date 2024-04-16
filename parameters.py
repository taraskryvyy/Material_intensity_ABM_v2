# parameters.py

import os
import re

class Parameters:
    def __init__(self):
        self.miningSiteShocks = {"val": 0, "symbol": r"\varepsilon_{R^{D}}", "desc": "shocks to mining site deposits"}
        self.oreCostShocks = {"val": 0, "symbol": r"\varepsilon_{\gamma^{ore}_1}", "desc": "shocks to ore extraction cost parameter 1"}

        # Simulation parameters
        self.nrTimesteps={"val": 200, "symbol": r"\#_{timesteps}", "desc": "number of timesteps"}
        self.nrMonteCarlo={"val": 100, "symbol": r"\#_{MonteCarlo}", "desc": "number of Monte Carlo repetitions"}
        self.maxNumberOfMatchingRounds={"val": 50, "symbol": r"{\#^{matching}_{rounds}}_{max}", "desc": "maximum number of rounds in a market during matching"}
        self.epsilonPrecision={"val": 0.001, "symbol": r"\epsilon_{precision}", "desc": "precision parameter to avoid floating point errors"}

        ## Model parameters
        self.adaptiveExpectation={"val": 0.5, "symbol": r"\alpha_{exp}", "desc": "adaptive expectation parameter"}
        self.logitCompetitionParam={"val": 5, "symbol": r"\gamma^{logit}", "desc": "logit competition parameter"}
        self.finalGoodBuffer={"val": 0.1, "symbol": r"\beta_{FG}", "desc": "final good inventory buffer parameter"}
        self.materialBuffer={"val": 0.3, "symbol": r"\beta_{M}", "desc": "material inventory buffer parameter"}
        self.energyBuffer={"val": 0.5, "symbol": r"\beta_{E}", "desc": "desired excess capacity of the energy grid"}
        self.cashBuffer={"val": 0.5, "symbol": r"\beta_{cash}", "desc": "how much cash a firm would want to keep"}
        self.muMarkup={"val": 0.02, "symbol": r"\mu_{FN_{markup}}", "desc": "Folded Normal Distribution expected value for markup adjustment"}
        self.sigmaSqMarkup={"val": 0.008, "symbol": r"\sigma^2_{FN_{markup}}", "desc": "Folded Normal Distribution variance for markup adjustment"}
        # Final Good Sector Parameters
        self.fgLaborProductivity={"val": 15, "symbol": r"\alpha^{FG}", "desc": " labor productivity in final good sector"}
        self.fgCapitalLifeSpan={"val": 10, "symbol": r"\tau^{K_{FG}}", "desc": "useful lifespan of final good capital"}
        self.fgCapitalDepreciationRate={"val": round(1/self.fgCapitalLifeSpan["val"], 4), "symbol": r"\delta^{K_{FG}}", "desc": "depreciation rate of final good capital"}
        self.fgCapitalLoanDuration={"val": self.fgCapitalLifeSpan["val"], "symbol": r"\eta^{K_{FG}}", "desc": "duration of a loan to cover final good capital investment"}
        self.fgCapitalDeliveryTime={"val": 1, "symbol": r"{dt}^{{K}_{FG}}", "desc": "time to deliver final good capital"}
        self.fgEntryProbability={"val": 0, "symbol": r"{prob}^{FG}", "desc": "entry probability of a final good firm"}
        # Energy Sector Parameters
        self.reLaborProductivity={"val": 10, "symbol": r"\alpha^{RE}", "desc": " labor productivity in renewable energy sector"}
        self.feLaborProductivity={"val": 10, "symbol": r"\alpha^{FE}", "desc": " labor productivity in fossil-fuel energy sector"}
        self.feFuelProductivity={"val": 20, "symbol": r"\phi", "desc": "thermal efficiency (energy-output-to-fuel-input ratio)"}
        self.fuelPrice={"val": 0.1, "symbol": r"p_{fuel}", "desc": "fuel price"}
        self.fuelPriceDrift={"val": 0.002, "symbol": r"\mu_{p_{fuel}}", "desc": "fuel price drift"}
        self.fuelPriceVolatility={"val": 0.00003, "symbol": r"\sigma_{p_{fuel}}", "desc": "fuel price volatility (variance of the Brownian motion)"}
        self.fuelPriceSensitivity={"val": 0, "symbol": r"\beta_{fuel}", "desc": "sensitivity of fuel price to fuel demand"}
        self.energyProductivity={"val": 2, "symbol": r"\varepsilon", "desc": "energy productivity in final good sector"}
        self.energyPricing={"val": 0, "symbol": r"{pricing}_{E}", "desc": "energy market pricing: 0 for weighted average, 1 for marginal"}
        self.reCapitalLifeSpan={"val": 20, "symbol": r"\tau^{K_{RE}}", "desc": "useful lifespan of renewable energy capital"}
        self.feCapitalLifeSpan={"val": 30, "symbol": r"\tau^{K_{FE}}", "desc": "useful lifespan of fossil-fuel energy capital"}
        self.reCapitalDepreciationRate={"val": round(1/self.reCapitalLifeSpan["val"], 4), "symbol": r"\delta^{K_{RE}}", "desc": "depreciation rate of renewable energy capital"}
        self.feCapitalDepreciationRate={"val": round(1/self.feCapitalLifeSpan["val"], 4), "symbol": r"\delta^{K_{FE}}", "desc": "depreciation rate of fossil-fuel energy capital"}
        self.reCapitalLoanDuration={"val": self.reCapitalLifeSpan["val"], "symbol": r"\eta^{K_{RE}}", "desc": "duration of a loan to cover renewable energy capital investment"}
        self.feCapitalLoanDuration={"val": self.feCapitalLifeSpan["val"], "symbol": r"\eta^{K_{FE}}", "desc": "duration of a loan to cover fossil-fuel energy capital investment"}
        self.reCapitalDeliveryTime={"val": 1, "symbol": r"{dt}^{{K}_{RE}}", "desc": "time to deliver renewable energy capital"}
        self.feCapitalDeliveryTime={"val": 1, "symbol": r"{dt}^{{K}_{FE}}", "desc": "time to deliver fossil-fuel energy capital"}
        # Material Sector Parameters
        self.mLaborProductivity={"val": 10, "symbol": r"\alpha^{M}", "desc": " labor productivity in material sector"}
        self.oreProductivity={"val": 1, "symbol": r"\rho", "desc": "ore productivity in material sector"}
        self.oreCostParamOne={"val": 0.3, "symbol": r"\gamma^{ore}_1", "desc": "ore extraction cost parameter 1 (ore cost of newly explored ore deposit)"}
        self.oreCostParamTwo={"val": 0.5, "symbol": r"\gamma^{ore}_2", "desc": "ore extraction cost parameter 2 (controls speed of ore cost increase)"}
        self.muOreDeposit={"val": 150, "symbol": r"\mu_{R^{D}}", "desc": "average ore deposit of the newly explored mining site"}
        self.minimumViableOreDeposit={"val": round(self.muOreDeposit["val"] / 20, 4), "symbol": r"R^{D}_{min}", "desc": "minimum ore deposit that is viable for mining"}
        self.sigmaSqOreDeposit={"val": 400, "symbol": r"\sigma^2_{R^{D}}", "desc": "variance of ore deposit of the newly explored mining site"}
        self.sigmaOreCostParamOne={"val": 0.05, "symbol": r"\sigma^2_{\gamma^{ore}_1}", "desc": "variance of ore cost parameter 1"}
        self.materialPricing={"val": 0, "symbol": r"{pricing}_{M}", "desc": "material market pricing: 0 for weighted average, 1 for marginal"}
        self.randomPickOreDeposit={"val": 0, "symbol": r"\chi^{R^{D}}", "desc": "randomly pick ore deposit"}
        self.miningSiteExplorationProbability={"val": 0.5, "symbol": r"{prob}^{R^{D}}", "desc": "exploration probability of a mining site"}
        self.logitCompetitionParamMining={"val": 10, "symbol": r"\gamma^{logit}_{mining}", "desc": "logit competition parameter for mining site selection"}
        self.adaptiveExpectationMaterialPrice={"val": 0.5, "symbol": r"\alpha_{exp}^{p_{M,t}}", "desc": "adaptive expectation parameter for material price"}
        # self.miningSiteExplorationParam={"val": -100, "symbol": r"\gamma_{R^{stor}}", "desc": "mining site exploration parameter"}
        # self.storageCostParamOne={"val": 1, "symbol": r"\gamma^{stor}_1", "desc": "storage cost parameter 1 (storage cost when inventory is empty)"}
        # self.storageCostParamTwo={"val": 1, "symbol": r"\gamma^{stor}_2", "desc": "storage cost parameter 2 (controls speed of storage cost increase)"}
        # self.materialRiskAversion={"val": 1, "symbol": r"\varsigma_{M}", "desc": "risk aversion of firms in material sector"}
        self.mCapitalLifeSpan={"val": 30, "symbol": r"\tau^{K_{M}}", "desc": "useful lifespan of material capital"}
        self.mCapitalDepreciationRate={"val": round(1/self.mCapitalLifeSpan["val"],4), "symbol": r"\delta^{K_{M}}", "desc": "depreciation rate of material capital"}
        self.mCapitalLoanDuration={"val": self.mCapitalLifeSpan["val"], "symbol": r"\eta^{K_{M}}", "desc": "duration of a loan to cover material capital investment"}
        self.mCapitalDeliveryTime={"val": 1, "symbol": r"{dt}^{{K}_{M}}", "desc": "time to deliver material capital"}
        self.materialDeliveryTime={"val": 0, "symbol": r"{dt}^{M}", "desc": "time to deliver material"}
        # Capital Sector Parameters
        # self.fgcRiskAversion={"val": 1, "symbol": r"\varsigma_{K_{FG}}", "desc": "risk aversion of firms in final good capital sector"}
        # self.recRiskAversion={"val": 1, "symbol": r"\varsigma_{K_{RE}}", "desc": "risk aversion of firms in renewable energy capital sector"}
        # self.fecRiskAversion={"val": 1, "symbol": r"\varsigma_{K_{FE}}", "desc": "risk aversion of firms in fossil-fuel energy capital sector"}
        # self.mcRiskAversion={"val": 1, "symbol": r"\varsigma_{K_{M}}", "desc": "risk aversion of firms in material capital sector"}
        self.fgcMaterialProductivity={"val": 1, "symbol": r"m^{K_{FG}}", "desc": "material productivity in final good capital sector"}
        self.recMaterialProductivity={"val": 1.25, "symbol": r"m^{K_{RE}}", "desc": "material productivity in renewable energy capital sector"}
        self.fecMaterialProductivity={"val": 15, "symbol": r"m^{K_{FE}}", "desc": "material productivity in fossil-fuel energy capital sector"}
        self.mcMaterialProductivity={"val": 7, "symbol": r"m^{K_{M}}", "desc": "material productivity in material capital sector"}
        # self.loanDurationInCapitalSector={"val": 10, "symbol": r"\eta^{K}", "desc": "duration of a loan in capital sectors"}
        # Household Parameters
        self.wage={"val": 0.1, "symbol": r"w", "desc": "wage rate"}
        self.unemploymentBenefit={"val": self.wage["val"] / 2, "symbol": r"u", "desc": "unemployment benefit"}
        self.propensityIncome={"val": 0.8, "symbol": r"c_{Y}^{HH}", "desc": "propensity to consume out of income"}
        self.propensityWealth={"val": 0.1, "symbol": r"c_{D}^{HH}", "desc": "propensity to consume out of wealth"}
        self.taxRate={"val": 0.3, "symbol": r"\theta^{tax}", "desc": "tax rate"}
        self.dividendRate={"val": 0.01, "symbol": r"\theta^{div}", "desc": "dividend payout ratio"}
        # Research and Development Parameters
        self.RDbudgetFraction={"val": 0.1, "symbol": r"\nu^{R\&D}", "desc": "fraction of net profit allocated for the R\&D"}
        self.imitationFraction={"val": 0, "symbol": r"\chi^{imit}", "desc": "fraction of the R\&D budget allocated towards imitation"}
        self.innovationFraction={"val": 1 - self.imitationFraction["val"], "symbol": r"\chi^{innov}", "desc": "fraction of the R\&D budget allocated towards innovation"}
        self.RDsuccessParam={"val": 0.8, "symbol": r"\rho^{R\&D}", "desc": "parameter managing success probability of the R\&D process"}
        self.muProductInnovation={"val": 0.003, "symbol": r"\mu_{FN^{product}_{innov}}", "desc": "Folded Normal Distribution expected value for product innovation"}
        self.sigmaSqProductInnovation={"val": 0.0008, "symbol": r"\sigma^2_{FN^{product}_{innov}}", "desc": "Folded Normal Distribution variance for product innovation"}
        self.muProcessInnovation={"val": 0.002, "symbol": r"\mu_{FN^{process}_{innov}}", "desc": "Folded Normal Distribution expected value for process innovation"}
        self.sigmaSqProcessInnovation={"val": 0.0008, "symbol": r"\sigma^2_{FN^{process}_{innov}}", "desc": "Folded Normal Distribution variance for process innovation"}
        # Banking parameters
        self.loanParamCritLeverage={"val": 0.5, "symbol": r"\lambda^{loan}_1", "desc": "critical value of leverage ratio, under which probability of granting loan falls below 0.5"}
        self.loanParamSpeedLeverage={"val": 10, "symbol": r"\lambda^{loan}_2", "desc": "bank's lending decision sensitivivity to borrower'leverage ratio bank"}
        self.bnkMaxLoanToDepositRatio={"val": 500, "symbol": r"\lambda^{loan}_3", "desc": "maximum loan to deposit ratio of a bank"}
        self.CBloanInterestRate={"val": 0.00015, "symbol": r"r^{L_{CB}}", "desc": "loan interest rate of the central bank"}
        self.CBdepositInterestRate={"val": 0.0005, "symbol": r"r^{D_{CB}}", "desc": "deposit interest rate of the central bank"}
        self.shortTermLoanDuration={"val": 10, "symbol": r"\tau^{short}", "desc": "duration of a short-term loan"}
        self.loanInterestRate={"val": 0.001, "symbol": r"r^{L}", "desc": "loan interest rate"}
        self.depositInterestRate={"val": 0.0001, "symbol": r"r^{D}", "desc": "deposit interest rate"}


        ### Initial state of economy

        ## Initial number of Agents at the beginning of a simulation
        self.nrHouseholds={"val": 100, "symbol": r"\#_{HH}", "desc": "number of households"}
        self.nrFinalGoodCapitalFirms={"val": 1, "symbol": r"\#_{FGC}", "desc": "number of final good capital firms"}
        self.nrFinalGoodFirms={"val": 10, "symbol": r"\#_{FG}", "desc": "number of final good firms"}
        self.nrCommercialBanks={"val": 1, "symbol": r"\#_{BNK}", "desc": "number of commercial banks"}
        self.nrFossilFuelEnergyPowerPlants={"val": 10, "symbol": r"\#_{FE}", "desc": "number of fossil-fuel energy power plants"}
        self.nrRenewableEnergyPowerPlants={"val": 2, "symbol": r"\#_{RE}", "desc": "number of renewable energy power plants"}
        self.nrMaterialFirms={"val": 5, "symbol": r"\#_{M}", "desc": "number of material firms"}
        self.nrMiningSites={"val": 100, "symbol": r"\#_{R^{D}}", "desc": "number of mining sites"}
        self.nrFossilFuelEnergyCapitalFirms={"val": 1, "symbol": r"\#_{FEC}", "desc": "number of fossil-fuel energy capital firms"}
        self.nrRenewableEnergyCapitalFirms={"val": 1, "symbol": r"\#_{REC}", "desc": "number of renewable energy capital firms"}
        self.nrMaterialCapitalFirms={"val": 1, "symbol": r"\#_{MC}", "desc": "number of material capital firms"}
        
        ## Initial state of Agents at the beginning of a simulation
        # Initial Markups
        self.fgMarkupInitial={"val": 0.1, "symbol": r"\mu_{FG,0}", "desc": "initial markup of a final good firm"}
        # self.fgcMarkupInitial={"val": 0.1, "symbol": r"\mu_{FGC,0}", "desc": "initial markup of a final good capital firm"}
        self.mMarkupInitial={"val": 0.3, "symbol": r"\mu_{M,0}", "desc": "initial markup of a material firm"}
        # self.mcMarkupInitial={"val": 0.5, "symbol": r"\mu_{MC,0}", "desc": "initial markup of a material capital firm"}
        self.eMarkup={"val": 0.3, "symbol": r"\mu_{E}", "desc": "markup for the energy sector"}
        self.fgcMarkup={"val": 0.5, "symbol": r"\mu_{FGC}", "desc": "markup for the final good capital sector"}
        self.mcMarkup={"val": 0.5, "symbol": r"\mu_{MC}", "desc": "markup for the material capital sector"}
        self.recMarkup={"val": 0.5, "symbol": r"\mu_{K_{RE}}", "desc": "markup for the renewable energy capital sector"}
        self.fecMarkup={"val": 0.5, "symbol": r"\mu_{K_{FE}}", "desc": "markup for the fossil-fuel energy capital sector"}
        # self.reMarkupInitial={"val": 0.1, "symbol": r"\mu_{RE,0}", "desc": "initial markup of a renewable energy power plant"}
        # self.feMarkupInitial={"val": 0.1, "symbol": r"\mu_{FE,0}", "desc": "initial markup of a fossil-fuel energy power plant"}
        # Inital Labor Productivities
        self.fgcLaborProductivityInitial={"val": 10, "symbol": r"\alpha^{K_{FG}}_{i, 0}", "desc": "initial labor productivity in final good capital sector"}
        self.recLaborProductivityInitial={"val": 10, "symbol": r"\alpha^{K_{RE}}_{i, 0}", "desc": "initial labor productivity in renewable energy capital sector"}
        self.fecLaborProductivityInitial={"val": 10, "symbol": r"\alpha^{K_{FE}}_{i, 0}", "desc": "initial labor productivity in fossil-fuel energy capital sector"}
        self.mcLaborProductivityInitial={"val": 10, "symbol": r"\alpha^{K_M}_{i, 0}", "desc": "initial labor productivity in material capital sector"}
        # Initial Capital Productivities
        self.fgcCapitalProductivityInitial={"val": 2, "symbol": r"\kappa^{K_{FG}}_{i, 0}", "desc": "initial productivity of capital for final good sector"}
        self.fecCapitalProductivityInitial={"val": 2, "symbol": r"\kappa^{K_{FE}}_{i, 0}", "desc": "initial productivity of capital for fossil-fuel energy sector"}
        self.recCapitalProductivityInitial={"val": 2, "symbol": r"\kappa^{K_{RE}}_{i, 0}", "desc": "initial productivity of capital for renewable energy sector"}
        self.mcCapitalProductivityInitial={"val": 2, "symbol": r"\kappa^{K_{M}}_{i, 0}", "desc": "initial productivity of capital for material sector"}
        # Initial Deposit Balances
        self.fgDepositInitial={"val": 0, "symbol": r"D^{FG}_{i,0}", "desc": "initial deposit of a final good firm"}
        self.fgcDepositInitial={"val": 3, "symbol": r"D^{K_{FG}}_{i,0}", "desc": "initial deposit of a final good capital firm"}
        self.mDepositInitial={"val": 0, "symbol": r"D^{M}_{i,0}", "desc": "initial deposit of a material firm"}
        self.mcDepositInitial={"val": 300, "symbol": r"D^{K_{M}}_{i,0}", "desc": "initial deposit of a material capital firm"}
        self.feDepositInitial={"val": 0, "symbol": r"D^{FE}_{i,0}", "desc": "initial deposit of a fossil-fuel energy power plant"}
        self.reDepositInitial={"val": 0, "symbol": r"D^{RE}_{i,0}", "desc": "initial deposit of a renewable energy power plant"}
        self.fecDepositInitial={"val": 3, "symbol": r"D^{K_{FE}}_{i,0}", "desc": "initial deposit of a fossil-fuel energy capital firm"}
        self.recDepositInitial={"val": 3, "symbol": r"D^{K_{RE}}_{i,0}", "desc": "initial deposit of a renewable energy capital firm"}
        self.hhDepositInitial={"val": 0.01, "symbol": r"D^{HH}_{i,0}", "desc": "initial deposit of a household"}
        # Initial Output Inventories
        self.fgOutputInventoryInitial={"val": 0, "symbol": r"inv^{FG}_{i,0}", "desc": "initial output inventory of a final good firm"}
        # self.fgcOutputInventoryInitial={"val": 10, "symbol": r"inv^{K_{FG}}_{i,0}", "desc": "initial output inventory of a final good capital firm"}
        self.mOutputInventoryInitial={"val": 0, "symbol": r"inv^{M}_{i,0}", "desc": "initial output inventory of a material firm"}
        # self.mcOutputInventoryInitial={"val": 10, "symbol": r"inv^{K_{M}}_{i,0}", "desc": "initial output inventory of a material capital firm"}
        # self.fecOutputInventoryInitial={"val": 10, "symbol": r"inv^{K_{FE}}_{i,0}", "desc": "initial output inventory of a fossil-fuel energy capital firm"}
        # self.recOutputInventoryInitial={"val": 10, "symbol": r"inv^{K_{RE}}_{i,0}", "desc": "initial output inventory of a renewable energy capital firm"}
        # Initial Capital Stocks
        self.fgCapitalStockInitial={"val": 1, "symbol": r"K^{FG}_{i,0}", "desc": "initial capital stock of a final good firm"}
        self.mCapitalStockInitial={"val": 1, "symbol": r"K^{M}_{i,0}", "desc": "initial capital stock of a material firm"}
        # Initial Power Generation Capacities
        self.feCapitalStockInitial={"val": 1, "symbol": r"K^{FE}_{i,0}", "desc": "initial capital stock of a fossil-fuel energy power plant"}
        self.reCapitalStockInitial={"val": 1, "symbol": r"K^{RE}_{i,0}", "desc": "initial capital stock of a renewable energy power plant"}
        # Initial Material Stocks
        self.fgcMaterialInventoryInitial={"val": 0, "symbol": r"M^{K_{FG}}_{i,0}", "desc": "initial material inventory of a final good capital firm"}
        self.recMaterialInventoryInitial={"val": 0, "symbol": r"M^{K_{RE}}_{i,0}", "desc": "initial material inventory of a renewable energy capital firm"}
        self.fecMaterialInventoryInitial={"val": 0, "symbol": r"M^{K_{FE}}_{i,0}", "desc": "initial material inventory of a fossil-fuel energy capital firm"}
        self.mcMaterialInventoryInitial={"val": 0, "symbol": r"M^{K_{M}}_{i,0}", "desc": "initial material inventory of a material capital firm"}
        
        self.foreignEconomyFuelInventoryInitial={"val": 1000000000, "symbol": r"\hat{F}^{FE}_{i,0}", "desc": "initial fuel inventory of the foreign economy"}
        self.feFuelInventoryInitial={"val": 0, "symbol": r"F_{i,0}", "desc": "initial fuel inventory of a fossil-fuel energy power plant"}

        # Notation simplification
        # self.xCapitalLifeSpan={"val": 0, "symbol": r"\tau^{K_{x}}", "desc": "useful lifespan of x type of capital"}
        # self.xCapitalDeliveryTime={"val": 0, "symbol": r"{dt}^{{K}_{x}}", "desc": "time to deliver x type of capital"}
        # self.xCapitalDepreciationRate={"val": 0, "symbol": r"\delta^{K_{x}}", "desc": "depreciation rate of x type of capital"}
        # self.xCapitalLoanDuration={"val": 0, "symbol": r"\eta^{K_{x}}", "desc": "duration of a loan to cover x type of capital investment"}
        # self.xLoanDuration={"val": 0, "symbol": r"\eta^{x}", "desc": "duration of a loan in sector x"}
        # self.xGracePeriod={"val": 0, "symbol": r"{gp}^{x}", "desc": "grace period of a loan in sector x"}
        # self.xMaterialProductivity={"val": 0, "symbol": r"m^{K_{x}}", "desc": "material productivity in x type of capital sector"}
        # self.xDeliveryTime={"val": 0, "symbol": r"{dt}^{x}", "desc": "time to deliver x type of good"}
        # self.xCapitalRiskAversion={"val": 0, "symbol": r"\varsigma_{K_{x}}", "desc": "risk aversion of firms in x type of capital sector"}


        ### State variables

    def to_dict(self):
        # Convert the instance to a dictionary
        return vars(self)
    
    @classmethod
    def from_dict(cls, data):
        # Create a Parameters instance from a dictionary
        return cls(**data)
    
    def generate_latex_parameters_file(self):
        '''
        This function generates a LaTeX variables file from the class instance.
        Each variable should yield three LaTeX commands of the form:
        \newcommand\variableName{variableNameSymbol}
        \newcommand\variableNameValue{variableNameValue}
        \newcommand\variableNameDesc{variableNameDesc}
        '''

        with open('latex_parameters_file.tex', 'w') as f:
            f.write("% LaTeX Parameters File\n")
            for attribute_name, attribute_dict in self.__dict__.items():
                # latex_symbol = attribute_dict['symbol'].replace('\\', '\\\\').replace('_', '\\_')
                # f.write(f"\\newcommand{{{attribute_name}}}{{{attribute_dict['symbol']}}}\n")
                # f.write(f"\\newcommand{{{attribute_name}Value}}{{{attribute_dict['val']}}}\n")
                # f.write(f"\\newcommand{{{attribute_name}Desc}}{{{attribute_dict['desc']}}}\n")

                f.write(f"\\newcommand{{\\{attribute_name}}}{{{attribute_dict['symbol']}}}\n")
                f.write(f"\\newcommand{{\\{attribute_name}Value}}{{{attribute_dict['val']}}}\n")
                f.write(f"\\newcommand{{\\{attribute_name}Desc}}{{{attribute_dict['desc']}}}\n")

    # Function to read a .tex file, convert LaTeX \newcommand definitions to a LaTeX table, and write it to another .tex file
    def latex_file_to_table_to_file(self, output_filename):
        # Read the content of the input .tex file
        # with open(input_filename, "r") as infile:
        #     latex_text = infile.read()
        
        # Initialize the table header
        table_header = r"""\begin{table}[ht]
    \centering
    \caption{General Simulation Parameters}
    \begin{tabular}{lrl}
    \toprule
    Parameter  & Value & Description  \\
    \midrule
    """
        
        # Initialize the table body
        table_body = ""
        
        # # Define a regular expression pattern to capture LaTeX \newcommand definitions
        # pattern = r"\\newcommand{\\([a-zA-Z0-9_]+)}{(.+)}"
        
        # # Find all matches
        # matches = re.findall(pattern, latex_text)
        
        # Loop through matches and populate the table body
        for command in self.__dict__.keys():
            table_body += f"  $\\{command}$ & \\{command}Value & \\{command}Desc \\\\\n"
        
        # Initialize the table footer
        table_footer = r"""  \bottomrule
    \end{tabular}
    \end{table}"""
        
        # Combine header, body, and footer to create the full table
        full_table = table_header + table_body + table_footer
        
        if os.path.exists(output_filename):
            os.remove(output_filename)
        # Write the full table to the output .tex file
        with open(output_filename, "w") as outfile:
            outfile.write(full_table)

    # # Example input and output filenames
    # input_filename = "/mnt/data/sample_input.tex"
    # output_filename = "/mnt/data/sample_output_table.tex"

    # # Dummy content for the sample_input.tex file (you can replace this with your actual content)
    # sample_content = r"""
    # \newcommand{\nrTimesteps}{\#_{timesteps}}
    # \newcommand{\nrTimestepsValue}{100}
    # \newcommand{\nrTimestepsDesc}{number of timesteps}
    # """

    # # Write the sample content to the input .tex file
    # with open(input_filename, "w") as infile:
    #     infile.write(sample_content)

    # # Generate the LaTeX table and write it to the output .tex file
    # latex_file_to_table_to_file(input_filename, output_filename)

    # output_filename

    #     def generate_parameter_tables(self):
    #         '''

    #         '''


# Create an instance of the Parameters class
scenario = Parameters()
scenario.generate_latex_parameters_file()
input_name = "latex_parameters_file.tex"
output_name = "latex_parameters_table.tex"
scenario.latex_file_to_table_to_file(output_name)