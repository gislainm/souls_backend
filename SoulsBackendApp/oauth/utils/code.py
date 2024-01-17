import secrets
import string

# characters to be used to randomly generate a oauth code
OAUTH_CODE_CHARS = string.ascii_uppercase + string.digits


def generate_oauth_code(len=8):
    return "".join(secrets.choice(OAUTH_CODE_CHARS) for _i in range(len))
