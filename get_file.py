from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials
import urllib.request as req
import cv2
import datetime
import time
import json

def generate_download_signed_url_v4(bucket_name, blob_name):
    """Generates a signed URL for downloading a blob.

    Note that this method requires a service account key file. You can not use
    this if you are using Application Default Credentials from Google Compute
    Engine or from the Google Cloud SDK.
    """
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
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    url = blob.generate_signed_url(
        # This URL is valid for 15 minutes
        expiration=datetime.timedelta(minutes=3600),
        # Allow GET requests using this URL.
        method='GET'
        )

    print('Generated GET signed URL:')
    print(url)
    print('You can use this URL with any user agent, for example:')
    print('curl \'{}\''.format(url))
    return url

url = generate_download_signed_url_v4("evidence_stream", "session_2/session_2.mp4")
# req.urlretrieve(url, "matilda")
cap = cv2.VideoCapture(url)

begin = 0
with open('video/video_info.json') as json_file:
    data = json.load(json_file)
i = 0
time_eslapsed = 0
if cap.isOpened():
    print ("File Can be Opened")
    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()
        #print cap.isOpened(), ret
        if frame is not None:
            if begin == 0:
                begin = time.time()
            wait_time = (data[i]['time_eslaped'] - time_eslapsed)/1000-27/1000
            if wait_time < 0:
                wait_time = 0 
            time.sleep(wait_time)
            time_eslapsed = data[i]['time_eslaped']
            i+=1
            # print(time_eslapsed/1000)
            # Display the resulting frame
            # time.sleep(1/15)
            
            current = time.time() 
            print(int(round((current - begin)*1000)))
            cv2.putText(frame, "time eslapsed: {}".format(int(round((current - begin)*1000))), (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.imshow('frame',frame)
            # Press q to close the video windows before it ends if you want
            if cv2.waitKey(22) & 0xFF == ord('q'):
                break
        else:
            print("Frame is None")
            break
    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
    print ("Video stop")
else:
    print("Not Working")