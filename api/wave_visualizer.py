from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np

from asteval import Interpreter, make_symbol_table


def step(x):
    return np.heaviside(x, 0)


syms = make_symbol_table(use_numpy=True, step=step)

aeval = Interpreter(syms)


_CONTINUOUS_STEPS = 1000

def visualize_wave(equation_str: str, variable: str, var_range: Tuple[float, float], discretization_step: float = None,
                   wave_title: str = None):
    """
    Displays a plot for visualizing a continuous function over a small period of time. Optionally can display
    discretization as an overlayed plot

    :param equation_str: String representing equation
    :param variable:  String representing single variable
    :param var_range:  Range of function to plot
    :param discretization_step: Optionally display discretization steps
    :param wave_title: Optionally change the title of the plot. Default is equation_str
    """

    if wave_title is None:
        wave_title = 'Visualization of %s' % equation_str

    # Continuous first
    aeval.symtable[variable] = np.arange(var_range[0], var_range[1], (var_range[1]-var_range[0])/_CONTINUOUS_STEPS)
    cont_var = aeval.symtable[variable]
    aeval('cont_func = %s' % equation_str)
    cont_func = aeval.symtable['cont_func']

    fig, ax = plt.subplots()
    ax.plot(cont_var, cont_func, label='Desired')
    ax.set(xlabel='Time (s)', ylabel='Current (A)', title=wave_title)
    ax.grid()

    if discretization_step is not None:
        # Discrete next
        aeval.symtable[variable] = np.arange(var_range[0], var_range[1], discretization_step)
        disc_var = aeval.symtable[variable]
        aeval('disc_func = %s' % equation_str)
        disc_func = aeval.symtable['disc_func']
        plt.step(disc_var, disc_func, where='post', label='Actual')
        plt.legend()

    plt.show()
