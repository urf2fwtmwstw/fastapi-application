import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from internal.reports.repository.reports_repository import ReportsRepository
from internal.schemas.report_schema import ReportCreateSchema
from internal.schemas.transaction_schema import TransactionSchema
from internal.schemas.user_schema import UserSchema
from internal.services.transaction_service import TransactionService
from internal.services.user_service import UserService


class ReportService:
    def __init__(
        self,
        repo: ReportsRepository,
        transaction_service: TransactionService,
        user_service: UserService,
    ):
        self.repo = repo
        self.transaction_service = transaction_service
        self.user_service = user_service

    @staticmethod
    async def __get_month_dependant_attributes(
        report_month_transactions: list[TransactionSchema],
    ) -> dict[str:float, str:float, str : dict[str:float]]:
        month_income: float = 0
        month_expenses: float = 0
        expenses_in_category: dict[str:float] = {}
        for transaction in report_month_transactions:
            if transaction.transaction_type == "income":
                month_income += transaction.transaction_value
            else:
                expense_value: float = transaction.transaction_value
                month_expenses += expense_value
                category_id: str = transaction.category_id
                expenses_in_category[category_id] = (
                    expenses_in_category.get(category_id, 0) + expense_value
                )
        return {
            "month_income": month_income,
            "month_expenses": month_expenses,
            "expenses_in_category": expenses_in_category,
        }

    @staticmethod
    async def __get_balance(transactions: list[TransactionSchema]) -> float:
        balance: float = 0
        for transaction in transactions:
            if transaction.transaction_type == "income":
                balance += transaction.transaction_value
            elif transaction.transaction_type == "expenses":
                balance -= transaction.transaction_value
        return balance

    # sort dictionary of {category_id: expenses} by value and return a string with ids of the most expensive categories
    @staticmethod
    async def __sort_category_dict(expense_categories: dict[str:float]) -> str:
        most_expensive_categories_ids = [
            str(category_id)
            for category_id, expenses in sorted(
                expense_categories.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        ][:5]
        return ", ".join(most_expensive_categories_ids)

    async def add_report(
        self,
        session: async_sessionmaker[AsyncSession],
        transactions: list[TransactionSchema],
        user_id,
        report_year: int,
        report_month: int,
    ) -> None:
        report_month_transactions = [
            transaction
            for transaction in transactions
            if transaction.transaction_date.year == report_year
            and transaction.transaction_date.month == report_month
        ]
        month_dependant_attributes = await self.__get_month_dependant_attributes(
            report_month_transactions
        )
        month_income: float = month_dependant_attributes["month_income"]
        month_expenses: float = month_dependant_attributes["month_expenses"]
        expenses_in_category: dict[str:float] = month_dependant_attributes[
            "expenses_in_category"
        ]
        most_expensive_categories: str = await self.__sort_category_dict(
            expenses_in_category
        )
        balance: float = await self.__get_balance(transactions)
        balance += month_income - month_expenses

        report = ReportCreateSchema(
            report_year_month=str(report_year) + "-" + str(report_month),
            month_income=month_income,
            month_expenses=month_expenses,
            balance=balance,
            most_expensive_categories=most_expensive_categories,
            user_id=user_id,
        )
        await self.repo.add_report(session, report)

    async def async_report_generation(
        self,
        session: async_sessionmaker[AsyncSession],
        report_year: int,
        report_month: int,
    ) -> None:
        async_tasks = []
        users: list[UserSchema] = await self.user_service.get_users(session)
        user_ids: list[str] = [str(user.user_id) for user in users]

        for user_id in user_ids:
            transactions: list[
                TransactionSchema
            ] = await self.transaction_service.get_transactions(session, user_id)
            task = asyncio.create_task(
                self.add_report(
                    session, transactions, user_id, report_year, report_month
                )
            )
            async_tasks.append(task)

        await asyncio.gather(*async_tasks)
