class OpsManagerOrgRole():
    """
    MongoDB Ops Manager Org Role

    """
    ORG_OWNER           = "ORG_OWNER"
    ORG_MEMBER          = "ORG_MEMBER"
    ORG_GROUP_CREATOR   = "ORG_GROUP_CREATOR"
    ORG_READ_ONLY       = "ORG_READ_ONLY"
    VALUES = [ ORG_MEMBER, ORG_OWNER, ORG_GROUP_CREATOR, ORG_READ_ONLY ]

    @staticmethod
    def isValid(opsMgrOrgRole):
        """
        isValid

        A static method that determines whether the specified string represents a
        valid deployment topology
        """
        return (opsMgrOrgRole.upper() in OpsManagerOrgRole.VALUES)

    @staticmethod
    def valuesToStr():
        """
        Values to String
        """
        str = "["
        ctr = 0
        for value in OpsManagerOrgRole.VALUES:
            ctr += 1
            if ctr != len(OpsManagerOrgRole.VALUES):
                str += value + ","
        str += "]"
        return str


class OpsManagerGroupRole():
    """
    MongoDB Ops Manager Group Role

    """
    GROUP_AUTOMATION_ADMIN = "GROUP_AUTOMATION_ADMIN"
    GROUP_BACKUP_ADMIN = "GROUP_BACKUP_ADMIN"
    GROUP_DATA_ACCESS_ADMIN = "GROUP_DATA_ACCESS_ADMIN"
    GROUP_DATA_ACCESS_READ_ONLY = "GROUP_DATA_ACCESS_READ_ONLY"
    GROUP_DATA_ACCESS_READ_WRITE = "GROUP_DATA_ACCESS_READ_WRITE"
    GROUP_MONITORING_ADMIN = "GROUP_MONITORING_ADMIN"
    GROUP_OWNER = "GROUP_OWNER"
    GROUP_READ_ONLY = "GROUP_READ_ONLY"
    GROUP_USER_ADMIN = "GROUP_USER_ADMIN"
    VALUES = [GROUP_AUTOMATION_ADMIN, GROUP_BACKUP_ADMIN, GROUP_DATA_ACCESS_ADMIN, GROUP_DATA_ACCESS_READ_WRITE,
              GROUP_DATA_ACCESS_READ_ONLY,
              GROUP_MONITORING_ADMIN, GROUP_OWNER, GROUP_READ_ONLY, GROUP_USER_ADMIN]

    @staticmethod
    def isValid(opsManagerGroupRole):
        """
        isValid

        A static method that determines whether the specified string represents a
        valid deployment topology
        """
        return (opsManagerGroupRole.upper() in OpsManagerGroupRole.VALUES)

    @staticmethod
    def valuesToStr():
        """
        Values to String
        """
        str = "["
        ctr = 0
        for value in OpsManagerGroupRole.VALUES:
            ctr += 1
            if ctr != len(OpsManagerGroupRole.VALUES):
                str += value + ","
        str += "]"
        return str