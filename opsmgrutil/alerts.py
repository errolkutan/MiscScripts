# TODO there is currently lots of unnecessary redundant code here. This is due to some
# lack of understanding on python inheritance, and the lack of enums in pre 3.4
# thereby forcing me to implement my own enums as static classes. Need to research
# and fix this for simplication

################################################################################
# Ops Manager UI Enums
#
# The following enums represent values the ops manager UI allows users to select
# during the alerts-creation process. There is a slight disconnect between the
# values the user selects during manual alert creation and those that are entered
# into the content body and submitted via the API, so these classes account for
# the disconnect and provide the mapping
################################################################################

################################################################################
# Ops Manager API Alert Enums
#
# The following enums represent values that the alerts creation ops manager API
# resource can takes
################################################################################

class EventTypeName():
    """
    EventTypeName class

    Effectively a static class used in lieu of an enum (only supported by python
     3.4+), representing possible event type on which alerts report
    """
    # Host alert event types
    HOST_DOWN = "HOST_DOWN"
    ADD_HOST_TO_REPLICA_SET_AUDIT = "ADD_HOST_TO_REPLICA_SET_AUDIT"             # NOT listed in API spec--possibly might not work
    ADD_HOST_AUDIT = "ADD_HOST_AUDIT"                                           # NOT listed in API spec--possibly might not work
    REMOVE_HOST_FROM_REPLICA_SET_AUDIT = "REMOVE_HOST_FROM_REPLICA_SET_AUDIT"   # NOT listed in API spec--possibly might not work
    HOST_RESTARTED = "HOST_RESTARTED"                                           # NOT listed in API spec--possibly might not work
    HOST_VERSION_BEHIND = "HOST_VERSION_BEHIND"                                 # NOT listed in API spec--possibly might not work
    HOST_SSL_CERTIFICATE_STALE = "HOST_SSL_CERTIFICATE_STALE"                   # NOT listed in API spec--possibly might not work
    HOST_RECOVERING = "HOST_RECOVERING"
    VERSION_BEHIND = "VERSION_BEHIND"
    HOST_EXPOSED = "HOST_EXPOSED"
    OUTSIDE_METRIC_THRESHOLD = "OUTSIDE_METRIC_THRESHOLD"

    # Agent alert event types
    MONITORING_AGENT_DOWN = "MONITORING_AGENT_DOWN"
    MONITORING_AGENT_VERSION_BEHIND = "MONITORING_AGENT_VERSION_BEHIND"
    BACKUP_AGENT_DOWN = "BACKUP_AGENT_DOWN"
    BACKUP_AGENT_VERSION_BEHIND = "BACKUP_AGENT_VERSION_BEHIND"
    BACKUP_AGENT_CONF_CALL_FAILURE = "BACKUP_AGENT_CONF_CALL_FAILURE"

    # Backup alert event types
    OPLOG_BEHIND = "OPLOG_BEHIND"
    CLUSTER_MONGOS_IS_MISSING = "CLUSTER_MONGOS_IS_MISSING"
    RESYNC_REQUIRED = "RESYNC_REQUIRED"
    BAD_CLUSTERSHOTS = "BAD_CLUSTERSHOTS"
    RS_BIND_ERROR = "RS_BIND_ERROR"
    BACKUP_TOO_MANY_RETRIES = "BACKUP_TOO_MANY_RETRIES"
    BACKUP_IN_UNEXPECTED_STATE = "BACKUP_IN_UNEXPECTED_STATE"
    LATE_SNAPSHOT = "LATE_SNAPSHOT"
    SYNC_SLICE_HAS_NOT_PROGRESSED = "SYNC_SLICE_HAS_NOT_PROGRESSED"
    BACKUP_JOB_TOO_BUSY = "BACKUP_JOB_TOO_BUSY"
    GROUP_TAGS_CHANGED = "GROUP_TAGS_CHANGED"

    # Project alert event types
    USERS_AWAITING_APPROVAL = "USERS_AWAITING_APPROVAL"
    USERS_WITHOUT_MULTI_FACTOR_AUTH = "USERS_WITHOUT_MULTI_FACTOR_AUTH"

    # Replica set alert event types
    CONFIGURATION_CHANGED = "CONFIGURATION_CHANGED"
    PRIMARY_ELECTED = "PRIMARY_ELECTED"
    TOO_FEW_HEALTHY_MEMBERS = "TOO_FEW_HEALTHY_MEMBERS"
    TOO_MANY_UNHEALTHY_MEMBERS = "TOO_MANY_UNHEALTHY_MEMBERS"
    NO_PRIMARY = "NO_PRIMARY"

    # Cluster alert event types
    CLUSTER_MONGOS_IS_MISSING = "CLUSTER_MONGOS_IS_MISSING"

    # User alert event types
    JOINED_GROUP = "JOINED_GROUP"
    REMOVED_FROM_GROUP = "REMOVED_FROM_GROUP"

    VALUES = [HOST_DOWN, HOST_RECOVERING, VERSION_BEHIND, HOST_EXPOSED, OUTSIDE_METRIC_THRESHOLD,
              MONITORING_AGENT_DOWN, MONITORING_AGENT_VERSION_BEHIND, BACKUP_AGENT_DOWN, BACKUP_AGENT_VERSION_BEHIND, BACKUP_AGENT_CONF_CALL_FAILURE,
              OPLOG_BEHIND, CLUSTER_MONGOS_IS_MISSING, RESYNC_REQUIRED, BAD_CLUSTERSHOTS, RS_BIND_ERROR, BACKUP_TOO_MANY_RETRIES, BACKUP_IN_UNEXPECTED_STATE,
              LATE_SNAPSHOT, SYNC_SLICE_HAS_NOT_PROGRESSED, BACKUP_JOB_TOO_BUSY, GROUP_TAGS_CHANGED,
              USERS_AWAITING_APPROVAL, USERS_WITHOUT_MULTI_FACTOR_AUTH, CONFIGURATION_CHANGED, PRIMARY_ELECTED, TOO_FEW_HEALTHY_MEMBERS, TOO_MANY_UNHEALTHY_MEMBERS,
              NO_PRIMARY, CLUSTER_MONGOS_IS_MISSING, JOINED_GROUP, REMOVED_FROM_GROUP]

    @staticmethod
    def isValid(eventTypeName):
        """
        isValid

        A static method that determines whether the specified string represents a
        valid event type for which ops manager can produce an alert
        """
        return (eventTypeName.upper() in EventTypeName.VALUES)

    @staticmethod
    def valuesToStr():
        """
        Values to String
        """
        str = "["
        for value in EventTypeName.VALUES:
            str += value + ","
        str += "]"
        return str

class MatchersOperators():
    """
    MatchersOperators class

    Effectively a static class used in lieu of an enum (only supported by python
     3.4+), representing possible operators that alerts use to compare thresholds
     to object values.
    """
    EQUALS = "EQUALS"
    NOT_EQUALS = "NOT_EQUALS"
    CONTAINS = "CONTAINS"
    NOT_CONTAINS = "NOT_CONTAINS"
    STARTS_WITH = "STARTS_WITH"
    ENDS_WITH = "ENDS_WITH"
    REGEX = "REGEX"

    VALUES = [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS, STARTS_WITH, ENDS_WITH, REGEX ]

    @staticmethod
    def isValid(matchersOperatorsStr):
        """
        isValid

        A static method that determines whether the specified string represents a
        valid event type for which ops manager can produce an alert
        """
        return (matchersOperatorsStr.upper() in MatchersOperators.VALUES)

    @staticmethod
    def valuesToStr():
        """
        Values to String
        """
        str = "["
        for value in MatchersOperators.VALUES:
            str += value + ","
        str += "]"
        return str

class MatchersValues():
    """
    MatchersValues class

    Effectively a static class used in lieu of an enum (only supported by python
     3.4+), representing possible values to test against specific matcher operators.
    """
    ANY = "ANY"             # Not technically supported via ops manager, but we will use this to indicate any host
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    STANDALONE = "STANDALONE"
    CONFIG = "CONFIG"
    MONGOS = "MONGOS"
    ARBITER = "ARBITER"

    VALUES = [ANY, PRIMARY, SECONDARY, STANDALONE, CONFIG, MONGOS, ARBITER]

    @staticmethod
    def isValid(matchersValuesStr):
        """
        isValid

        A static method that determines whether the specified string represents a
        valid event type for which ops manager can produce an alert
        """
        return (matchersValuesStr.upper() in MatchersValues.VALUES)

    @staticmethod
    def valuesToStr():
        """
        Values to String
        """
        str = "["
        for value in MatchersValues.VALUES:
            str += value + ","
        str += "]"
        return str

class AlertNotificationsTypeName():
    """
    Alert Notifications Type Name class

    Effectively a static class used in lieu of an enum (only supported by python
     3.4+), representing the possible delivery methods for alert notifications.
    """
    GROUP = "GROUP"
    USER = "USER"
    SNMP = "SNMP"
    EMAIL = "EMAIL"
    SMS = "SMS"
    HIPCHAT = "HIPCHAT"
    SLACK = "SLACK"
    FLOWDOCK = "FLOWDOCK"
    PAGER_DUTY = "PAGER_DUTY"
    WEBHOOK = "WEBHOOK"

    VALUES = [ GROUP, USER, SNMP, EMAIL, SMS, HIPCHAT, SLACK, FLOWDOCK, PAGER_DUTY, WEBHOOK]

    @staticmethod
    def isValid(alertNotificationsTypeStr):
        """
        isValid

        A static method that determines whether the specified string represents a
        valid event type for which ops manager can produce an alert
        """
        return (alertNotificationsTypeStr.upper() in AlertNotificationsTypeName.VALUES)

    @staticmethod
    def valuesToStr():
        """
        Values to String
        """
        str = "["
        for value in AlertNotificationsTypeName.VALUES:
            str += value + ","
        str += "]"
        return str

class MetricThresholdUnits():
    """
    Alert Threshold Value Units class

    Effectively a static class used in lieu of an enum (only supported by python
     3.4+), representing the possible units for various different alert types.
    """
    RAW = "RAW"
    BITS = "BITS"
    BYTES = "BYTES"
    KILOBITS = "KILOBITS"
    KILOBYTES = "KILOBYTES"
    MEGABITS = "MEGABITS"
    MEGABYTES = "MEGABYTES"
    GIGABITS = "GIGABITS"
    GIGABYTES = "GIGABYTES"
    TERABYTES = "TERABYTES"
    PETABYTES = "PETABYTES"
    MILLISECONDS = "MILLISECONDS"
    SECONDS = "SECONDS"
    MINUTES = "MINUTES"
    HOURS = "HOURS"
    DAYS = "DAYS"

    VALUES = [RAW, BITS, BYTES, KILOBITS, KILOBYTES, MEGABITS, MEGABYTES, GIGABITS, GIGABYTES,
              TERABYTES, PETABYTES, MILLISECONDS, SECONDS, MINUTES, HOURS, DAYS]

    @staticmethod
    def isValid(alertThresholdValueUnitsStr):
        """
        isValid

        A static method that determines whether the specified string represents a
        valid event type for which ops manager can produce an alert
        """
        return (alertThresholdValueUnitsStr.upper() in MetricThresholdUnits.VALUES)

    @staticmethod
    def valuesToStr():
        """
        Values to String
        """
        str = "["
        for value in MetricThresholdUnits.VALUES:
            str += value + ","
        str += "]"
        return str

class AlertThreshold():
    """
    Alert Threshold class

    Effectively a static class used in lieu of an enum (only supported by python
     3.4+), representing the possible thresholds for various different alert types.
    """
    TOO_FEW_HEALTHY_MEMBERS = "TOO_FEW_HEALTHY_MEMBERS"
    TOO_MANY_UNHEALTHY_MEMBERS = "TOO_MANY_UNHEALTHY_MEMBERS"

    VALUES = [TOO_FEW_HEALTHY_MEMBERS, TOO_MANY_UNHEALTHY_MEMBERS]

    @staticmethod
    def isValid(alertThresholdStr):
        """
        isValid

        A static method that determines whether the specified string represents a
        valid event type for which ops manager can produce an alert
        """
        return (alertThresholdStr.upper() in AlertThreshold.VALUES)

    @staticmethod
    def valuesToStr():
        """
        Values to String
        """
        str = "["
        for value in AlertThreshold.VALUES:
            str += value + ","
        str += "]"
        return str

class AlertThresholdOperator():
    """
    Alert Threshold Operator class

    Effectively a static class used in lieu of an enum (only supported by python
     3.4+), representing the operator to apply when checking the current metric
    value against the threshold value.
    """
    GREATER_THAN = "GREATER_THAN"
    LESS_THAN = "LESS_THAN"

    VALUES = [GREATER_THAN, LESS_THAN]

    @staticmethod
    def isValid(alertThresholdOperatorStr):
        """
        isValid

        A static method that determines whether the specified string represents a
        valid event type for which ops manager can produce an alert
        """
        return (alertThresholdOperatorStr.upper() in AlertThresholdOperator.VALUES)

    @staticmethod
    def valuesToStr():
        """
        Values to String
        """
        str = "["
        for value in AlertThresholdOperator.VALUES:
            str += value + ","
        str += "]"
        return str

class HostMetricName():
    """
    Host Metric Name

    Effectively a static class used in lieu of an enum (only supported by python
     3.4+), representing the metric name of a host object.
    """
    ASSERT_REGULAR = "ASSERT_REGULAR"
    ASSERT_WARNING = "ASSERT_WARNING"
    ASSERT_MSG = "ASSERT_MSG"
    ASSERT_USER = "ASSERT_USER"
    BACKGROUND_FLUSH_AVG = "BACKGROUND_FLUSH_AVG"
    CACHE_BYTES_READ_INTO = "CACHE_BYTES_READ_INTO"
    CACHE_BYTES_WRITTEN_FROM = "CACHE_BYTES_WRITTEN_FROM"
    CACHE_USAGE_DIRTY = "CACHE_USAGE_DIRTY"
    CACHE_USAGE_USED = "CACHE_USAGE_USED"
    TICKETS_AVAILABLE_READS = "TICKETS_AVAILABLE_READS"
    TICKETS_AVAILABLE_WRITES = "TICKETS_AVAILABLE_WRITES"
    CONNECTIONS = "CONNECTIONS"
    CURSORS_TOTAL_OPEN = "CURSORS_TOTAL_OPEN"
    CURSORS_TOTAL_TIMED_OUT = "CURSORS_TOTAL_TIMED_OUT"
    EXTRA_INFO_PAGE_FAULTS = "EXTRA_INFO_PAGE_FAULTS"
    GLOBAL_ACCESSES_NOT_IN_MEMORY = "GLOBAL_ACCESSES_NOT_IN_MEMORY"
    GLOBAL_PAGE_FAULT_EXCEPTIONS_THROWN = "GLOBAL_PAGE_FAULT_EXCEPTIONS_THROWN"
    GLOBAL_LOCK_CURRENT_QUEUE_TOTAL = "GLOBAL_LOCK_CURRENT_QUEUE_TOTAL"
    GLOBAL_LOCK_CURRENT_QUEUE_READERS = "GLOBAL_LOCK_CURRENT_QUEUE_READERS"
    GLOBAL_LOCK_CURRENT_QUEUE_WRITERS = "GLOBAL_LOCK_CURRENT_QUEUE_WRITERS"
    GLOBAL_LOCK_PERCENTAGE = "GLOBAL_LOCK_PERCENTAGE"
    INDEX_COUNTERS_BTREE_ACCESSES = "INDEX_COUNTERS_BTREE_ACCESSES"
    INDEX_COUNTERS_BTREE_HITS = "INDEX_COUNTERS_BTREE_HITS"
    INDEX_COUNTERS_BTREE_MISSES = "INDEX_COUNTERS_BTREE_MISSES"
    INDEX_COUNTERS_BTREE_MISS_RATIO = "INDEX_COUNTERS_BTREE_MISS_RATIO"
    JOURNALING_COMMITS_IN_WRITE_LOCK = "JOURNALING_COMMITS_IN_WRITE_LOCK"
    JOURNALING_MB = "JOURNALING_MB"
    JOURNALING_WRITE_DATA_FILES_MB = "JOURNALING_WRITE_DATA_FILES_MB"
    MEMORY_RESIDENT = "MEMORY_RESIDENT"
    MEMORY_VIRTUAL = "MEMORY_VIRTUAL"
    MEMORY_MAPPED = "MEMORY_MAPPED"
    COMPUTED_MEMORY = "COMPUTED_MEMORY"
    NETWORK_BYTES_IN = "NETWORK_BYTES_IN"
    NETWORK_BYTES_OUT = "NETWORK_BYTES_OUT"
    NETWORK_NUM_REQUESTS = "NETWORK_NUM_REQUESTS"
    OPLOG_SLAVE_LAG_MASTER_TIME = "OPLOG_SLAVE_LAG_MASTER_TIME"
    OPLOG_MASTER_TIME = "OPLOG_MASTER_TIME"
    OPLOG_MASTER_LAG_TIME_DIFF = "OPLOG_MASTER_LAG_TIME_DIFF"
    OPLOG_RATE_GB_PER_HOUR = "OPLOG_RATE_GB_PER_HOUR"
    DB_STORAGE_TOTAL = "DB_STORAGE_TOTAL"
    DB_DATA_SIZE_TOTAL = "DB_DATA_SIZE_TOTAL"
    OPCOUNTER_CMD = "OPCOUNTER_CMD"
    OPCOUNTER_QUERY = "OPCOUNTER_QUERY"
    OPCOUNTER_UPDATE = "OPCOUNTER_UPDATE"
    OPCOUNTER_REPL_DELETE = "OPCOUNTER_REPL_DELETE"
    OPCOUNTER_REPL_INSERT = "OPCOUNTER_REPL_INSERT"
    DOCUMENT_RETURNED = "DOCUMENT_RETURNED"
    DOCUMENT_INSERTED = "DOCUMENT_INSERTED"
    DOCUMENT_UPDATED = "DOCUMENT_UPDATED"
    DOCUMENT_DELETED = "DOCUMENT_DELETED"
    OPERATIONS_SCAN_AND_ORDER = "OPERATIONS_SCAN_AND_ORDER"
    AVG_READ_EXECUTION_TIME = "AVG_READ_EXECUTION_TIME"
    AVG_WRITE_EXECUTION_TIME = "AVG_WRITE_EXECUTION_TIME"
    AVG_COMMAND_EXECUTION_TIME = "AVG_COMMAND_EXECUTION_TIME"
    QUERY_EXECUTOR_SCANNED = "QUERY_EXECUTOR_SCANNED"
    QUERY_EXECUTOR_SCANNED_OBJECTS = "QUERY_EXECUTOR_SCANNED_OBJECTS"
    QUERY_TARGETING_SCANNED_PER_RETURNED = "QUERY_TARGETING_SCANNED_PER_RETURNED"
    QUERY_TARGETING_SCANNED_OBJECTS_PER_RETURNED ="QUERY_TARGETING_SCANNED_OBJECTS_PER_RETURNED"
    DISK_PARTITION_SPACE_USED_DATA="DISK_PARTITION_SPACE_USED_DATA"

    VALUES = [ASSERT_REGULAR, ASSERT_WARNING, ASSERT_MSG, ASSERT_USER,
                BACKGROUND_FLUSH_AVG,
                CACHE_BYTES_READ_INTO, CACHE_BYTES_WRITTEN_FROM, CACHE_USAGE_DIRTY, CACHE_USAGE_USED,
                TICKETS_AVAILABLE_READS, TICKETS_AVAILABLE_WRITES, CONNECTIONS,
                CURSORS_TOTAL_OPEN, CURSORS_TOTAL_TIMED_OUT,
                EXTRA_INFO_PAGE_FAULTS, GLOBAL_ACCESSES_NOT_IN_MEMORY, GLOBAL_PAGE_FAULT_EXCEPTIONS_THROWN,
                GLOBAL_LOCK_CURRENT_QUEUE_TOTAL, GLOBAL_LOCK_CURRENT_QUEUE_READERS,
                GLOBAL_LOCK_CURRENT_QUEUE_WRITERS, GLOBAL_LOCK_PERCENTAGE,
                INDEX_COUNTERS_BTREE_ACCESSES, INDEX_COUNTERS_BTREE_HITS,
                INDEX_COUNTERS_BTREE_MISSES, INDEX_COUNTERS_BTREE_MISS_RATIO,
                JOURNALING_COMMITS_IN_WRITE_LOCK, JOURNALING_MB, JOURNALING_WRITE_DATA_FILES_MB,
                MEMORY_RESIDENT, MEMORY_VIRTUAL, MEMORY_MAPPED, COMPUTED_MEMORY,
                NETWORK_BYTES_IN, NETWORK_BYTES_OUT, NETWORK_NUM_REQUESTS,
                OPLOG_SLAVE_LAG_MASTER_TIME, OPLOG_MASTER_TIME, OPLOG_MASTER_LAG_TIME_DIFF, OPLOG_RATE_GB_PER_HOUR,
                DB_STORAGE_TOTAL, DB_DATA_SIZE_TOTAL,
                OPCOUNTER_CMD, OPCOUNTER_QUERY, OPCOUNTER_UPDATE, OPCOUNTER_REPL_DELETE, OPCOUNTER_REPL_INSERT,
                DOCUMENT_RETURNED, DOCUMENT_INSERTED, DOCUMENT_UPDATED, DOCUMENT_DELETED,
                OPERATIONS_SCAN_AND_ORDER, AVG_READ_EXECUTION_TIME, AVG_WRITE_EXECUTION_TIME, AVG_COMMAND_EXECUTION_TIME,
                QUERY_EXECUTOR_SCANNED, QUERY_EXECUTOR_SCANNED_OBJECTS,
                QUERY_TARGETING_SCANNED_PER_RETURNED, QUERY_TARGETING_SCANNED_OBJECTS_PER_RETURNED,DISK_PARTITION_SPACE_USED_DATA ]

    @staticmethod
    def isValid(hostMetricNameStr):
        """
        isValid

        A static method that determines whether the specified string represents a
        valid event type for which ops manager can produce an alert
        """
        return (hostMetricNameStr.upper() in HostMetricName.VALUES)

    @staticmethod
    def valuesToStr():
        """
        Values to String
        """
        str = "["
        for value in HostMetricName.VALUES:
            str += value + ","
        str += "]"
        return str

class TargetName():
    """
    """
    HOST = "HOST"
    REPLICA_SET = "REPLICA_SET"
    SHARDED_CLUSTER = "SHARDED_CLUSTER"
    AGENT = "AGENT"
    BACKUP = "BACKUP"
    BI_CONNECTOR = "BI_CONNECTOR"
    USER = "USER"
    PROJECT = "PROJECT"

    VALUES = [HOST, REPLICA_SET, SHARDED_CLUSTER, AGENT, BI_CONNECTOR, USER, PROJECT]
    MAPPINGS = { HOST : [EventTypeName.HOST_DOWN, EventTypeName.ADD_HOST_TO_REPLICA_SET_AUDIT, EventTypeName.ADD_HOST_AUDIT,
                        EventTypeName.REMOVE_HOST_FROM_REPLICA_SET_AUDIT, EventTypeName.HOST_RESTARTED, EventTypeName.HOST_VERSION_BEHIND,
                        EventTypeName.HOST_SSL_CERTIFICATE_STALE, EventTypeName.HOST_RECOVERING, EventTypeName.VERSION_BEHIND,
                        EventTypeName.HOST_EXPOSED, HostMetricName.ASSERT_REGULAR, HostMetricName.ASSERT_WARNING, HostMetricName.ASSERT_MSG,
                        HostMetricName.ASSERT_USER, HostMetricName.BACKGROUND_FLUSH_AVG, HostMetricName.CACHE_BYTES_READ_INTO,
                        HostMetricName.CACHE_BYTES_WRITTEN_FROM, HostMetricName.CACHE_USAGE_DIRTY, HostMetricName.CACHE_USAGE_USED,
                        HostMetricName.TICKETS_AVAILABLE_READS, HostMetricName.TICKETS_AVAILABLE_WRITES, HostMetricName.CONNECTIONS,
                        HostMetricName.CURSORS_TOTAL_OPEN, HostMetricName.CURSORS_TOTAL_TIMED_OUT, HostMetricName.EXTRA_INFO_PAGE_FAULTS,
                        HostMetricName.GLOBAL_ACCESSES_NOT_IN_MEMORY, HostMetricName.GLOBAL_PAGE_FAULT_EXCEPTIONS_THROWN,
                        HostMetricName.GLOBAL_LOCK_CURRENT_QUEUE_TOTAL, HostMetricName.GLOBAL_LOCK_CURRENT_QUEUE_READERS,
                        HostMetricName.GLOBAL_LOCK_CURRENT_QUEUE_WRITERS, HostMetricName.GLOBAL_LOCK_PERCENTAGE, HostMetricName.INDEX_COUNTERS_BTREE_ACCESSES,
                        HostMetricName.INDEX_COUNTERS_BTREE_HITS, HostMetricName.INDEX_COUNTERS_BTREE_MISSES, HostMetricName.INDEX_COUNTERS_BTREE_MISS_RATIO,
                        HostMetricName.JOURNALING_COMMITS_IN_WRITE_LOCK, HostMetricName.JOURNALING_MB, HostMetricName.JOURNALING_WRITE_DATA_FILES_MB,
                        HostMetricName.MEMORY_RESIDENT, HostMetricName.MEMORY_VIRTUAL, HostMetricName.MEMORY_MAPPED, HostMetricName.COMPUTED_MEMORY,
                        HostMetricName.NETWORK_BYTES_IN, HostMetricName.NETWORK_BYTES_OUT, HostMetricName.NETWORK_NUM_REQUESTS,
                        HostMetricName.OPLOG_SLAVE_LAG_MASTER_TIME, HostMetricName.OPLOG_MASTER_TIME, HostMetricName.OPLOG_MASTER_LAG_TIME_DIFF,
                        HostMetricName.OPLOG_RATE_GB_PER_HOUR, HostMetricName.DB_STORAGE_TOTAL, HostMetricName.DB_DATA_SIZE_TOTAL, HostMetricName.OPCOUNTER_CMD,
                        HostMetricName.OPCOUNTER_QUERY, HostMetricName.OPCOUNTER_UPDATE, HostMetricName.OPCOUNTER_REPL_DELETE,
                        HostMetricName.OPCOUNTER_REPL_INSERT, HostMetricName.DOCUMENT_RETURNED, HostMetricName.DOCUMENT_INSERTED,
                        HostMetricName.DOCUMENT_UPDATED, HostMetricName.DOCUMENT_DELETED, HostMetricName.OPERATIONS_SCAN_AND_ORDER,
                        HostMetricName.AVG_READ_EXECUTION_TIME, HostMetricName.AVG_WRITE_EXECUTION_TIME, HostMetricName.AVG_COMMAND_EXECUTION_TIME,
                        HostMetricName.QUERY_EXECUTOR_SCANNED, HostMetricName.QUERY_EXECUTOR_SCANNED_OBJECTS, HostMetricName.QUERY_TARGETING_SCANNED_PER_RETURNED,
                        HostMetricName.QUERY_TARGETING_SCANNED_OBJECTS_PER_RETURNED, HostMetricName.DISK_PARTITION_SPACE_USED_DATA],
                REPLICA_SET : [EventTypeName.CONFIGURATION_CHANGED, EventTypeName.PRIMARY_ELECTED, EventTypeName.TOO_FEW_HEALTHY_MEMBERS, EventTypeName.TOO_MANY_UNHEALTHY_MEMBERS, EventTypeName.NO_PRIMARY],
                SHARDED_CLUSTER : [EventTypeName.CLUSTER_MONGOS_IS_MISSING],
                AGENT : [EventTypeName.MONITORING_AGENT_DOWN, EventTypeName.MONITORING_AGENT_VERSION_BEHIND, EventTypeName.BACKUP_AGENT_DOWN, EventTypeName.BACKUP_AGENT_VERSION_BEHIND, EventTypeName.BACKUP_AGENT_CONF_CALL_FAILURE],
                BACKUP : [EventTypeName.OPLOG_BEHIND, EventTypeName.CLUSTER_MONGOS_IS_MISSING, EventTypeName.RESYNC_REQUIRED, EventTypeName.BAD_CLUSTERSHOTS, EventTypeName.RS_BIND_ERROR, EventTypeName.BACKUP_TOO_MANY_RETRIES, EventTypeName.BACKUP_IN_UNEXPECTED_STATE, EventTypeName.LATE_SNAPSHOT, EventTypeName.SYNC_SLICE_HAS_NOT_PROGRESSED, EventTypeName.BACKUP_JOB_TOO_BUSY, EventTypeName.GROUP_TAGS_CHANGED],
                BI_CONNECTOR : [],
                USER : [EventTypeName.JOINED_GROUP, EventTypeName.REMOVED_FROM_GROUP],
                PROJECT : [EventTypeName.USERS_AWAITING_APPROVAL, EventTypeName.USERS_WITHOUT_MULTI_FACTOR_AUTH] }

    @staticmethod
    def isValid(targetNameStr):
        """
        isValid

        A static method that determines whether the specified string represents a
        valid event type for which ops manager can produce an alert
        """
        return (targetNameStr.upper() in TargetName.VALUES)

    @staticmethod
    def valuesToStr():
        """
        Values to String
        """
        str = "["
        for value in TargetName.VALUES:
            str += value + ","
        str += "]"
        return str

    @staticmethod
    def getMappingForType(targetNameStr):
        """
        """
        return TargetName.MAPPINGS[targetNameStr]

class MetricThresholdMode():
    """
    """
    AVERAGE = "AVERAGE"

    VALUES = [AVERAGE]

    @staticmethod
    def isValid(metricThresholdMode):
        """
        isValid

        A static method that determines whether the specified string represents a
        valid metric threshold mode for which ops manager can produce an alert
        """
        return (metricThresholdMode.upper() in MetricThresholdMode.VALUES)

    @staticmethod
    def valuesToStr():
        """
        Values to String
        """
        str = "["
        for value in MetricThresholdMode.VALUES:
            str += value + ","
        str += "]"
        return str

class MatchersFieldName():
    """
    MatchersFieldName class

    Effectively a static class used in lieu of an enum (only supported by python
     3.4+), representing possible field names within objects of concern that the
     alerts will measure against
    """
    # Host alert fields
    HOSTNAME = "HOSTNAME"
    PORT = "PORT"
    HOSTNAME_AND_PORT = "HOSTNAME_AND_PORT"
    REPLICA_SET_NAME = "REPLICA_SET_NAME"
    TYPE_NAME = "TYPE_NAME"

    # Replica set alert fields
    REPLICA_SET_NAME = "REPLICA_SET_NAME"
    SHARD_NAME = "SHARD_NAME"
    CLUSTER_NAME = "CLUSTER_NAME"

    VALUES = [ HOSTNAME, PORT, HOSTNAME_AND_PORT, REPLICA_SET_NAME, TYPE_NAME, REPLICA_SET_NAME,
                SHARD_NAME, CLUSTER_NAME ]
    MAPPINGS = { TargetName.HOST: [HOSTNAME, PORT, HOSTNAME_AND_PORT, REPLICA_SET_NAME, TYPE_NAME],
                 TargetName.REPLICA_SET : [REPLICA_SET_NAME, SHARD_NAME, CLUSTER_NAME],
                 TargetName.SHARDED_CLUSTER : [CLUSTER_NAME, SHARD_NAME]
                }

    @staticmethod
    def isValid(matchersFieldNameStr):
        """
        isValid

        A static method that determines whether the specified string represents a
        valid event type for which ops manager can produce an alert
        """
        return (matchersFieldNameStr.upper() in MatchersFieldName.VALUES)

    @staticmethod
    def valuesToStr():
        """
        Values to String
        """
        str = "["
        for value in MatchersFieldName.VALUES:
            str += value + ","
        str += "]"
        return str

    @staticmethod
    def getMappingForType(targetNameStr):
        """
        """
        return MatchersFieldName.MAPPINGS[targetNameStr]
