from requests_html import HTMLSession
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

session = HTMLSession()

BASE_URL = "http://www.proveyourworth.net/level3/"
ACTIVATE_URL = BASE_URL + "activate?statefulhash"
CV_DATA = {
    "name": "Javier Cardenas",
    "email": "javierjcardenas@gmail.com",
    "aboutme": "Full-stack developer with experience on Python and JavaScript. Backend: Django, DRF, Flask. Frontend: React, Vue",
    "resume": "javiercardenas.dev",
}


def find_statefulhash():
    """ get the hash inside the input element """
    r = session.get(BASE_URL)
    sel = 'input[name="statefulhash"]'
    statefulhash = r.html.find(sel, first=True).attrs["value"]
    return statefulhash


def get_payload_url(hash):
    """ get the payload from the custom header X-Payload-URL """
    r = session.get(ACTIVATE_URL + f"={hash}")
    payload_url = r.headers["X-Payload-URL"]
    return payload_url


def get_image_and_postback_url(url):
    """Download image from the payload url and get the post back url from the custom header X-Post-Back-To"""
    r = session.get(url, stream=True)
    i = Image.open(BytesIO(r.content))
    postback_url = r.headers["X-Post-Back-To"]
    return i, postback_url


def sign_save_image(im, text):
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype("impact.ttf", size=25)
    draw.text(
        (10, 10),
        text,
        fill="white",
        font=font,
        spacing=4,
        stroke_width=2,
        stroke_fill="black",
    )
    im.save("signed_image.jpg", "JPEG")


def post_back_data(url, data, files):
    cookie = session.cookies.get("PHPSESSID")
    cookies = {"PHPSESSID": cookie}
    request = session.post(url, data=data, files=files, cookies=cookies)
    print(request.status_code)
    print(request.text)


def run_code():
    stateful_hash = find_statefulhash()
    payload_url = get_payload_url(stateful_hash)
    image, postback_url = get_image_and_postback_url(payload_url)

    signature_text = (
        f"Name: {CV_DATA['name']}\nEmail: {CV_DATA['email']}\nHash: {stateful_hash}"
    )
    sign_save_image(image, signature_text)

    files = {
        "image": open("signed_image.jpg", "rb"),
        "code": open("pyw.py", "rb"),
        "resume": open("javier-cardenas-cv.pdf", "rb"),
    }

    post_back_data(postback_url, CV_DATA, files)


if __name__ == "__main__":
    run_code()
