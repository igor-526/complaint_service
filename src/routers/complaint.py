from datetime import datetime
from typing import List, Optional

from database import async_session_maker

from fastapi import (APIRouter,
                     BackgroundTasks,
                     HTTPException,
                     Query,
                     Request,
                     status)

from models.models import ComplaintDB
from models.schemas import (ComplaintCategory,
                            ComplaintCreate,
                            ComplaintResponse,
                            ComplaintSentiment,
                            ComplaintStatus,
                            ComplaintUpdate)

from settings import AI_SPAM_PROMT

from sqlalchemy import and_, select, update

from tools.complaint import post_create
from tools.yandex_cloud import YandexCloudClassifier


router = APIRouter(prefix="/api/v1", tags=["Complaints"])


@router.post(
    "/complaint/",
    response_model=ComplaintResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую жалобу",
    description="Регистрирует в системе новую жалобу и "
                "обрабатывает в дальнейшем",
    responses={
        400: {"description": "Некорректные данные"},
    },
)
async def create_complaint(
        complaint: ComplaintCreate,
        background_tasks: BackgroundTasks,
        request: Request
):
    spam_classifier = YandexCloudClassifier(
        input_text=complaint.text,
        task_description=AI_SPAM_PROMT,
        choices=["спам", "не спам"],
        default_value="не спам",
        action="spam_detect"
    )
    spam_result = await spam_classifier.y_cloud_classify_text()
    if spam_result == "спам":
        raise HTTPException(status_code=400, detail="В запросе обнаружен спам")
    ip_address = request.client.host
    db_complaint = ComplaintDB(
        text=complaint.text,
        category=complaint.category,
        ip_address=ip_address,
    )
    async with async_session_maker() as session:
        session.add(db_complaint)
        await session.commit()
        await session.refresh(db_complaint)
    background_tasks.add_task(post_create, db_complaint)
    return db_complaint


@router.get(
    "/complaint/",
    response_model=List[ComplaintResponse],
    status_code=status.HTTP_200_OK,
    summary="Получить жалобы",
    description="Отдаёт все жалобы клиентов, "
                "подходящие под условия фильтрации",
)
async def list_complaints(
        category: Optional[ComplaintCategory] = Query(
            None,
            description="Фильтр по категории",
            examples=["техническая", "оплата", "другое"]
        ),
        status: Optional[ComplaintStatus] = Query(
            None,
            description="Фильтр по статусу",
            examples=["open", "closed"]
        ),
        sentiment: Optional[ComplaintSentiment] = Query(
            None,
            description="Фильтр по тональности",
            examples=["positive", "neutral", "negative"]
        ),
        start_date: Optional[datetime] = Query(
            None,
            description="Начальная дата (включительно), "
                        "формат: YYYY-MM-DDTHH:MM:SS",
            examples=["2025-01-15T00:00:00"],
        ),
        end_date: Optional[datetime] = Query(
            None,
            description="Конечная дата (включительно), "
                        "формат: YYYY-MM-DDTHH:MM:SS",
            examples=["2025-01-20T00:00:00"],
        ),
        offset: int = Query(0, ge=0, description="Смещение (пагинация)"),
        limit: int = Query(50, ge=1, le=100, description="Лимит записей")
):
    async with async_session_maker() as session:
        query = select(ComplaintDB)
        filters = []
        if category:
            filters.append(ComplaintDB.category == category.value)
        if status:
            filters.append(ComplaintDB.status == status)
        if sentiment:
            filters.append(ComplaintDB.sentiment == sentiment)
        if start_date:
            filters.append(ComplaintDB.timestamp >= start_date)
        if end_date:
            filters.append(ComplaintDB.timestamp <= end_date)
        if filters:
            query = query.where(and_(*filters))
        query = query.offset(offset).limit(limit).order_by(
            ComplaintDB.timestamp.desc()
        )
        result = await session.execute(query)
        complaints = result.scalars().all()
    return complaints


@router.get(
    "/complaint/{complaint_id}/",
    response_model=ComplaintResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить жалобу",
    description="Отдаёт жалобу клиента по ID",
)
async def get_complaint(complaint_id: int):
    async with async_session_maker() as session:
        query = select(ComplaintDB).where(ComplaintDB.id == complaint_id)
        result = await session.execute(query)
        complaint = result.scalar_one_or_none()
        if not complaint:
            raise HTTPException(status_code=404, detail="Жалоба не найдена")
    return complaint


@router.patch("/complaint/{complaint_id}/",
              response_model=ComplaintResponse,
              status_code=status.HTTP_200_OK,
              summary="Редактировать",
              description="Редактирует жалобу клиента и определяет заново "
                          "тональность и её категорию в случае изменения "
                          "текста",
              responses={
                  400: {"description": "Некорректные данные"},
              },)
async def patch_complaint(complaint_id: int,
                          complaint: ComplaintUpdate,
                          background_tasks: BackgroundTasks):
    async with async_session_maker() as session:
        query = select(ComplaintDB).where(ComplaintDB.id == complaint_id)
        result = await session.execute(query)
        complaint_db = result.scalar_one_or_none()
        if not complaint_db:
            raise HTTPException(status_code=404, detail="Жалоба не найдена")
        update_fields = dict()
        if complaint.status:
            update_fields['status'] = complaint.status
        if complaint.text:
            update_fields['text'] = complaint.text
        if update_fields:
            query_u = update(ComplaintDB).where(
                ComplaintDB.id == complaint_id
            ).values(**update_fields)
            await session.execute(query_u)
            await session.commit()
            await session.refresh(complaint_db)
    if complaint.text:
        background_tasks.add_task(post_create, complaint_db)
    return complaint_db
