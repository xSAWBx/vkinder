import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from config import community_token, access_token
from core import VkTools


class BotInterface:
    MISSING_INFO_MESSAGES = {
        'age': 'Извините, {name}, я не смог обработать ваше сообщение. Пожалуйста, введите информацию о возрасте в следующем формате:\n\nВозраст <возраст>',
        'gender': 'Извините, {name}, я не смог обработать ваше сообщение. Пожалуйста, введите информацию о поле в следующем формате:\n\nПол <мужской/женский>',
        'city': 'Извините, {name}, я не смог обработать ваше сообщение. Пожалуйста, введите информацию о городе в следующем формате:\n\nГород <город>',
        'relation': 'Извините, {name}, я не смог обработать ваше сообщение. Пожалуйста, введите информацию о семейном положении в следующем формате:\n\nСемейное положение <семейное положение>'
    }

    def __init__(self, community_token, access_token):
        self.vk = vk_api.VkApi(token=community_token)
        self.longpoll = VkLongPoll(self.vk)
        self.vk_tools = VkTools(access_token)
        self.params = {}
        self.worksheets = []
        self.offset = 0
        self.matches = {}

    def message_send(self, user_id, message, attachment=None, keyboard=None):
        self.vk.method('messages.send', {
            'user_id': user_id,
            'message': message,
            'attachment': attachment,
            'random_id': get_random_id(),
            'keyboard': keyboard
        })

    def process_search(self, event):
        if 'city' not in self.params:
            self.message_send(
                event.user_id,
                f'Для поиска анкет необходимо указать ваш город. Введите информацию о городе в следующем формате:\n\nГород <город>',
                keyboard=self.create_keyboard()
            )
            return

        if self.worksheets:
            worksheet = self.worksheets.pop()
            photos = self.vk_tools.get_photos(worksheet['id'])
            photo_string = ','.join([f'photo{photo["owner_id"]}_{photo["id"]}' for photo in photos])
            self.message_send(
                event.user_id,
                f'Имя: {worksheet["name"]} Ссылка: vk.com/{worksheet["id"]}',
                attachment=photo_string,
                keyboard=self.create_keyboard()
            )
            self.save_match(event.user_id, worksheet['id'])
        else:
            self.worksheets = self.vk_tools.search_worksheet(
                self.params, self.offset)
            while self.worksheets:
                worksheet = self.worksheets.pop()
                if not self.check_database(event.user_id, worksheet['id']):
                    break
            else:
                worksheet = None

            if worksheet:
                photos = self.vk_tools.get_photos(worksheet['id'])
                photo_string = ','.join([f'photo{photo["owner_id"]}_{photo["id"]}' for photo in photos])
                self.offset += 10
                self.message_send(
                    event.user_id,
                    f'Имя: {worksheet["name"]} Ссылка: vk.com/{worksheet["id"]}',
                    attachment=photo_string,
                    keyboard=self.create_keyboard()
                )
                self.save_match(event.user_id, worksheet['id'])
            else:
                self.message_send(event.user_id, 'Подходящих анкет не найдено')

    def check_database(self, user_id, worksheet_id):
        return self.get_match(user_id) == worksheet_id

    def get_match(self, user_id):
        return self.matches.get(user_id)

    def save_match(self, user_id, worksheet_id):
        self.matches[user_id] = worksheet_id

    def create_keyboard(self):
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('Следующая анкета', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Пока', color=VkKeyboardColor.NEGATIVE)
        return keyboard.get_keyboard()

    def process_user_info(self, event):
        if event.text.lower().startswith('возраст'):
            try:
                age = int(event.text.lower().split()[1])
                self.params['year'] = age
                self.message_send(
                    event.user_id,
                    'Спасибо, {}! Информация о возрасте обновлена.'.format(self.params["name"]),
                    keyboard=self.create_keyboard()
                )
            except (IndexError, ValueError):
                self.message_send(
                    event.user_id,
                    self.MISSING_INFO_MESSAGES['age'].format(name=self.params["name"]),
                    keyboard=self.create_keyboard()
                )
        elif event.text.lower().startswith('пол'):
            try:
                gender = event.text.lower().split()[1]
                if gender == 'мужской':
                    self.params['sex'] = 2
                elif gender == 'женский':
                    self.params['sex'] = 1
                else:
                    self.message_send(
                        event.user_id,
                        self.MISSING_INFO_MESSAGES['gender'].format(name=self.params["name"]),
                        keyboard=self.create_keyboard()
                    )
                    return

                self.message_send(
                    event.user_id,
                    'Спасибо, {}! Информация о поле обновлена.'.format(self.params["name"]),
                    keyboard=self.create_keyboard()
                )
                if not self.params.get('city'):
                    self.message_send(
                        event.user_id,
                        'Информации о городе нет. Пожалуйста, укажите ваш город.',
                        keyboard=self.create_keyboard()
                    )
                elif not self.params.get('relation'):
                    self.message_send(
                        event.user_id,
                        'Информации о семейном положении нет. Пожалуйста, укажите ваше семейное положение.',
                        keyboard=self.create_keyboard()
                    )
                else:
                    self.message_send(
                        event.user_id,
                        'Спасибо за предоставленную информацию, {}! Мы готовы искать подходящие анкеты.'.format(
                            self.params["name"]),
                        keyboard=self.create_keyboard()
                    )
                    self.process_search(event)
            except IndexError:
                self.message_send(
                    event.user_id,
                    self.MISSING_INFO_MESSAGES['gender'].format(name=self.params["name"]),
                    keyboard=self.create_keyboard()
                )
        elif event.text.lower().startswith('город'):
            try:
                city = event.text.lower().split()[1]
                self.params['city'] = city
                self.message_send(
                    event.user_id,
                    'Спасибо, {}! Информация о городе обновлена.'.format(self.params["name"]),
                    keyboard=self.create_keyboard()
                )
                if not self.params.get('sex'):
                    self.message_send(
                        event.user_id,
                        'Информации о поле нет. Пожалуйста, укажите ваш пол.',
                        keyboard=self.create_keyboard()
                    )
                elif not self.params.get('relation'):
                    self.message_send(
                        event.user_id,
                        'Информации о семейном положении нет. Пожалуйста, укажите ваше семейное положение.',
                        keyboard=self.create_keyboard()
                    )
                else:
                    self.message_send(
                        event.user_id,
                        'Спасибо за предоставленную информацию, {}! Мы готовы искать подходящие анкеты.'.format(
                            self.params["name"]),
                        keyboard=self.create_keyboard()
                    )
                    self.process_search(event)
            except IndexError:
                self.message_send(
                    event.user_id,
                    self.MISSING_INFO_MESSAGES['city'].format(name=self.params["name"]),
                    keyboard=self.create_keyboard()
                )
        elif event.text.lower().startswith('семейное положение'):
            try:
                relation = event.text.lower().split()[2]
                self.params['relation'] = relation
                self.message_send(
                    event.user_id,
                    'Спасибо, {}! Информация о семейном положении обновлена.'.format(self.params["name"]),
                    keyboard=self.create_keyboard()
                )
                if not self.params.get('sex'):
                    self.message_send(
                        event.user_id,
                        'Информации о поле нет. Пожалуйста, укажите ваш пол.',
                        keyboard=self.create_keyboard()
                    )
                elif not self.params.get('city'):
                    self.message_send(
                        event.user_id,
                        'Информации о городе нет. Пожалуйста, укажите ваш город.',
                        keyboard=self.create_keyboard()
                    )
                else:
                    self.message_send(
                        event.user_id,
                        'Спасибо за предоставленную информацию, {}! Мы готовы искать подходящие анкеты.'.format(
                            self.params["name"]),
                        keyboard=self.create_keyboard()
                    )
                    self.process_search(event)
            except IndexError:
                self.message_send(
                    event.user_id,
                    self.MISSING_INFO_MESSAGES['relation'].format(name=self.params["name"]),
                    keyboard=self.create_keyboard()
                )
        else:
            self.message_send(
                event.user_id,
                'Извините, {}, я не смог обработать ваше сообщение. Пожалуйста, введите информацию о возрасте, поле, городе или семейном положении в соответствующем формате:\n\n'
                'Возраст <возраст>\n'
                'Пол <мужской/женский>\n'
                'Город <город>\n'
                'Семейное положение <семейное положение>'.format(self.params["name"]),
                keyboard=self.create_keyboard()
            )

    def event_handler(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text.lower() == 'привет':
                    self.params = self.vk_tools.get_profile_info(event.user_id)
                    missing_info = []

                    if not self.params.get('year'):
                        missing_info.append('возраст')
                    if not self.params.get('sex'):
                        missing_info.append('пол')
                    if not self.params.get('city'):
                        missing_info.append('город')
                    if not self.params.get('relation'):
                        missing_info.append('семейное положение')

                    if missing_info:
                        self.message_send(
                            event.user_id,
                            f'Привет! Рад видеть вас, {self.params["name"]}! Кажется, у нас недостаточно информации о вас. Пожалуйста, предоставьте информацию о {", ".join(missing_info)}.',
                            keyboard=self.create_keyboard()
                        )
                        continue

                    self.message_send(
                        event.user_id,
                        f'Привет, {self.params["name"]}! Я готов помочь вам найти подходящие анкеты.',
                        keyboard=self.create_keyboard()
                    )
                elif event.text.lower() == 'пока':
                    self.message_send(
                        event.user_id, 'Счастливо, возвращайтесь!',
                        keyboard=self.create_keyboard()
                    )
                elif event.text.lower() == 'поиск':
                    missing_info = []

                    if not self.params.get('year'):
                        missing_info.append('возраст')
                    if not self.params.get('sex'):
                        missing_info.append('пол')
                    if not self.params.get('city'):
                        missing_info.append('город')
                    if not self.params.get('relation'):
                        missing_info.append('семейное положение')

                    if missing_info:
                        missing_info_str = ', '.join(missing_info)
                        self.message_send(
                            event.user_id,
                            f'Для поиска анкет необходима информация о {missing_info_str}. Пожалуйста, предоставьте эту информацию.',
                            keyboard=self.create_keyboard()
                        )
                        continue

                    self.message_send(
                        event.user_id, f'Ищем подходящие анкеты',
                        keyboard=self.create_keyboard()
                    )
                    self.offset = 0
                    self.process_search(event)
                elif event.text.lower() == 'следующая анкета':
                    self.process_search(event)
                elif missing_info:
                    self.process_user_info(event)
                else:
                    self.message_send(
                        event.user_id,
                        'Извините, я не понимаю вашу команду. Пожалуйста, воспользуйтесь доступными командами.',
                        keyboard=self.create_keyboard()
                    )


if __name__ == '__main__':
    bot_interface = BotInterface(community_token, access_token)
    bot_interface.event_handler()
