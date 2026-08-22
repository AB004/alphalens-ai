class CompanyChatError(Exception):
    """
    Base exception for Company Chat.
    """


class CompanyNotFoundError(CompanyChatError):
    """
    Raised when the requested company does not exist.
    """


class EmptyQuestionError(CompanyChatError):
    """
    Raised when the user question is empty.
    """


class ConversationNotFoundError(CompanyChatError):
    """
    Raised when the requested conversation does not exist.
    """


class InvalidConversationError(CompanyChatError):
    """
    Raised when a conversation cannot be used
    for the requested company.
    """


class CompanyChatProcessingError(CompanyChatError):
    """
    Raised when Company Chat processing fails.
    """