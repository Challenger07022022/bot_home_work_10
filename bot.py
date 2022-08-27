from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, Filters, MessageHandler, ConversationHandler
import sqlite3 as dbe
import os.path
import logging


def open_data_base():
    try:
        if os.path.exists('db.db'):
            return dbe.connect('db.db')
        else:
            raise
    except:
        db = dbe.connect('db.db')
        cur = db.cursor()
        cur.execute(
            'CREATE TABLE departments (id INTEGER PRIMARY KEY AUTOINCREMENT, department text NOT NULL)')
        cur.execute(
            'CREATE TABLE positions (id INTEGER PRIMARY KEY AUTOINCREMENT, position text NOT NULL);')
        cur.execute('''CREATE TABLE staffs (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                             name text NOT NULL,
                                             tel  text  NOT NULL,
                                             department INTEGER NOT NULL REFERENCES departments (id),
                                             position   INTEGER NOT NULL REFERENCES positions (id));''')
        db.commit()
        return db


def save_data_base(database: dbe.Connection):
    database.commit()


def close_data_base(database: dbe.Connection):
    database.close()


def get_departmentid(database: dbe.Connection, department: str):
    cur = database.cursor()
    cur.execute(
        f'SELECT id FROM departments WHERE department = "{department}";')
    result = cur.fetchall()
    if len(result) != 0:
        return result[0][0]
    else:
        return None


def add_department(database: dbe.Connection, department: str):
    departmentid = get_departmentid(database, department)
    if departmentid is None:
        cur = database.cursor()
        cur.execute(
            f'INSERT INTO departments (department) VALUES("{department}");')
    departmentid = get_departmentid(database, department)
    return departmentid


def get_all_departments(database):
    cur = database.cursor()
    cur.execute('SELECT * FROM departments;')
    result = cur.fetchall()
    return result


def get_positionstid(database: dbe.Connection, position: str):
    cur = database.cursor()
    cur.execute(
        f'SELECT id FROM positions WHERE position = "{position}";')
    result = cur.fetchall()
    if len(result) != 0:
        return result[0][0]
    else:
        return None


def add_position(database: dbe.Connection, position: str):
    positionid = get_positionstid(database, position)
    if positionid is None:
        cur = database.cursor()
        cur.execute(
            f'INSERT INTO positions (position) VALUES("{position}");')
    positionid = get_positionstid(database, position)
    return positionid


def get_all_positions(database):
    cur = database.cursor()
    cur.execute('SELECT * FROM positions;')
    result = cur.fetchall()
    return result


def add_person(database: dbe.Connection, name: str, tel: str, department: str, position: str):
    departmentid = add_department(database, department)
    positionid = add_position(database, position)
    cur = database.cursor()
    cur.execute(f'''INSERT INTO staffs
                    (name, tel, department, position) 
                    VALUES('{name}', '{tel}', {departmentid}, {positionid});''')


def get_person(database: dbe.Connection, id: int):
    cur = database.cursor()
    cur.execute(f'''SELECT staffs.id, staffs.name, staffs.tel, departments.department, positions.position
                    FROM  staffs
                    LEFT JOIN departments ON staffs.department=departments.id
                    LEFT JOIN positions ON staffs.position=positions.id
                    WHERE staffs.id={id};
                 ''')
    result = cur.fetchall()
    return result[0] if len(result) != 0 else None


def get_all_staffs(database: dbe.Connection):
    cur = database.cursor()
    cur.execute(f'''SELECT staffs.id, staffs.name, staffs.tel, departments.department, positions.position
                    FROM  staffs
                    LEFT JOIN departments ON staffs.department=departments.id
                    LEFT JOIN positions ON staffs.position=positions.id;
                 ''')
    result = cur.fetchall()
    return result


def get_filter_person(database: dbe.Connection, search: str):
    data = get_all_staffs(database)
    result = [item for item in data if search in search.lower()
              in item[1].lower()]
    return result


def remove_person(database: dbe.Connection, id: int):
    cur = database.cursor()
    cur.execute(f'DELETE FROM staffs WHERE id={id};')


def main() -> None:
    updater = Updater('5564454006:AAHONt2C53lVkF2Q1qw_iEc2_LnOqmVhihw')

    # добавление обработчиков
    updater.dispatcher.add_handler(conv_handler)
    updater.dispatcher.add_handler(MessageHandler(Filters.command, unknown))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, text))

    # Запуск бота
    print('server start')
    updater.start_polling()
    updater.idle()


db = None
new_name = ''
new_tel = ''
new_department = ''
new_position = ''
id = 0


SELECT, input_name, input_tel, INPUTDEP, INPUTPOS, INPUTFILTER, input_id, CONFIRMREM = range(
    8)


def send_menu(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Выберите действие:\n'
        '/show_all - Показать все записи\n'
        '/add - Добавить запись\n'
        '/remove - Удалить запись\n'
        '/save - сохранить изменения\n'
        '/exit - завершить работу'
    )


def start(update: Update, context: CallbackContext) -> int:
    global db
    user = update.message.from_user
    logger.info(f'Пользователь {user.full_name} начал работу с базой')
    db = open_data_base()
    send_menu(update, context)
    return SELECT


def show_all(update: Update, context: CallbackContext) -> int:
    global db
    user = update.message.from_user
    logger.info(f'Пользователь {user.full_name} выбрал просмотр всей базы')
    data = get_all_staffs(db)
    message = "\n".join(
        [f"{item[0]}, {item[1]}, {item[2]}, {item[3]}, {item[4]}" for item in data])
    update.message.reply_text(message)
    send_menu(update, context)
    return SELECT


def add_item(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info(f'Пользователь {user.full_name} выбрал добавление записи')
    update.message.reply_text('Введите имя сотрудника или /cancel для отмены.')
    return input_name


def input_name(update: Update, context: CallbackContext) -> int:
    global new_name
    user = update.message.from_user
    text = update.message.text
    logger.info(f'Пользователь {user.full_name} ввел имя сотрудника "{text}"')
    new_name = text
    update.message.reply_text(
        'Введите телефон сотрудника или /cancel для отмены.')
    return input_tel


def input_tel(update: Update, context: CallbackContext) -> int:
    global new_tel
    user = update.message.from_user
    text = update.message.text
    logger.info(
        f'Пользователь {user.full_name} ввел телефон сотрудника "{text}"')
    new_tel = text
    update.message.reply_text(
        'Введите название отдела или /cancel для отмены.')
    return INPUTDEP


def input_department(update: Update, context: CallbackContext) -> int:
    global new_department
    user = update.message.from_user
    text = update.message.text
    logger.info(
        f'Пользователь {user.full_name} ввел название отдела "{text}"')
    new_department = text
    update.message.reply_text(
        'Введите должность сотрудника или /cancel для отмены.')
    return INPUTPOS


def input_position(update: Update, context: CallbackContext) -> int:
    global new_name, new_tel, new_department, new_position, db
    user = update.message.from_user
    text = update.message.text
    logger.info(
        f'Пользователь {user.full_name} ввел должность сотрудника "{text}"')
    new_position = text
    add_person(db, new_name, new_tel, new_department, new_position)
    logger.info(
        f'Пользователь {user.full_name} добавил нового сотрудника "{new_name}, {new_tel}, {new_department}, {new_position}"')
    new_name, new_tel, new_department, new_position = ('', '', '', '')
    send_menu(update, context)
    return SELECT


def cancel_add(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info(
        f'Пользователь {user.full_name} отменил добавление новой записи')
    send_menu(update, context)
    return SELECT


def remove_item(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info(f'Пользователь {user.full_name} выбрал удаление записи')
    update.message.reply_text(
        'Введите id сотрудника для удаления или /cancel для отмены.')
    return input_id


def input_id(update: Update, context: CallbackContext) -> int:
    global id
    user = update.message.from_user
    text = update.message.text
    logger.info(
        f'Пользователь {user.full_name} ввел id сотрудника для удаления "{text}"')
    try:
        id = int(text)
        person = get_person(db, id)
        if person == None:
            raise
    except:
        update.message.reply_text(
            'Вы ввели не верный id.\nВведите id сотрудника для удаления или /cancel для отмены.')
        return input_id
    update.message.reply_text('Вы хотите удалить сотрудника?\n\n'
                              f'{person[0]}, {person[1]}, {person[2]}, {person[3]}, {person[4]}\n\n'
                              'Введите /delete для подтвержденияили или /cancel для отмены')
    return CONFIRMREM


def confirm_remove(update: Update, context: CallbackContext) -> int:
    global db, id
    user = update.message.from_user
    logger.info(
        f'Пользователь {user.full_name} подтвердил удаление записи с id = {id}')
    remove_person(db, id)
    send_menu(update, context)
    return SELECT


def cancel_remove(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info(
        f'Пользователь {user.full_name} отменил удаление записи')
    send_menu(update, context)
    return SELECT


def save_db(update: Update, context: CallbackContext) -> int:
    save_data_base(db)
    user = update.message.from_user
    logger.info(f'Пользователь {user.full_name} сохранил базу')
    send_menu(update, context)
    return SELECT


def exit(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info(f'Пользователь {user.full_name} завершил работу с базой')
    update.message.reply_text('Работа завершена')
    return ConversationHandler.END


def text(update, context):
    user = update.message.from_user
    text_received = update.message.text
    logger.info(
        f'Пользователь {user.full_name} ввел сообщение "{update.message.text}"')


def unknown(update, context):
    user = update.message.from_user
    logger.info(
        f'Пользователь {user.full_name} ввел не обработанную комаду "{update.message.text}"')


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        SELECT: [CommandHandler('show_all', show_all),
                 CommandHandler('add', add_item),
                 CommandHandler('remove', remove_item),
                 CommandHandler('save', save_db)
                 ],

        # добавление состояний
        input_name: [MessageHandler(Filters.text & ~Filters.command, input_name),
                     CommandHandler('cancel', cancel_add)],
        input_tel: [MessageHandler(Filters.text & ~Filters.command, input_tel),
                    CommandHandler('cancel', cancel_add)],
        INPUTDEP: [MessageHandler(Filters.text & ~Filters.command, input_department),
                   CommandHandler('cancel', cancel_add)],
        INPUTPOS: [MessageHandler(Filters.text & ~Filters.command, input_position),
                   CommandHandler('cancel', cancel_add)],

        # закрытие состояний
        input_id: [MessageHandler(Filters.text & ~Filters.command, input_id),
                   CommandHandler('cancel', cancel_remove)],
        CONFIRMREM: [CommandHandler('delete', confirm_remove),
                     CommandHandler('cancel', cancel_remove)]
    },
    fallbacks=[CommandHandler('exit', exit)],
)

if __name__ == '__main__':
    main()