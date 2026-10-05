import shlex

import prompt
from prettytable import PrettyTable

from src.primitive_db.constants import META_FILE
from src.primitive_db.core import (
    check_clause,
    create_table,
    delete,
    drop_table,
    info,
    insert,
    list_tables,
    select,
    table_exists,
    update,
)
from src.primitive_db.decorators import handle_db_errors
from src.primitive_db.parser import parse_condition, parse_set, parse_values
from src.primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help():
    """Prints the help message for the current mode."""

    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\n***Операции с данными***")
    print("Функции:")
    print("<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) - создать запись.")  # noqa: E501
    print("<command> select from <имя_таблицы> where <столбец> = <значение> - прочитать записи по условию.")  # noqa: E501
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print("<command> update <имя_таблицы> set <столбец1> = <новое_значение1> where <столбец_условия> = <значение_условия> - обновить запись.")  # noqa: E501
    print("<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить запись.")  # noqa: E501
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def print_records(metadata, table_name, records):
    """Печатает записи в виде таблицы через prettytable."""
    names = []
    for column in metadata[table_name]:
        names.append(column.split(":")[0])
    table = PrettyTable()
    table.field_names = names
    for record in records:
        row = []
        for name in names:
            row.append(record[name])
        table.add_row(row)
    print(table)


def handle_insert(metadata, user_input, args):
    """Разбирает и выполняет команду insert."""
    if len(args) < 5 or args[1] != "into" or args[3] != "values":
        print(f"Некорректное значение: {user_input}. Попробуйте снова.")
        return
    table_name = args[2]
    if not table_exists(metadata, table_name):
        return
    values = parse_values(user_input.split(" values ", 1)[1])
    table_data = load_table_data(table_name)
    table_data = insert(metadata, table_name, values, table_data)
    if table_data is not None:
        save_table_data(table_name, table_data)


def handle_select(metadata, user_input, args):
    """Разбирает и выполняет команду select."""
    if len(args) < 3 or args[1] != "from":
        print(f"Некорректное значение: {user_input}. Попробуйте снова.")
        return
    table_name = args[2]
    if not table_exists(metadata, table_name):
        return
    where_clause = None
    if len(args) > 3:
        if args[3] != "where":
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            return
        where_clause = parse_condition(user_input.split(" where ", 1)[1])
        if not check_clause(metadata, table_name, where_clause):
            return
    table_data = load_table_data(table_name)
    records = select(table_data, where_clause)
    if records is not None:
        print_records(metadata, table_name, records)


def handle_update(metadata, user_input, args):
    """Разбирает и выполняет команду update."""
    if len(args) < 4 or args[2] != "set" or " where " not in user_input:
        print(f"Некорректное значение: {user_input}. Попробуйте снова.")
        return
    table_name = args[1]
    if not table_exists(metadata, table_name):
        return
    set_text, where_text = user_input.split(" set ", 1)[1].split(" where ", 1)
    set_clause = parse_set(set_text)
    where_clause = parse_condition(where_text)
    if not check_clause(metadata, table_name, set_clause):
        return
    if not check_clause(metadata, table_name, where_clause):
        return
    table_data = load_table_data(table_name)
    table_data = update(table_name, table_data, set_clause, where_clause)
    if table_data is not None:
        save_table_data(table_name, table_data)


def handle_delete(metadata, user_input, args):
    """Разбирает и выполняет команду delete."""
    if len(args) < 5 or args[1] != "from" or args[3] != "where":
        print(f"Некорректное значение: {user_input}. Попробуйте снова.")
        return
    table_name = args[2]
    if not table_exists(metadata, table_name):
        return
    where_clause = parse_condition(user_input.split(" where ", 1)[1])
    if not check_clause(metadata, table_name, where_clause):
        return
    table_data = load_table_data(table_name)
    table_data = delete(table_name, table_data, where_clause)
    if table_data is not None:
        save_table_data(table_name, table_data)


def handle_info(metadata, user_input, args):
    """Разбирает и выполняет команду info."""
    if len(args) != 2:
        print(f"Некорректное значение: {user_input}. Попробуйте снова.")
        return
    table_name = args[1]
    if not table_exists(metadata, table_name):
        return
    table_data = load_table_data(table_name)
    info(metadata, table_name, table_data)


@handle_db_errors
def execute_command(metadata, user_input):
    """Разбирает введенную команду и вызывает нужную функцию."""
    args = shlex.split(user_input)
    if not args:
        return
    command = args[0]
    if command == "help":
        print_help()
    elif command == "list_tables":
        list_tables(metadata)
    elif command == "create_table":
        if len(args) < 3:
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            return
        new_metadata = create_table(metadata, args[1], args[2:])
        if new_metadata is not None:
            save_metadata(META_FILE, new_metadata)
    elif command == "drop_table":
        if len(args) != 2:
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            return
        new_metadata = drop_table(metadata, args[1])
        if new_metadata is not None:
            save_metadata(META_FILE, new_metadata)
    elif command == "insert":
        handle_insert(metadata, user_input, args)
    elif command == "select":
        handle_select(metadata, user_input, args)
    elif command == "update":
        handle_update(metadata, user_input, args)
    elif command == "delete":
        handle_delete(metadata, user_input, args)
    elif command == "info":
        handle_info(metadata, user_input, args)
    else:
        print(f"Функции {command} нет. Попробуйте снова.")


def run():
    """Запускает основной цикл программы."""
    print_help()
    while True:
        metadata = load_metadata(META_FILE)
        user_input = prompt.string(">>>Введите команду: ")
        if user_input.strip() == "exit":
            break
        execute_command(metadata, user_input)