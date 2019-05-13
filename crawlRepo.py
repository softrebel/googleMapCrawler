from config import *
import mysql.connector


class crawlRepo:
    def __init__(self):
        True

    def insertEntity(self, entity, search_input, status=status_in_queue):
        query = 'INSERT INTO place(category,image,geoPoint,title,subtitle,' \
                'phone,website,hours,score,address_en,address_fa,lastCrawlDate,numberOfTry,searchInput,ProfileShahrestanID,status)' \
                'VALUES("{category}","{image}","{geoPoint}","{title}","{subtitle}","{phone}",' \
                '"{website}","{hours}","{score}","{address_en}","{address_fa}",NOW(),1,"{searchInput}",{ProfileShahrestanID},{status}) ' \
                'ON DUPLICATE KEY ' \
                'UPDATE ' \
                'category="{category}",image="{image}",geoPoint="{geoPoint}",title="{title}",subtitle="{subtitle}",phone="{phone}"' \
                ',website="{website}",hours="{hours}",score="{score}",address_en="{address_en}",ProfileShahrestanID={ProfileShahrestanID},status={status},' \
                'address_fa="{address_fa}",lastCrawlDate=NOW(),numberOfTry=numberOfTry+1;' \
            .format(category=entity['category'], image=entity['image'], geoPoint=entity['geo_point'].strip(),
                    title=entity['title'], subtitle=entity['subtitle'], phone=entity['phone'],
                    website=entity['website'], hours=entity['hours'], score=entity['score'],
                    address_en=entity['address_en'], address_fa=entity['address_fa'], searchInput=search_input,
                    ProfileShahrestanID=entity['ProfileShahrestanID'], status=status)
        return self.setResult(query)

    def checkEntityExist(self, entity):
        response = False
        try:
            cnx = mysql.connector.connect(**dbConfig)
            cursor = cnx.cursor(buffered=True)
        except mysql.connector.Error as err:
            logging.error("Failed connect db: {}".format(err))
            return 'Error'
        try:
            query = 'SELECT ID FROM place WHERE geoPoint = "{geoPoint}"'.format(geoPoint=entity['geo_point'].strip())
            cursor.execute(query)
            if cursor.rowcount == 0:
                response = False  # Not Exist
            else:
                response = True  # Record Already Exist
        except mysql.connector.Error as err:
            logging.error("Failed check Exist: {}".format(err))
            response = 'Error'
        finally:
            cursor.close()
            cnx.close()
            return response

    def checkTitleExist(self, title, profileShahrestanID, score=None):
        response = False
        try:
            cnx = mysql.connector.connect(**dbConfig)
            cursor = cnx.cursor(buffered=True)
        except mysql.connector.Error as err:
            logging.error("Failed connect db: {}".format(err))
            return 'Error'
        try:
            title = title.strip()
            query = 'SELECT ID FROM place WHERE (title = "{title}" OR subtitle="{subtitle}") AND profileShahrestanID="{profileShahrestanID}"'.format(
                title=title,
                subtitle=title, profileShahrestanID=profileShahrestanID)
            if score:
                query += 'AND score="{score}"'.format(score=score)
            cursor.execute(query)
            if cursor.rowcount == 0:
                response = False  # Not Exist
            else:
                response = True  # Record Already Exist
        except mysql.connector.Error as err:
            logging.error("Failed check Exist: {}".format(err))
            response = 'Error'
        finally:
            cursor.close()
            cnx.close()
            return response

    def insertPointQueue(self, geoPoint, search_input):
        query = 'INSERT INTO pointsqueue ' \
                '(geoPoint,search_input,status,lastCrawlDate,numberOfTry)' \
                'VALUES' \
                '("{geoPoint}","{searchInput}",1,NOW() ,1)' \
                'ON DUPLICATE KEY ' \
                'UPDATE ' \
                'lastCrawlDate=NOW(),numberOfTry=numberOfTry+1;' \
            .format(geoPoint=geoPoint.strip(), searchInput=search_input)
        return self.setResult(query)

    def setResult(self, query):
        res = False
        try:
            cnx = mysql.connector.connect(**dbConfig)
            cursor = cnx.cursor(buffered=True)
        except mysql.connector.Error as err:
            logging.error("Failed connect db: {}".format(err))
            return res
        try:
            cursor.execute(query)
            cnx.commit()
            res = True
        except mysql.connector.Error as err:
            logging.error("Failed Insert Result member: {}".format(err))
            res = False
        finally:
            cursor.close()
            cnx.close()
            return res

    def checkGeoInTownship(self, geoPoint, profileShahrestanID):
        townshipID = self.getTownship(geoPoint)
        if townshipID:
            if int(townshipID) == profileShahrestanID:
                return True
            else:
                return False
        else:
            return False

    def getTownship(self, geoPoint):
        import requests
        import json
        url = find_gps_point_service + '?gps_point=' + geoPoint
        res = requests.get(url)
        if res.status_code == 200:
            response = json.loads(res.content)
            return response['data']['township_id']
        else:
            logging.error("Failed to call service: {}".format(res.content))
            return False

    def getCategories(self):
        response = False
        try:
            cnx = mysql.connector.connect(**dbConfig)
            cursor = cnx.cursor(buffered=True)
        except mysql.connector.Error as err:
            logging.error("Failed connect db: {}".format(err))
            return 'Error'
        try:
            query = 'SELECT onvan FROM profileghalebsakhtarmajmooeh'
            cursor.execute(query)
            if cursor.rowcount == 0:
                response = False  # Not Exist
            else:
                response = [item[0] for item in cursor.fetchall()]  # query List
        except mysql.connector.Error as err:
            logging.error("Failed get Categories: {}".format(err))
            response = 'Error'
        finally:
            cursor.close()
            cnx.close()
            return response

    def checkCategoryExistForShahrestan(self, category, profileShahrestanID):
        response = False
        try:
            cnx = mysql.connector.connect(**dbConfig)
            cursor = cnx.cursor(buffered=True)
        except mysql.connector.Error as err:
            logging.error("Failed connect db: {}".format(err))
            return 'Error'
        try:
            query = 'SELECT ID FROM place WHERE ProfileShahrestanID={ProfileShahrestanID} AND searchInput="{searchInput}"'.format(
                searchInput=category.strip(), ProfileShahrestanID=profileShahrestanID)
            cursor.execute(query)
            if cursor.rowcount == 0:
                response = False  # Not Exist
            else:
                response = True  # query List
        except mysql.connector.Error as err:
            logging.error("Failed get Categories: {}".format(err))
            response = 'Error'
        finally:
            cursor.close()
            cnx.close()
            return response

    def getSearchPoints(self, category, profileShahrestanID):
        response = False
        try:
            cnx = mysql.connector.connect(**dbConfig)
            cursor = cnx.cursor(buffered=True)
        except mysql.connector.Error as err:
            logging.error("Failed connect db: {}".format(err))
            return 'Error'
        try:
            query = 'SELECT geoPoint FROM place WHERE ProfileShahrestanID={ProfileShahrestanID} AND searchInput="{searchInput}" AND status != {status} ORDER BY ID ASC'.format(
                searchInput=category.strip(), ProfileShahrestanID=profileShahrestanID, status=status_did_progress)
            cursor.execute(query)
            if cursor.rowcount == 0:
                response = False  # Not Exist
            else:
                response = [item[0] for item in cursor.fetchall()]  # query List
        except mysql.connector.Error as err:
            logging.error("Failed get Categories: {}".format(err))
            response = 'Error'
        finally:
            cursor.close()
            cnx.close()
            return response

    def updatePointStatus(self, geoPoint, status):
        query = 'UPDATE place SET status={status},numberOfTry=numberOfTry+1 where geoPoint="{geoPoint}"'.format(
            status=status, geoPoint=geoPoint)
        return self.setResult(query)

    def pointInProgress(self, geoPoint):
        return self.updatePointStatus(geoPoint, status_in_progress)

    def pointDidProgress(self, geoPoint):
        return self.updatePointStatus(geoPoint, status_did_progress)
