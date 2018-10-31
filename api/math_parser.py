from typing import Tuple, List

import cexprtk


def step(x):
    """
    Heaviside step function
    step(x) = 0 if x < 0
            = 1 if x >= 0

    :param x:
    :return:
    """
    return int(x >= 0)


def parse_equation(equation_str: str, variable: str, var_range: Tuple[float, float], var_step: float) -> List[
    Tuple[float, float]]:
    """
    Transforms a continuous single variable equation string into a list of discrete values.
    For supported operations see: http://www.partow.net/programming/exprtk/index.html

    Also supports step(x) for Heaviside step function. (Useful if a piecewise function is needed)

    :param equation_str: String that contains variable and operators
    :param variable: String that represents the variable
    :param var_range: start <= variable < end
    :param var_step: Discretization increment for variable
    :returns: A list of tuples representing the (variable, equation_str(variable)) pairs within the range
    """

    start = var_range[0]
    end = var_range[1]

    st = cexprtk.Symbol_Table({variable: start})
    st.functions['step'] = step

    # Stores points (variable, f(variable))
    computed_values = []

    f = cexprtk.Expression(equation_str, st)

    x = start
    while x < end:
        computed_values.append((x, f()))
        x += var_step
        st.variables[variable] = x

    return computed_values
