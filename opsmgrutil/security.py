class MongoDBRole():
    """
    MongoDBRole
    """
    READ                    = "read"
    READ_WRITE              = "readWrite"
    DB_ADMIN                = "dbAdmin"
    DB_OWNER                = "dbOwner"
    USER_ADMIN              = "userAdmin"
    ENABLE_SHARDING         = "enableSharding"
    CLUSTER_ADMIN           = "clusterAdmin"
    CLUSTER_MONITOR         = "clusterMonitor"
    HOST_MANAGER            = "hostManager"
    BACKUP                  = "backup"
    RESTORE                 = "restore"
    READ_ANY_DATABASE       = "readAnyDatabase"
    READ_WRITE_ANY_DATABASE = "readWriteAnyDatabase"
    USER_ADMIN_ANY_DATABASE = "userAdminAnyDatabase"
    DB_ADMIN_ANY_DATABASE   = "dbAdminAnyDatabase"
    ROOT                    = "root"
    VALUES = [READ, READ_WRITE, DB_ADMIN, DB_OWNER, USER_ADMIN, ENABLE_SHARDING, CLUSTER_ADMIN, CLUSTER_MONITOR, HOST_MANAGER,
              BACKUP, RESTORE, READ_ANY_DATABASE, READ_WRITE_ANY_DATABASE, USER_ADMIN_ANY_DATABASE, DB_ADMIN_ANY_DATABASE, ROOT]

    @staticmethod
    def isValid(mongoDbRole):
        """
        isValid

        A static method that determines whether the specified string represents a
        valid deployment topology
        """
        return (mongoDbRole.upper() in MongoDBRole.VALUES)

    @staticmethod
    def valuesToStr():
        """
        Values to String
        """
        str = "["
        ctr = 0
        for value in MongoDBRole.VALUES:
            ctr += 1
            if ctr != len(MongoDBRole.VALUES):
                str += value + ","
        str += "]"
        return str

class Role():

    def __init__(self, db, role):
        """

        :param db:
        :param role:
        """
        self.db = db
        self.role = role

    def getValue(self):
        return {
            "db"    : self.db,
            "role"  : self.role
        }

class AuthMechanisms():
    """

    :return:
    """
    MONGODB_CR      = "MONGODB-CR"          # MONGODB-CR/SCRAM-SHA-1
    MONGODB_X509    = "MONGODB-X509"        # x.509 Client Certificate
    PLAIN           = "PLAIN"               # LDAP
    GSSAPI          = "GSSAPI"              # Kerberos
    VALUES = [MONGODB_CR, MONGODB_X509, PLAIN, GSSAPI]

    @staticmethod
    def isValid(authMechanism):
        """
        isValid

        A static method that determines whether the specified string represents a
        valid deployment topology
        """
        return (authMechanism.upper() in AuthMechanisms.VALUES)

    @staticmethod
    def valuesToStr():
        """
        Values to String
        """
        str = "["
        ctr = 0
        for value in AuthMechanisms.VALUES:
            ctr += 1
            if ctr != len(AuthMechanisms.VALUES):
                str += value + ","
        str += "]"
        return str
