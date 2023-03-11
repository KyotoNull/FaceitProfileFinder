import requests
from bs4 import BeautifulSoup
from config import BOT_TOKEN
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer('Здравствуйте, пришлите мне ссылку на стим профиль пользователя, и я отправлю вам'
                         ' полную информацию об его Faceit аккаунте! ')

@dp.message_handler()
async def get_profile(message):
    wait = await message.answer(f'Please wait 1-10 seconds!')
    try:
        message.text += ' '
        if message.text[-2] == '/':
            message.text = message.text[30:-2]
        elif message.text[-20] == 's':
            message.text = message.text[36:-1]
        elif message.text[-1] == ' ':
            message.text = message.text[30:-1]

        url = f'https://www.steamidfinder.com/lookup/{message.text}/'
        response = requests.get(url)

        soup = BeautifulSoup(response.text, 'html.parser')
        steam_id = soup.find('div', class_='panel-body').find('a', class_='btn btn-default').get('href')
        steam_id = str(steam_id)
        steam_id = steam_id[48:]

        url = f'https://faceitfinder.com/stats/{steam_id}'
        rec = requests.get(url)

        soup = BeautifulSoup(rec.text, 'html.parser')

        lowest_elo_value = soup.find_all('span', class_='stats_totals_block_item_value')
        matches = soup.find_all('span', class_='stats_totals_block_main_value_span')
        win_rate = soup.find_all('span', class_='stats_totals_block_main_value_span positive')

        #main
        faceit_nickname = soup.find('span', class_='stats_profile_name_span').text
        now_elo = soup.find('span', class_='stats_profile_elo_span').text
        avg = lowest_elo_value[0].text
        highest_elo = lowest_elo_value[11].text
        lowest_elo = lowest_elo_value[10].text
        now_lvl_value = soup.find('img', class_='stats_profile_level_image').get('alt')
        now_lvl_png = soup.find('img', class_='stats_totals_block_level_image').get('src')
        avatar = soup.find('div', class_='stats_profile_inner').find('img', class_='stats_profile_avatar').get('src')
        hs_rate = matches[4].text
        matches_value = matches[5].text

        try:
            k_d = soup.find('div', class_='stats_totals_block_main_value').find('span', class_='stats_totals_block_main_value_span positive').text
            checker = True
        except:
            k_d = soup.find_all('span', class_='stats_totals_block_main_value_span negative')
            k_d = k_d[0].text
            checker = False

        try:
            win_rate_value = win_rate[1].text
        except:
            win_rate_value = soup.find_all('span', class_='stats_totals_block_main_value_span negative')
            if checker == False:
                win_rate_value = win_rate_value[1].text
            else:
                win_rate_value = win_rate_value[0].text

        buttons = [
            types.InlineKeyboardButton(text="Avatar", url=f"{avatar}"),
            types.InlineKeyboardButton(text="Faceit", url=f"https://www.faceit.com/ru/players/{faceit_nickname}")
        ]
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*buttons)

        await bot.send_photo(message.chat.id, photo=avatar, caption=f'Faceit nickname: {faceit_nickname} ✅\n'
              f'Now elo: {now_elo} ({now_lvl_value[13:-5]})\n'
              f'------------------------------------\n'
              f'Lowest elo: {lowest_elo}\n'
              f'Highest elo: {highest_elo}\n'
              f'Avg kills: {avg}\n'
              f'K/D ratio: {k_d}\n'
              f'Win rate: {win_rate_value}\n'
              f'HS rate%: {hs_rate}\n'
              f'Matches: {matches_value}\n', reply_markup=keyboard)

    except:
        await message.answer('❌ Player not found or link not correct!')

    await wait.delete()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

