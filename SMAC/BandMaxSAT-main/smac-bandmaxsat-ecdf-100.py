
from genericpath import exists
import sys
from os import listdir,mkdir
from os.path import isfile, join
from ConfigSpace import ConfigurationSpace
from ConfigSpace import Integer,Float, Configuration
from contextlib import redirect_stdout
from smac import AlgorithmConfigurationFacade as ACFacade
from smac import Scenario
import random
from BandMaxSAT_ecdf import ecdf,set_cpu_time,set_target_folder

ins_path = '/the/path/of/maxsat/ins'
set_cpu_time(100)

seed = int(sys.argv[1])
files = [join(ins_path,f) for f in listdir(ins_path) if isfile(join(ins_path, f))]
random.seed(seed)
instances = random.sample(files,int(len(files) * 0.2))
tmp_d = random.randint(1,99999999)
set_target_folder('target-100-'+str(tmp_d))
if not exists('target-100-'+str(tmp_d)):
    mkdir('target-100-'+str(tmp_d))

class NuWLsfunction:
    @property
    def configspace(self) -> ConfigurationSpace:
        bms_num = Integer("bms_num",(5,25))
        lambda_ = Float("lambda_",(0.1,2))
        gamma = Float("gamma",(0.8,1.0))
        armnum = Integer("armnum",(10,30))
        backward_step = Integer("backward_step",(10,30))
        cs = ConfigurationSpace(seed=seed)
        cs.add_hyperparameters([bms_num, lambda_, gamma, armnum, backward_step])
        return cs

    def train(self, config: Configuration, instance: str, seed: int = 0) -> float:
        """Returns the y value of a quadratic function with a minimum we know to be at x=0."""
        y = ecdf(config, instance, seed)
        return y

# Scenario object specifying the optimization "environment"

model = NuWLsfunction()
scenario = Scenario(model.configspace, instances=instances, deterministic=True, cputime_limit=60000, n_workers=1,n_trials=1000,seed=seed)

# Now we use SMAC to find the best hyperparameters
smac = ACFacade(
    scenario,
    model.train,
    overwrite=True,  # Overrides any previous results that are found that are inconsistent with the meta-data
)

incumbent = smac.optimize()

# Let's calculate the cost of the incumbent
incumbent_cost = smac.validate(incumbent)


with open("smac_out.log","a") as f:
    with redirect_stdout(f):
        print(f"Incumbent result: {incumbent}\nIncumbent cost: {incumbent_cost}")
