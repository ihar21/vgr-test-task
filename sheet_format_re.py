rule_red = {
    "addConditionalFormatRule": {
        "rule": {
            "ranges": [
                {"startColumnIndex": 19, "endColumnIndex": 20, "startRowIndex": 2, "endRowIndex": 3}
            ],
            "booleanRule": {
                "condition": {
                    "type": "CUSTOM_FORMULA",
                    "values": [{"userEnteredValue": "=U3=0"}]
                },
                "format": {
                    "backgroundColor": {"red": 1.0, "green": 0.8, "blue": 0.8}
                }
            }
        },
        "index": 0
    }
}


rule_green = {
    "addConditionalFormatRule": {
        "rule": {
            "ranges": [
                    {"startColumnIndex": 19, "endColumnIndex": 20, "startRowIndex": 2, "endRowIndex": 3}
                ],
                "booleanRule": {
                    "condition": {
                        "type": "CUSTOM_FORMULA",
                        "values": [{"userEnteredValue": "=U3=1"}]
                    },
                    "format": {
                        "backgroundColor": {"red": 0.8, "green": 1.0, "blue": 0.8}
                    }
                }
            },
            "index": 0
        }
    }
form_requests = [rule_red, rule_green]  

def make_copy_request(
    from_row: int,
    to_row: int,
    paste_type: str = "PASTE_FORMAT"
) -> dict:
    """Создаёт типизированный запрос для копирования форматирования строки."""
    req = {
        "copyPaste": {
            "source": {
                "startRowIndex": from_row - 1,
                "endRowIndex": from_row,
            },
            "destination": {
                "startRowIndex": to_row - 1,
                "endRowIndex": to_row,
            },
            "pasteType": paste_type,
            "pasteOrientation": "NORMAL",
        }
    }
    return req