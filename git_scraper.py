import requests
from parsel import Selector
import mongodb_storage

STARS_COUNT = '>100000'
search_api_link = "https://api.github.com/search/repositories?q=stars:{}".format(STARS_COUNT)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0'
}
PROXIES = 'http://5.189.151.227:24001'


def get_json(link):
    response = requests.request("GET", link, headers=HEADERS)
    content = response.json()
    return content

# def get_selector(link):
#     response = requests.request("GET", link, headers=HEADERS, proxies=PROXIES)
#     content = response.text()
#     return content


def get_main_info(json_data: dict):
    repo_dicts = json_data['items']
    repo_list = list()
    for repo_dict in repo_dicts:
        certain_repo_data = dict()
        certain_repo_data['repo_name'] = repo_dict['name']
        certain_repo_data['full_repo_name'] = repo_dict['full_name']
        certain_repo_data['repo_link'] = repo_dict['html_url']
        certain_repo_data['repo_creation_date'] = repo_dict['created_at']
        certain_repo_data['repo_license'] = repo_dict['license']
        certain_repo_data['repo_last_pull'] = repo_dict['updated_at']
        repo_list.append(certain_repo_data)
    print(repo_list)
    return repo_list


def get_repo_names():
    repo_list = get_main_info(get_json(search_api_link))
    all_repo_names = list()
    for repo in repo_list:
        all_repo_names.append(repo['full_repo_name'])
    return all_repo_names

def get_language_percentage():
    repo_names = get_repo_names()
    all_values = list()
    for repo_name in repo_names:
        language_api_link = 'https://api.github.com/repos/{}/languages'.format(repo_name)
        value = get_json(language_api_link).values()
        all_values.append(value)
    print(all_values)
    return 1

get_language_percentage()

def get_site_time(selector: Selector):
    site_time = selector.xpath('//*[@class="rankmini-daily"]/div/text()').get().split()[0]
    return site_time


def get_keywords_traffic(selector: Selector):
    keywords_traffic = dict()
    rows = selector.xpath('//*[@id="card_mini_topkw"]//div[@class="Row"]')
    for row in rows:
        keyword = row.xpath('.//span/text()')[0].get()
        percent = row.xpath('.//span/text()')[1].get()
        percent = float(percent.strip('%'))
        keywords_traffic[keyword] = percent
    return keywords_traffic


def get_traffic_sources(selector: Selector):
    values_selector = selector.xpath('//*[@class="FolderTarget"]/div[1]/div/div[2]/span/text()').getall()
    sources_keys = selector.xpath('//*[@class="FolderTarget"]//*[@class="Third"]/@title').getall()
    sources_values = [float(value.split()[0].strip('%')) for value in values_selector]
    sources_dict = dict(zip(sources_keys, sources_values))
    return sources_dict


def get_total_site_linking_in(selector: Selector):
    total_site_linking_in = selector.xpath('//*[@class="enun"]/span[1]/text()').get()
    return total_site_linking_in


def get_alexa_data():
    json_data = get_json(search_api_link)
    # selector = get_selector()
    alexa_data = dict()
    alexa_data['site_rank'] = get_main_info(json_data)
    # alexa_data['site_time'] = get_site_time(selector)
    # alexa_data['keywords_traffic'] = get_keywords_traffic(selector)
    # alexa_data['traffic_sources'] = get_traffic_sources(selector)
    # alexa_data['total_site_linking_in'] = get_total_site_linking_in(selector)
    return alexa_data


def run():
    alexa_data = get_alexa_data()
    mongo_instance = mongodb_storage.MongoDBStorage()
    # mongo_instance.run(alexa_data, WEBSITE)


if __name__ == '__main__':
    run()
