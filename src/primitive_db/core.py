from src.primitive_db.constants import ID_COLUMN, VALID_TYPES
from src.primitive_db.utils import save_table_data


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
    save_table_data(table_name, [])
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


def table_exists(metadata, table_name):
    """Проверяет, что таблица есть. Если нет, печатает ошибку."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return False
    return True


def get_column_types(metadata, table_name):
    """Возвращает словарь {имя столбца: тип} для таблицы."""
    column_types = {}
    for column in metadata[table_name]:
        name, column_type = column.split(":")
        column_types[name] = column_type
    return column_types


def check_clause(metadata, table_name, clause):
    """Проверяет, что столбцы из условия есть в таблице и значения нужного типа."""
    column_types = get_column_types(metadata, table_name)
    for name, value in clause.items():
        if name not in column_types:
            print(f'Ошибка: Столбца "{name}" нет в таблице "{table_name}".')
            return False
        if type(value).__name__ != column_types[name]:
            print(f"Некорректное значение: {value}. Попробуйте снова.")
            return False
    return True


def matches(record, where_clause):
    """Проверяет, подходит ли запись под условие."""
    for name, value in where_clause.items():
        if record[name] != value:
            return False
    return True


def insert(metadata, table_name, values, table_data):
    """Добавляет новую запись в таблицу и сама назначает ей ID."""
    column_types = get_column_types(metadata, table_name)
    del column_types["ID"]
    if len(values) != len(column_types):
        print(f"Ошибка: Нужно {len(column_types)} значений, введено {len(values)}.")
        return table_data
    new_id = 1
    for record in table_data:
        if record["ID"] >= new_id:
            new_id = record["ID"] + 1
    new_record = {"ID": new_id}
    for name, value in zip(column_types, values):
        if type(value).__name__ != column_types[name]:
            print(f"Некорректное значение: {value}. Попробуйте снова.")
            return table_data
        new_record[name] = value
    table_data.append(new_record)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data


def select(table_data, where_clause=None):
    """Возвращает все записи или только те, что подходят под условие."""
    if where_clause is None:
        return table_data
    result = []
    for record in table_data:
        if matches(record, where_clause):
            result.append(record)
    return result


def update(table_name, table_data, set_clause, where_clause):
    """Меняет поля у записей, которые подходят под условие."""
    if "ID" in set_clause:
        print("Ошибка: Столбец ID менять нельзя.")
        return table_data
    found = False
    for record in table_data:
        if matches(record, where_clause):
            record.update(set_clause)
            record_id = record["ID"]
            print(
                f'Запись с ID={record_id} в таблице "{table_name}" успешно обновлена.'
            )
            found = True
    if not found:
        print("Записи по условию не найдены.")
    return table_data


def delete(table_name, table_data, where_clause):
    """Удаляет записи, которые подходят под условие."""
    result = []
    for record in table_data:
        if matches(record, where_clause):
            record_id = record["ID"]
            print(
                f'Запись с ID={record_id} успешно удалена из таблицы "{table_name}".'
            )
        else:
            result.append(record)
    if len(result) == len(table_data):
        print("Записи по условию не найдены.")
    return result


def info(metadata, table_name, table_data):
    """Печатает описание таблицы и количество записей."""
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {', '.join(metadata[table_name])}")
    print(f"Количество записей: {len(table_data)}")