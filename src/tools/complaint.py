import asyncio
import logging

from database import async_session_maker

from models.models import ComplaintDB

from settings import AI_COMPLAINT_CATEGORY_PROMT, AI_COMPLAINT_SENTIMENT_PROMT

from sqlalchemy import select, update

from tools.dadata import get_geo_by_ip
from tools.yandex_cloud import YandexCloudClassifier

logger = logging.getLogger("app")


class ComplaintService:
    """Управляет жалобами.

    Attributes:
        complaint (ComplaintDB): жалоба.
    """
    complaint: ComplaintDB = None

    def __init__(self, complaint: ComplaintDB):
        self.complaint = complaint

    async def update_sentiment_and_category(self) -> None:
        """Взаимодействуя с YandexCloudClassifier определяет
        тональность и категорию жалобы, после чего редактирует
        запись в базе данных.

        Returns:
            None.
        """
        ycc_sentiment = YandexCloudClassifier(
            input_text=self.complaint.text,
            task_description=AI_COMPLAINT_SENTIMENT_PROMT,
            choices=["positive", "negative", "neutral"],
            default_value="unknown",
            action="get_text_sentiment",
        )
        ycc_category = YandexCloudClassifier(
            input_text=self.complaint.text,
            task_description=AI_COMPLAINT_CATEGORY_PROMT,
            choices=["техническая", "оплата", "другое"],
            default_value="другое",
            action="get_text_category",
        )
        tasks = [
            asyncio.create_task(ycc_sentiment.y_cloud_classify_text()),
            asyncio.create_task(ycc_category.y_cloud_classify_text()),
        ]
        result = await asyncio.gather(*tasks, return_exceptions=True)
        async with async_session_maker() as db_session:
            query = update(ComplaintDB).where(
                ComplaintDB.id == self.complaint.id
            ).values(sentiment=result[0],
                     category=result[1])
            await db_session.execute(query)
            await db_session.commit()

    async def update_geolocation(self) -> None:
        """
        Обработка IP адреса запроса жалобы после её сохранения в базу данных.
        Функция проверяет наличие такого IP адреса в базе данных и в случае
        отсутствия делает запрос на получение данных

        Returns:
            None.
        """
        if not self.complaint.ip_address:
            logger.error("No IP address to locate")
            return None
        async with async_session_maker() as db_session:
            query = select(ComplaintDB).where(
                ComplaintDB.ip_address == self.complaint.ip_address,
                ComplaintDB.geo_country.is_not(None),
                ComplaintDB.geo_city.is_not(None)
            )
            result = await db_session.execute(query)
            q_complaint = result.scalar_one_or_none()
            if q_complaint:
                query = update(ComplaintDB).where(
                    ComplaintDB.id == self.complaint.id
                ).values(geo_country=q_complaint.geo_country,
                         geo_city=q_complaint.geo_city)
                await db_session.execute(query)
                await db_session.commit()
                return None
        try:
            result = await get_geo_by_ip(self.complaint.ip_address)
            async with async_session_maker() as db_session:
                query = update(ComplaintDB).where(
                    ComplaintDB.id == self.complaint.id
                ).values(geo_country=result["country"],
                         geo_city=result["city"])
                await db_session.execute(query)
                await db_session.commit()
                return None
        except ValueError:
            logger.error(f"IP address {self.complaint.ip_address} "
                         f"is incorrect")
        except Exception as e:
            logger.error(f"Failed to locate IP Address "
                         f"{self.complaint.ip_address}: {e}")


async def post_create(complaint: ComplaintDB):
    """Обработка жалобы после её сохранения в базу данных.

    Args:
        complaint (ComplaintDB): экземпляр жалобы для анализа

    Returns:
        None.
    """
    cs = ComplaintService(complaint)
    tasks = [
        asyncio.create_task(cs.update_sentiment_and_category()),
        asyncio.create_task(cs.update_geolocation()),
    ]
    await asyncio.gather(*tasks, return_exceptions=True)
