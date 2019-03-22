"""
Generate Test Data

Two main uses.
Producing the mock data...
    1. ...as a standalone SQL script (useful for interfacing with the DockerFile
    2. ...as data sent through mysql with the mysql-connector library
"""

import random
import sys
from datetime import datetime

from tso.util import persistence as persistence_util


def generate_mock_observation_values():
    values = []
    for x in range(0, 1000):
        # TODO: Update to include valid and meaningful values
        values.append({
            'id': x,
            'token': "Token_%s" % x,
            'observing_groups_id': 123,
            'observing_block_data': "-1",
            'candidate': -1,
            'sky_address': -1,
            'public': -1,
            'active_runid': x,
            'min_qrun_millis': -1,
            'max_qrun_millis': -1,
            'contiguous_exposure_time_millis': random.randint(100, 18000),
            'priority': random.randint(1, 100),
            'next_observable_at': -1,
            'unobservable_at': -1,
            'remaining_observing_chances': random.randint(1, 10),
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'dirty': -1,
            'version': -1,
            'label': x,
            'program_id': x
        })

    return values


observation_sql = "INSERT INTO observing_blocks " \
                  "( id, token, observing_groups_id, observing_block_data, candidate, sky_address, public, " \
                  "active_runid, min_qrun_millis, max_qrun_millis, contiguous_exposure_time_millis, priority, " \
                  "next_observable_at, unobservable_at, remaining_observing_chances, created_at, updated_at, " \
                  "dirty, version, label, program_id )" \
                  "VALUES (%(id)s, %(token)s, %(observing_groups_id)s, %(observing_block_data)s, " \
                  "%(candidate)s, %(sky_address)s, %(public)s, %(active_runid)s, " \
                  "%(min_qrun_millis)s, %(max_qrun_millis)s, %(contiguous_exposure_time_millis)s, %(priority)s, " \
                  "%(next_observable_at)s, %(unobservable_at)s, %(remaining_observing_chances)s, " \
                  "%(created_at)s, %(updated_at)s, %(dirty)s, %(version)s, %(label)s, %(program_id)s)"


mode = sys.argv[1]

if mode == 'file':
    statements = []

    statements.append("# ---------------- Observation Mock Data ----------------")
    for v in generate_mock_observation_values():
        statements.append(observation_sql % v)

    filename = "XXXX_Generated_TSO_Test_Data.sql"
    with open(filename, "w") as f:
        for s in statements:
            f.write(str(s) + "\n")

    print("Generate %s!" % filename)
elif mode == 'sql':
    my_db = persistence_util.get_mysql_connection()
    my_cursor = my_db.cursor()

    my_cursor.executemany(
        observation_sql,
        generate_mock_observation_values()
    )

    my_db.commit()
else:
    raise NotImplementedError("Unsupported Test Data Generation Mode")

