from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


# helper function that sends email
def post_message(message):
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
    except Exception as e:
        print(e.message)


def test_email(name: str, oauth_code: str, record_link: str) -> None:
    # {
    #     "leader_name": "Ben Carey",
    #     "oauth_code": "RFH203LW",
    #     "record_link": "www.google.com",
    # }

    #  message = Mail(from_email="admin@seatstock.app", to_emails=email)

    #     message.template_id = "d-3e031183ed854fe391d3c1ad10304980"
    #     message.dynamic_template_data = {"TWO_FACTOR_CODE": code}
    message = Mail(
        from_email="ignitesouls.web@gmail.com",
        to_emails="gmuhikira2@gmail.com",
        # subject="Sendgrid API - Test",
        # html_content=f"<strong>An Oauth Code was generated for a user successfully</strong><br>user-emai: {user_email}, oauth_code:{oauth_code}",
    )
    message.template_id = "d-2089b7a654384bb093ca1fed3f11e5de"
    message.dynamic_template_data = {
        "leader_name": name,
        "oauth_code": oauth_code,
        "record_link": record_link,
    }
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        print("Status-Code: ", response.status_code)
        print("Body: ", response.body)
        print("Header: ", response.headers)
    except Exception as e:
        print(e.message)


# This function will send an email to the group leader with an authorization code and  a link to save weekly attendance
def send_email_to_group_leader(
    email: str, name: str, oauth_code: str, record_link: str
) -> None:
    message = Mail(
        from_email="ignitesouls.web@gmail.com",
        to_emails=email,
    )
    message.template_id = "d-2089b7a654384bb093ca1fed3f11e5de"
    message.dynamic_template_data = {
        "leader_name": name,
        "oauth_code": oauth_code,
        "record_link": record_link,
    }
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        print("Status-Code: ", response.status_code)
        print("Body: ", response.body)
        print("Header: ", response.headers)
    except Exception as e:
        print(e.message)
