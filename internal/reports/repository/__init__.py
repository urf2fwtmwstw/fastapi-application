from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from internal.databases.models import Report as ReportModel
from internal.schemas.report_schema import (
    ReportFSMStatuses,
    ReportSchema,
)


class ReportsRepository:
    @staticmethod
    async def add_report(
        async_session: async_sessionmaker[AsyncSession],
        report_data: ReportSchema,
    ) -> None:
        async with async_session() as session:
            if report_data.fsm_status == ReportFSMStatuses.created:
                report = ReportModel(
                    report_id=report_data.report_id,
                    report_year_month=report_data.report_year_month,
                    user_id=report_data.user_id,
                    fsm_status=report_data.fsm_status,
                )
                session.add(report)
            elif report_data.fsm_status == ReportFSMStatuses.generated:
                statement = (
                    update(ReportModel)
                    .where(ReportModel.report_id == report_data.report_id)
                    .values(
                        month_income=report_data.month_income,
                        month_expenses=report_data.month_expenses,
                        balance=report_data.balance,
                        most_expensive_categories=report_data.most_expensive_categories,
                        fsm_status=report_data.fsm_status,
                    )
                )
                await session.execute(statement)
            elif report_data.fsm_status == ReportFSMStatuses.failed:
                update(ReportModel).where(ReportModel.report_id == report.report_id).values(fsm_status=report_data.fsm_status)
            await session.commit()

    @staticmethod
    async def get_report(
        async_session: async_sessionmaker[AsyncSession],
        report_id: str,
    ) -> ReportSchema:
        async with async_session() as session:
            statement = select(ReportModel).filter(ReportModel.report_id == report_id)
            result = await session.execute(statement)
            reportDB: ReportModel = result.scalars().one()
            report = ReportSchema(
                report_id=reportDB.report_id,
                report_created=reportDB.report_created,
                report_year_month=reportDB.report_year_month,
                month_income=reportDB.month_income,
                month_expenses=reportDB.month_expenses,
                balance=reportDB.balance,
                most_expensive_categories=reportDB.most_expensive_categories,
                user_id=reportDB.user_id,
                fsm_status=reportDB.fsm_status,
            )
            return report

    @staticmethod
    async def delete_report(
        async_session: async_sessionmaker[AsyncSession],
        report_id: str,
    ) -> None:
        async with async_session() as session:
            statement = delete(ReportModel).where(ReportModel.report_id == report_id)
            await session.execute(statement)
            await session.commit()
