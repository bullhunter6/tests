import requests
import json
from utils.db_utils import save_article
import logging

logging.basicConfig(level=logging.DEBUG)


def fitch_articles():
    url = "https://api.fitchratings.com/"
    payload = json.dumps({
    "query": "query Search($item: SearchItem, $term: String!, $filter: SearchFilterInput, $sort: String, $dateRange: String, $offset: Int, $limit: Int) { search( item: $item term: $term filter: $filter sort: $sort dateRange: $dateRange offset: $offset limit: $limit ) { totalResearchHits totalRacsHits totalEntityHits totalIssueHits totalVideoHits totalEventHits totalWebinarHits totalAudioHits totalPageHits totalHits audio { image { poster __typename } createdDate permalink title __typename } event { title permalink eventType locationName startDate endDate timeZone image { poster thumbnail __typename } __typename } webinar { title permalink eventType locationName startDate endDate timeZone image { poster thumbnail __typename } __typename } research { docType marketing { contentAccessType { name slug __typename } language { name slug __typename } analysts { firstName lastName role sequenceNumber type __typename } countries { name slug __typename } sectors { name slug __typename } __typename } title permalink abstract reportType publishedDate ratingOutlookCode ratingOutlook sectorOutlookCode sectorOutlook __typename } racs { docType marketing { contentAccessType { name slug __typename } language { name slug __typename } analysts { firstName lastName role sequenceNumber type __typename } countries { name slug __typename } sectors { name slug __typename } __typename } title permalink abstract reportType publishedDate __typename } entity { marketing { analysts { firstName lastName role sequenceNumber type __typename } countries { name slug __typename } sectors { name slug __typename } __typename } name ultimateParent ratings { orangeDisplay ratingCode ratingAlertCode ratingActionDescription ratingAlertDescription ratingTypeDescription ratingEffectiveDate correctionFlag ratingChangeDate __typename } permalink __typename } issue { permalink issue issueName issuer entityName debtLevel deal className subClass transaction { description id securityList { typeDescription __typename } __typename } ratingDate maturityDate cusip isin originalAmount currency couponRate subgroupName ratableTypeDescription commercialPaperType marketing { analysts { firstName lastName type sequenceNumber __typename } countries { name slug __typename } sectors { name slug __typename } __typename } ratings { orangeDisplay ratableName ratingActionDescription ratingAlertCode ratingAlertDescription ratingCode ratingEffectiveDate ratingLocalActionDescription ratingLocalValue ratingTypeDescription ratingTypeId recoveryEstimate recoveryRatingValue solicitFlag sortOrder filterRatingType filterNationalRatingType filterInvestmentGradeType correctionFlag ratingChangeDate __typename } __typename } video { image { poster __typename } createdDate permalink title __typename } page { title slug image { poster thumbnail __typename } __typename } totalHits __typename } }",
    "variables": {
        "item": "ALL",
        "term": "",
        "filter": {
        "country": [
            "",
            "Kyrgyzstan",
            "Kazakhstan",
            "Uzbekistan",
            "United Arab Emirates",
            "Saudi Arabia",
            "Qatar",
            "Oman",
            "Russia"
        ],
        "language": [
            "English",
            "Russian"
        ],
        "region": [
            ""
        ],
        "sector": [
            "",
            "Banks",
            "Sovereigns",
            "Islamic Finance",
            "Supranationals, Subnationals, and Agencies"
        ],
        "topic": [
            ""
        ]
        },
        "sort": "",
        "dateRange": "",
        "offset": 0,
        "limit": 24
    }
    })
    headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://www.fitchratings.com',
    'priority': 'u=1, i',
    'referer': 'https://www.fitchratings.com/',
    'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code == 200:
        data = response.json()
        research_articles = data['data']['search']['research']
        results = []
        for article in research_articles:
            title = article['title']
            abstract = article['abstract']
            permalink = article['permalink']
            published_date = article['publishedDate'].split("T")[0]
            article_url = "https://www.fitchratings.com" + permalink

            article_data = {
                'title': title,
                'date': published_date,
                'summary': abstract,
                'url': article_url,
                'source': 'Fitch',
                'keywords': 'Without keywords'
            }
            save_article(article_data)
            logging.debug(f"Saved article to database: {title}")
            results.append(article_data)

    return results