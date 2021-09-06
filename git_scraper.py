from typing import Union

import requests
import mongodb_storage
import const

search_api_link = 'https://api.github.com/search/repositories?q=stars:{}'.format(const.STARS_COUNT)


def get_json(link: str) -> dict:
    proxy_dict = {'http': const.PROXIES, 'https': const.PROXIES}
    response = requests.request( # PROXY
        'GET',
        link,
        headers=const.HEADERS,
        proxies=proxy_dict)
    # response = requests.request(
    #     'GET',
    #     link,
    #     headers=const.HEADERS)
    content = response.json()
    return content


def get_language_percentage(repo_name: str) -> Union[str, dict]:
    language_api_link = f'https://api.github.com/repos/{repo_name}/languages'
    language_api_dict = get_json(language_api_link)
    if len(language_api_dict) == 0:
        return 'no programming language in the repo'
    else:
        keys = [*language_api_dict]
        values = list(language_api_dict.values())
        values_sum = sum(values)
        values = list(map(lambda x: (x * 100) / values_sum, values))
        language_dict = dict(zip(keys, values))
        return language_dict


def get_last_issue(repo_name: str) -> str:
    issue_api_link = f'https://api.github.com/repos/{repo_name}/issues?per_page=1'
    last_issue = get_json(issue_api_link)[0]['created_at']
    return last_issue


def get_last_pull(repo_name: str) -> str:
    pull_api_link = f'https://api.github.com/repos/{repo_name}/pulls?per_page=1'
    last_pull = get_json(pull_api_link)[0]['created_at']
    return last_pull


def get_repo_data(json_data: dict) -> list:
    repo_dicts = json_data['items']
    repos_list = list()
    for repo_dict in repo_dicts:
        certain_repo_data = dict()
        certain_repo_data['_id'] = repo_dict['name']
        certain_repo_data['repo_name'] = repo_dict['name']
        certain_repo_data['full_repo_name'] = repo_dict['full_name']
        certain_repo_data['repo_link'] = repo_dict['html_url']
        certain_repo_data['repo_creation_date'] = repo_dict['created_at']
        certain_repo_data['repo_license'] = repo_dict['license']
        certain_repo_data['repo_last_pull'] = get_last_pull(certain_repo_data['full_repo_name'])
        certain_repo_data['repo_last_issue'] = get_last_issue(certain_repo_data['full_repo_name'])
        certain_repo_data['repo_language_percentage'] = get_language_percentage(certain_repo_data['full_repo_name'])
        repos_list.append(certain_repo_data)
    return repos_list


def run():
    json_data = get_json(search_api_link)
    repos_data = get_repo_data(json_data)
    print(repos_data)
    mongo_instance = mongodb_storage.MongoDBStorage()
    for repo in repos_data:
        mongo_instance.run(repo)


if __name__ == '__main__':
    run()
