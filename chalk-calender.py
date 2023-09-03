import datetime
import json

# config
# 在这里设置学期结束时间，当前是 2024-01-27 结束
END_REPEATING_TIME = "20240127T235959"

# 把希悦上events?开头的请求 Response 的 json 数据放在同一目录下到 data.json
# 首先打开 F12，把课程表选择周视图，切换至有课程的一页
# F12控制台 - Network - 筛选 Fetch/XHR - events?end_time ... 这条请求 - Response

try:
    with open("data.json", "r") as f:
        data = json.load(f)
except FileNotFoundError:
    print("文件未找到 把希悦上events?开头的请求 Response 的 json 数据放在同一目录下到 data.json")
    exit(1)

# 合并两个课位的课
def merge_events(data):
    merged_data = []

    for event in data:
        if not merged_data:
            merged_data.append(event)
            continue

        last_event = merged_data[-1]
        can_merge = (
            last_event["title"] == event["title"] and
            last_event["address"] == event["address"]
        )
        if can_merge:
            last_event["end_time"] = event["end_time"]
        else:
            merged_data.append(event)

    return merged_data

merged_data = merge_events(data)

ics_content = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//BDFZ//Calendar Export//"
]

for event in merged_data:
    start_time = datetime.datetime.strptime(event["start_time"], '%Y-%m-%d %H:%M:%S').strftime('%Y%m%dT%H%M%S')
    end_time = datetime.datetime.strptime(event["end_time"], '%Y-%m-%d %H:%M:%S').strftime('%Y%m%dT%H%M%S')
    ics_content.extend([
        "BEGIN:VEVENT",
        f"UID:{start_time}@i.pkuschool.edu.cn",
        f"DTSTART:{start_time}",
        f"DTEND:{end_time}",
        f"SUMMARY:{event['title']}",
        f"LOCATION:{event['address']}",
        f"RRULE:FREQ=WEEKLY;UNTIL={END_REPEATING_TIME}",
        "END:VEVENT"
    ])

ics_content.append("END:VCALENDAR")

ics_string = "\r\n".join(ics_content)
file_path = "schedule.ics"
with open(file_path, 'w') as file:
    file.write(ics_string)
