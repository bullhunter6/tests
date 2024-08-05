import requests
from bs4 import BeautifulSoup
import time
from utils.db_utils import save_article
import logging
from datetime import datetime
from utils.keywords import CREDIT_RATING_KEYWORDS

logging.basicConfig(level=logging.DEBUG)

def is_credit_rating_related(title, summary):
    content = title.lower() + " " + summary.lower()
    matched_keywords = [keyword for keyword in CREDIT_RATING_KEYWORDS if keyword.lower() in content]
    return matched_keywords

def parse_date(date_str):
    for fmt in ("%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    logging.error(f"Invalid date format: {date_str}")
    return None

def clean_summary(html_summary):
    soup = BeautifulSoup(html_summary, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)
    return text[:200] + '...' if len(text) > 200 else text

def get_full_summary(url):

  payload = {}
  headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'cookie': 'imf^#lang=en; ASP.NET_SessionId=2rsrxdisgjzipn5alivkj2ii; cookie_persistence=^!61XqRP7zgMJ/B5a0IZLUXH4EId3rOBTIMFMTbS+V2rr7DpD3xaJiMPfoyatwmPkeMJKf+V6AHSNb7eg=; ak_bmsc=E4DECFB9F37C491CDBF7863A0D04B9AC~000000000000000000000000000000~YAAQLPttaABedv6QAQAAi/RrAhiO4i1xn6MYSwAyPfR/gy2plqnkKFjP6deejPDttMjQTvksAmPPPWs3dzEZwyKHqTo6cMeY9Gts2CEe8ZLhFIoNlkHVK+2STejq2QN1/EN79MsiWfSd/DJSAYKIGbEss8sxl+TkW/stqvJr5p1Rj8IlTozAr5bkE68rjHFmad7n6EezBBw5280wSQQ4HHuLswMsuZtl7j9VuH2nED3VCNgLZcXUV2p9dpsWL+bAvIZC5CiB1GRD5jLqowiKwo2YbagAQo1kQgYKjKpnU+2GY+kAonetzzlDSnoqbrueQYCXFy/19k5CYM7+OYPOONz4TPj1wC95YsRhZVyBuyXhT+E39Ext2FveEYBFgbWwx6zT2Qnz; _ga=GA1.1.137989144.1722322499; _parsely_session={%22sid%22:1%2C%22surl%22:%22https://www.imf.org/en/News/SearchNews^#sort=%2540imfdate%2520descending%22%2C%22sref%22:%22%22%2C%22sts%22:1722322499777%2C%22slts%22:0}; _parsely_visitor={%22id%22:%22pid=73a99888-3367-4437-9444-9a659e082899%22%2C%22session_count%22:1%2C%22last_session_ts%22:1722322499777}; s_fid=7E962ED66D0890C2-3ACC18690ADAD180; s_vnum=1722456000791%26vn%3D1; s_invisit=true; s_cc=true; s_vi=[CS]v1|3354472ABA9008DD-60001BCCE0579478[CE]; fpestid=WQINKHrGgHUxYiBdCaBAHj56GKioe7rsMz3WLE8eYa7Rzsz7NXVlP9v2Vpz6n16gfBB0_Q; coveo_visitorId=c202f032-6ff7-be37-ea50-3ded78615321; TS01e41fe4=01250698b2eae05c07b43678f96cbbac21e1375da40d8e891b43605cf693b2de88b2a73dfd9829b9c10d86471371e88a6a19ffa8574b44ed783ec6ae1b84ef8c2edb13db104431dfd2f7c77f110596a96c632cc9070768170394fea6260ccf6b1c300b7dfe; _ga_CPJPTDPL31=GS1.1.1722322499.1.1.1722323169.0.0.0; s_ppn=News%3AArticles%3A2024%3Apr24293-egypt-imf-exec-board-completes-3rd-rev-extended-arr-eff; s_ips=945; s_sq=%5B%5BB%5D%5D; bm_sv=9E779AB5A4602E5740637CD499C54E36~YAAQT/ttaKOuVf6QAQAAwjV2AhhEZ8/2zWWuCrJ8ySnyDxFaXvQ/U2vyed/JHAjw4wzS80LE/PJw4aqk44LVEOVQAVTWKbTQxUdOYW0RZDTKzkj+rg0aOer4MVtTBN4XC6PMfhvgeblGk0OPJ1xfHxTJvcMWsBnWjOSgvYj+xkp6kv05Eb3rGHRunwo+PaCcd3lmjdE6v4pK1VxnskGmgnxSGEoMuzPUbrh9PLku/MvHDr+qCDORLralaBHdRQ==~1; s_tp=2951; s_ppv=News%253AArticles%253A2024%253Apr24293-egypt-imf-exec-board-completes-3rd-rev-extended-arr-eff%2C32%2C73%2C32%2C2145%2C3%2C2; _4c_=lVLLbtswEPyVgIecQvGpBw0EhWL7UjQJ0hboMZDFlS3ElgSSsZIG%2BfcubdnusZUAYnc4Oxxy94OMG%2BjITORSKvy11FrfkBd492T2Qeohrvu4vLotmZFNCIOfMTaOY9LumqR3awYde4DRs9KFtt6CZ5JLzXjOpGGDQ0mjKKzfh0CxgsIb1HTVV87Sut8NWwjgqcLMwR43A3QWLK2co9A05IbUvQU8WJhE8EQgEH5jKjXHEDq0RgZnMX68%2F%2Fn9%2BW5Zzh8f%2FvLpR1j5UAV%2Fdrti3jNMdlXbDa63TLCvP6hMJE84%2FbZ4umdei9QIk%2BeGF1pkX8qnu1tx3bT2Nl%2BaTC4XWbbgheFzSVU5n4siM7xclAtR8OvyaXkbTUbl1zo8h%2FchukcXV96%2B4IaFfVvD89jasInXynl%2BQTfQrjchwjw7wIOLSZJiPLad7cdLoZDigp4LjY7cletHD7F2vnH9Dq6EjHI99pT8OlR4TB004NyBhplvQ3Q6PdME4BwcMXrEhvjeCoNtX1fbyMfhQSrUoe27%2BO542lCtgXzekLfjWGlu0pyLTGLrAs5QkWkeP2S41k7zRazSsjErnBSdZlRnOdBKyYquVJobAVkjZUEmTcW5KbQxhhsU2bcnjUYVKerUtK4zTXVlc2oqBbTgtbCmylOoUnL2hcNu0Fd68oXtm2wN20lRXMgqK%2FBAqU5kfb7EsJ%2FY6l%2BufGwNPb0The5%2F6j8%2F%2FwA%3D; bm_sv=9E779AB5A4602E5740637CD499C54E36~YAAQLPttaFYGd/6QAQAA6tp3AhivtXtUK99E3ukRFol0Hw65ilCKpljx2XyB5/ciWOb4lJSJNtM5esqFMAqXlgqLM4ZpenN8gxFD5FEEdCb/4Acitf4duchOUzaz8UMQl1iymA7ABUMU4CcQpyKfxus67b9gDPaTgznAOMVJ6KWQrTxmMPNU2YZa/TE5ItTQF58d6D0jbJ4LfaEnU+3iU1qk2k+66lazCpgobF7yGpENr3H/aSKfvSgXi9lVzw==~1; TS01e41fe4=01250698b203d78fe97b8d0485d19c4d12ee6ec196821c35d62c2ad79181a0a71b32c1e2a74348fb0f378f73fdd494c8d4c5ff707b991c85b88fb65682ca2894f555214a60d853db2677d0b4fd76dbc2da3c5a8097942d77b48b3997d85e918e6775050346; cookie_persistence=!HFhiMps4I1D+sda0IZLUXH4EId3rOCFi8wDwaLR9lf4gi88J9l40tT1yRIobf0nwvLEEYgG+p1crM90=',
    'priority': 'u=0, i',
    'referer': 'https://www.imf.org/en/News/SearchNews',
    'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
  }

  for _ in range(5):
    try:
        response = requests.get(url, headers=headers, data=payload)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
            
        article_text = ''
        for p in paragraphs:
            article_text += p.get_text() + '\n'
            
        return article_text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        time.sleep(2)
  return "Failed to retrieve the article"


def imf_1_articles():
    url = "https://www.imf.org/coveo/rest/search/v2?sitecoreItemUri=sitecore%3A%2F%2Fweb%2F%7B5ABCDAEC-30A6-4F1B-835C-5D1AB8F77FB5%7D%3Flang%3Den%26amp%3Bver%3D2&siteName=imf"

    payload = "actionsHistory=%5B%7B%22name%22%3A%22Query%22%2C%22time%22%3A%22%5C%222024-07-30T06%3A55%3A13.686Z%5C%22%22%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%225ABCDAEC30A64F1B835C5D1AB8F77FB5%22%2C%22time%22%3A%222024-07-30T06%3A55%3A13.641Z%22%7D%2C%7B%22name%22%3A%22Query%22%2C%22time%22%3A%22%5C%222024-07-30T06%3A54%3A59.630Z%5C%22%22%7D%5D&referrer=&analytics=%7B%22clientId%22%3A%22c202f032-6ff7-be37-ea50-3ded78615321%22%2C%22documentLocation%22%3A%22https%3A%2F%2Fwww.imf.org%2Fen%2FNews%2FSearchNews%23sort%3D%2540imfdate%2520descending%22%2C%22documentReferrer%22%3A%22%22%2C%22pageId%22%3A%225ABCDAEC30A64F1B835C5D1AB8F77FB5%22%7D&visitorId=c202f032-6ff7-be37-ea50-3ded78615321&isGuestUser=false&aq=((((((((((((%40imftype%3D%3D%22News%20Article%22%20OR%20%40imftype%3D%3D%22Press%20Release%22)%20OR%20%40imftype%3D%3DCommunique)%20OR%20%40imftype%3D%3D%22Mission%20Concluding%20Statement%22)%20OR%20%40imftype%3D%3D%22News%20Brief%22)%20OR%20%40imftype%3D%3D%22Public%20Information%20Notice%22)%20OR%20%40imftype%3D%3DSpeech)%20OR%20%40imftype%3D%3D%22Statements%20at%20Donor%20Meeting%22)%20OR%20%40imftype%3D%3DTranscript)%20OR%20%40imftype%3D%3D%22Views%20and%20Commentaries%22)%20OR%20%40imftype%3D%3D%22Blog%20Page%22)%20NOT%20%40z95xtemplate%3D%3D(ADB6CA4F03EF4F47B9AC9CE2BA53FF97%2CFE5DD82648C6436DB87A7C4210C7413B)))%20(%40imfdate)&cq=(%40z95xlanguage%3D%3Den)%20(%40z95xlatestversion%3D%3D1)%20(%40source%3D%3D%22Coveo_web_index%20-%20PRD93-SITECORE-IMFORG%22)&searchHub=SearchNews&locale=en&maximumAge=900000&firstResult=0&numberOfResults=10&excerptLength=200&fieldsToExclude=%5B%22createdby%22%2C%22parsedcreatedby%22%2C%22updatedby%22%2C%22parsedupdatedby%22%2C%22z95xeditor%22%2C%22z95xcreator%22%5D&enableDidYouMean=true&sortCriteria=%40imfdate%20descending&queryFunctions=%5B%5D&rankingFunctions=%5B%5D&groupBy=%5B%7B%22field%22%3A%22%40z95xtemplatename%22%2C%22maximumNumberOfValues%22%3A20%2C%22sortCriteria%22%3A%22AlphaAscending%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%2C%22allowedValues%22%3A%5B%5D%7D%5D&facetOptions=%7B%7D&categoryFacets=%5B%5D&retrieveFirstSentences=true&timezone=Asia%2FDubai&enableQuerySyntax=false&enableDuplicateFiltering=true&enableCollaborativeRating=false&debug=false&allowQueriesWithoutKeywords=true"
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJ2OCI6dHJ1ZSwidG9rZW5JZCI6InN6ejQ0eXZibnp2Z3NqY3NqYmhoYmZrbHRtIiwib3JnYW5pemF0aW9uIjoiaW1mcHJvZHVjdGlvbjU2MXMzMDh1IiwidXNlcklkcyI6W3sidHlwZSI6IlVzZXIiLCJuYW1lIjoiYW5vbnltb3VzIiwicHJvdmlkZXIiOiJFbWFpbCBTZWN1cml0eSBQcm92aWRlciJ9XSwicm9sZXMiOlsicXVlcnlFeGVjdXRvciJdLCJpc3MiOiJTZWFyY2hBcGkiLCJleHAiOjE3MjI0MDU2MjUsImlhdCI6MTcyMjMxOTIyNX0.UcyZPMoX8G-Hv5W6nJFDZmR2Tv6MvFckbXzvtWq6QqU',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'cookie': 'imf^#lang=en; ASP.NET_SessionId=2rsrxdisgjzipn5alivkj2ii; cookie_persistence=^!61XqRP7zgMJ/B5a0IZLUXH4EId3rOBTIMFMTbS+V2rr7DpD3xaJiMPfoyatwmPkeMJKf+V6AHSNb7eg=; TS01e41fe4=01250698b20f1f47dffd52e19eb1c46d0dfa0864c0821c35d62c2ad79181a0a71b32c1e2a74348fb0f378f73fdd494c8d4c5ff707b991c85b88fb65682ca2894f555214a60d853db2677d0b4fd76dbc2da3c5a809717ec02ae57333a310987cbae9eab5e87; ak_bmsc=E4DECFB9F37C491CDBF7863A0D04B9AC~000000000000000000000000000000~YAAQLPttaABedv6QAQAAi/RrAhiO4i1xn6MYSwAyPfR/gy2plqnkKFjP6deejPDttMjQTvksAmPPPWs3dzEZwyKHqTo6cMeY9Gts2CEe8ZLhFIoNlkHVK+2STejq2QN1/EN79MsiWfSd/DJSAYKIGbEss8sxl+TkW/stqvJr5p1Rj8IlTozAr5bkE68rjHFmad7n6EezBBw5280wSQQ4HHuLswMsuZtl7j9VuH2nED3VCNgLZcXUV2p9dpsWL+bAvIZC5CiB1GRD5jLqowiKwo2YbagAQo1kQgYKjKpnU+2GY+kAonetzzlDSnoqbrueQYCXFy/19k5CYM7+OYPOONz4TPj1wC95YsRhZVyBuyXhT+E39Ext2FveEYBFgbWwx6zT2Qnz; _ga=GA1.1.137989144.1722322499; _parsely_session={%22sid%22:1%2C%22surl%22:%22https://www.imf.org/en/News/SearchNews^#sort=%2540imfdate%2520descending%22%2C%22sref%22:%22%22%2C%22sts%22:1722322499777%2C%22slts%22:0}; _parsely_visitor={%22id%22:%22pid=73a99888-3367-4437-9444-9a659e082899%22%2C%22session_count%22:1%2C%22last_session_ts%22:1722322499777}; s_fid=7E962ED66D0890C2-3ACC18690ADAD180; s_ppn=News%3ASearchNews%23sort%3D%2540imfdate%2520descending; s_vnum=1722456000791%26vn%3D1; s_invisit=true; s_cc=true; s_vi=[CS]v1|3354472ABA9008DD-60001BCCE0579478[CE]; fpestid=WQINKHrGgHUxYiBdCaBAHj56GKioe7rsMz3WLE8eYa7Rzsz7NXVlP9v2Vpz6n16gfBB0_Q; _4c_=fVLvT9swEP1XkCf4hBP%2FihNXqqbS9ss0QIxJ%2B4jS%2BNpElCSyTTOG%2BN85t2mZhrR8sO5e3j2%2FO98rGWpoyYTnQkghMi65UZfkEV48mbySqo%2FnLh7PbksmpA6h95M0HYYhaZ7WSec2KbTpDQw%2BvYfSVXUMv%2FjOhem5YkixZYBzwSz4ClrbtBtySarOAopxk3CWcATCH0yFYhhCi9eR3lmMb69%2F%2Fni4Ws7mtzd%2F3e0HWPlQBn9ysEq9TzF5Kpu2d51NefrtnopEsITR74u769SrImOaca6VzPOvs7urKb9YN3aaL40Wy4XWC1YYNhdUzuZzXmjDZovZghfsYna3nEaPUfi5Cg%2FhpY%2Fm0cSZt4%2F4w8KuqeBhaGyoY1c5yz%2FQGppNHSLM9B7uXUySDOOhaW03%2FFs4oqdCoyJ35brBQ6yd1657gjMuIrnDZyK%2F9hUeUwdrcG5Pw8w3ITodpzQC%2BLQHjB6wPo479rftqnIb%2BbgPSIUqNF0bx4639eUGyNsl%2BX3YFMWKwhgjcFNCwLUotGLxQ4Zr7LgyxEol1mYlKahMU6VzoKUUJV3JLDcc9FqIgoyakjFTKNRkBkV2zVFjLYsMdSpaVVpRVdqcmlICLVjFrSnzDMqMnHxJoQRq8KMvfL7RVr8dFfkHWep9E%2FJIVqcm%2Bt0n9rFl%2Bbnlw9PQ45wotP%2Bp%2FzSyt7d3; _ga_CPJPTDPL31=GS1.1.1722322499.1.1.1722322513.0.0.0; s_ips=945; s_tp=1020; s_ppv=News%253ASearchNews%2523sort%253D%252540imfdate%252520descending%2C93%2C93%2C93%2C945%2C1%2C1; bm_sv=9E779AB5A4602E5740637CD499C54E36~YAAQLPttaChhdv6QAQAAEC9sAhgHEnICbHgx2J8dju06mfJiLZfuWjIoJHgXH5N2zfnnKsma0+8TS+JsxyWiPkeKs/aoI73Vwy9qjSlwZmKfZj9EDmBhfAq9/nndisuFTfo8psT2lJGjNaQNC/S1jhwgEYh4JFiBTEI0AcmHZvtuxt8hYGwHASlu3iqk7C3oZp7uwX151A8TQVopKBR+i6fHRtc8UDQx7HjhCpJ5puriGCJY7nhwRys1kJ8F~1; coveo_visitorId=c202f032-6ff7-be37-ea50-3ded78615321; bm_sv=9E779AB5A4602E5740637CD499C54E36~YAAQT/ttaGs9Vf6QAQAAB0NuAhg4Q4+827TqUvwe7p59Lt4dw64X0Kfi5f1vMA9eAkPSLfv+XUA4gZjV+tVmTEA/aNk0W5dnZuecLZ/N5W75mip6dUpBwCIUuCesqJ2MRZFk5Nn7w4pCM7rgtqhcORTV/0WDj+dU2U+qgI5gQM2yRaM/XBjoLYzB4WP63Zm9Gx0X8bIquBIw2Q/1VM6nl2J1ca2WQk5LaZhM9BCq8sPPjcnWFZLe72SgAhu3~1; TS01e41fe4=01250698b203d78fe97b8d0485d19c4d12ee6ec196821c35d62c2ad79181a0a71b32c1e2a74348fb0f378f73fdd494c8d4c5ff707b991c85b88fb65682ca2894f555214a60d853db2677d0b4fd76dbc2da3c5a8097942d77b48b3997d85e918e6775050346; cookie_persistence=!HFhiMps4I1D+sda0IZLUXH4EId3rOCFi8wDwaLR9lf4gi88J9l40tT1yRIobf0nwvLEEYgG+p1crM90=',
        'origin': 'https://www.imf.org',
        'priority': 'u=1, i',
        'referer': 'https://www.imf.org/en/News/SearchNews',
        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    }

    response = requests.post(url, headers=headers, data=payload)
    response.raise_for_status()
    response_json = response.json()
    articles_data = response_json.get('results', [])

    articles = []

    for article in articles_data:
        title = article.get('title', 'No title')
        url = article.get('printableUri')
        date = article.get('raw', {}).get('imfdatedisplay', 'No date')
        full_summary = get_full_summary(url)
        summary = clean_summary(full_summary)

        matched_keywords = is_credit_rating_related(title, full_summary)
        if not matched_keywords:
            logging.debug(f"Skipping non-relevant article: {title}")
            continue

        parsed_date = parse_date(date)
        if not parsed_date:
            continue

        article_data = {
            'title': title,
            'url': url,
            'date': parsed_date,
            'summary': summary,
            'source': 'IMF',
            'keywords': ', '.join(matched_keywords)
        }
        
        save_article(article_data)
        logging.debug(f"Saved article to database: {title}")

    return articles
