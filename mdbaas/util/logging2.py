class LogLevel():
    """
    LogLevel

    A static class serving the function of an enum
    """
    NONE = 0
    NONE_STR = "none"
    SPARSE = 1
    SPARSE_STR = "sparse"
    INFO = 2
    INFO_STR = "info"
    VERBOSE = 3
    VERBOSE_STR = "verbose"

class Logger():
    """
    Logger

    A class to implement multi-verbosity logging
    """
    def __init__(self, logLevelStr):
        self.logLevelStr = logLevelStr
        if LogLevel.VERBOSE_STR == logLevelStr:
            self.logLevel = LogLevel.VERBOSE
        elif LogLevel.NONE == logLevelStr:
            self.logLevel = LogLevel.NONE
        elif LogLevel.SPARSE_STR == logLevelStr:
            self.logLevel = LogLevel.SPARSE
        else:
            self.logLevel = LogLevel.INFO

    def log(self, msg, logLevel):
        """
        log
        Logs msg if the log level is sufficiently high

        msg:        A String representing the message to log out
        logLevel:   The log level of the message
        """
        logLevelStr = "NONE"
        if LogLevel.VERBOSE == logLevel:
            logLevelStr =  LogLevel.VERBOSE_STR
        elif LogLevel.NONE == logLevel:
            logLevelStr =  LogLevel.NONE_STR
        elif LogLevel.SPARSE_STR == logLevel:
            logLevelStr =  LogLevel.SPARSE_STR
        if self.logLevel >= logLevel and not self.logLevel <= LogLevel.NONE:
            print(logLevelStr.upper() + ": " + msg)
