import os
import asyncio
import io
import requests
from PIL import Image

from llm_prettified import browse
from image_parser import get_all_photos


from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import F
from aiogram.fsm.state import State
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InputMediaPhoto, BufferedInputFile

def convert(url: str) -> BufferedInputFile:
    resp = requests.get(url)
    if resp.status_code != 200:
        return None
    img = Image.open(io.BytesIO(resp.content))
    buf = io.BytesIO()
    img.convert('RGB').save(buf, format='JPEG')
    buf.seek(0)
    return BufferedInputFile(buf.read(), filename='photo.jpg')






load_dotenv()
Token = os.getenv('TOKEN')
bot = Bot(token=Token)
dp = Dispatcher()

class searchStates(StatesGroup):
    waiting = State()
    browsing = State()

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text='Поиск по запросу'))
    builder.row(types.KeyboardButton(text='Листать предложения'))
    await message.answer('Привет, это бот - доска обьявлений квартир в Белграде', reply_markup=builder.as_markup(resize_keyboard=True))


@dp.message(F.text == 'Поиск по запросу')
@dp.message(Command('search'))
async def search(message: types.Message, state: FSMContext):
    await message.answer('Опишите свои требования, например:\n"Квартира в Врачаре до 600 евро с мебелью"')
    await state.set_state(searchStates.waiting)

@dp.message(searchStates.waiting)
async def query(message: types.Message, state: FSMContext):
    await message.answer('Поиск...')
    res = browse(message.text)
    if res.empty:
        await message.answer('Квартир по запросу не найдено')
        await state.clear()
        return
    await state.update_data(results=res.to_dict('records'), index=0)
    await state.set_state(searchStates.browsing)
    await send_apartment(message, state)

@dp.message(F.text == 'Листать предложения')
async def query(message: types.Message, state: FSMContext):
    await message.answer('Поиск...')
    res = browse('.')
    if res.empty:
        await message.answer('Квартир по запросу не найдено')
        await state.clear()
        return
    await state.update_data(results=res.to_dict('records'), index=0)
    await state.set_state(searchStates.browsing)
    await send_apartment(message, state)

async def send_apartment(message: types.Message, state: FSMContext):
    data = await state.get_data()
    results = data['results']
    index = data['index']
    apt = results[index]

    urls = get_all_photos(apt['propId'], apt['coverPhoto'])
    photos = [convert(url) for url in urls]
    photos = [p for p in photos if p is not None]
    if photos:
        media = [InputMediaPhoto(media=p) for p in photos]
        await message.answer_media_group(media=media)
    pet_map = {1: '🐕 Собаки', 2: '🐈 Кошки', 3: '🐠 Аквариумные', 4: '🐹 Мелкие в клетке', 5: '🦎 Террариумные'}

    pets_text = ''
    if apt['pets'] is not None:
        pets_list = '\n'.join(pet_map[p] for p in apt['pets'] if p in pet_map)
        pets_text = f'😺 <b>Разрешены питомцы:</b>\n{pets_list}'
    else:
        pets_text = '<b>домашние питомцы не разрешены</b>'

    distance_text=''
    if apt['distance'] is not None:
        if apt['distance'] == 1.0: distance_text = '📍 Недалеко от центра города'
        if apt['distance'] == 2.0: distance_text = '📍 От 5 до 10км от центра города'
        if apt['distance'] == 3.0: distance_text = '📍 Далеко от центра города'
    else:
        distance_text = ''

    rooms_text=''
    if apt['structure'] is not None:
        if apt['structure'] == 1.0: rooms_text = '🗄️ <b>Студия</b>'
        if apt['structure'] == 2.0: rooms_text = '🗄️ <b>Количество комнат: 1</b>'
        if apt['structure'] == 3.0: rooms_text = '🗄️ <b>Количество комнат: 2</b>'
        if apt['structure'] == 4.0: rooms_text = '🗄️ <b>Количество комнат: 3</b>'
        if apt['structure'] == 5.0: rooms_text = '🗄️ <b>Количество комнат: 4</b>'
        if apt['structure'] > 5: rooms_text = '🗄️ <b>Количество комнат: более 4</b>'
    else:
        rooms_text = ''


    furnished_text = 'С мебелью' if apt['furnished'] else 'Без мебели'
    floor_text = ''
    if apt['floor'] is not None:
        if apt['floor'] == 1: floor_text = 'Первый'
        if apt['floor'] == 2: floor_text = '2-4'
        if apt['floor'] == 3: floor_text = '5-10'
        if apt['floor'] == 4: floor_text = 'выше 10'
        if apt['floor'] == 5: floor_text = 'Мансарда'
        if apt['floor'] == 0: floor_text = 'Высокий цокольный'
        if apt['floor'] == -1: floor_text = 'Подвал'
    else:
        floor_text = ''

    heat_map = {1: 'Центральное отопление', 4: 'Электрическое отопление', 99: 'Газовое отопление подъезда', 21: 'Подогрев пола'}

    heat_text = ''
    if apt['heatingArray'] is not None:
        heat_list = '\n'.join(heat_map[p] for p in set(apt['heatingArray']) if p in heat_map)
        heat_text = f'🔥 <b>Доступное отопление:</b>\n{heat_list}'
    else:
        heat_text = '<b>Без отопления</b>'


    text = (
        f'🏠 <b>Квартира в {apt["municipality"]}, ул. {apt["street"]}</b>\n\n'
        f'🏢 <b>Этаж:</b> {floor_text}\n'
        f'{rooms_text}\n'
        f'💶 <b>Цена:</b> {int(apt["price"])} евро / мес.\n'
        f'📐 <b>Площадь:</b> {apt["size"]} кв.м.\n'
        f'🛋 <b>Мебель:</b> {furnished_text}\n'
        f'{distance_text}\n\n'
        f'{heat_text}\n\n'
        f'{pets_text}\n\n'
        f'🌐 <a href="https://cityexpert.rs/ru/properties-for-rent/belgrade/{apt["propId"]}/other-office-space-mijacka-vozdovac">Перейти к полному объявлению</a>\n'
        f'📍 <a href="https://www.google.com/maps?q={apt['location'].replace(' ', '')}">Локация квартиры на карте</a>\n'
        f'{index + 1} из {len(results)}'
    )
    builder = InlineKeyboardBuilder()
    builder.button(text='Новый запрос', callback_data='new')
    if index+1 < len(results):
        builder.button(text='далее', callback_data='next')
    builder.adjust(2)
    await message.answer(text, parse_mode='HTML', reply_markup=builder.as_markup())
    
    
@dp.callback_query(F.data=='next')
async def next_apt(callback_data: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.update_data(index=data['index'] + 1)
    await send_apartment(callback_data.message, state)
    await callback_data.answer()

@dp.callback_query(F.data == 'new')
async def new_search(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer('Опишите свои требования, например:\n"Квартира в Врачаре до 600 евро с мебелью"')
    await state.set_state(searchStates.waiting)
    await callback.answer()


async def main():
    print('В работе')
    await dp.start_polling(bot)
if __name__ == '__main__':
    asyncio.run(main())