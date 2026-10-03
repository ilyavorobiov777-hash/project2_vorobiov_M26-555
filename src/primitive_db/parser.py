def parse_value(text):
    """Превращает текст значения в str, bool или int."""
    text = text.strip()
    if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
        return text[1:-1]
    if text.lower() == "true":
        return True
    if text.lower() == "false":
        return False
    return int(text)


def parse_condition(text):
    """Превращает строку вида age = 28 в словарь {"age": 28}."""
    column, value = text.split("=", 1)
    return {column.strip(): parse_value(value)}


def parse_set(text):
    """Превращает строку вида age = 29, name = "Ivan" в словарь."""
    result = {}
    for part in text.split(","):
        result.update(parse_condition(part))
    return result


def parse_values(text):
    """Превращает строку вида ("Sergei", 28, true) в список значений."""
    text = text.strip()
    if text.startswith("(") and text.endswith(")"):
        text = text[1:-1]
    values = []
    for part in text.split(","):
        values.append(parse_value(part))
    return values