from internal.auth.repository import UsersRepository
from internal.categories.repository import CategoriesRepository
from internal.reports.repository import ReportsRepository
from internal.services.category_service import CategoryService
from internal.services.report_service import ReportService
from internal.services.transaction_service import TransactionService
from internal.services.user_service import UserService
from internal.transactions.repository import TransactionsRepository


async def get_dependency(dependency_name: str, resource):
    dependency = resource.get(f"{dependency_name}", None)
    if dependency is None:
        raise ModuleNotFoundError(f'"{dependency_name}" was not initialized')
    return dependency


async def initialize_repositories():
    repositories = {}
    repositories["user_repository"] = UsersRepository()
    repositories["category_repository"] = CategoriesRepository()
    repositories["transaction_repository"] = TransactionsRepository()
    repositories["report_repository"] = ReportsRepository()
    return repositories


async def initialize_services(resources):
    services = {}
    services["user_service"] = UserService(
        await get_dependency("user_repository", resources["repositories"])
    )
    services["category_service"] = CategoryService(
        await get_dependency("category_repository", resources["repositories"])
    )
    services["transaction_service"] = TransactionService(
        await get_dependency("transaction_repository", resources["repositories"])
    )
    services["report_service"] = ReportService(
        await get_dependency("report_repository", resources["repositories"]),
        await get_dependency("transaction_service", services),
        await get_dependency("user_service", services),
    )
    return services


async def initialize_dependencies(resources) -> None:
    resources["repositories"] = await initialize_repositories()
    resources["services"] = await initialize_services(resources)
