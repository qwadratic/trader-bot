from models.db_models import UserSet

new_user_txt = 'Hello!\n' \
                'choose a language\n\n' \
                'Привет!!\n' \
                'Выбери язык'


def choice_currency_txt(user_id):
    lang = UserSet.get_by_id(user_id)

    if lang == 1:
        txt = 'Отлично!\n' \
              'С какой валютой работаем?'

    else:
        txt = 'Отлично!\n' \
              'С какой валютой работаем?'

    return txt


end_reg_txt = 'Поздравляю!\n' \
              'Регистрация окончена, язык и валюту можно изменить в настройках\n' \
              '*какой-то еще текст*'
