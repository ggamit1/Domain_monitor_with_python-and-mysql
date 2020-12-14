import mysql.connector
import socket
import whois  
from urllib.request import ssl, socket
import os
import certifi
import datetime
import requests
import re



def domain_start_and_expire_date(domain_name):
    """
    A function that returns a boolean indicating
    whether a `domain_name` is registered
    """
    row = {}
    try:
        w = whois.whois(domain_name)
        if str(type(w.creation_date)) == "<class 'datetime.datetime'>":
            row["create_date"] = w.creation_date.strftime('%Y-%m-%d %H:%M:%S')
            row['expire_date'] = w.expiration_date.strftime('%Y-%m-%d %H:%M:%S')
        else:
            row["create_date"] = w.creation_date[0].strftime('%Y-%m-%d %H:%M:%S')
            row['expire_date'] = w.expiration_date[0].strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        print("error in socket ")
    return row


def get_ssl_date(base_url, port=443 ):
    """[summary]

    Args:
        base_url (string): give domain name that you want 
        port (int): give your website port if do not know it, use defaults

    Returns:
        dictionary: it,s return dictionary  with startdate and enddate of certificate 
    """
    hostname = base_url
    row = {}
    try:
        context=ssl.create_default_context(cafile=certifi.where())
        with socket.create_connection((hostname, port)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                start_date = ssock.getpeercert()['notBefore']
                expire_date = ssock.getpeercert()['notAfter']
                row = {
                    "start_date": start_date,
                    "expire_date": expire_date
                }
                
    except Exception as error:
        print("error to find ssl expire date: {}".format(error))
    return row

if __name__ == "__main__":
  
    user = 'root'
    password = 'codefire'
    database = 'domain_monitor'
    host = "127.0.0.1"

    try:
        # To connect with database 
        cnx = mysql.connector.connect(user=user, password=password,
                                    host=host,
                                    database=database,
                                )
        cursor = cnx.cursor()
        
        query = "select URL, PORT from domain_info where (Status = 1)"
        cursor.execute(query)
        urls = cursor.fetchall()
        for url in urls:
            # print(url[0],url[1])
            base_url = url[0]
            port =  url[1]
            
            #domain information fatched
            domain_date_dic = domain_start_and_expire_date(base_url)
            # geting date 
            # domain_create_date = domain_date_dic.get('create_date')
            domain_expire_date = domain_date_dic.get('expire_date')
            # update in database 
            # cursor.execute(f"UPDATE domain_info SET Certificate_created_datetime = '{ssl_create_date_obj}' WHERE URL = '{base_url}' ")
            cursor.execute("UPDATE domain_info SET Domain_Expiry_Date = '{}' WHERE URL = '{}' ".format(domain_expire_date, base_url))
            
            # ssl infomation fatched 
            ssl_date_dic = get_ssl_date(base_url, port )
            # geting date 
            ssl_create_date = ssl_date_dic.get('start_date')
            ssl_expire_date = ssl_date_dic.get('expire_date')
            # convert in database date format 
            ssl_expire_date_obj = datetime.datetime.strptime(ssl_expire_date, "%b %d %H:%M:%S %Y %Z")
            ssl_create_date_obj = datetime.datetime.strptime(ssl_create_date, "%b %d %H:%M:%S %Y %Z")
            # update in database 
            cursor.execute("UPDATE domain_info SET Certificate_created_datetime = '{}' WHERE URL = '{}' ".format(ssl_create_date_obj, base_url))
            cursor.execute("UPDATE domain_info SET Certificate_Expiry_date = '{}' WHERE URL = '{}' ".format(ssl_expire_date_obj, base_url))
            
        # commit update
        cnx.commit()
        # close connection
        cnx.close()
    except Exception as er:
        print(f'Error : {er}')