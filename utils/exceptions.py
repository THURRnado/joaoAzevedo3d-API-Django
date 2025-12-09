from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404


class AppError(Exception):
    """
    Exceção base para o projeto.
    Todas as exceções personalizadas devem herdar desta.
    """
    default_message = "Ocorreu um erro."

    def __init__(self, message=None):
        super().__init__(message or self.default_message)


class ResourceNotFound(Http404):
    """
    Quando um recurso não existe — 404.
    Substitui o Http404 com mensagem personalizada.
    """
    default_message = "Recurso não encontrado."

    def __init__(self, message=None):
        super().__init__(message or self.default_message)


class UnauthorizedError(PermissionDenied):
    """
    Usuário não tem permissão — 403.
    """
    default_message = "Você não tem permissão para realizar esta ação."

    def __init__(self, message=None):
        super().__init__(message or self.default_message)


class InvalidRequestError(ValidationError):
    """
    Erros de validação — 400.
    Ex.: parâmetros inválidos, campos faltando etc.
    """
    default_message = "Requisição inválida."

    def __init__(self, message=None, code=None, params=None):
        super().__init__(message or self.default_message, code=code, params=params)


class ServiceError(AppError):
    """
    Erros genéricos de serviços, APIs ou regras de negócio.
    Não expõe detalhes sensíveis ao cliente.
    """
    default_message = "Erro interno ao processar a operação."


class ExternalAPIError(AppError):
    """
    Quando uma API externa falha (timeout, erro 500, etc.)
    """
    default_message = "Erro ao comunicar com serviço externo."


class ConflictError(AppError):
    """
    Quando há conflito de estado — 409.
    Ex.: tentar criar algo que já existe.
    """
    default_message = "Conflito ao processar o recurso."
