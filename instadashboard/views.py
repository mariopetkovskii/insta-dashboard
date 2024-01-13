import json

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import zipfile
import io

@csrf_exempt
def upload_zip(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('zipFile')

        data_from_zip = {}

        if uploaded_file and uploaded_file.name.endswith('.zip'):
            type = request.POST.get('type')
            if type == 'unfollowers':
                data_from_zip = unfollowers(uploaded_file)
            else:
                data_from_zip = process_zip_file(uploaded_file, type)
            return JsonResponse({'result': data_from_zip})
        else:
            return JsonResponse({'error': 'Invalid file. Please upload a zip file.'}, status=400)

    return render(request, 'upload.html')


def process_zip_file(uploaded_file, type):
    try:
        with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
            if 'connections/followers_and_following/' + type + '.json' in zip_ref.namelist():
                json_file_content = zip_ref.read('connections/followers_and_following/' + type + '.json')
                json_data = json.loads(json_file_content.decode('utf-8'))

                return json_data
            else:
                return {'error': type + '.json not found in the zip file.'}
    except Exception as e:
        return {'error': f'Error processing zip file: {str(e)}'}


def unfollowers(uploaded_file):
    try:
        with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
            json_file_content_following = zip_ref.read('connections/followers_and_following/following.json')
            json_data_following = json.loads(json_file_content_following.decode('utf-8'))
            json_file_content_followers = zip_ref.read('connections/followers_and_following/followers_1.json')
            json_data_followers = json.loads(json_file_content_followers.decode('utf-8'))

            following_values = [item['string_list_data'][0]['value'] for item in json_data_following['relationships_following']]
            followers_values = [item['string_list_data'][0]['value'] for item in json_data_followers]

            not_in_followers = [value for value in following_values if value not in followers_values]

            result = {"relationships_not_in_followers": not_in_followers}
            return result

    except Exception as e:
        return {'error': f'Error processing zip file: {str(e)}'}

