from pprint import pprint
from datetime import datetime
import vk_api
from vk_api.exceptions import ApiError
from config import access_token


class VkTools:
    def __init__(self, access_token):
        self.vkapi = vk_api.VkApi(token=access_token)

    def _bdate_toyear(self, bdate):
        user_year = bdate.split('.')[2] if bdate else None
        now = datetime.now().year
        return now - int(user_year)

    def get_profile_info(self, user_id):
        try:
            info = self.vkapi.method('users.get', {'user_id': user_id, 'fields': 'city,sex,bdate,relation'})
            if info:
                info = info[0]  # Принимаем первый элемент из списка, если он есть
            else:
                info = {}
        except ApiError as e:
            info = {}
            print(f'error = {e}')

        result = {
            'name': f'{info.get("first_name", "")} {info.get("last_name", "")}',
            'sex': info.get('sex'),
            'city': info.get('city', {}).get('title'),
            'year': self._bdate_toyear(info.get('bdate'))
        }
        return result

    def search_worksheet(self, params, offset=0):
        try:
            users = self.vkapi.method('users.search', {
                'count': 1,
                'offset': offset,
                'hometown': params['city'],
                'sex': 1 if params['sex'] == 2 else 2,
                'has_photo': True,
                'age_from': params['year'] - 3,
                'age_to': params['year'] + 3,
            })
        except ApiError as e:
            users = []
            print(f'error = {e}')

        result = [{
            'name': item['first_name'] + item['last_name'],
            'id': item['id']
        } for item in users['items'] if not item['is_closed']]
        return result

    def get_photos(self, id):
        try:
            photos = self.vkapi.method('photos.get', {
                'owner_id': id,
                'album_id': 'profile',
                'extended': 1
            })
        except ApiError as e:
            photos = {}
            print(f'error = {e}')

        result = [{
            'owner_id': item['owner_id'],
            'id': item['id'],
            'likes': item['likes']['count'],
            'comments': item['comments']['count']
        } for item in photos['items']]
        '''Сортировка по лайкам и комментариям'''
        return sorted(result, key=lambda x: (x['likes'], x['comments']), reverse=True)[:3]


if __name__ == '__main__':
    user_id = 757119831
    tools = VkTools(access_token)
    params = tools.get_profile_info(user_id)
    worksheets = tools.search_worksheet(params)
    worksheet = worksheets.pop()
    photos = tools.get_photos(worksheet['id'])

    pprint(worksheets)
