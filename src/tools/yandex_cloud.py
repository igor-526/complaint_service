import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, List
from typing import Optional
from uuid import uuid4

import aiohttp

from pydantic import BaseModel

from settings import (HTTP_CONNECTION_RETRIES,
                      HTTP_CONNECTION_RETRY_DELAY,
                      HTTP_CONNECTION_TIMEOUT,
                      YA_CLOUD_CATALOG_ID,
                      YA_CLOUD_OAUTH_TOKEN)

logger = logging.getLogger("app")


class YCIAMToken(BaseModel):
    token: str
    expires_at: datetime


class YCTokenManager:
    """Управляет OAuth-токенами для API Yandex Cloud.

    Автоматически обновляет токены при истечении срока действия.
    Использует asyncio.Lock для потокобезопасности.

    Attributes:
        _token (str | None): Текущий IAM-токен (кешируется).
        _lock (asyncio.Lock): Блокировка для избежания race condition.
    """
    def __init__(self):
        self._token: Optional[YCIAMToken] = None

    async def get_token(self) -> str | None:
        """Получает IAM Token из кэша или делает его обновление при
        отсутствии или истечения срока действия.

        Returns:
            str | None. Строку с IAM Token в случае его удачного
            получения или None в случае ошибки
        """
        logger.info("Requested Yandex Cloud IAM Token")
        if (self._token is None or
                self._token.expires_at + timedelta(minutes=1) >
                datetime.now()):
            try:
                await self._refresh_token()
                return self._token.token if self._token else None
            except Exception as e:
                logger.info(f"Failed to refresh Yandex Cloud IAM Token: {e}")
                return None
        return self._token.token if self._token else None

    async def _refresh_token(self) -> None:
        """Получает IAM Token на основе OAuth токена и обновляет его
        в атрибутах класса

        Raises:
            Exception: Если код ответа сервера не 200.

        Returns:
            None.
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    url="https://iam.api.cloud.yandex.net/iam/v1/tokens",
                    json={
                        "yandexPassportOauthToken": YA_CLOUD_OAUTH_TOKEN
                    }
            ) as response:
                data = await response.json()

                if response.status != 200:
                    raise Exception(f"Token refresh failed: {data}")

                exp_at = data["expiresAt"][:26] + 'Z'
                exp_at = datetime.strptime(exp_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                self._token = YCIAMToken(
                    token=data["iamToken"],
                    expires_at=exp_at
                )


class YandexCloudClassifier:
    """Классифицирует полученный текст на один из предложенных
    вариантов.

    Attributes:
        input_text (str): текст, который необходимо классифицировать.
        task_description (str): промт, описывающий задачу.
        choices: (List[str]): список значений, среди которых нужно
        выбрать.
        default_value (str): значение, которое вернёт функция при
        возникновении ошибок.
        action (str): какое действие выполняется для логирования
        request_id (str): сгенерированный uuid4 запроса для логов
        last_error (Exception | str | None): последняя ошибка для
        логов
        data (dict[str, Any] | None): JSON, полученный в сервера
    """
    input_text: str
    task_description: str
    choices: List[str]
    default_value: str
    action: str
    request_id: str
    last_error: Exception | str | None
    data: dict[str, Any] | None

    def __init__(self,
                 input_text: str,
                 task_description: str,
                 choices: List[str],
                 default_value: str = "not classified",
                 action: str = "yc_classification",
                 ):
        """Инициирует класс для последующей обработки.

        Args:
            input_text (str): текст, который необходимо
            классифицировать.
            task_description (str): промт, описывающий задачу.
            choices: (List[str]): список значений, среди которых
            нужно выбрать.
            default_value (str, optional, default="not classified"):
            значение, которое вернёт функция при возникновении ошибок.
            action (str, optional, default="yc_classification"):
            какое действие выполняется для логирования

        Returns:
            str. Одно из значений, перечисленных в choices или default
        """
        self.input_text = input_text
        self.task_description = task_description
        self.choices = choices
        self.default_value = default_value
        self.action = action
        self.request_id = str(uuid4())
        self.last_error: Exception | str | None = None
        self.data = None

    def _log(self,
             message: str,
             level: int = logging.INFO,
             **kwargs) -> None:
        """
        Логирует событие. Автоматически включает информацию о
        request_id и action

        Args:
            message (str): сообщение лога.
            level (int, optional, default=logging.INFO): уровень лога.
            kwargs: дополнительные extra для логирования.

        Returns:
            None

        Example:
            >> self._log("Forbidden", logging.WARNING,
                        response_status=403)
        """
        logger.log(
            level=level,
            msg=message,
            extra={"request_id": self.request_id,
                   "action": self.action,
                   **kwargs}
        )
        return None

    def _process_success(self) -> str:
        """
        Обрабатывает ответ YandexCloudAPI.

        Returns:
            str. Возвращает классифицированное значение или
            default в случае ошибки
        """
        sorted_predictions = sorted(self.data['predictions'],
                                    key=lambda x: x["confidence"],
                                    reverse=True)
        if sorted_predictions[0]["label"] in self.choices:
            result = sorted_predictions[0]["label"]
            self._log(f"Classifying succeeded. "
                      f"Returned '{result}'",
                      logging.DEBUG)
            return result
        else:
            self._log(f"Classifying failed. "
                      f"Returned '{self.default_value}'",
                      logging.DEBUG)
            return self.default_value

    def _process_error(self, status_code: int) -> bool:
        """
        Обрабатывает неуспешные коды ошибок от YandexCloudAPI.

        Args:
            status_code (int): код, который вернул YandexCloudAPI.

        Returns:
            Bool. True если необходимо выполнить ещё одну попытку
            запроса. False если нет необходимости
        """
        need_retry = False
        log_params = {
            "level": logging.ERROR,
            "message": self.data.get("message")
        }

        if self.last_error:
            log_params["last_error"] = str(self.last_error)
        if status_code == 400:
            if log_params.get("message") is None:
                log_params["message"] = "Invalid data"
        elif status_code == 401:
            if log_params.get("message") is None:
                log_params["message"] = "Invalid IAM token"
            need_retry = True
        elif status_code == 403:
            if log_params.get("message") is None:
                log_params["message"] = (f"Access to catalog id "
                                         f"{YA_CLOUD_CATALOG_ID} "
                                         f"forbidden")
        elif status_code == 404:
            log_params["level"] = logging.CRITICAL
            if log_params.get("message") is None:
                log_params["message"] = "Error in URL or model"
        elif status_code == 429:
            need_retry = True
        elif status_code == 500:
            if log_params.get("message") is None:
                log_params["message"] = "Failed to process request"
            need_retry = True

        self._log(**log_params)
        self.last_error = log_params["message"]
        return need_retry

    async def y_cloud_classify_text(self) -> str:
        """
        Выполняет HTTP-запрос к серверу YandexCloud с целью
        классификации текста на одну из категорий.

        Returns:
            str. Одно из значений, перечисленных в choices или default
        """
        async with (aiohttp.ClientSession() as session):
            for attempt in range(1, HTTP_CONNECTION_RETRIES + 1):
                try:
                    self._log(f"Attempt {attempt}/"
                              f"{HTTP_CONNECTION_RETRIES}")
                    yc_iam_token = await yc_token_manager.get_token()
                    if yc_iam_token is None:
                        continue
                    async with session.post(
                            url="https://llm.api.cloud.yandex.net/"
                                "foundationModels/v1/"
                                "fewShotTextClassification",
                            headers={
                                "Authorization": f'Bearer '
                                                 f'{yc_iam_token}',
                                "Content-Type": "application/json"
                            },
                            json={
                                "modelUri": f"cls://"
                                            f"{YA_CLOUD_CATALOG_ID}/"
                                            f"yandexgpt-lite/latest",
                                "taskDescription": self.task_description,
                                "labels": self.choices,
                                "text": self.input_text
                            },
                            timeout=aiohttp.ClientTimeout(
                                total=HTTP_CONNECTION_TIMEOUT
                            )
                    ) as response:
                        self.data = await response.json()
                        self._log("Request succeeded",
                                  logging.DEBUG,
                                  status=response.status,
                                  response_size=len(str(self.data)))
                        if (response.status == 200 and
                                self.data.get("predictions") is not None and
                                self.data["predictions"]):
                            return self._process_success()
                        if self._process_error(response.status):
                            if attempt < HTTP_CONNECTION_RETRIES:
                                await asyncio.sleep(
                                    HTTP_CONNECTION_RETRY_DELAY *
                                    attempt
                                )
                            continue
                        return self.default_value

                except aiohttp.ClientError as e:
                    self.last_error = e
                    self._log(f"Request failed "
                              f"(attempt {attempt}): {str(e)}",
                              logging.WARNING,
                              error_type=type(e).__name__)
                    if attempt < HTTP_CONNECTION_RETRIES:
                        await asyncio.sleep(
                            HTTP_CONNECTION_RETRY_DELAY * attempt
                        )
                    continue

                except asyncio.TimeoutError:
                    self.last_error = "Timeout exceeded"
                    self._log("Timeout exceeded",
                              logging.ERROR,
                              timeout=HTTP_CONNECTION_RETRY_DELAY * attempt)
                    if attempt < HTTP_CONNECTION_RETRIES:
                        await asyncio.sleep(
                            HTTP_CONNECTION_RETRY_DELAY * attempt
                        )
                    continue

                except Exception as e:
                    self._log(
                        message="Unexpected error. Returned default value",
                        level=logging.ERROR,
                        error=str(e),
                        error_type=type(e).__name__,
                        traceback=True
                    )
                    return self.default_value

            self._log(f"Max retries "
                      f"({HTTP_CONNECTION_RETRIES}) exceeded. "
                      f"Last error: {str(self.last_error)}. "
                      f"Returned default value",
                      logging.WARNING)
            return self.default_value


yc_token_manager = YCTokenManager()
