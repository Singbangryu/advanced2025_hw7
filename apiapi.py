import requests
import pandas as pd
import json

SERVICE_KEY = "b858b3bd6a834d1e1a17a7e590d5850930d1a4fa778c35d5e9498a9fa3b43fcb"
BASE_URL = "https://apis.data.go.kr/1360000/AsosHourlyInfoService/getWthrDataList"


def get_weather_data(params):

    common_params = {
        "serviceKey": SERVICE_KEY,
        "dataType": "JSON",
        "dataCd": "ASOS",
        "dateCd": "HR",
        "stnIds": "108",
        "numOfRows": "10",
        "pageNo": "1"
    }
    all_params = {**common_params, **params}
    try:
        response = requests.get(BASE_URL, params=all_params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data

    except requests.exceptions.HTTPError as http_err:
        print(f"❌ HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"❌ An error occurred: {req_err}")
    except json.JSONDecodeError:
        print(f"❌ Failed to decode JSON. Response was: {response.text}")

    return None
request_cases = [
    {
        "description": "2024-12-04 (15-18h)",
        "params": {
            "startDt": "20241204",
            "startHh": "15",
            "endDt": "20241204",
            "endHh": "18"
        }
    },
    {
        "description": "2025-06-04 (12-16h)",
        "params": {
            "startDt": "20250604",
            "startHh": "12",
            "endDt": "20250604",
            "endHh": "16"
        }
    },
    {
        "description": "2025-11-13 (00-03h)",
        "params": {
            "startDt": "20251113",
            "startHh": "00",
            "endDt": "20251113",
            "endHh": "03"
        }
    }
]
all_data_frames = []
print("데이터 조회를 시작합니다...")
for case in request_cases:
    weather_data = get_weather_data(case["params"])
    if weather_data:
        header = weather_data.get('response', {}).get('header', {})
        body = weather_data.get('response', {}).get('body', {})
        if header.get('resultCode') == '00':
            items = body.get('items', {}).get('item', [])

            if items:

                df = pd.DataFrame(items)


                df['조회조건'] = case["description"]

                all_data_frames.append(df)
                print(f" {case['description']} 데이터 조회 성공")
            else:
                print(f"{case['description']} 데이터 없음 (totalCount: 0)")
        else:
            print(f"API 오류 ({case['description']}): {header.get('resultMsg')}")


if all_data_frames:
    final_df = pd.concat(all_data_frames, ignore_index=True)
    output_filename = "weather_data.xlsx"
    try:
        final_df.to_excel(output_filename, index=False, engine='openpyxl')
        print(f"\n{output_filename}")
    except Exception as e:
        print(f"\n오류: {e}")
else:

    print("\nx")
