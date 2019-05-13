from map import *
from config import *
from crawlRepo import *

repo = crawlRepo()
categories = repo.getCategories()
for category in categories:
    category = search_input_default
    crawl = mapCrawl(category=category,profileShahrestanID=profileShahrestanID_default,profileShahrestanName=profileShahrestanName_default,crawler=repo)
    checkExist = repo.checkCategoryExistForShahrestan(category, profileShahrestanID_default)
    if checkExist == 'Error':
        logging.error('stopped working because of check category exist')
        break
    if checkExist:
        geo_points = repo.getSearchPoints(category, profileShahrestanID_default)
        if geo_points:
            for geo_point in geo_points:
                status = repo.pointInProgress(geo_point)
                if not status:
                    logging.error('can not change status of record: ' + geo_point)
                crawl.search_start_from_point(geo_point)
                crawl.crawl()
                status = repo.pointDidProgress(geo_point)
                if not status:
                    logging.error('can not change status of record: ' + geo_point)
        else:
            crawl.__del__()
            continue
    else:
        crawl.initial_search()
        crawl.crawl()

    crawl.__del__()
