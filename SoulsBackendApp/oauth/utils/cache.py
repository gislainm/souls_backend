from django.core.cache import cache


def store_oauth_code(email: str, code: str, valid_for: int):
    """
    store group leader oauth code in db_cache to be used to authenticate t
    he group leader before the could add a member in the group or save the a
    ttendance of the group in the database.
    """
    cache.set(f"{email}.oauth", code, valid_for)


def test_oauth_code(email: str, test_code: str) -> bool:
    """
    checks whether test_code provided by user matches code associated with the 
    user's email in cache. This function fails safely and only returns true if code is valid.

    Parameters:
        (str) email: User email associated with code.
        (str) code: user provided code to test for match.

    Returns:
        (bool) Whether or not code matches cached code.
    """
    return __get_oauth_code(email) == test_code


def __get_oauth_code(email: str):
    return cache.get(f"{email}.oauth")


def delete_oauth_code(email: str):
    """
    Deletes group leader login code after the code was used to authenticate user once.
    """
    cache.delete(f"{email}.oauth")
