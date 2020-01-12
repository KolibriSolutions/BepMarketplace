#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
def quantize_number(x, prec=2, base=.05):
    """
    Quantize a number.
    This function sometimes gives rounding errors, because of imperfect float representation.
    This is not critical as people should enter grades already rounded to the correct decimals.
    And check the grade given afterwards.
    It might be fixable using the python decimal module, but is difficult.

    :param x: number
    :param prec: number of digits after dot
    :param base: quantization step
    :return:
    """
    return round(base * round(float(x) / base), prec)
