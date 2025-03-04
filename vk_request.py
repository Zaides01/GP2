import requests
import logging

logger_requests = logging.getLogger(__name__)
logger_requests.setLevel(logging.INFO)

handler_requests = logging.FileHandler(f"{__name__}.log", mode='w')
formatter_requests = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

handler_requests.setFormatter(formatter_requests)
logger_requests.addHandler(handler_requests)

logger_requests.info(f"Логирование {__name__}...")


VERSION = "5.199"
BASE_URL = "https://api.vk.com/method/"
ACCESS_TOKEN = "vk1.a.dX_jqJVnS3YBG4xVsKBPHLTYi5T3gLRXusvJUCHSmFnabRSvLVKPpvUqtMPxwMvwk7sifVNK3VzJfNOr-IOBpxLOSmoe0_COertbeFp87NaG07dUZ4wEhg-nbJ62Cd5tPtxAH3LppDBsb_94-FF2Nd-UmWnK1wrInMqydUBNihn94DYkVCcsE1JhaGgffz4FGtPme0BvYOaHrrDFKHZOnw"


def vk_request(method, params):
    url = f"{BASE_URL}{method}"
    params.update(
        {
            "access_token": ACCESS_TOKEN, 
            "v"           : VERSION,
        }
    )
    response = requests.get(url, params=params).json()
    if "error" in response:
        logger_requests.error(f"Ошибка: {response['error']['error_msg']}")
        return None
    return response.get("response", {})