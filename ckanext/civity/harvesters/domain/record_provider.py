from abc import abstractmethod


class RecordProviderException(Exception):
    """
    Exception class for RecordToPackageConverter
    """
    pass


class IRecordProvider:

    def __init__(self):
        pass

    @abstractmethod
    def get_record_ids(self):
        """Get a dictionary with records from the harvest source."""

        # TODO Python 3: use type and return annotations

        pass

    @abstractmethod
    def get_record_by_id(self, guid):
        """Get a record with a specific ID from the harvest source."""
        pass
