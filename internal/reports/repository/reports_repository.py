from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from internal.databases.models import Report
from internal.schemas.report_schema import ReportCreateSchema


class ReportsRepository:
    async def add_report(
        self,
        async_session: async_sessionmaker[AsyncSession],
        report_data: ReportCreateSchema,
    ) -> None:
        report = Report(
            report_id=report_data.report_id,
            report_year_month=report_data.report_year_month,
            month_income=report_data.month_income,
            month_expenses=report_data.month_expenses,
            balance=report_data.balance,
            most_expensive_categories=report_data.most_expensive_categories,
            user_id=report_data.user_id,
        )
        async with async_session() as session:
            session.add(report)
            await session.commit()
