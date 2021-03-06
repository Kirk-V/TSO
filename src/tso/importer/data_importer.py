"""
Data Importer

Allows importing TSO data from TSO persistence.
"""

from tso.observation.cfht_observation_block import CFHTObservationBlock
from tso.util import persistence as persistence_util
from sys import maxsize as MAX_SIZE
import json


def convert_to_cfht(
    values,
    max_program_priority=MAX_SIZE,
    exposure_count_data={}
):
    """Summary: Takes data from the observations Database and transforms 
    it to the current CFHT data model. This replicated the current CFHT process
    
    Args:
        values (rows of Observation data from database as alist): 
        max_program_priority (int, optional): the priority of the program 
        who generated the request. Defaults to lowes priority
        exposure_count_data (json, optional): Exposure information required to 
        calculate the number of exposures
    """
    observation_blocks = []
    for line_values in values:

        new_block = CFHTObservationBlock(**line_values)

        blob_data = json.loads(new_block.observing_block_data)
        # Filter only those blocks that comply with the program priority
        if int(blob_data["program_priority"]) <= int(max_program_priority):

            # For those blocks that are valid, set their exposure count
            new_block.exposure_count = exposure_count_data.get(new_block.observation_block_id)
            observation_blocks.append(
                new_block
            )

    return observation_blocks


def get_all_observations(db_config=None):

    """
    Summary "Retrieve all observation_blocks found in persistence.
    Potentially dangerous if a large amount of entries exist
    
    
    Args:
        db_config (Dict, optional): Database connection info
    
    Returns:
        CFHT_observation_block: all observations in TSO persistence
    
    Raises:
        RuntimeError: Data information does not exist
    """

    if db_config is None:
        raise RuntimeError("Error :: Cannot import without database configuration")

    my_db = persistence_util.get_mysql_connection(db_config)
    cursor = my_db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM observing_blocks;")

    return convert_to_cfht(
        cursor.fetchall(),
        MAX_SIZE,
        get_exposure_counts_per_observation_id(db_config)
    )


def get_observations_with_args(db_config=None, **kwargs):
    """Summary: imports data from database, restricting the data based on arguments
    passed.  
    
    Args:
        db_config (Dict, optional): Description
        **kwargs: variable number of constraints on database row retrieved
        This includes limiting data retrival based on max priorty, program priority, 
        remaining obseration chances, obseration duration min/max.
    Returns:
        TYPE: rows of observations that meet the criteria
    
    Raises:
        RuntimeError: No configuration file
    """
    if db_config is None:
        raise RuntimeError("Error :: Cannot import without database configuration")

    return get_observations(
        db_config=db_config,
        max_observation_priority=int(kwargs.get("max_observation_priority")),
        max_program_priority=int(kwargs.get("max_program_priority")),
        max_remaining_observing_chances=int(kwargs.get("max_remaining_observing_chances")),
        observation_duration_min=int(kwargs.get("observation_duration_min")),
        observation_duration_max=int(kwargs.get("observation_duration_max"))
    )


def get_observations(
    db_config=None,
    max_observation_priority=MAX_SIZE,
    max_program_priority=MAX_SIZE,
    max_remaining_observing_chances=-1,
    observation_duration_min=-1,
    observation_duration_max=MAX_SIZE
):
    """
    Summary:Get CFHT observation blocks with given constraints.
    The default values allow for the maximal amount of requests to be returned,
    or in other words, the default values provide the same functionality
    
    Args:
        db_config (Dict, optional): DAtabase configuration info
        max_observation_priority (Int, optional): priority of obserations
        max_program_priority (Int, optional): priority of program
        max_remaining_observing_chances (Int, optional): remaining observation
        opportunities
        observation_duration_min (int, optional): the lowest time required for 
        observation
        observation_duration_max (int, optional): the largest amount of time for
        observations
    """
    if db_config is None:
        raise RuntimeError("Error :: Cannot import without database configuration")

    sql = "SELECT * FROM observing_blocks WHERE priority <= %s;" % str(max_observation_priority)
    if max_remaining_observing_chances > 0:
        sql += " AND remaining_observing_chances < " + str(max_remaining_observing_chances)
    if observation_duration_min > 0:
        sql += " AND contiguous_exposure_time_millis >= " + str(observation_duration_min)
    if observation_duration_max > 0:
        sql += " AND contiguous_exposure_time_millis <= " + str(observation_duration_max)

    my_db = persistence_util.get_mysql_connection(db_config)
    cursor = my_db.cursor(dictionary=True)
    cursor.execute(sql)

    return convert_to_cfht(
        cursor.fetchall(),
        max_program_priority,
        get_exposure_counts_per_observation_id(db_config)
    )


def get_exposure_counts_per_observation_id(db_config=None):

    """
    Summary: Get Exposure Counts Per Observation Id
    
    
    Args:
        db_config (Dict, optional): Description of DB configuration
    
    Returns:
        dict: with schema -> { observationId: exposureCount }
    
    Raises:
        RuntimeError: No configuration provided
    """

    if db_config is None:
        raise RuntimeError("Error :: Cannot import without database configuration")

    my_db = persistence_util.get_mysql_connection(db_config)
    cursor = my_db.cursor(dictionary=True)
    cursor.execute("SELECT observing_block_id, count(*) AS exposure_count FROM exposures GROUP BY observing_block_id;")
    raw_dict = cursor.fetchall()

    final = {}
    for sub in raw_dict:
        final[sub['observing_block_id']] = sub['exposure_count']

    return final


