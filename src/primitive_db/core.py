from src.primitive_db.constants import ID_COLUMN, VALID_TYPES


def create_table(metadata, table_name, columns):
    """Создает таблицу и добавляет ее описание в метаданные."""
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata
    for column in columns:
        parts = column.split(":")
        if len(parts) != 2 or parts[1] not in VALID_TYPES:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return metadata
    metadata[table_name] = [ID_COLUMN] + columns
    columns_text = ", ".join(metadata[table_name])
    print(f'Таблица "{table_name}" успешно создана со столбцами: {columns_text}')
    return metadata


def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata
    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata):
    """Печатает список всех таблиц."""
    if not metadata:
        print("Таблиц пока нет.")
        return
    for table_name in metadata:
        print(f"- {table_name}")