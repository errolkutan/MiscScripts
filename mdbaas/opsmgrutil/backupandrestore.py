# TODO there is currently lots of unnecessary redundant code here. This is due to some
# lack of understanding on python inheritance, and the lack of enums in pre 3.4
# thereby forcing me to implement my own enums as static classes. Need to research
# and fix this for simplication

################################################################################
# Ops Manager API Backup and Restore Enums
#
# The following enums represent values that the backup and restore ops manager API
# resource can takes
################################################################################

class BackupConfigStatusName():
    """
    BackupConfigStatusName class

    Effectively a static class used in lieu of an enum (only supported by python
     3.4+), representing possible states a backup configuraiton can assume.
    """
    INACTIVE    = "INACTIVE"
    PROVISIONING= "PROVISIONING"
    STARTED     = "STARTED"
    STOPPED     = "STOPPED"
    TERMINATING = "TERMINATING"

    VALUES = [INACTIVE, PROVISIONING, STARTED, STOPPED, TERMINATING]

    @staticmethod
    def isValid(backupConfigStatusStr):
        """
        isValid

        A static method that determines whether the specified string represents a
        valid state that an ops manager backup can assume
        """
        return (backupConfigStatusStr.upper() in BackupConfigStatusName.VALUES)

    @staticmethod
    def valuesToStr():
        """
        Values to String
        """
        str = "["
        for value in BackupConfigStatusName.VALUES:
            str += value + ","
        str += "]"
        return str

class BackupConfigStorageEngineName():
    """
    BackupConfigStorageEngineName class

    Effectively a static class used in lieu of an enum (only supported by python
     3.4+), representing possible storage engines that can be used for snapshots.
    """
    MEMORY_MAPPED   = "MEMORY_MAPPED"
    WIRED_TIGER     = "WIRED_TIGER"

    VALUES = [MEMORY_MAPPED, WIRED_TIGER]

    @staticmethod
    def isValid(backupConfigStorageEngineStr):
        """
        isValid

        A static method that determines whether the specified string represents a
        valid storage engine that an ops manager backup can use
        """
        return (backupConfigStorageEngineStr.upper() in BackupConfigStorageEngineName.VALUES)

    @staticmethod
    def valuesToStr():
        """
        Values to String
        """
        str = "["
        for value in BackupConfigStorageEngineName.VALUES:
            str += value + ","
        str += "]"
        return str
