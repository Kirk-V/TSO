from astroplan import Constraint
import warnings
from astropy.time import Time
import numpy as np


class TsoOutageConstraint(Constraint):
    """
    Tso Outage Constraint

    This is a class representing a global constraint that will live if TSO users have configured any planned outages.
    This will be configured through a JSON config file and created through the constraint aggregator.
    """

    @staticmethod
    def default_outage_config():
        return {
        }

    def __init__(self, outage_config=None):
        self.outage_config = outage_config if outage_config is not None else TsoOutageConstraint.default_outage_config()

    def compute_constraint(self, times, observer, targets):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            min_time = Time("1950-01-01T00:00:00")
            max_time = Time("2120-01-01T00:00:00")

        mask = True
        for outage in self.outage_config.times:
            min_out_time = Time(outage.get("start")) if "start" not in outage else max_time
            max_out_time = Time(outage.get("end")) if "end" not in outage else min_time

            # if the time is OUTSIDE of the given range, it is valid
            mask = mask and np.logical_and(times < min_out_time, times > max_out_time)
        return mask
