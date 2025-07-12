import asyncio
import logging
from typing import Any, Dict
from uuid import uuid4

import aiohttp

from settings import (DADATA_API_KEY,
                      HTTP_CONNECTION_RETRIES,
                      HTTP_CONNECTION_RETRY_DELAY,
                      HTTP_CONNECTION_TIMEOUT)

logger = logging.getLogger("app")


async def get_geo_by_ip(ip: str) -> Dict[str, str]:
    """
    Обрабатывает IP-адрес запроса на сервиса DaData.

    Args:
        ip (str): IP адрес для обработки.

    Returns:
        {
            "country": (str) страна на русском языке или "UNKNOWN"
                в случае ошибки,
            "city": (str) город на русском языке или "UNKNOWN" в случае ошибки,
        }
    """

    def validate_ip() -> str:
        """
        Валидирует IP адрес на соответствие всем стандартам.

        Raises:
            ValueError: Если ip адрес None или не соответствует стандартам.

        Returns:
            str. "localhost" в случае, если IP-адрес 127.0.0.1 или
            "ok" в случае прохождения валидации
        """
        if ip is None:
            raise ValueError("IP cannot be None")
        if ip == "127.0.0.1":
            return "localhost"
        if len(ip) > 15:
            raise ValueError("IP should not exceed 15 characters")
        split_ip = [int(digit) for digit in ip.split(".")]
        if len(split_ip) != 4:
            raise ValueError("IP should have 4 digits")
        for digit in split_ip:
            if digit < 0 or digit > 255:
                raise ValueError("IP digit will be between 0 and 255")
        return "ok"

    def process_error_code(status_code: int) -> Dict[str, bool | str | Any]:
        """
        Обрабатывает неуспешные коды ошибок от DaData.

        Args:
            status_code (int): код, который вернул DaData.

        Returns:
            {
            "need_retry": Необходимость повторной попытки запроса,
            "last_error": Ошибка из ответа сервера,
            }
        """
        need_retry = False
        log_params = {
            "message": data.get("message")
        }
        if status_code == 400:
            if log_params.get("message") is None:
                log_params["message"] = "Invalid IP address"
        elif status_code == 401:
            if log_params.get("message") is None:
                log_params["message"] = "API key is missing or invalid"
            need_retry = True
        elif status_code == 403:
            if log_params.get("message") is None:
                log_params["message"] = "Request limit exceeded"
        elif status_code == 404:
            if log_params.get("message") is None:
                log_params["message"] = "IP not found"
        elif status_code == 429:
            need_retry = True
        elif status_code == 500:
            if log_params.get("message") is None:
                log_params["message"] = "Failed to process request"
            need_retry = True

        logger.error(
            msg="Request failed",
            extra=log_params)
        return {
            "need_retry": need_retry,
            "last_error": log_params["message"],
        }

    if validate_ip() == "localhost":
        return {
            "country": "LOCALHOST",
            "city": "LOCALHOST"
        }
    request_id = str(uuid4())
    last_error: Exception | str | None = None

    async with (aiohttp.ClientSession() as session):
        for attempt in range(1, HTTP_CONNECTION_RETRIES + 1):
            try:
                logger.info(
                    msg=f"Attempt {attempt}/"
                        f"{HTTP_CONNECTION_RETRIES}",
                    extra={"request_id": request_id,
                           "action": "geo_by_ip"}
                )
                async with session.post(
                        url="https://suggestions.dadata.ru/suggestions/"
                            "api/4_1/rs/iplocate/address",
                        headers={
                            "Authorization": f'Token {DADATA_API_KEY}',
                            "Content-Type": "application/json",
                            "Accept": "application/json",
                        },
                        json={
                            "ip": ip,
                            "language": "ru"
                        },
                        timeout=aiohttp.ClientTimeout(
                            total=HTTP_CONNECTION_TIMEOUT
                        )
                ) as response:
                    data = await response.json()
                    logger.debug(
                        msg="Request succeeded",
                        extra={"request_id": request_id,
                               "action": "geo_by_ip",
                               "status": response.status,
                               "response_size": len(str(data))})

                    if (response.status == 200 and
                            data.get("location") is not None and
                            data.get("location").get("data") is not None):
                        logger.debug(
                            msg="The location is defined",
                            extra={"request_id": request_id,
                                   "action": "geo_by_ip"}
                        )
                        return {
                            "country": data["location"]["data"]
                            .get("country", "UNKNOWN"),
                            "city": data["location"]["data"]
                            .get("city", "UNKNOWN"),
                        }

                    err_processing = process_error_code(response.status)
                    last_error = err_processing["last_error"]
                    if err_processing["need_retry"]:
                        if attempt < HTTP_CONNECTION_RETRIES:
                            await asyncio.sleep(
                                HTTP_CONNECTION_RETRY_DELAY *
                                attempt
                            )
                        continue
                    return {
                        "country": "UNKNOWN",
                        "city": "UNKNOWN",
                    }

            except aiohttp.ClientError as e:
                last_error = e
                logger.warning(
                    msg=f"Request failed (attempt {attempt}): {str(e)}",
                    extra={"request_id": request_id,
                           "action": "geo_by_ip",
                           "error_type": type(e).__name__}
                )
                if attempt < HTTP_CONNECTION_RETRIES:
                    await asyncio.sleep(
                        HTTP_CONNECTION_RETRY_DELAY * attempt
                    )
                continue

            except asyncio.TimeoutError:
                last_error = "Timeout exceeded"
                logger.warning(
                    msg=f"Request failed (attempt {attempt}): Timeout",
                    extra={"request_id": request_id,
                           "action": "geo_by_ip",
                           "timeout": HTTP_CONNECTION_RETRY_DELAY * attempt}
                )
                if attempt < HTTP_CONNECTION_RETRIES:
                    await asyncio.sleep(
                        HTTP_CONNECTION_RETRY_DELAY * attempt
                    )
                continue

            except Exception as e:
                logger.error(
                    msg="Unexpected error. Returned None",
                    extra={"request_id": request_id,
                           "action": "geo_by_ip",
                           "error": str(e),
                           "error_type": type(e).__name__,
                           "traceback": True}
                )
                return {
                    "country": "UNKNOWN",
                    "city": "UNKNOWN",
                }
        logger.warning(msg=f"Max retries "
                           f"({HTTP_CONNECTION_RETRIES}) exceeded. "
                           f"Last error: {str(last_error)}. "
                           f"Returned None",
                       extra={"request_id": request_id,
                              "action": "geo_by_ip"})
        return {
            "country": "UNKNOWN",
            "city": "UNKNOWN",
        }
