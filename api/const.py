ENDPOINT = "https://uportal.livre.cgi.com/uPortal2/gaia"
LOGIN_PATH = "/login"
SUBSCRIPTIONS_PATH = "/Subscription/listSubscriptions"
LASTDOC_PATH = "/Billing/getDadosUltimoDocumento"
LASTDOC_PATH_PARAM = "subscriptionId"

JSON_CONTENT = "application/json"

DEFAULT_HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"
}

USER_PARAM = "username"
PWD_PARAM = "password"