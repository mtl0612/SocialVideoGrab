from w3lib.html import remove_tags

def remove_html_tag(content):
    text_cleaned = remove_tags(content, keep = ("br",))
    text_cleaned = text_cleaned.replace("<br> ","\n")
    return text_cleaned