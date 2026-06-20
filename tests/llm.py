import json
from difflib import get_close_matches

from pydantic import BaseModel, Field
from typing import Optional
from openai import OpenAI
import httpx
import pandas as pd


df = pd.read_csv('apartments.csv')

class Filter(BaseModel):
    municipality: Optional[str] = Field(None, description='Название района на латинице с большой буквы, например: Vracar, Zvezdara')
    street: Optional[str] = Field(None, description='Название улицы на латинице с большой буквы, например: Ozrenska, Sarajevska')
    max_price: Optional[float] = Field(None, description='Максимальная цена в евро')
    min_price: Optional[float] = Field(None, description='Минимальная цена в евро')
    furnished: Optional[int] = Field(None, description='1 если нужна мебель в квартире, 0 если не нужна')
    max_size: Optional[int] = Field(None, description='Максимальная площадь квартиры в кв метрах')
    min_size: Optional[int] = Field(None, description='Минимальная площадь квартиры в кв метрах')





def llm(user_text: str) -> Filter:
    municipalities = df['municipality'].dropna().unique().tolist()
    client = OpenAI(
        base_url='http://127.0.0.1:11434/v1',
        api_key='ollama',
        timeout=60.0,
        http_client=httpx.Client(
            mounts={"all://127.0.0.1": None}  # не использовать прокси для localhost
        )
    )
    prompt = (
        "Верни ТОЛЬКО этот JSON, заполнив значения из текста пользователя:\n"
        "{\"municipality\": null, \"street\": null, \"max_price\": null, \"min_price\": null, \"furnished\": null, \"max_size\": null, \"min_size\": null}\n"
        "Правила:\n"
        "- Используй ТОЛЬКО эти 7 ключей, никаких других\n"
        "- max_size и min_size — площадь квартиры в кв. метрах\n"
        "- Если параметр не указан — оставь null\n"
        f"- municipality выбирай из: {municipalities}\n"
        "- street — транслитерируй название улицы с русского на Сербскую латиницу: "
        "- Например Кулина Бана -> Kulina Bana Первая буква заглавная.\n"
    )




    try:
        completion = client.chat.completions.create(
            model='qwen2.5:7b',
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_text}
            ],
            response_format={'type': 'json_object'},
            temperature=0.0
        )
        response_text = completion.choices[0].message.content
        #print(response_text)
        data = json.loads(response_text)
        if "properties" in data:
            data = data["properties"]


        return Filter(**data)
    except Exception as e:
        print(type(e).__name__)
        print(str(e))
        raise





if __name__ == '__main__':
    #request = str(input())
    res = llm('нужна квартира на улице Светозара Радойчича, площадью не более 40 кв метров')
    df_filtered = df.copy()
    if res.street is not None:
        all = df['street'].dropna().unique().tolist()
        matches = get_close_matches(res.street, all, n=1, cutoff=0.3)
        if matches:
            df_filtered = df_filtered[df_filtered['street'] == matches[0]]
    if res.furnished is not None:
        df_filtered = df_filtered[df_filtered['furnished'] == int(res.furnished)]
    if res.max_price is not None:
        df_filtered = df_filtered[df_filtered['price'] <= res.max_price]
    if res.min_price is not None:
        df_filtered = df_filtered[df_filtered['price'] >= res.min_price]
    if res.max_size is not None:
        df_filtered = df_filtered[df_filtered['size'] <= res.max_size]
    if res.min_size is not None:
        df_filtered = df_filtered[df_filtered['size'] >= res.min_size]
    if res.municipality is not None:
        df_filtered = df_filtered[df_filtered['municipality'] == res.municipality]
    #print(df_filtered[['price', 'size', 'municipality', 'street', 'furnished']])
    print(res)