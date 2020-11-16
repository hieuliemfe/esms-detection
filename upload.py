from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials
import argparse
import cv2
import json
from time import sleep
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from pathlib import Path


ap = argparse.ArgumentParser()
ap.add_argument("--fr", help="path for upload")
ap.add_argument("--to", help="path destination")
fr = ap.parse_args().fr
to = ap.parse_args().to

Path(fr + "/angry_periods/").mkdir(parents=True, exist_ok=True)
period_file = open(fr + "periods_info.json", 'r')
periods = json.loads(period_file.read())
evidence_file_names = []
evidence_file = 1
while len(periods) > 0:
    period_info = periods.pop(0)
    print(period_info)
    start_time = period_info["period_start"]/1000
    end_time = period_info["period_end"]/1000
    ffmpeg_extract_subclip(fr + "video.mp4", start_time, end_time, targetname=fr+"angry_periods/evidence_{}.mp4".format(evidence_file))
    evidence_file_names.append("evidence_{}.mp4".format(evidence_file))
    evidence_file += 1
print(evidence_file_names)


credentials_dict = {
    'type': 'service_account',
    'client_id': '101555805101458693726',
    'client_email': 'evidence-streaming-service@emotion-detection-project-2020.iam.gserviceaccount.com',
    'private_key_id': '3f28ef810237cf4628123a84f37c2a89a52a7c27',
    'private_key': '-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDFfUCENvtp3ABy\n5WkbtWEkyb56BDbddJaFpKVjAHrg2vMP+GVw0jI+fKteJ5lj08CUsEHUnFTNKiUr\nHE7++BekU1mSgOBIz24YwLgd3myC/qxcPtzChd7vJIBkkWQvvfqPG3eROaU57iMe\ni2IMn8vMlB4SUdfFUV5U4Z0AceOtkMKHhV8vlpKCH/nnIgyt+3czJsaIQYFmD3CT\nEj1ymKhCZz8cUnh9zHxluN5VWxtabIh2vb7CotNZCjiP7xwdBhy6EMXdus/5sV4k\nDRs2A6SfF7Vpvv9M2qxNnN2Uz762JS2HAbD7gRv5PYsW2JrqIOZ2p9HAuzyU68C6\n19r2+GUTAgMBAAECggEABHEsrcWJDQ31NtlGYEwtIU/tRMX/t0LP+GAGQMHvc2f8\n6hHTCPaBZiVOLQc2U7YrRt6vnij67DdazKuNj1NII/cWNM262jMS5o6FY+Pvb8pr\nWPZ95yRuKdXEdf6iUNHtrhMIpK+1zkJTjJDjl16oVMHLQEEgko5o+8Y6eUVPa9Oj\ngZcyp1xbOdk+SvUsfX374vOtC+yoP0CJP+teM40R9JEBt6E4hMV/BTN3A8bJuaWq\nMBvVobtMt3nI1rIqIQfinwYZYvvWOQAjE8Apq6guoRBO1L+V6qSrzyqc7b0g1/Vx\nBNuUBD6L5mXJuIuGfHDebBS5I79KHeZaPT62keDruQKBgQDnLb/AHY/LejH/B2oT\n7zr0Z+Nwy9avewgH78eKc2QeyG8mx2fbv+oB51jWaR3LyzrqZYvgHXejp4Ei1Mi5\nycEzqCBY5aLZ5A4JicDztH5qq6NRYWDgqOthY+fEee8LI8uhrO/56aHCJqIznZz4\nvylEBNLk+0JuriQdGIfIThuDrQKBgQDasYEd4hftGt+7+P4XvBCP6DmhGS+cAGN/\nowLIBjhsjpV2Z6njE7Xw3ooPCinK5qcZ0CnUap4EH6DrMkhp/Y3LQRbZkmdKNGkZ\n2Lx6+R+QX6iCGvlMY9jeiUUWa227MqF3YnwTwpCKTc7cWIqWWGLnzZ3pi1/R/3ly\nbAWpPUKjvwKBgQCULmbypgA91R2m8wGztWx8rPrEmmQKJzqGm9OzkzNh5+gXW0nf\nOayte7Ud+lL3BlXFWUHHbhv58qx7vxjKvd/xVJsnYEp6kAvPYVUk4VUG2u3chCas\n2pnF21v8PIxU/6TPBSLtdiwRXuIpY6Xya9Xvm4fy7nsupsDPRaIDas2IIQKBgFGx\nFtsz1t4yOLs94qS5ErK++7AK+Xbbyk8mdGaFtFQQ2xIU3Sg+96rXZlkB4eSyTl9d\nHBMGFKrTqcfRy60UEwCG+uMhRkY4173Y8Wc6YikLIqYfL1ryvVM7kbwzOxU/b4Nq\nHZFAD8AqGojC5loNAD042LEh6BRIy3QLl/3FLXx/AoGAEXDO6ilPOXsJ9FNlAwbd\ng7MXhZKdYRelZAi6bd/qVHJS6WEYyTYQw3agrVkxjon4eayydNOkatxU3kkPLTrO\n+Wfy9Dca9pmXzeoWC+dJ3qsFLD3bGgfG2XV3QA9xoaY3wJdh7dCH8rKqyzbkxxaB\nwFqw9gIs/D0Q06Wu//S1bxY=\n-----END PRIVATE KEY-----\n',
}
credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    credentials_dict
)
client = storage.Client(credentials=credentials, project='emotion-detection-project-2020')
bucket = client.get_bucket('evidence_stream')
blob_video = bucket.blob(to + 'video.mp4')
blob_json = bucket.blob(to + 'video_info.json')
blob_video.upload_from_filename(fr + 'video.mp4')
blob_json.upload_from_filename(fr + 'video_info.json')
blob_period_json = bucket.blob(to +"angry_periods/periods_info.json")
blob_period_json.upload_from_filename(fr + "periods_info.json")
while len(evidence_file_names) > 0:
    file_name = evidence_file_names.pop()
    blob_video = bucket.blob(to + "angry_periods/" + file_name)
    blob_video.upload_from_filename(fr + "angry_periods/" + file_name)