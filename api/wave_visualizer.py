from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np

from asteval import Interpreter

aeval = Interpreter()

aeval("""
def step(x):
    \"\"\"
    Heaviside step function
    step(x) = 0 if x < 0
            = 1 if x >= 0

    :param x:
    :return:
    \"\"\"

    return int(x >= 0)
""")

def visualize_wave(equation_str: str, variable: str, var_range: Tuple[float, float], discretization_step: float = None):
    """
    Displays a plot for visualizing a continuous function over a small period of time. Optionally can display
    discretization as an overlayed plot

    :param equation_str: String representing equation
    :param variable:  String representing single variable
    :param var_range:  Range of function to plot
    :param discretization_step: Optionally display discretization steps
    """

    # Continuous first
    aeval.symtable[variable] = np.arange(var_range[0], var_range[1], 0.01)
    cont_var = aeval.symtable[variable]
    aeval('cont_func = %s' % equation_str)
    cont_func = aeval.symtable['cont_func']

    fig, ax = plt.subplots()
    ax.plot(cont_var, cont_func, label='Continuous')
    ax.set(xlabel='Time (s)', ylabel='Current (A)', title='Visualization of %s' % equation_str)
    ax.grid()

    if discretization_step is not None:
        # Discrete next
        aeval.symtable[variable] = np.arange(var_range[0], var_range[1], discretization_step)
        disc_var = aeval.symtable[variable]
        aeval('disc_func = %s' % equation_str)
        disc_func = aeval.symtable['disc_func']
        plt.step(disc_var, disc_func, where='post', label='Discrete')
        plt.legend()

    plt.show()
