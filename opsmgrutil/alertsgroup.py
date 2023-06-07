from opsmgrutil import HostMetricName, AlertNotificationsTypeName, MetricThresholdUnits, AlertThresholdOperator, \
    TargetName, EventTypeName, MetricThresholdMode
import copy

class AlertNotification():
    """
    Alert Notification

    Represents a notification method for an alert
    """
    def __init__(self, typeName, intervalMin, delayMin):
        """

        :param typeName:
        :param intervalMin:
        :param delayMin:
        """
        # Required variables
        self.typeName       = typeName
        self.intervalMin    = intervalMin
        self.delayMin       = delayMin

        # User group notification variables
        self.emailEnabled   = None
        self.smsEnabled     = None
        self.username       = None

        # SNMP notification variables
        self.snmpAddress    = None

        # Email notification variables
        self.emailAddress   = None

        # Hipchat notification variables
        self.notificationToken  = None
        self.roomName           = None

        # Slack notification variables
        self.channelName    = None
        self.apiToken       = None

        # Flowdock notification variables
        self.orgName        = None
        self.flowName       = None
        self.flowdockApiToken = None

        # Pager duty notification variables
        self.serviceKey     = None

    def toDocument(self):
        """

        :return:
        """
        document = {}
        document["typeName"]    = self.typeName
        document["intervalMin"] = self.intervalMin
        document["delayMin"]    = self.delayMin

        if self.emailEnabled is not None:
            document["emailEnabled"] = self.emailEnabled
        if self.smsEnabled is not None:
            document["smsEnabled"] = self.smsEnabled
        if self.username is not None:
            document["username"] = self.username
        if self.snmpAddress is not None:
            document["snmpAddress"] = self.snmpAddress
        if self.emailAddress is not None:
            document["emailAddress"] = self.emailAddress
        if self.notificationToken is not None:
            document["notificationToken"] = self.notificationToken
        if self.roomName is not None:
            document["roomName"] = self.roomName
        if self.channelName is not None:
            document["channelName"] = self.channelName
        if self.apiToken is not None:
            document["apiToken"] = self.apiToken
        if self.orgName is not None:
            document["orgName"] = self.orgName
        if self.flowName is not None:
            document["flowName"] = self.flowName
        if self.flowdockApiToken is not None:
            document["flowdockApiToken"] = self.flowdockApiToken
        if self.serviceKey is not None:
            document["serviceKey"] = self.serviceKey
        return document

class AlertGroupsNames():
    """
    AlertGroupsNames

    Represents the names of possible different alert types
    """
    DEFAULT_ALERT_GROUP = "DEFAULT"
    PROD_ALERT_GROUP    = "PROD"
    NONPROD_ALERT_GROUP     = "NONPROD"
    PERF_ALERT_GROUP = "PERF"

    VALUES = [DEFAULT_ALERT_GROUP, PROD_ALERT_GROUP, NONPROD_ALERT_GROUP, PERF_ALERT_GROUP]

    @staticmethod
    def isValid(alertGroupNameStr):
        """
        isValid

        A static method that determines whether the specified string represents a
        valid alert group name
        """
        return (alertGroupNameStr.upper() in AlertGroupsNames.VALUES)

    @staticmethod
    def valuesToStr():
        """
        Values to String
        """
        str = "["
        ctr = 0
        for value in AlertGroupsNames.VALUES:
            ctr += 1
            if ctr != len(AlertGroupsNames.VALUES):
                str += value + ","
        str += "]"
        return str



class AlertsGroup():
    """
    AlertsGroup

    Represents a group of different alerts
    """
    def __init__(self):
        """
        Alerts Groups Default Constructor
        :return:
        """
        self.alertConfigs = []

    def __init__(self, alertConfigsArr):
        """
        Alerts Groups Constructor 2
        :return:
        """
        self.alertConfigs = alertConfigsArr

    def addAlert(self, alertArgs):
        """
        Add Alert
        :param alertArgs:       An args object representing command line arguments to specify an alert
        :return:
        """
        self.alertConfigs.append(alertArgs)

class AlertConfig():
    """
    Alert Config

    An empty object representing alert configurations
    """
    def AlertConfig(self):
        """

        :return:
        """

# Specify all the existing alert groups and what alerts they contain
class AlertGroups():
    """
    Alert Groups

    A registry of all the possible alert groups and which alerts they contain
    """

    alertConfigs = []

    # Set createalertforgroup arguments not present here to None
    args = AlertConfig()
    args.target = None
    args.targetConditionMetric = None
    args.hostType = None
    args.metricThresholdOperator = None
    args.metricThresholdValue = None
    args.metricThresholdUnits = None
    args.metricThresholdMode = None
    args.matcherType = None
    args.matcherOperator = None
    args.matcherValue = None

    args.notifications = None

    args.notificationType = None
    args.notificationIntervalMin = None
    args.notificationDelayMin = None
    args.notificationEmailEnabled = None
    args.notificationSmsEnabled = None
    args.notificationUsername = None
    args.notificationSnmpAddr = None
    args.notificationEmailAddr = None
    args.notificationNotificationToken = None
    args.notificationRoomName = None
    args.notificationChannelName = None
    args.notificationApiToken = None
    args.notificationOrgName = None
    args.notificationFlowName = None
    args.notificationFlowDockApiToken = None
    args.notificationServiceKey = None
    args.thresholdOperator = None
    args.thresholdValue = None

    ####################################################################################################################
    # CREATE DEFAULT ALERTS
    ####################################################################################################################

    alertConfigs = []

    # --------- Alert 1
    # Host is down
    # It is worth noting that this alert is not real-time, meaning there is typically
    # a delay involved (up to 15-20 minutes in the worst case) in detecting the condition.
    # If real-time notifications are desired, we recommend complementing OpsManager
    # with an appropriate hardware monitoring system
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.HOST
    newArgs.hostType = "ANY"
    newArgs.targetConditionMetric = EventTypeName.HOST_DOWN

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # --------- Alert 2
    # Host is recovering
    # The Recovering state can be a transient state, or an indicator that the node
    # is out of sync . To differentiate between the two, we recommend to set an alert
    # if the 2 condition lasts for at least 30 minutes
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.HOST
    newArgs.hostType = "ANY"
    newArgs.targetConditionMetric = EventTypeName.HOST_RECOVERING

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 30)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # --------- Alert 3
    # Montioring Agent Down
    #
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.AGENT
    newArgs.targetConditionMetric = EventTypeName.MONITORING_AGENT_DOWN

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # --------- Alert 4
    # Backup Agent Down
    #
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.AGENT
    newArgs.targetConditionMetric = EventTypeName.BACKUP_AGENT_DOWN

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # --------- Alert 5
    # Backup Resync Required
    #
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.BACKUP
    newArgs.targetConditionMetric = EventTypeName.RESYNC_REQUIRED

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)


    # --------- Alert 6
    # DISK SPACE % USED ON PARTITION
    #  Need to code this Alert but not Found in automation
    # DISK Alert
    #
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.HOST
    newArgs.hostType = "ANY"

    newArgs.targetConditionMetric = HostMetricName.DISK_PARTITION_SPACE_USED_DATA
    newArgs.metricThresholdOperator = AlertThresholdOperator.GREATER_THAN
    newArgs.metricThresholdValue = 75
    newArgs.metricThresholdUnits = MetricThresholdUnits.RAW

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []

    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"
    alertNotifications.append(emailNotification)

    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    DEFAULT_ALERT_GROUP = AlertsGroup(alertConfigs)


    ####################################################################################################################
    # CREATE NONPROD ALERTS
    ####################################################################################################################
    alertConfigs = []

    # --------- Alert 1
    # Host is down
    # It is worth noting that this alert is not real-time, meaning there is typically
    # a delay involved (up to 15-20 minutes in the worst case) in detecting the condition.
    # If real-time notifications are desired, we recommend complementing OpsManager
    # with an appropriate hardware monitoring system
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.HOST
    newArgs.hostType = "ANY"
    newArgs.targetConditionMetric = EventTypeName.HOST_DOWN

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # --------- Alert 2
    # Host is recovering
    # The Recovering state can be a transient state, or an indicator that the node
    # is out of sync . To differentiate between the two, we recommend to set an alert
    # if the 2 condition lasts for at least 30 minutes
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.HOST
    newArgs.hostType = "ANY"
    newArgs.targetConditionMetric = EventTypeName.HOST_RECOVERING

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 30)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # --------- Alert 3
    # Montioring Agent Down
    #
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.AGENT
    newArgs.targetConditionMetric = EventTypeName.MONITORING_AGENT_DOWN

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # --------- Alert 4
    # Backup Agent Down
    #
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.AGENT
    newArgs.targetConditionMetric = EventTypeName.BACKUP_AGENT_DOWN

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)


    # --------- Alert 5
    # Backup Resync Required
    #
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.BACKUP
    newArgs.targetConditionMetric = EventTypeName.RESYNC_REQUIRED

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)


    # --------- Alert 6
    # DISK SPACE % USED ON PARTITION
    #  Need to code this Alert but not Found in automation
    # DISK Alert
    #
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.HOST
    newArgs.hostType = "ANY"

    newArgs.targetConditionMetric = HostMetricName.DISK_PARTITION_SPACE_USED_DATA
    newArgs.metricThresholdOperator = AlertThresholdOperator.GREATER_THAN
    newArgs.metricThresholdValue = 75
    newArgs.metricThresholdUnits = MetricThresholdUnits.RAW

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []

    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"
    alertNotifications.append(emailNotification)


    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)


    NONPROD_ALERT_GROUP = AlertsGroup(alertConfigs)


    ####################################################################################################################
    # CREATE PERF ALERTS
    ####################################################################################################################
    # Query Targeting: Scanned/Returned
    # This helps catch improper index usage.  It refers to the ratio between the
    # number of index items scanned and the number of documents returned by queries.
    # If this value is 1.0, then your query scanned exactly as many index items as
    # documents it returned; it is an efficient query
    alertConfigs = []

    #Put aboce code here as per requirment in future if needed
    # ------------alert 1
    # Queues
    # Continuous spikes of queues might mean that your system is overloaded. I
    # suggest to set an alert to 100-500 if the condition lasts for more than 5 minutes
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.HOST
    newArgs.targetConditionMetric = HostMetricName.GLOBAL_LOCK_CURRENT_QUEUE_READERS
    newArgs.hostType = "ANY"
    newArgs.metricThresholdOperator = AlertThresholdOperator.GREATER_THAN
    newArgs.metricThresholdValue = 100
    newArgs.metricThresholdUnits = MetricThresholdUnits.RAW

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # -----alert 2
    newArgs = copy.deepcopy(newArgs)
    newArgs.targetConditionMetric = HostMetricName.GLOBAL_LOCK_CURRENT_QUEUE_WRITERS
    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object
    alertConfigs.append(newArgs)

    # --Alert 3
    # Page Faults
    # For the WiredTiger storage engine, page faults mean that the cache was swapped
    # out by the OS. It might indicate a memory leak or an OS misconfiguration. We recommend
    # to set this alert to a small non-zero value.
    # TODO need to double check this
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.HOST
    newArgs.targetConditionMetric = HostMetricName.EXTRA_INFO_PAGE_FAULTS
    newArgs.hostType = "ANY"
    newArgs.metricThresholdOperator = AlertThresholdOperator.GREATER_THAN
    newArgs.metricThresholdValue = 10
    newArgs.metricThresholdMode = MetricThresholdMode.AVERAGE
    newArgs.metricThresholdUnits = MetricThresholdUnits.RAW

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # ----- Alert 4
    # Replication Lag
    # It is recommended to set an alert to 5-10 seconds (or whatever is more appropriate
    # for your application needs) if the condition lasts for more than 5 minutes. The
    # latter is meant to prevent false-positives due to network delays and fluctuations
    # related to the sampling algorithm.
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.HOST
    newArgs.targetConditionMetric = HostMetricName.OPLOG_MASTER_LAG_TIME_DIFF
    newArgs.hostType = "ANY"
    newArgs.metricThresholdOperator = AlertThresholdOperator.GREATER_THAN
    newArgs.metricThresholdValue = 240
    newArgs.metricThresholdUnits = MetricThresholdUnits.SECONDS

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # Alert 5
    # Replication headroom
    # This is the difference between the primary's oplog window and a secondary's
    # replication lag. It represents the "safety margin" for that secondary, that
    # is to say how long it can drop off replication without having to restart an
    # initial sync. If the replication headroom drops to zero, the secondary will
    # enter "RECOVERING" state and stop replicating. Set an alert for this value
    # dropping lower than 48 hours, a normal maintenance window duration, time
    # needed to resync a replica set member - whichever is larger
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.HOST
    newArgs.targetConditionMetric = HostMetricName.OPLOG_SLAVE_LAG_MASTER_TIME
    newArgs.hostType = "ANY"
    newArgs.metricThresholdOperator = AlertThresholdOperator.LESS_THAN
    newArgs.metricThresholdValue = 24
    newArgs.metricThresholdUnits = MetricThresholdUnits.HOURS

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # --------alert 6
    # Oplog Window
    # We recommend to set an alert for this value dropping lower than 48 hours,
    # normal maintenance window duration, time needed to resync a replica set member
    # - whichever is larger. Insufficiently small replication oplog window may
    # result in replica set members going out of sync.
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.HOST
    newArgs.targetConditionMetric = HostMetricName.OPLOG_MASTER_TIME
    newArgs.hostType = "ANY"
    newArgs.metricThresholdOperator = AlertThresholdOperator.LESS_THAN
    newArgs.metricThresholdValue = 24
    newArgs.metricThresholdUnits = MetricThresholdUnits.HOURS

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # --------- Alert 7
    # Tickets available
    # This value controls how many active connections can access the WiredTiger
    # storage engine at the same time. It is recommended to set an alert for this
    # value when it approaches 0 (e.g. 10).
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.HOST
    newArgs.targetConditionMetric = HostMetricName.TICKETS_AVAILABLE_READS
    newArgs.hostType = "ANY"
    newArgs.metricThresholdOperator = AlertThresholdOperator.LESS_THAN
    newArgs.metricThresholdValue = 10
    newArgs.metricThresholdUnits = MetricThresholdUnits.RAW

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object
    alertConfigs.append(newArgs)

    # --------- Alert 8
    newArgs = copy.deepcopy(newArgs)
    newArgs.targetConditionMetric = HostMetricName.TICKETS_AVAILABLE_WRITES
    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object
    alertConfigs.append(newArgs)

    # --------- Alert 9
    # Bytes read into cache
    # Abnormally high number of bytes read into cache might indicate that the working
    # set is bigger than the cache. As there might be other causes for a high number
    # of bytes read into cache, e.g. initial cache population, it might not be practical
    # to set up an alert, but instead check this graph periodically as part of the maintenance
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.HOST
    newArgs.targetConditionMetric = HostMetricName.CACHE_BYTES_READ_INTO
    newArgs.hostType = "ANY"
    newArgs.metricThresholdOperator = AlertThresholdOperator.GREATER_THAN
    newArgs.metricThresholdValue = 2
    newArgs.metricThresholdUnits = MetricThresholdUnits.GIGABYTES

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # --------- Alert 10
    # Replica Set Elections
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.REPLICA_SET
    newArgs.targetConditionMetric = EventTypeName.PRIMARY_ELECTED

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 0)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # --------- Alert 11
    # Number of healthy members
    # In replica sets with more than 3 voting members, it may be useful to add an
    # alert when nearing a loss of majority, so that Ops teams can take preventive
    # actions to restore health to the replica set
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.REPLICA_SET
    newArgs.targetConditionMetric = EventTypeName.TOO_FEW_HEALTHY_MEMBERS
    newArgs.thresholdOperator = AlertThresholdOperator.LESS_THAN
    newArgs.thresholdValue = 2
    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # --------- Alert 12
    newArgs = copy.deepcopy(newArgs)
    newArgs.targetConditionMetric = EventTypeName.TOO_MANY_UNHEALTHY_MEMBERS
    newArgs.thresholdOperator = AlertThresholdOperator.GREATER_THAN
    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object
    alertConfigs.append(newArgs)

    # --------- Alert 13
    # Replica set has no primary
    # This alert triggers when all surviving members of the replica set are in "secondary"
    # state. It is recommended to set this alert if the condition lasts for more
    # than 1 minute, as this can happen transiently when performing administrative
    # operations involving a rolling restart or when a primary fails.
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.REPLICA_SET
    newArgs.targetConditionMetric = EventTypeName.NO_PRIMARY
    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 0)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object
    alertConfigs.append(newArgs)

    # --------- Alert 14
    # Host is recovering
    # The Recovering state can be a transient state, or an indicator that the node
    # is out of sync . To differentiate between the two, we recommend to set an alert
    # if the 2 condition lasts for at least 30 minutes
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.HOST
    newArgs.hostType = "ANY"
    newArgs.targetConditionMetric = EventTypeName.HOST_RECOVERING

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 30)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # --------- Alert 15
    # Host is down
    # It is worth noting that this alert is not real-time, meaning there is typically
    # a delay involved (up to 15-20 minutes in the worst case) in detecting the condition.
    # If real-time notifications are desired, we recommend complementing OpsManager
    # with an appropriate hardware monitoring system
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.HOST
    newArgs.hostType = "ANY"
    newArgs.targetConditionMetric = EventTypeName.HOST_DOWN

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 0)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # --------- Alert 16
    # Query Targeting: Scanned/Returned
    # This helps catch improper index usage.  It refers to the ratio between the
    # number of index items scanned and the number of documents returned by queries.
    # If this value is 1.0, then your query scanned exactly as many index items as
    # documents it returned; it is an efficient query
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.HOST
    newArgs.targetConditionMetric = HostMetricName.QUERY_TARGETING_SCANNED_PER_RETURNED
    newArgs.metricThresholdOperator = AlertThresholdOperator.GREATER_THAN
    newArgs.hostType = "ANY"
    newArgs.metricThresholdValue = 5
    newArgs.metricThresholdUnits = MetricThresholdUnits.RAW

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # --------- Alert 17
    newArgs = copy.deepcopy(newArgs)
    newArgs.targetConditionMetric = HostMetricName.QUERY_TARGETING_SCANNED_PER_RETURNED
    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object
    alertConfigs.append(newArgs)

    # --------- Alert 18
    # Montioring Agent Down
    #
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.AGENT
    newArgs.targetConditionMetric = EventTypeName.MONITORING_AGENT_DOWN

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # --------- Alert 19
    # Backup Resync Required
    #
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.BACKUP
    newArgs.targetConditionMetric = EventTypeName.RESYNC_REQUIRED

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)


    # --------- Alert 20
    # Backup Agent Down
    #
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.AGENT
    newArgs.targetConditionMetric = EventTypeName.BACKUP_AGENT_DOWN

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)


    # --------- Alert 21
    # Backup OPLOG BEHIND
    #
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.BACKUP
    newArgs.targetConditionMetric = EventTypeName.OPLOG_BEHIND

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # --------- Alert 22
    # Connections > 1000
    #
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.HOST
    newArgs.targetConditionMetric = HostMetricName.CONNECTIONS
    newArgs.metricThresholdOperator = AlertThresholdOperator.GREATER_THAN
    newArgs.hostType = "ANY"
    newArgs.metricThresholdValue = 1000
    newArgs.metricThresholdUnits = MetricThresholdUnits.RAW

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []

    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 0)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"
    alertNotifications.append(emailNotification)

    snmpNotification = AlertNotification(AlertNotificationsTypeName.SNMP, 60, 5)
    snmpNotification.snmpAddress = "va10tuvtos001.wellpoint.com,va10puvtos001.wellpoint.com,va10puvtos002.wellpoint.com:162"
    alertNotifications.append(snmpNotification)

    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # --------- Alert 23
    # DISK SPACE % USED ON PARTITION
    #  Need to code this Alert but not Found in automation
    # DISK Alert
    #
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.HOST
    newArgs.hostType = "ANY"

    newArgs.targetConditionMetric = HostMetricName.DISK_PARTITION_SPACE_USED_DATA
    newArgs.metricThresholdOperator = AlertThresholdOperator.GREATER_THAN
    newArgs.metricThresholdValue = 75
    newArgs.metricThresholdUnits = MetricThresholdUnits.RAW

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []

    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"
    alertNotifications.append(emailNotification)

    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    PERF_ALERT_GROUP = AlertsGroup(alertConfigs)
    VALUES = [DEFAULT_ALERT_GROUP, PERF_ALERT_GROUP]

####################################################################################################################
    # CREATE PROD ALERTS
    ####################################################################################################################
    alertConfigs = []

    #--------------alert 1
    # Queues
    # Continuous spikes of queues might mean that your system is overloaded. I
    # suggest to set an alert to 100-500 if the condition lasts for more than 5 minutes
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.HOST
    newArgs.targetConditionMetric = HostMetricName.GLOBAL_LOCK_CURRENT_QUEUE_READERS
    newArgs.hostType = "ANY"
    newArgs.metricThresholdOperator = AlertThresholdOperator.GREATER_THAN
    newArgs.metricThresholdValue = 100
    newArgs.metricThresholdUnits = MetricThresholdUnits.RAW
    # ---------------------------------------------------------------------------
    # TODO copy this to every alert where email and SNMP is required
    #---------------------------------------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"
    alertNotifications.append(emailNotification)

    newArgs.notifications = alertNotifications
    #-------------------end of logic to create notification object

    alertConfigs.append(newArgs)

    # -----alert 2
    newArgs = copy.deepcopy(newArgs)
    newArgs.targetConditionMetric = HostMetricName.GLOBAL_LOCK_CURRENT_QUEUE_WRITERS
    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object
    alertConfigs.append(newArgs)

    # --Alert 3
    # Page Faults
    # For the WiredTiger storage engine, page faults mean that the cache was swapped
    # out by the OS. It might indicate a memory leak or an OS misconfiguration. We recommend
    # to set this alert to a small non-zero value.
    # TODO need to double check this
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.HOST
    newArgs.targetConditionMetric = HostMetricName.EXTRA_INFO_PAGE_FAULTS
    newArgs.hostType = "ANY"
    newArgs.metricThresholdOperator = AlertThresholdOperator.GREATER_THAN
    newArgs.metricThresholdValue = 10
    newArgs.metricThresholdMode = MetricThresholdMode.AVERAGE
    newArgs.metricThresholdUnits = MetricThresholdUnits.RAW

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 1)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # ----- Alert 4
    # Replication Lag
    # It is recommended to set an alert to 5-10 seconds (or whatever is more appropriate
    # for your application needs) if the condition lasts for more than 5 minutes. The
    # latter is meant to prevent false-positives due to network delays and fluctuations
    # related to the sampling algorithm.
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.HOST
    newArgs.targetConditionMetric = HostMetricName.OPLOG_MASTER_LAG_TIME_DIFF
    newArgs.hostType = "ANY"
    newArgs.metricThresholdOperator = AlertThresholdOperator.GREATER_THAN
    newArgs.metricThresholdValue = 240
    newArgs.metricThresholdUnits = MetricThresholdUnits.SECONDS

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []

    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"
    alertNotifications.append(emailNotification)


    snmpNotification = AlertNotification(AlertNotificationsTypeName.SNMP, 60, 5)
    snmpNotification.snmpAddress = "va10tuvtos001.wellpoint.com,va10puvtos001.wellpoint.com,va10puvtos002.wellpoint.com:162"
    alertNotifications.append(snmpNotification)

    newArgs.notifications = alertNotifications

    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # Alert 5
    # Replication headroom
    # This is the difference between the primary's oplog window and a secondary's
    # replication lag. It represents the "safety margin" for that secondary, that
    # is to say how long it can drop off replication without having to restart an
    # initial sync. If the replication headroom drops to zero, the secondary will
    # enter "RECOVERING" state and stop replicating. Set an alert for this value
    # dropping lower than 48 hours, a normal maintenance window duration, time
    # needed to resync a replica set member - whichever is larger
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.HOST
    newArgs.targetConditionMetric = HostMetricName.OPLOG_SLAVE_LAG_MASTER_TIME
    newArgs.hostType = "ANY"
    newArgs.metricThresholdOperator = AlertThresholdOperator.LESS_THAN
    newArgs.metricThresholdValue = 24
    newArgs.metricThresholdUnits = MetricThresholdUnits.HOURS

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []

    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"
    alertNotifications.append(emailNotification)


    snmpNotification = AlertNotification(AlertNotificationsTypeName.SNMP, 60, 5)
    snmpNotification.snmpAddress = "va10tuvtos001.wellpoint.com,va10puvtos001.wellpoint.com,va10puvtos002.wellpoint.com:162"
    alertNotifications.append(snmpNotification)


    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # --------alert 6
    # Oplog Window
    # We recommend to set an alert for this value dropping lower than 48 hours,
    # normal maintenance window duration, time needed to resync a replica set member
    # - whichever is larger. Insufficiently small replication oplog window may
    # result in replica set members going out of sync.
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.HOST
    newArgs.targetConditionMetric = HostMetricName.OPLOG_MASTER_TIME
    newArgs.hostType = "ANY"
    newArgs.metricThresholdOperator = AlertThresholdOperator.LESS_THAN
    newArgs.metricThresholdValue = 24
    newArgs.metricThresholdUnits = MetricThresholdUnits.HOURS

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []

    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"
    alertNotifications.append(emailNotification)


    snmpNotification = AlertNotification(AlertNotificationsTypeName.SNMP, 60, 5)
    snmpNotification.snmpAddress = "va10tuvtos001.wellpoint.com,va10puvtos001.wellpoint.com,va10puvtos002.wellpoint.com:162"
    alertNotifications.append(snmpNotification)


    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # --------- Alert 7
    # Tickets available
    # This value controls how many active connections can access the WiredTiger
    # storage engine at the same time. It is recommended to set an alert for this
    # value when it approaches 0 (e.g. 10).
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.HOST
    newArgs.targetConditionMetric = HostMetricName.TICKETS_AVAILABLE_READS
    newArgs.hostType = "ANY"
    newArgs.metricThresholdOperator = AlertThresholdOperator.LESS_THAN
    newArgs.metricThresholdValue = 10
    newArgs.metricThresholdUnits = MetricThresholdUnits.RAW

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 1)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object
    alertConfigs.append(newArgs)

    # --------- Alert 8
    newArgs = copy.deepcopy(newArgs)
    newArgs.targetConditionMetric = HostMetricName.TICKETS_AVAILABLE_WRITES
    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 1)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object
    alertConfigs.append(newArgs)

    # --------- Alert 9
    # Bytes read into cache
    # Abnormally high number of bytes read into cache might indicate that the working
    # set is bigger than the cache. As there might be other causes for a high number
    # of bytes read into cache, e.g. initial cache population, it might not be practical
    # to set up an alert, but instead check this graph periodically as part of the maintenance
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.HOST
    newArgs.targetConditionMetric = HostMetricName.CACHE_BYTES_READ_INTO
    newArgs.hostType = "ANY"
    newArgs.metricThresholdOperator = AlertThresholdOperator.GREATER_THAN
    newArgs.metricThresholdValue = 2
    newArgs.metricThresholdUnits = MetricThresholdUnits.GIGABYTES

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # --------- Alert 10
    # Replica Set Elections
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.REPLICA_SET
    newArgs.targetConditionMetric = EventTypeName.PRIMARY_ELECTED

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # --------- Alert 11
    # Number of healthy members
    # In replica sets with more than 3 voting members, it may be useful to add an
    # alert when nearing a loss of majority, so that Ops teams can take preventive
    # actions to restore health to the replica set
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.REPLICA_SET
    newArgs.targetConditionMetric = EventTypeName.TOO_FEW_HEALTHY_MEMBERS
    newArgs.thresholdOperator = AlertThresholdOperator.LESS_THAN
    newArgs.thresholdValue = 2
    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []

    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 0)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"
    alertNotifications.append(emailNotification)


    snmpNotification = AlertNotification(AlertNotificationsTypeName.SNMP, 60, 0)
    snmpNotification.snmpAddress = "va10tuvtos001.wellpoint.com,va10puvtos001.wellpoint.com,va10puvtos002.wellpoint.com:162"
    alertNotifications.append(snmpNotification)

    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # --------- Alert 12
    newArgs = copy.deepcopy(newArgs)
    newArgs.targetConditionMetric = EventTypeName.TOO_MANY_UNHEALTHY_MEMBERS
    newArgs.thresholdOperator = AlertThresholdOperator.GREATER_THAN
    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []

    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 0)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"
    alertNotifications.append(emailNotification)

    snmpNotification = AlertNotification(AlertNotificationsTypeName.SNMP, 60, 0)
    snmpNotification.snmpAddress = "va10tuvtos001.wellpoint.com,va10puvtos001.wellpoint.com,va10puvtos002.wellpoint.com:162"
    alertNotifications.append(snmpNotification)

    newArgs.notifications = alertNotifications
    # -------end of code to add notification object
    alertConfigs.append(newArgs)

    # --------- Alert 13
    # Replica set has no primary
    # This alert triggers when all surviving members of the replica set are in "secondary"
    # state. It is recommended to set this alert if the condition lasts for more
    # than 1 minute, as this can happen transiently when performing administrative
    # operations involving a rolling restart or when a primary fails.
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.REPLICA_SET
    newArgs.targetConditionMetric = EventTypeName.NO_PRIMARY
    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []

    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 0)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"
    alertNotifications.append(emailNotification)


    snmpNotification = AlertNotification(AlertNotificationsTypeName.SNMP, 60, 0)
    snmpNotification.snmpAddress = "va10tuvtos001.wellpoint.com,va10puvtos001.wellpoint.com,va10puvtos002.wellpoint.com:162"
    alertNotifications.append(snmpNotification)

    newArgs.notifications = alertNotifications
    # -------end of code to add notification object
    alertConfigs.append(newArgs)

    # --------- Alert 14
    # Host is recovering
    # The Recovering state can be a transient state, or an indicator that the node
    # is out of sync . To differentiate between the two, we recommend to set an alert
    # if the 2 condition lasts for at least 30 minutes
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.HOST
    newArgs.hostType = "ANY"
    newArgs.targetConditionMetric = EventTypeName.HOST_RECOVERING

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []

    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 30)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"
    alertNotifications.append(emailNotification)


    snmpNotification = AlertNotification(AlertNotificationsTypeName.SNMP, 60, 30)
    snmpNotification.snmpAddress = "va10tuvtos001.wellpoint.com,va10puvtos001.wellpoint.com,va10puvtos002.wellpoint.com:162"
    alertNotifications.append(snmpNotification)

    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # --------- Alert 15
    # Host is down
    # It is worth noting that this alert is not real-time, meaning there is typically
    # a delay involved (up to 15-20 minutes in the worst case) in detecting the condition.
    # If real-time notifications are desired, we recommend complementing OpsManager
    # with an appropriate hardware monitoring system
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.HOST
    newArgs.hostType = "ANY"
    newArgs.targetConditionMetric = EventTypeName.HOST_DOWN

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []

    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 0)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"
    alertNotifications.append(emailNotification)

    snmpNotification = AlertNotification(AlertNotificationsTypeName.SNMP, 60, 0)
    snmpNotification.snmpAddress = "va10tuvtos001.wellpoint.com,va10puvtos001.wellpoint.com,va10puvtos002.wellpoint.com:162"
    alertNotifications.append(snmpNotification)

    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # --------- Alert 16
    # Query Targeting: Scanned/Returned
    # This helps catch improper index usage.  It refers to the ratio between the
    # number of index items scanned and the number of documents returned by queries.
    # If this value is 1.0, then your query scanned exactly as many index items as
    # documents it returned; it is an efficient query
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.HOST
    newArgs.targetConditionMetric = HostMetricName.QUERY_TARGETING_SCANNED_PER_RETURNED
    newArgs.metricThresholdOperator = AlertThresholdOperator.GREATER_THAN
    newArgs.hostType = "ANY"
    newArgs.metricThresholdValue = 5
    newArgs.metricThresholdUnits = MetricThresholdUnits.RAW

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # --------- Alert 17
    newArgs = copy.deepcopy(newArgs)
    newArgs.targetConditionMetric = HostMetricName.QUERY_TARGETING_SCANNED_PER_RETURNED
    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []
    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"

    alertNotifications.append(emailNotification)
    newArgs.notifications = alertNotifications
    # -------end of code to add notification object
    alertConfigs.append(newArgs)

    # --------- Alert 18
    # Montioring Agent Down
    #
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.AGENT
    newArgs.targetConditionMetric = EventTypeName.MONITORING_AGENT_DOWN

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []

    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"
    alertNotifications.append(emailNotification)


    snmpNotification = AlertNotification(AlertNotificationsTypeName.SNMP, 60, 5)
    snmpNotification.snmpAddress = "va10tuvtos001.wellpoint.com,va10puvtos001.wellpoint.com,va10puvtos002.wellpoint.com:162"
    alertNotifications.append(snmpNotification)

    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # --------- Alert 19
    # Backup Resync Required
    #
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.BACKUP
    newArgs.targetConditionMetric = EventTypeName.RESYNC_REQUIRED

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []

    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"
    alertNotifications.append(emailNotification)


    snmpNotification = AlertNotification(AlertNotificationsTypeName.SNMP, 60, 5)
    snmpNotification.snmpAddress = "va10tuvtos001.wellpoint.com,va10puvtos001.wellpoint.com,va10puvtos002.wellpoint.com:162"
    alertNotifications.append(snmpNotification)

    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # --------- Alert 20
    # Backup Agent Down
    #
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.AGENT
    newArgs.targetConditionMetric = EventTypeName.BACKUP_AGENT_DOWN

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []

    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"
    alertNotifications.append(emailNotification)


    snmpNotification = AlertNotification(AlertNotificationsTypeName.SNMP, 60, 5)
    snmpNotification.snmpAddress = "va10tuvtos001.wellpoint.com,va10puvtos001.wellpoint.com,va10puvtos002.wellpoint.com:162"
    alertNotifications.append(snmpNotification)


    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # --------- Alert 21
    # Backup OPLOG BEHIND
    #
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.BACKUP
    newArgs.targetConditionMetric = EventTypeName.OPLOG_BEHIND

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []

    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"
    alertNotifications.append(emailNotification)


    snmpNotification = AlertNotification(AlertNotificationsTypeName.SNMP, 60, 5)
    snmpNotification.snmpAddress = "va10tuvtos001.wellpoint.com,va10puvtos001.wellpoint.com,va10puvtos002.wellpoint.com:162"
    alertNotifications.append(snmpNotification)

    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # --------- Alert 22
    # Connection > 1000
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.HOST
    newArgs.targetConditionMetric = HostMetricName.CONNECTIONS
    newArgs.metricThresholdOperator = AlertThresholdOperator.GREATER_THAN
    newArgs.hostType = "ANY"
    newArgs.metricThresholdValue = 1000
    newArgs.metricThresholdUnits = MetricThresholdUnits.RAW

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []

    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"
    alertNotifications.append(emailNotification)


    snmpNotification = AlertNotification(AlertNotificationsTypeName.SNMP, 60, 5)
    snmpNotification.snmpAddress = "va10tuvtos001.wellpoint.com,va10puvtos001.wellpoint.com,va10puvtos002.wellpoint.com:162"
    alertNotifications.append(snmpNotification)

    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    # --------- Alert 23
    # DISK SPACE % USED ON PARTITION
    #  Need to code this Alert but not Found in automation
    # DISK Alert
    #
    newArgs = copy.deepcopy(args)
    newArgs.target = TargetName.HOST
    newArgs.hostType = "ANY"

    newArgs.targetConditionMetric = HostMetricName.DISK_PARTITION_SPACE_USED_DATA
    newArgs.metricThresholdOperator = AlertThresholdOperator.GREATER_THAN
    newArgs.metricThresholdValue = 75
    newArgs.metricThresholdUnits = MetricThresholdUnits.RAW

    # -------------------------------------------
    # Notification Code
    # --------------------------------------------
    alertNotifications = []

    emailNotification = AlertNotification(AlertNotificationsTypeName.EMAIL, 60, 5)
    emailNotification.emailAddress = "dl-adbs-mongodb@customer.com"
    alertNotifications.append(emailNotification)

    snmpNotification = AlertNotification(AlertNotificationsTypeName.SNMP, 60, 5)
    snmpNotification.snmpAddress = "va10tuvtos001.wellpoint.com,va10puvtos001.wellpoint.com,va10puvtos002.wellpoint.com:162"
    alertNotifications.append(snmpNotification)

    newArgs.notifications = alertNotifications
    # -------end of code to add notification object

    alertConfigs.append(newArgs)

    PROD_ALERT_GROUP = AlertsGroup(alertConfigs)

