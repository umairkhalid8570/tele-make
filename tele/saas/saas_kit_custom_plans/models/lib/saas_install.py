import os,time,sys,shutil
import random, string
import json
import subprocess
import imp,re,shutil
import argparse
import logging
import functools
import xmlrpc.client
import socket
import logging
from collections import defaultdict
from contextlib import closing
from configparser import SafeConfigParser
from . import saas_client_db
from .  pg_query import PgQuery

_logger = logging.getLogger(__name__)

try:
    import docker
except ImportError as e:
    _logger.info("Docker Library not installed!!")

try:
    import erppeek
except ImportError as e:
    _logger.info("erppeek library not installed!!")

class tele_container:
    def  __init__(self,db="dummy",tele_image="tele:12.5",tele_config = None,host_server = None, db_server = None, version = "1.0"):
        self.tele_image = tele_image
        self.location = tele_config
        self.remote_host = host_server['host']
        self.remote_port = host_server['port']
        self.remote_user = host_server['user']
        self.remote_password = host_server['password']
        self.default_version = version
        self.db_host = db_server['host']
        self.db_port = db_server['port']
        self.db_user = db_server['user']
        self.db_password = db_server['password']
        self.response = {}
        self.read_variables(self.location+"/models/lib/saas.conf")

    def read_variables(self,path):
        _logger.info("Reading Conf from %r"%path)
        parser = SafeConfigParser()
        parser.read(path)
        version = self.default_version.split(".")[0]
        self.template_master = parser.get("options","template_master")
        self.container_master = parser.get("options","container_master")
        self.container_user = parser.get("options","container_user")
        self.tele_config = parser.get("options","tele_saas_data")
        self.container_passwd = parser.get("options","container_passwd")
        self.template_tele_port = parser.get("options","template_tele_port_v"+version)
        self.template_tele_lport = parser.get("options","template_tele_lport_v"+version)
        self.common_applets = parser.get("options","common_applets_v"+version)
        self.tele_template = parser.get("options","tele_template_v"+version)
        self.data_dir = parser.get("options","data_dir_path")
        self.tele_image = parser.get("options","tele_image_v"+version)
        #self.default_version =  parser.get("options","default_version")
        self.response['tele_image'] = self.tele_image
        self.ports_in_use = { self.template_tele_port,  self.template_tele_lport }

    def get_client(self):
        try:
            self.dclient = docker.from_env()
        except Exception as e:
            _logger.info("Docker Library not installed!!")
            raise e
        return True
    
    def check_error(self,func):
        functools.wraps(func)
        def wrapper(*args,**argc):
            try:
                return func(*args,**argc)
            except Exception as e:
                _logger.info("Error %s occurred at %s"%(str(e),func.__name__))
                exit(1)
        return wrapper

    
    def random_str(self,length):
        letters = string.ascii_uppercase
        return ''.join(random.choice(letters) for i in range(length))   
    
    def check_if_installed(self,program):
        return shutil.which(program)
    
    def is_container_available(self,name):
        try:
            self.dclient.containers.get(name)
            return True
        except (docker.errors.ContainerError, docker.errors.ImageNotFound, docker.errors.APIError, Exception) as e:
            _logger.info("Container %s not available")
            return False

    def check_if_db_exists(self,url,db):
        sock_db = xmlrpc.client.ServerProxy('{}/xmlrpc/2/db'.format(url))
        if db in sock_db.list():
            return True
        return False

def main(context=None):
    _logger.info(context)

    status_checks = {"server" : True, "dir" : True, "filestore" : True, "domain_mapping" : True, "db_clone" : True}

    db = context.get("db_name")
    modules = context.get('modules')
    tele_version = context.get("version",None)
    host_domain = context.get("host_domain")
    saas_port = context.get("container_port")

    TeleObject = tele_container(db = db, tele_config = context['config_path'], db_server = context['db_server'], host_server = context['host_server'], version=tele_version)
    TeleObject.get_client()
    if tele_version in ["1.0"]:
        TeleObject.default_version = tele_version

    if host_domain != db:
        raise Exception("Host Name should match the DB Name") 

    response = saas_client_db.create_saas_client(operation = "install", tele_url="http://{}:{}".format("localhost", saas_port),tele_username = context.get("login") ,tele_password = context.get("password"), database_name = db ,modules_list = modules,admin_passwd = context.get("password"))

    if not response:
        raise Exception("SAAS Clinet Could not be created!! Please follow logs for details")
    return response

