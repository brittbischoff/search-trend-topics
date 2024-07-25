def get_topic_ids(keyword):
    suggestions = pytrends.suggestions(keyword)
    ids = []
    if suggestions:
        for suggestion in suggestions:
            ids.append(f"{suggestion['title']}: {suggestion['mid']}")
    return ids
