"""This module contains a monte carlo example that illustrates the advantages of the grmpy estima-
tion strategy. For this purpose data and the associated parameterization from Cainero 2011 are
used. Additionally the module creates two different figures for the reliability section of the
documentation.
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

from grmpy.estimate.estimate import fit
from grmpy.read.read import read
from grmpy.simulate.simulate_auxiliary import simulate_unobservables
from grmpy.test.random_init import print_dict


def create_data():
    """This function creates the a data set based on the results from Caineiro 2011."""
    # Read in initialization file and the data set
    init_dict = read("reliability.grmpy.yml")
    df = pd.read_pickle("aer-simulation-mock.pkl")

    # Distribute information
    indicator, dep = (
        init_dict["ESTIMATION"]["indicator"],
        init_dict["ESTIMATION"]["dependent"],
    )
    label_out = init_dict["TREATED"]["order"]
    label_choice = init_dict["CHOICE"]["order"]
    seed = init_dict["SIMULATION"]["seed"]

    # Set random seed to ensure recomputabiltiy
    np.random.seed(seed)

    # Simulate unobservables
    U = simulate_unobservables(init_dict)

    df["U1"], df["U0"], df["V"] = U["U1"], U["U0"], U["V"]
    # Simulate choice and output
    df[dep + "1"] = np.dot(df[label_out], init_dict["TREATED"]["params"]) + df["U1"]
    df[dep + "0"] = np.dot(df[label_out], init_dict["UNTREATED"]["params"]) + df["U0"]
    df[indicator] = np.array(
        np.dot(df[label_choice], init_dict["CHOICE"]["params"]) - df["V"] > 0
    ).astype(int)
    df[dep] = df[indicator] * df[dep + "1"] + (1 - df[indicator]) * df[dep + "0"]

    # Save the data
    df.to_pickle("aer-simulation-mock.pkl")

    return df


def update_correlation_structure(model_dict, rho):
    """This function takes a valid model specification and updates the correlation structure
    among the unobservables."""

    # We first extract the baseline information from the model dictionary.
    sd_v = model_dict["DIST"]["params"][-1]
    sd_u = model_dict["DIST"]["params"][0]

    # Now we construct the implied covariance, which is relevant for the initialization file.
    cov = rho * sd_v * sd_u
    model_dict["DIST"]["params"][2] = cov

    # We print out the specification to an initialization file with the name mc_init.grmpy.ini.
    print_dict(model_dict, "reliability")


def get_effect_grmpy(file):
    """This function simply returns the ATE of the data set."""
    dict_ = read("reliability.grmpy.yml")
    df = pd.read_pickle("aer-simulation-mock.pkl")
    beta_diff = dict_["TREATED"]["params"] - dict_["UNTREATED"]["params"]
    covars = dict_["TREATED"]["order"]
    ATE = np.dot(np.mean(df[covars]), beta_diff)

    return ATE


def monte_carlo(file, grid_points):
    """This function estimates the ATE for a sample with different correlation structures between U1
    and V. Two different strategies for (OLS,LATE) are implemented.
    """

    # Define a dictionary with a key for each estimation strategy
    effects = {}
    for key_ in ["grmpy", "ols", "true"]:
        effects[key_] = []

    # Loop over different correlations between V and U_1
    for rho in np.linspace(0.00, 0.99, grid_points):

        # Readjust the initialization file values to add correlation
        model_spec = read(file)
        sim_spec = read("reliability.grmpy.yml")
        X = sim_spec["TREATED"]["order"]
        update_correlation_structure(model_spec, rho)

        # Simulate a Data set and specify exogeneous and endogeneous variables
        df_mc = create_data()
        endog, exog, exog_ols = df_mc["wage"], df_mc[X], df_mc[["state"] + X]

        # Calculate true average treatment effect
        ATE = np.mean(df_mc["wage1"] - df_mc["wage0"])
        effects["true"] += [ATE]

        # Estimate  via grmpy
        rslt = fit("reliability.grmpy.yml")
        beta_diff = rslt["TREATED"]["params"] - rslt["UNTREATED"]["params"]
        stat = np.dot(np.mean(exog), beta_diff)

        effects["grmpy"] += [stat]

        # Estimate via OLS
        ols = sm.OLS(endog, exog_ols).fit()
        stat = ols.params[0]

        effects["ols"] += [stat]

    return effects


def create_plots(effects, true):
    """The function creates the figures that illustrates the behavior of each estimator of the ATE
    when the correlation structure changes from 0 to 1."""

    # Determine the title for each strategy plot
    for strategy in ["grmpy", "ols"]:
        if strategy == "ols":
            title = "Ordinary Least Squares"
        elif strategy == "grmpy":
            title = "grmpy"

        # Create a figure for each estimation strategy
        ax = plt.figure().add_subplot(111)

        grid = np.linspace(0.00, 0.99, len(effects[strategy]))

        ax.set_xlim(0, 1)
        ax.set_ylim(0.3, 0.55)
        ax.set_ylabel(r"Effect")
        ax.set_xlabel(r"$\rho_{U_1, V}$")
        true_ = np.tile(true, len(effects[strategy]))
        ax.plot(grid, effects[strategy], label="Estimate")

        ax.plot(grid, true_, label="True")

        ax.yaxis.get_major_ticks()[0].set_visible(False)
        plt.title(title)
        plt.legend()
        file_name = f"fig-{strategy}-average-effect-estimation.png"
        plt.savefig(file_name)


if __name__ == "__main__":

    ATE = get_effect_grmpy("reliability.grmpy.yml")

    x = monte_carlo("reliability.grmpy.yml", 10)

    create_plots(x, ATE)
