#!/usr/bin/env python3

# This file is a python script that describes the cpp test framework test configuration options.

class Method:
    def __init__(self, config):
        # Deal with duplicates: with complex configurations (like
        # WT_SESSION::create), it's simpler to deal with duplicates once than
        # manually as configurations are defined
        self.config = []
        lastname = None
        for c in sorted(config):
            if '.' in c.name:
                raise "Bad config key '%s'" % c.name
            if c.name == lastname:
                continue
            lastname = c.name
            self.config.append(c)

class Config:
    def __init__(self, name, default, desc, subconfig=None, **flags):
        self.name = name
        self.default = default
        self.desc = desc
        self.subconfig = subconfig
        self.flags = flags

    # Comparators for sorting.
    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return self.name != other.name

    def __lt__(self, other):
        return self.name < other.name

    def __le__(self, other):
        return self.name <= other.name

    def __gt__(self, other):
        return self.name > other.name

    def __ge__(self, other):
        return self.name >= other.name
#
# A generic configuration used by some components to define their tick rate.
#
throttle_config = [
    Config('op_rate', '1s', r'''
        The rate at which a given operation will happen. Can be either s, ms, or m, combined with an
        integer. E.g. 20ms means do this operation every 20ms.''')
]

#
# Record config specifies the size of the keys and values to be generated by default.
#
record_config = [
    Config('key_size', 5, r'''
        The size of the keys created''', min=1),
    Config('value_size', 5, r'''
        The size of the values created''', min=1),
]

#
# The populate config defines how large the initially loaded database will be.
#
populate_config = record_config + [
    Config('collection_count', 1, r'''
        The number of collections the workload generator operates over''', min=0, max=200000),
    Config('key_count_per_collection', 0, r'''
        The number of keys to be operated on per collection''', min=0, max=1000000),
    Config('thread_count', 1, r'''
        The number of worker threads to use while populating the database.''')
]

#
# A generic configuration used by various other configurations to define whether that component or
# similar is enabled or not.
#
enabled_config_true = [
    Config('enabled', 'true', r'''
        Whether or not this is relevant to the workload''',
        type='boolean'),
]

enabled_config_false = [
    Config('enabled', 'false', r'''
        Whether or not this is relevant to the workload''',
        type='boolean'),
]

range_config = [
    Config('min', 0, r'''
        Lower limit''', min=0),
    Config('max', 1, r'''
        Upper limit''')
]

stat_config = range_config + [
    Config('postrun', 'false', r'''
        Whether the stat needs to be checked post run.''', type='boolean'),
    Config('runtime', 'false', r'''
        Whether the stat needs to be checked at runtime.''', type='boolean'),
    Config('save', 'false', r'''
        Whether the stat needs to be saved in a JSON file post run.''', type='boolean'),
]

component_config = throttle_config

transaction_config = [
    Config('ops_per_transaction', '', r'''
        Defines how many operations a transaction can perform, the range is defined with a minimum
        and a maximum and a random number is chosen between the two using a linear distribution.''',
        type='category', subconfig=range_config),
]

thread_count = [
    Config('thread_count', 0, r'''
        Specifies the number of threads that will be used to perform a certain function.''', min=0)
]

checkpoint_operation_thread_config = [
    Config('thread_count', 1, r'''
        Specifies the number of threads that will be used to perform the checkpoint operation.''',
        min=0, max=1),
    Config('op_rate', '60s', r'''
        The rate at which checkpoint is executed.''')
]

background_compact_thread_config = throttle_config + [
    Config('thread_count', 0, r'''
        Specifies the number of threads that will be used to perform background compaction
           operation.''',
        min=0, max=1),
    Config('free_space_target_mb', '20', r'''
        Minimum amount of space in MB recoverable for compaction to proceed.''')
]
custom_operation_thread_config = thread_count + transaction_config + throttle_config + record_config
read_thread_config = thread_count + throttle_config + transaction_config + record_config
remove_thread_config = thread_count + transaction_config + throttle_config
update_insert_thread_config = thread_count + transaction_config + throttle_config + record_config

#
# Configuration that applies to the runtime monitor component, this should be a list of statistics
# that need to be checked by the component.
#
metrics_monitor = enabled_config_true + component_config + [
    Config('cache_hs_insert', '', r'''
        Number of history store table insert calls.''',
        type='category', subconfig=stat_config),
    Config('cc_pages_removed', '', r'''
        Number of pages removed.''',
        type='category', subconfig=stat_config),
    Config('stat_cache_size', '', r'''
        Cache size statistics.''',
        type='category', subconfig=stat_config),
    Config('stat_db_size', '', r'''
        Size of the database.''',
        type='category', subconfig=stat_config),
]

#
# Configuration that applies to the timestamp_manager component.
#
timestamp_manager = enabled_config_true + component_config +  [
    Config('oldest_lag', 1, r'''
        The duration between the stable and oldest timestamps''', min=0, max=1000000),
    Config('stable_lag', 1, r'''
        The duration between the latest and stable timestamps''', min=0, max=1000000),
]

tracking_config = [
    Config('tracking_key_format', 'QSQ', r'''
        Key format for the tracking table. By default, the collection id, key and timestamp are
        stored.'''),
    Config('tracking_value_format', 'iS', r'''
        Value format for the tracking table. By default, the operation type and value are
        stored.''')
]

#
# Configuration that applies to the operation tracker component.
#
operation_tracker = enabled_config_true + component_config + tracking_config

#
# Configuration that applies to the workload_manager component.
#
workload_manager = enabled_config_true + component_config + [
    Config('background_compact_config', '',r'''
        Config that specifies if background compaction is enabled and its behaviour.''',
        type='category', subconfig=background_compact_thread_config),
    Config('checkpoint_config', '',r'''
        Config that specifies if the checkpoint thread is enabled and its behaviour.''',
        type='category', subconfig=checkpoint_operation_thread_config),
    Config('custom_config', '',r'''
        Config that specifies the number of custom_operation threads and their behaviour.''',
        type='category', subconfig=custom_operation_thread_config),
    Config('insert_config', '', r'''
        Config that specifies the number of insert_operation threads and their behaviour.''',
        type='category', subconfig=update_insert_thread_config),
    Config('populate_config', '', r'''
        Config that specifies how the database will be populated initially.''',
        type='category', subconfig=populate_config),
    Config('remove_config', '',r'''
        Config that specifies the number of remove_operation threads and their behaviour.''',
        type='category', subconfig=remove_thread_config),
    Config('read_config', '', r'''
        Config that specifies the number of read_operation threads and their behaviour.''',
        type='category', subconfig=read_thread_config),
    Config('update_config', '',r'''
        Config that specifies the number of update_operation threads and their behaviour.''',
        type='category', subconfig=update_insert_thread_config),
]

test_config = [
# Component configurations.
    Config('metrics_monitor', '', r'''
        Configuration options for the metrics_monitor''',
        type='category', subconfig=metrics_monitor),
    Config('timestamp_manager', '', r'''
        Configuration options for the timestamp manager''',
        type='category', subconfig=timestamp_manager),
    Config('workload_manager','', r'''
        Configuration options for the workload manager''',
        type='category', subconfig=workload_manager),
    Config('operation_tracker','', r'''
        Configuration options for the workload tracker''',
        type='category', subconfig=operation_tracker),

# Non component top level configuration.
    Config('background_compact_debug_mode', 'false', r'''
        If true, background compact aggressively removes compact statistics for a file and decreases
        the max amount of time a file can be skipped for.''', type='boolean'),
    Config('cache_max_wait_ms', 0, r'''
        The strict equivalent of cache_max_wait_ms defined in wiredtiger.''', min=0),
    Config('cache_size_mb', 0, r'''
        The cache size that wiredtiger will be configured to run with''', min=0, max=100000000000),
    Config('compression_enabled', 'false', r'''
        Whether the database files will use snappy compression or not.''', type='boolean'),
    Config('duration_seconds', 0, r'''
        The duration that the test run will last''', min=0, max=1000000),
    Config('enable_logging', 'false', r'''
        Enables write ahead logs''', type='boolean'),
    Config('reverse_collator', 'false', r'''
        Configure the database files to use the reverse collator.''', type='boolean'),
    Config('statistics_config', '', r'''
        Statistic configuration that is passed into wiredtiger on open.''',
        type='category', subconfig=[
            Config('type', 'all', r'''
            The configuration that will get passed to wiredtiger to determine the style of
            statistics gathering'''),
            Config('enable_logging', 'true', r'''
            Configuration enabling or disabling statistics logging in the form of json logging.''',
            type='boolean')
        ]),
    Config('validate', 'true', r'''
        Enables the validation stage.''', type='boolean'),
]

#
# Test and their respective configuration sorted alphabetically.
#
methods = {
    'background_compact' : Method(test_config),
    'bounded_cursor_perf' : Method(test_config),
    'bounded_cursor_prefix_indices' : Method(test_config),
    'bounded_cursor_prefix_search_near' : Method(test_config),
    'bounded_cursor_prefix_stat' : Method(test_config + [
        Config("search_near_threads", 10, r'''
        Number of threads that execute search near calls.''')]),
    'bounded_cursor_stress' : Method(test_config),
    'burst_inserts' : Method(test_config + [
        Config("burst_duration", 90, r'''
        How long the insertions will occur for.''')]),
    'cache_resize' : Method(test_config),
    'hs_cleanup' : Method(test_config),
    'operations_test' : Method(test_config),
    'reverse_split' : Method(test_config),
    'search_near_01' : Method(test_config + [
        Config("search_near_threads", 10, r'''
        Number of threads that execute search near calls.''')]),
    'search_near_02' : Method(test_config),
    'search_near_03' : Method(test_config),
    'test_template' : Method(test_config),
}
