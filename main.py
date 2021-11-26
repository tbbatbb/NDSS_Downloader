#!python3
# -*- encoding: utf-8 -*-

import re, urllib, requests, time, html
from os import path

header = {
	'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
	'accept-encoding': 'gzip, deflate, br',
	'accept-language': 'en-US,en;q=0.9,en-GB;q=0.8,zh-CN;q=0.7,zh;q=0.6',
	'cache-control': 'no-cache',
	'dnt': '1',
	'pragma': 'no-cache',
	'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
	'sec-ch-ua-mobile': '?0',
	'sec-fetch-dest': 'document',
	'sec-fetch-mode': 'navigate',
	'sec-fetch-site': 'none',
	'sec-fetch-user': '?1',
	'upgrade-insecure-requests': '1',
	'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36'
}
base_url = 'https://www.ndss-symposium.org'
reg_paper_title = re.compile(r'<p><strong>(?P<title>.*?)(?:</strong>|<br>)+(?P<authors>.*?)(?:<br>)?</p>')
reg_pdf_url = re.compile(r'<a role="button" class="btn btn-light btn-sm" href="(?P<pdf_url>.*?)">Paper</a>')

def strip_title(paper_name):
    '''
    Transfer Name Of The Paper To URL
    '''
    return re.sub(r'[^0-9a-zA-Z- \.µ]', '', html.unescape(paper_name)).replace(' ', '-').replace('µ', 'mu').lower()


def list_papers(html):
    '''
    Retrieve Title And Authors Of Papers Listed In Web Page Based On CSS Style
    '''
    return list(map(lambda g: dict(zip(['title', 'authors'], g)), reg_paper_title.findall(html)))


def get_pdf_url(html):
    '''
    Extract URL For PDF File From HTML Content
    '''
    return reg_pdf_url.findall(html)[0] if len(reg_pdf_url.findall(html)) > 0 else ''


def download_pdf(url, save_to):
    '''
    Download And Save PDF From URL Given
    '''
    if path.isfile(save_to):
        return
    try:
        resp = requests.get(url, headers=header)
        if resp.status_code != 200:
            print('Failed')
            return
        open(save_to, 'wb').write(resp.content)
        time.sleep(3)
    except Exception as e:
        print(e)


def get_html(url):
    '''
    Retrive HTML Content
    '''
    try:
        resp = requests.get(url)
        return resp.text if resp.status_code == 200 else ''
    except Exception as e:
        print(e)
        return ''


def download_with_title(title, save_to):
    '''
    Download PDF File With Title Of Paper Given
    '''
    paper_page_html = get_html(base_url + '/ndss-paper/' + strip_title(title))
    if len(paper_page_html) < 0:
        return
    download_pdf(get_pdf_url(paper_page_html), save_to)


def download_with_symposia(symposia, save_to_dir):
    '''
    Download All Paper In A Symposia
    '''
    html = get_html(base_url + '/' + symposia + '/accepted-papers/')
    if len(html) < 0:
        return
    papers = list_papers(html)
    for paper in papers:
        print('Downloading ' + paper['title'])
        download_with_title(paper['title'], path.join(save_to_dir, strip_title(paper['title']) + '.pdf'))


if __name__ == '__main__':
    year = input('Which Year Do You Want To Download > ')
    dst_dir = input('Store To? > ')
    download_with_symposia('ndss' + year, dst_dir)
