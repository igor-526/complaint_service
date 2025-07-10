import asyncio

from database import async_session_maker

from models.models import ComplaintDB

from settings import AI_COMPLAINT_CATEGORY_PROMT, AI_COMPLAINT_SENTIMENT_PROMT

from sqlalchemy import update

from tools.yandex_cloud import YandexCloudClassifier


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


async def post_create(complaint: ComplaintDB):
    """Обработка жалобы после её сохранения в базу данных.

    Args:
        complaint (ComplaintDB): экземпляр жалобы для анализа

    Returns:
        None.
    """
    cs = ComplaintService(complaint)
    await cs.update_sentiment_and_category()
