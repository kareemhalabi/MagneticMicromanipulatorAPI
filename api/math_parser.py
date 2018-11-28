from typing import Tuple, List

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

def parse_equation(equation_str: str, variable: str, var_range: Tuple[float, float], var_step: float) -> List[
    Tuple[float, float]]:
    """
    Transforms a continuous single variable equation string into a list of discrete values.
    For supported operations see http://newville.github.io/asteval/basics.html#built-in-functions

    Also supports step(x) for Heaviside step function. (Useful if a piecewise function is needed)

    :param equation_str: String that contains variable and operators
    :param variable: String that represents the variable
    :param var_range: start <= variable < end
    :param var_step: Discretization increment for variable
    :returns: A list of tuples representing the (variable, equation_str(variable)) pairs within the range
    """

    aeval.symtable['start'] = var_range[0]
    aeval.symtable['end'] = var_range[1]
    aeval.symtable['computed_values'] = []
    aeval.symtable['step'] = var_step
    aeval.symtable[variable] = aeval.symtable['start']


    aeval(
"""
while %(variable)s < end:
    computed_values.append((%(variable)s, %(expression)s))
    %(variable)s += step
"""
        % {'variable': variable, 'expression': equation_str}
    )


    return aeval.symtable['computed_values']