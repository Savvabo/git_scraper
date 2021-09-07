import requests
import mongodb_storage
import const
from dataclasses import dataclass

search_api_link = f'{const.GIT_API}/search/repositories?q=stars:{const.STARS_COUNT}'


def get_json(link: str) -> dict:
    proxy_dict = {'http': const.PROXIES, 'https': const.PROXIES}
    response = requests.request(  # PROXY
        'GET',
        link,
        headers=const.HEADERS,
        proxies=proxy_dict if const.USER_PROXY else None)
    content = response.json()
    return content


def get_language_percentage(repo_name: str) -> dict:
    language_api_link = f'{const.GIT_API}/repos/{repo_name}/languages'
    language_api_dict = get_json(language_api_link)
    language_dict = {}
    if len(language_api_dict) != 0:
        keys = [*language_api_dict]
        values = list(language_api_dict.values())
        values_sum = sum(values)
        values = list(map(lambda x: (x * 100) / values_sum, values))
        language_dict = dict(zip(keys, values))
    return language_dict


def get_last_data(repo_name: str, suffix: str) -> str:
    issue_api_link = f'{const.GIT_API}/repos/{repo_name}/{suffix}?per_page=1'
    last_data = get_json(issue_api_link)[0]['created_at']
    return last_data


def get_last_issue(repo_name: str) -> str:
    return get_last_data(repo_name, 'issues')


def get_last_pull(repo_name: str) -> str:
    return get_last_data(repo_name, 'pulls')


@dataclass
class RepositoryData:
    _id: str
    full_repo_name: str
    repo_link: str
    repo_creation_date: str
    repo_license: dict
    repo_last_pull: str
    repo_last_issue: str
    repo_language_percentage: dict


def get_repo_data(json_data: dict) -> list:
    repo_dicts = json_data['items']
    repos_list = list()
    for repo_dict in repo_dicts:
        repository_dataclass = RepositoryData(
            repo_dict['name'],
            repo_dict['full_name'],
            repo_dict['html_url'],
            repo_dict['created_at'],
            repo_dict['license'],
            get_last_pull(repo_dict['full_name']),
            get_last_issue(repo_dict['full_name']),
            get_language_percentage(repo_dict['full_name']),
        )
        repos_list.append(repository_dataclass)
        # certain_repo_data = dict()
        # certain_repo_data['_id'] = repo_dict['name']
        # certain_repo_data['full_repo_name'] = repo_dict['full_name']
        # certain_repo_data['repo_link'] = repo_dict['html_url']
        # certain_repo_data['repo_creation_date'] = repo_dict['created_at']
        # certain_repo_data['repo_license'] = repo_dict['license']
        # certain_repo_data['repo_last_pull'] = get_last_pull(certain_repo_data['full_repo_name'])
        # certain_repo_data['repo_last_issue'] = get_last_issue(certain_repo_data['full_repo_name'])
        # certain_repo_data['repo_language_percentage'] = get_language_percentage(certain_repo_data['full_repo_name'])
        # repos_list.append(certain_repo_data)
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
