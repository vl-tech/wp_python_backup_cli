#!/usr/bin/env python3
import sqlite3
from pprint import pprint
import argparse
conn = sqlite3.connect(database='wordpress_support.db')




parser = argparse.ArgumentParser(prog='Create and Restore WP site from database data',description='Supply domain argument to generate data input for the backup/restore')

parser.add_argument('-D','--wp_site',action='store',help='-D/--wp-site Provider domain argument <domain>/<wp_sute>')
args = parser.parse_args()
# class DbTesting:
#     def __init__(self):
#         self.domain_name = 'vladmin-dev.top'
#         self.username = 'vladimir87'
#         self.password = 'this is some pass'
#         self.hostname = 'localhost'
#         self.wp_path = '/home/vladmin-dev.top/public_html'
#         self.backup_folder = 'backup_wp_python_folder'
        
class WpDatabase:
    def __init__(self,domain_name,username,password,hostname,wp_path,backup_folder):
        self.domain_name = domain_name
        self.username = username
        self.password = password
        self.hostname = hostname
        self.wp_path = wp_path
        self.backup_folder = backup_folder
        
    def add_website(self):
        add_new_website = f"""
        INSERT INTO wordpress_sites(domain_name,username,password,hostname,wp_path,backup_folder)
        VALUES('{self.domain_name}',
        '{self.username}',
        '{self.password}',
        '{self.hostname}',
        '{self.wp_path}',
        '{self.backup_folder}')

        """ 
        return  add_new_website
    
        
class GenerateInput:
    def __init__(self) -> None:
        self.domain_name = args.wp_site  
    
    def show_site_data(self):
        query = f"""
                SELECT * FROM wordpress_sites WHERE domain_name='{self.domain_name}'
        """
        return query
    
update_table_data = """

INSERT INTO wordpress_sites(domain_name,username,password,hostname,wp_path,domain_name,backup_folder)

VALUES('python.vladmin.top','vladmint','*Ikmx9j&V%8(%hGBsNb','185.199.38.18','/home/vladmint/python.vladmin.top','python.vladmin.top','example_backup_folder');"""       
    

# print(domain_name,username,password,hostname,wp_path,domain_name,backup_folder)   

#domain_name,username,password,hostname,wp_path,domain_name,backup_folder = input('Enter data Space Separaterd: ').split(',')  
 

# creat_table_statement = """ CREATE TABLE if NOT EXISTS wordpress_sites (
#         wp_id integer primary key AUTOINCREMENT ,
#         domain_name VARCHAR(255),
#         username VARCHAR(255),
#         password VARCHAR(255),
#         hostname VARCHAR(255),
#         wp_path VARCHAR(255),
#         backup_folder VARCGAR(255)   
#         );"""

# test4.vladmin.top,vladmint,passwor_example,hostname_example,/home/vladmint/public_html/,vladmin.top,vladmint-backup-folder
#
 
list_websites = """
select * from wordpress_sites;

"""                
drop_table = """
drop table wordpress_sites;

"""
#  cursor = conn.cursor()
#     cursor.execute(drop_table)
#     conn.commit()
#     conn.close()

if __name__ == "__main__":
    # cursor = conn.cursor()
    # cursor.execute(creat_table_statement)
    # conn.commit()
    # conn.close()
    
    cursor = conn.cursor()
    gen_data = GenerateInput()
    cursor.execute(gen_data.show_site_data())
    site_data = cursor.fetchall()
    
    print(site_data)
    domain_name = site_data[0][1]
    user = site_data[0][2]
    password = site_data[0][3]
    hostname = site_data[0][4]
    wp_full_path = site_data[0][5]
    
    print(domain_name)
    print(user)
    print(hostname)
    print(wp_full_path)
    print(password)
    
    
    # query = gen_data.show_site_data
    
    
    #wp_site_data = WpDatabase()
    #domain_name,username,password,hostname,wp_path,domain_name,backup_folder = input('Enter data Space Separaterd: ').split(',')
    # wp_database = WpDatabase(vars_.domain_name,vars_.username,vars_.password,vars_.hostname,vars_.wp_path,vars_.backup_folder)
    # cursor.execute(wp_database.add_website())
    # conn.commit()
    # cursor.execute(list_websites)
    # variables = {}
    # list_of_websites = cursor.fetchall()
    # for site in list_of_websites[0]:
    # variables = {
    #         'domain_name':list_of_websites[0][1],
    #         'username':list_of_websites[0][2],
    #         'password':list_of_websites[0][3],
    #         'hostname':list_of_websites[0][4],
    #         'wp_path':list_of_websites[0][5],
    #         'backup_folder':list_of_websites[0][6],

    #     }
    # pprint(variables)
    conn.close()