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

    async def add_report(
        self,
        session: async_sessionmaker[AsyncSession],
        transactions: list[TransactionSchema],
        user_id,
        report_year: int,
        report_month: int,
    ) -> None:
        month_income: float = 0
        month_expenses: float = 0
        expenses_in_category: dict[str:float] = {}
        last_transaction_index: int = len(transactions)
        most_expensive_categories: None = None
        balance: None = None
        for i in range(last_transaction_index):
            transaction: TransactionSchema = transactions[i]
            if (
                transaction.transaction_date.year == report_year
                and transaction.transaction_date.month == report_month
            ):
                if transaction.transaction_type == "income":
                    month_income += transaction.transaction_value
                else:
                    expense_value: float = transaction.transaction_value
                    category_id: str = transaction.category_id
                    month_expenses += expense_value
                    expenses_in_category[category_id] = (
                        expenses_in_category.get(category_id, 0) + expense_value
                    )
            else:
                most_expensive_categories: str = ", ".join(
                    [
                        str(k)
                        for k, v in sorted(
                            expenses_in_category.items(),
                            key=lambda item: item[1],
                            reverse=True,
                        )
                    ][:5]
                )
                balance: float = month_income - month_expenses
                for j in range(i, last_transaction_index):
                    transaction: TransactionSchema = transactions[j]
                    if transaction.transaction_type == "income":
                        balance += transaction.transaction_value
                    else:
                        balance -= transaction.transaction_value
                break
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
