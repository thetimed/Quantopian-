"""
This is a template algorithm on Quantopian for you to adapt and fill in.
"""

from quantopian.pipeline import Pipeline
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.filters import QTradableStocksUS
from quantopian.pipeline.factors import AverageDollarVolume, SimpleMovingAverage
from quantopian.pipeline.data import EquityPricing
from quantopian.pipeline.data import Fundamentals
import quantopian.optimize as opt
import quantopian.algorithm as algo



def initialize(context):
    """
    Called once at the start of the algorithm.
    """
    # Rebalance every day, 1 hour after market open.
    algo.schedule_function(
        rebalance,
        algo.date_rules.every_day(),
        algo.time_rules.market_open(hours=1),
    )

    # Record tracking variables at the end of each day.
    algo.schedule_function(
        record_vars,
        algo.date_rules.every_day(),
        algo.time_rules.market_close(),
    )

    # Create our dynamic stock selector.
    algo.attach_pipeline(pipeline(), 'pipeline')


def pipeline():
    Dollar_volume = AverageDollarVolume(window_length=28)
    Decent_dollar_volume = Dollar_volume.percentile_between(80, 100)
    total_operation_growth = Fundamentals.net_income_growth.latest

# Add the factor to the pipeline.
    pipe = Pipeline(columns={'income growth': total_operation_growth,
                            'longs' : total_operation_growth>0,
                            'shorts' : total_operation_growth<0},
    screen = (QTradableStocksUS() & Decent_dollar_volume))

    return pipe


def before_trading_start(context, data):
    """
    Called every day before market open.
    """
    context.output = algo.pipeline_output('pipeline')

    # These are the securities that we are interested in trading each day.
    context.security_list = context.output.index


def rebalance(context, data):
    """
    Execute orders according to our schedule_function() timing.
    """
    long_secs = context.output[context.output['longs']].index
    long_weight = 0.55/len(long_secs)

    short_secs = context.output[context.output['shorts']].index
    short_weight = -0.45/len(short_secs)

    for security in long_secs:
        if data.can_trade(security):
            order_target_percent(security, long_weight)

    for security in short_secs:
        if data.can_trade(security):
            order_target_percent(security, short_weight)

    for security in context.portfolio.positions:
        if data.can_trade(security) and security not in long_secs and security not in short_secs:
            order_target_percent(security,0)


def record_vars(context, data):
    long_count = 0
    short_count = 0
    for position in context.portfolio.positions.values():
        if position.amount > 0:
            long_count += 1
        if position.amount < 0:
            short_count += 1

    # Plot the counts
    record(num_long=long_count, num_short=short_count, leverage=context.account.leverage)


def handle_data(context, data):
    """
    Called every minute.
    """
    pass
