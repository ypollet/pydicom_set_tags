from enum import Enum

    
class OrthancErrorCode(Enum):
    """Orthanc HTTP Error Code Status
    Copyrighted from https://www.orthanc-server.com/

    Returns:
        id: id of error
    """
    ErrorCode_InternalError = -1,    # Internal error
    ErrorCode_Success = 0,    # Success
    ErrorCode_Plugin = 1,    # Error encountered within the plugin engine
    ErrorCode_NotImplemented = 2,    # Not implemented yet
    ErrorCode_ParameterOutOfRange = 3,    # Parameter out of range
    ErrorCode_NotEnoughMemory = 4,    # The server hosting Orthanc is running out of memory
    ErrorCode_BadParameterType = 5,    # Bad type for a parameter
    ErrorCode_BadSequenceOfCalls = 6,    # Bad sequence of calls
    ErrorCode_InexistentItem = 7,    # Accessing an inexistent item
    ErrorCode_BadRequest = 8,    # Bad request
    ErrorCode_NetworkProtocol = 9,    # Error in the network protocol
    ErrorCode_SystemCommand = 10,    # Error while calling a system command
    ErrorCode_Database = 11,    # Error with the database engine
    ErrorCode_UriSyntax = 12,    # Badly formatted URI
    ErrorCode_InexistentFile = 13,    # Inexistent file
    ErrorCode_CannotWriteFile = 14,    # Cannot write to file
    ErrorCode_BadFileFormat = 15,    # Bad file format
    ErrorCode_Timeout = 16,    # Timeout
    ErrorCode_UnknownResource = 17,    # Unknown resource
    ErrorCode_IncompatibleDatabaseVersion = 18,    # Incompatible version of the database
    ErrorCode_FullStorage = 19,    # The file storage is full
    ErrorCode_CorruptedFile = 20,    # Corrupted file (e.g. inconsistent MD5 hash)
    ErrorCode_InexistentTag = 21,    # Inexistent tag
    ErrorCode_ReadOnly = 22,    # Cannot modify a read-only data structure
    ErrorCode_IncompatibleImageFormat = 23,    # Incompatible format of the images
    ErrorCode_IncompatibleImageSize = 24,    # Incompatible size of the images
    ErrorCode_SharedLibrary = 25,    # Error while using a shared library (plugin)
    ErrorCode_UnknownPluginService = 26,    # Plugin invoking an unknown service
    ErrorCode_UnknownDicomTag = 27,    # Unknown DICOM tag
    ErrorCode_BadJson = 28,    # Cannot parse a JSON document
    ErrorCode_Unauthorized = 29,    # Bad credentials were provided to an HTTP request
    ErrorCode_BadFont = 30,    # Badly formatted font file
    ErrorCode_DatabasePlugin = 31,    # The plugin implementing a custom database back-end does not fulfill the proper interface
    ErrorCode_StorageAreaPlugin = 32,    # Error in the plugin implementing a custom storage area
    ErrorCode_EmptyRequest = 33,    # The request is empty
    ErrorCode_NotAcceptable = 34,    # Cannot send a response which is acceptable according to the Accept HTTP header
    ErrorCode_NullPointer = 35,    # Cannot handle a NULL pointer
    ErrorCode_DatabaseUnavailable = 36,    # The database is currently not available (probably a transient situation)
    ErrorCode_CanceledJob = 37,    # This job was canceled
    ErrorCode_BadGeometry = 38,    # Geometry error encountered in Stone
    ErrorCode_SslInitialization = 39,    # Cannot initialize SSL encryption, check out your certificates
    ErrorCode_DiscontinuedAbi = 40,    # Calling a function that has been removed from the Orthanc Framework
    ErrorCode_BadRange = 41,    # Incorrect range request
    ErrorCode_DatabaseCannotSerialize = 42,    # Database could not serialize access due to concurrent update, the transaction should be retried
    ErrorCode_Revision = 43,    # A bad revision number was provided, which might indicate conflict between multiple writers
    ErrorCode_MainDicomTagsMultiplyDefined = 44,    # A main DICOM Tag has been defined multiple times for the same resource level
    ErrorCode_ForbiddenAccess = 45,    # Access to a resource is forbidden
    ErrorCode_SQLiteNotOpened = 1000,    # SQLite: The database is not opened
    ErrorCode_SQLiteAlreadyOpened = 1001,    # SQLite: Connection is already open
    ErrorCode_SQLiteCannotOpen = 1002,    # SQLite: Unable to open the database
    ErrorCode_SQLiteStatementAlreadyUsed = 1003,    # SQLite: This cached statement is already being referred to
    ErrorCode_SQLiteExecute = 1004,    # SQLite: Cannot execute a command
    ErrorCode_SQLiteRollbackWithoutTransaction = 1005,    # SQLite: Rolling back a nonexistent transaction (have you called Begin()?)
    ErrorCode_SQLiteCommitWithoutTransaction = 1006,    # SQLite: Committing a nonexistent transaction
    ErrorCode_SQLiteRegisterFunction = 1007,    # SQLite: Unable to register a function
    ErrorCode_SQLiteFlush = 1008,    # SQLite: Unable to flush the database
    ErrorCode_SQLiteCannotRun = 1009,    # SQLite: Cannot run a cached statement
    ErrorCode_SQLiteCannotStep = 1010,    # SQLite: Cannot step over a cached statement
    ErrorCode_SQLiteBindOutOfRange = 1011,    # SQLite: Bing a value while out of range (serious error)
    ErrorCode_SQLitePrepareStatement = 1012,    # SQLite: Cannot prepare a cached statement
    ErrorCode_SQLiteTransactionAlreadyStarted = 1013,    # SQLite: Beginning the same transaction twice
    ErrorCode_SQLiteTransactionCommit = 1014,    # SQLite: Failure when committing the transaction
    ErrorCode_SQLiteTransactionBegin = 1015,    # SQLite: Cannot start a transaction
    ErrorCode_DirectoryOverFile = 2000,    # The directory to be created is already occupied by a regular file
    ErrorCode_FileStorageCannotWrite = 2001,    # Unable to create a subdirectory or a file in the file storage
    ErrorCode_DirectoryExpected = 2002,    # The specified path does not point to a directory
    ErrorCode_HttpPortInUse = 2003,    # The TCP port of the HTTP server is privileged or already in use
    ErrorCode_DicomPortInUse = 2004,    # The TCP port of the DICOM server is privileged or already in use
    ErrorCode_BadHttpStatusInRest = 2005,    # This HTTP status is not allowed in a REST API
    ErrorCode_RegularFileExpected = 2006,    # The specified path does not point to a regular file
    ErrorCode_PathToExecutable = 2007,    # Unable to get the path to the executable
    ErrorCode_MakeDirectory = 2008,    # Cannot create a directory
    ErrorCode_BadApplicationEntityTitle = 2009,    # An application entity title (AET) cannot be empty or be longer than 16 characters
    ErrorCode_NoCFindHandler = 2010,    # No request handler factory for DICOM C-FIND SCP
    ErrorCode_NoCMoveHandler = 2011,    # No request handler factory for DICOM C-MOVE SCP
    ErrorCode_NoCStoreHandler = 2012,    # No request handler factory for DICOM C-STORE SCP
    ErrorCode_NoApplicationEntityFilter = 2013,    # No application entity filter
    ErrorCode_NoSopClassOrInstance = 2014,    # DicomUserConnection: Unable to find the SOP class and instance
    ErrorCode_NoPresentationContext = 2015,    # DicomUserConnection: No acceptable presentation context for modality
    ErrorCode_DicomFindUnavailable = 2016,    # DicomUserConnection: The C-FIND command is not supported by the remote SCP
    ErrorCode_DicomMoveUnavailable = 2017,    # DicomUserConnection: The C-MOVE command is not supported by the remote SCP
    ErrorCode_CannotStoreInstance = 2018,    # Cannot store an instance
    ErrorCode_CreateDicomNotString = 2019,    # Only string values are supported when creating DICOM instances
    ErrorCode_CreateDicomOverrideTag = 2020,    # Trying to override a value inherited from a parent module
    ErrorCode_CreateDicomUseContent = 2021,    # Use \"Content\" to inject an image into a new DICOM instance
    ErrorCode_CreateDicomNoPayload = 2022,    # No payload is present for one instance in the series
    ErrorCode_CreateDicomUseDataUriScheme = 2023,    # The payload of the DICOM instance must be specified according to Data URI scheme
    ErrorCode_CreateDicomBadParent = 2024,    # Trying to attach a new DICOM instance to an inexistent resource
    ErrorCode_CreateDicomParentIsInstance = 2025,    # Trying to attach a new DICOM instance to an instance (must be a series, study or patient)
    ErrorCode_CreateDicomParentEncoding = 2026,    # Unable to get the encoding of the parent resource
    ErrorCode_UnknownModality = 2027,    # Unknown modality
    ErrorCode_BadJobOrdering = 2028,    # Bad ordering of filters in a job
    ErrorCode_JsonToLuaTable = 2029,    # Cannot convert the given JSON object to a Lua table
    ErrorCode_CannotCreateLua = 2030,    # Cannot create the Lua context
    ErrorCode_CannotExecuteLua = 2031,    # Cannot execute a Lua command
    ErrorCode_LuaAlreadyExecuted = 2032,    # Arguments cannot be pushed after the Lua function is executed
    ErrorCode_LuaBadOutput = 2033,    # The Lua function does not give the expected number of outputs
    ErrorCode_NotLuaPredicate = 2034,    # The Lua function is not a predicate (only true/false outputs allowed)
    ErrorCode_LuaReturnsNoString = 2035,    # The Lua function does not return a string
    ErrorCode_StorageAreaAlreadyRegistered = 2036,    # Another plugin has already registered a custom storage area
    ErrorCode_DatabaseBackendAlreadyRegistered = 2037,    # Another plugin has already registered a custom database back-end
    ErrorCode_DatabaseNotInitialized = 2038,    # Plugin trying to call the database during its initialization
    ErrorCode_SslDisabled = 2039,    # Orthanc has been built without SSL support
    ErrorCode_CannotOrderSlices = 2040,    # Unable to order the slices of the series
    ErrorCode_NoWorklistHandler = 2041,    # No request handler factory for DICOM C-Find Modality SCP
    ErrorCode_AlreadyExistingTag = 2042,    # Cannot override the value of a tag that already exists
    ErrorCode_NoStorageCommitmentHandler = 2043,    # No request handler factory for DICOM N-ACTION SCP (storage commitment)
    ErrorCode_NoCGetHandler = 2044,    # No request handler factory for DICOM C-GET SCP
    ErrorCode_UnsupportedMediaType = 3000,    # Unsupported media type
    ErrorCode_START_PLUGINS = 1000000

class ImageType(Enum):
    IMAGE = "image/",
    FILE = "application/file",
    PDF = "application/pdf"

extension = {
    "jpg" : ImageType.IMAGE,
    "jpeg" : ImageType.IMAGE,
    "png" : ImageType.IMAGE,
    "tiff" : ImageType.IMAGE,
    "tif" : ImageType.IMAGE,
    "pdf" : ImageType.PDF
}

def get_type(ext : str):
    return extension[ext] if ext in extension else ImageType.FILE