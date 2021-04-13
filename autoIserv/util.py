import requests


def download_file_from_iserv(driver, download_url):
    cookies = driver.get_cookies()
    real_cookies = dict()
    for cookie in cookies:
        if cookie["secure"] == True or (not cookie["secure"] and not cookie["httpOnly"]):
            real_cookies[cookie["name"]] = cookie["value"]

    result = requests.get(download_url, cookies=real_cookies, allow_redirects=True)
    try:
        filename = result.headers.get("Content-Disposition").split(";")[1].split("=")[-1]
        if filename:
            return filename, result.content
    except:
        return None, None