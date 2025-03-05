import requests
import logging

logger_requests = logging.getLogger("../logs/vk_request")
logger_requests.setLevel(logging.INFO)

handler_requests = logging.FileHandler("../logs/vk_request.log", mode='w')
formatter_requests = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

handler_requests.setFormatter(formatter_requests)
logger_requests.addHandler(handler_requests)

logger_requests.info(f"Логирование logs/vk_request...")


VERSION = "5.199"
BASE_URL = "https://api.vk.com/method/"
ACCESS_TOKEN = "vk1.a.8ooHSQLB8bJLsADO023KJLN_kLShLt7DWgu7U4K53LgTeEL-HRu6Tz5FPzuAF2LuL2xIc_E_2AWWKQ0qPMT6erVXrD8xL2OiQwoIvNMhfoSOUQLggwF_tA7M1DwVnOINodH5yO6jIqwJrmhsALBlfnxX3OmEOHx9UkXDc37xtI4AkT4xxfTAxUmpoCaH2kreXUoNyzj7WPOP1w8r_j4YVQ"


def vk_request(method, params):
    url = f"{BASE_URL}{method}"
    params.update(
        {
            "access_token": ACCESS_TOKEN, 
            "v"           : VERSION,
        }
    )
    response = requests.get(url, params=params).json()
    logger_requests.info(response)
    if "error" in response:
        logger_requests.error(f"Ошибка: {response['error']['error_msg']}")
        return None
    return response.get("response", {})