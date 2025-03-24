from api.models import FlouciApp


def user_exists_by_tracking_id(tracking_id):
    """
    Check if a user exists in the FlouciApp model by tracking_id.

    Args:
        tracking_id (str): The tracking ID to filter by.

    Returns:
        bool: True if the user exists, False otherwise.
    """
    return FlouciApp.objects.filter(tracking_id=tracking_id).exists()
