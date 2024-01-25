from settings.settings import BASE_DIR


def generate_gc_card_body(endpoint_name, error_type=None):
    imageUrl = "https://icons.iconarchive.com/icons/paomedia/small-n-flat/256/sign-warning-icon.png"
    gc_card = {
        "cardsV2": [
            {
                "cardId": "createCardMessage",
                "card": {
                    "header": {
                        "title": str(BASE_DIR).split("/", -1)[-1],
                        "subtitle": f"alert from {endpoint_name}",
                        "imageUrl": imageUrl,
                    },
                    "sections": [
                        {
                            "widgets": [
                                {"textParagraph": {"text": f"Error : {error_type}"}},
                                {
                                    "buttonList": {
                                        "buttons": [
                                            {
                                                "text": "Read the docs!",
                                                "onClick": {"openLink": {"url": "https://developers.google.com/chat"}},
                                            }
                                        ]
                                    }
                                },
                            ]
                        }
                    ],
                },
            }
        ]
    }
    return gc_card
