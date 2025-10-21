import json

with open('form.json', 'r', encoding='utf-8') as f:
    template = json.load(f)

def build_promt(file_name: str) -> str:
    promt = (
        f"""
        1. Транскрибуй аудіо файл українською мовою, згідно з інструкціями (розділ transcript_section).
        2. Заповни анкету (розділ analysis_section).

        JSON структура відповіді яку потрібно заповнити:
        {json.dumps(template, ensure_ascii=False, indent=4)}

        Інструкції до анкети:
        - Там де question = empty просто поле порожнє
        - Там де text - напиши текстову відповідь
        - Там де yes_no - відповідай "так" = 1 або "ні" = 0
        - Там де single_choice - обирай одну відповідь зі списку варіантів з options
        - Там де telephone - візьми номер телефону з назви файлу: {file_name}

        Поверни відповідь строго строкою в форматі JSON яку можна буде разпарсити json.loads().
        """
    )
    return promt