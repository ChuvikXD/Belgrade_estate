import json
from difflib import get_close_matches

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional
from openai import OpenAI
import pandas as pd
import ast
import dotenv
import os

load_dotenv()
Token=os.getenv('TOKEN_LLM')


df = pd.read_csv('apartments.csv')
def transform_dist(val):
    if pd.isna(val):
        return None
    val = str(val)
    if '10+' in val or '10_' in val:
        return 3
    if '5_10' in val or '5-10' in val:
        return 2
    if '5' in val:
        return 1
    return None

df['petsArray'] = df['petsArray'].apply(ast.literal_eval)
def transform_pets(val):
    return val if val else None

df['distance']= df['distanceCenterArray'].apply(transform_dist)
df['pets'] = df['petsArray'].apply(transform_pets)
floor_map = {
    'PR': 1, 'SU': -1, 'VPR': 0,
    '2_4': 2, '5_10': 3, '11+': 4,
    'PTK': 5, 'NPR': 1, '1':1
}
df['floor'] = df['floor'].map(floor_map).fillna(df['floor'])
df['bedroomsArray'] = df['bedroomsArray'].apply(ast.literal_eval)
df['structure'] = pd.to_numeric(df['structure'], errors='coerce')
df['structure'] = df['structure'].apply(lambda x: round(x) if pd.notna(x) else x)
df['heatingArray'] = df['heatingArray'].apply(ast.literal_eval)


class Filter(BaseModel):
    municipality: Optional[str] = Field(None, description='Название района на латинице с большой буквы, например: Vracar, Zvezdara')
    street: Optional[str] = Field(None, description='Название улицы на латинице с большой буквы, например: Ozrenska, Sarajevska')
    max_price: Optional[float] = Field(None, description='Максимальная цена в евро')
    min_price: Optional[float] = Field(None, description='Минимальная цена в евро')
    furnished: Optional[int] = Field(None, description='1 если нужна мебель в квартире, 0 если не нужна')
    max_size: Optional[int] = Field(None, description='Максимальная площадь квартиры в кв метрах')
    min_size: Optional[int] = Field(None, description='Минимальная площадь квартиры в кв метрах')
    distance: Optional[int] = Field(None, description='Расстояние до центра')
    pets: Optional[int] = Field(None, description='Разрешение на питомцев')
    floor: Optional[int] = Field(None, description='Необходимый этаж')
    exclude_floor: Optional[int] = Field(None, description='Этаж который нужно исключить')
    structure: Optional[float] = Field(None, description='Количество комнат')



def llm(user_text: str) -> Filter:
    municipalities = df['municipality'].dropna().unique().tolist()
    client = OpenAI(
        base_url='https://api.groq.com/openai/v1',
        api_key=Token,
        timeout=60.0,
    )
    prompt = (
        "Верни ТОЛЬКО этот JSON, заполнив значения из текста пользователя:\n"
        "{\"municipality\": null, \"street\": null, \"max_price\": null, \"min_price\": null, \"furnished\": null, \"max_size\": null, \"min_size\": null, \"distance\": null, \"pets\": null, \"floor\": null,  \"exclude_floor\": null, \"structure\": null}\n"
        "Правила:\n"
        "- Используй ТОЛЬКО эти 12 ключей, никаких других\n"
        "- max_size и min_size - площадь квартиры в кв. метрах\n"
        "- Если параметр не указан - оставь null\n"
       f"- municipality выбирай из: {municipalities}\n"
        "- street - транслитерируй название улицы с русского на латиницу: "
        "- distance - 1- если близко к центру, 2 - если более 5 км от центра, 3 если далеко от центра, в остальных случаях null"
        "- pets: 1=собака, 2=кошка, 3=аквариумные, 4=мелкие в клетке (хомяк/кролик), 5=террариумные (змея/черепаха), 6=прочие. "
        "-Верни число если питомец упомянут, null если нет\n"
        "- floor: 1=первый этаж, 2=со второго по четвертый этаж, 3=с пятого по десятый этаж, 4=с десятого этажа и выше, -1=подвал, 0=цокольный этаж, 5=лофт/мансарда\n"
        "- exclude_floor: если пользователь говорит 'не на первом этаже' - верни 1, в остальных случаях null\n"
        "- structure: 1.0=студия, 2.0=однокомнатная, 3.0=двухкомнатная, 4.0=трёхкомнатная, и т.д.\n"
        "- Первая буква заглавная.\n"
    )

    try:
        completion = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_text}
            ],
            response_format={'type': 'json_object'},
            temperature=0.0
        )
        response_text = completion.choices[0].message.content
        data = json.loads(response_text)
        if "properties" in data:
            data = data["properties"]
        return Filter(**data)
    except Exception as e:
        print(type(e).__name__)
        print(str(e))
        raise



def browse(req):
    res = llm(req)
    df_filtered = df.copy()
    if res.street is not None:
        all = df['street'].dropna().unique().tolist()
        matches = get_close_matches(res.street, all, n=1, cutoff=0)
        if matches:
            df_filtered = df_filtered[df_filtered['street'] == matches[0]]
    if res.furnished is not None:
        df_filtered = df_filtered[df_filtered['furnished'] == int(res.furnished)]
    if res.max_price is not None:
        df_filtered = df_filtered[df_filtered['price'] <= res.max_price]
    if res.distance is not None:
        df_filtered = df_filtered[df_filtered['distance'] == res.distance]
    if res.min_price is not None:
        df_filtered = df_filtered[df_filtered['price'] >= res.min_price]
    if res.max_size is not None:
        df_filtered = df_filtered[df_filtered['size'] <= res.max_size]
    if res.min_size is not None:
        df_filtered = df_filtered[df_filtered['size'] >= res.min_size]
    if res.municipality is not None:
        df_filtered = df_filtered[df_filtered['municipality'] == res.municipality]
    if res.floor is not None:
        df_filtered = df_filtered[df_filtered['floor'] == res.floor]
    if res.exclude_floor is not None:
        df_filtered = df_filtered[df_filtered['floor'] != res.exclude_floor]
    if res.structure is not None:
        df_filtered = df_filtered[
            (df_filtered['structure'] == res.structure) | (df_filtered['structure'].isna())
            ]
    if res.pets is not None:
        df_filtered = df_filtered[df_filtered['pets'].apply(lambda x: x is not None and res.pets in x)]
    return df_filtered




if __name__ == '__main__':
    req = str(input())
    res = browse(req)
    #for _, row in res.iterrows():
    #    print(row['propId'], row['structure'])
    #print(res)