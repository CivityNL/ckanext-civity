from abc import abstractmethod


class RecordToPackageConverterException(Exception):
    """
    Exception class for RecordToPackageConverter
    """
    pass


class IRecordToPackageConverter:

    def __init__(self):
        pass

    @abstractmethod
    def record_to_package(self, guid, record):
        pass
