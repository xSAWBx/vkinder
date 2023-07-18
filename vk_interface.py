import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from config import community_token
from config import access_token
from core import VkTools


class BotInterface:
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
        if self.worksheets:
            worksheet = self.worksheets.pop()
            photos = self.vk_tools.get_photos(worksheet['id'])
            photo_string = ''
            for photo in photos:
                photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
            self.message_send(
                event.user_id,
                f'Имя: {worksheet["name"]} Ссылка: vk.com/{worksheet["id"]}',
                attachment=photo_string,
                keyboard=self.create_keyboard()
            )
            self.save_match(event.user_id, worksheet['id'])  # Сохраняем соответствие анкеты пользователю
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
                photo_string = ''
                for photo in photos:
                    photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
                self.offset += 10
                self.message_send(
                    event.user_id,
                    f'Имя: {worksheet["name"]} Ссылка: vk.com/{worksheet["id"]}',
                    attachment=photo_string,
                    keyboard=self.create_keyboard()
                )
                self.save_match(event.user_id, worksheet['id'])  # Сохраняем соответствие анкеты пользователю
            else:
                self.message_send(event.user_id, 'Подходящих анкет не найдено')

    def check_database(self, user_id, worksheet_id):
        # Проверка базы данных на соответствие event.user_id и worksheet_id
        # Вернуть True, если есть соответствие, и False в противном случае
        # В данном случае используем простой словарь для сохранения соответствий
        return self.get_match(user_id) == worksheet_id

    def get_match(self, user_id):
        # Получение соответствия анкеты пользователю из базы данных
        # В данном случае используем простой словарь для сохранения соответствий
        return self.matches.get(user_id)

    def save_match(self, user_id, worksheet_id):
        # Сохранение соответствия анкеты пользователю в базе данных
        # В данном случае используем простой словарь для сохранения соответствий
        self.matches[user_id] = worksheet_id

    def create_keyboard(self):
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('Следующая анкета', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()  # Переход на новую строку
        keyboard.add_button('Пока', color=VkKeyboardColor.NEGATIVE)
        return keyboard.get_keyboard()

    def event_handler(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text.lower() == 'привет':
                    self.params = self.vk_tools.get_profile_info(event.user_id)
                    missing_info = []

                    if not self.params['year']:
                        missing_info.append('возраст')
                    if not self.params['sex']:
                        missing_info.append('пол')

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
                    if not self.params['year'] or not self.params['sex']:
                        missing_info = []

                        if not self.params['year']:
                            missing_info.append('возраст')
                        if not self.params['sex']:
                            missing_info.append('пол')

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
                    self.offset = 0  # Сброс смещения перед началом нового поиска
                    self.process_search(event)
                elif event.text.lower() == 'следующая анкета':
                    self.process_search(event)
                else:
                    self.message_send(
                        event.user_id, 'Извините, я не понимаю вашу команду. Пожалуйста, воспользуйтесь доступными командами.',
                        keyboard=self.create_keyboard()
                    )


if __name__ == '__main__':
    bot_interface = BotInterface(community_token, access_token)
    bot_interface.event_handler()
