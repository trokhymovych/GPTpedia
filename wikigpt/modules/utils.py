def text_processing_base(text: str) -> str:
    """
    Method for internal basic text processing before vectorisation.
    """
    text = text.replace("===", " ")
    text = text.replace("==", " ")
    text = text.replace("\n", " ")
    return text
