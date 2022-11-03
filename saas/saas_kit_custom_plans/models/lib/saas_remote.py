import os,time,sys,shutil
import random, string
import json
import subprocess
import paramiko
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


class tele_remote_container:
    def __init__(self,db="dummy",tele_image="tele:12.5",tele_config = None,host_server = None, db_server = None):
        self.tele_image = tele_image
        self.location = tele_config
        self.remote_host = host_server['host']
        self.remote_port = host_server['port']
        self.remote_user = host_server['user']
        self.remote_password = host_server['password']
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
        self.template_master = parser.get("options","template_master")
        self.container_master = parser.get("options","container_master")
        self.container_user = parser.get("options","container_user")
        self.tele_config = parser.get("options","tele_saas_data")
        self.container_passwd = parser.get("options","container_passwd")
        self.template_tele_port = parser.get("options","template_tele_port")
        self.template_tele_lport = parser.get("options","template_tele_lport")
        self.common_applets = parser.get("options","common_applets")
        self.tele_template = parser.get("options","tele_template")
        self.data_dir = parser.get("options","data_dir_path")
        self.tele_image = parser.get("options","tele_image")
        self.response['tele_image'] = self.tele_image
        self.ports_in_use = { self.template_tele_port,  self.template_tele_lport }
        _logger.info("EREEE")

    def get_client(self):
        try:
            self.dclient = docker.DockerClient(base_url='tcp://%s:2375'%self.remote_host)
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

    def list_all_used_ports(self):
        containers = self.dclient.containers.list(all)
#        used_ports = [8888] #8888 to be used for DB templates 
        for each in containers:
            port_info =  each.attrs['HostConfig']['PortBindings']
            if port_info and port_info.get('8069/tcp',None):
#                used_ports.append(port_info['8069/tcp'][0]['HostPort'])
                self.ports_in_use.add(port_info['8069/tcp'][0]['HostPort'])
                if port_info.get('8071/tcp',None):
                    self.ports_in_use.add(port_info['8071/tcp'][0]['HostPort'])

#        return used_ports
    
    def find_me_an_available_port_within(self,a,b,c = None):
        if not c:
            c = 22 
        cmd = "python3 /tmp/find_me_a_port.py %r %r %r"%(a,b,c)
        ssh_obj = self.login_remote()
        try:
            sftp = ssh_obj.open_sftp()
            _logger.info("===> %r ===>"%self.location)
            sftp.put(self.location+"/models/lib/find_me_a_port.py", '/tmp/find_me_a_port.py')
            sftp.close()
            ssh_stdin, ssh_stdout, ssh_stderr = ssh_obj.exec_command(cmd)
            res = ssh_stdout.readlines()
            _logger.info("result = %r  %r"%(ssh_stderr.readlines(),res))
            if len(res) == 0:
               return False
            self.response['port'] = int(res[0].strip())
            return int(res[0].strip())
        except Exception as e:
            _logger.info("++++++++++ERROR++++%r",e)
        finally:
            ssh_obj.close()

        return False
    
    def random_str(self,length):
        letters = string.ascii_uppercase
        return ''.join(random.choice(letters) for i in range(length))   
    
    def create_db(self,url,db,admin_passwd):
        _logger.info(type(url))
        _logger.info("Connection initiated %s"%url)
        count = 0
        client = ""
        while count < 10:
            try:
                _logger.info("Attempting %d. Tele should be ready by now"%count)
                client = erppeek.Client(server=str(url))
                break
            except Exception as e:
                count += 1
                _logger.info("Error %r"%str(e))
                time.sleep(4)
        if count == 10:
           _logger.info("Connectio Could not be built")
           return False                

        _logger.info("Connection built %s"%url)
        try:
            client.create_database(admin_passwd,db, login = self.container_user, user_password = self.container_passwd) #using default admin password
            return True
        except Exception as e:
            _logger.info("Error",e)
            _logger.info("DB Create: %r"%(str(e)))
            return False
    
    def check_if_installed(self,program):
        cmd = "which $1 >/dev/null; echo $?"
    
    def remove_container(self,name): 
        try:
            cont = self.dclient.containers.get(name) #can fetch the data regarding all running or stopped containers.
            cont.remove(force=True)
            _logger.info("Container -->%s deleted"%name)
        except docker.errors.NotFound as e:
            _logger.info("%s is not available. Must have already been deleted"%name)

    def mkdir_TeleConfig(self,folder,conf_file):
        try:
            ssh_obj =  self.login_remote()
            _logger.info("In mkdir teleconfig %r %r %r"%(folder,self.tele_config,conf_file))
            path = self.tele_config + "/"+ folder
            cmd = "mkdir -p  %s"%path
            ssh_obj = self.login_remote()
            if not self.execute_on_remote_shell(ssh_obj,cmd):
                return False
            cmd = "cp %s %s/tele-server.conf"%(self.tele_config+"/"+conf_file,path)
            if self.execute_on_remote_shell(ssh_obj,cmd):
                self.response['path'] = path
                return path
        except Exception as e:
            _logger.info("Error: Creating Directory %r"%e)
            raise e

    def mkdir_mnt_extra_applets(self, folder):
        try:
            ssh_obj =  self.login_remote()
            path = self.tele_config+"/"+folder+"/data-dir"
            cmd = "mkdir -p %s; chmod -R 777 %s"%(path,path)
            if not self.execute_on_remote_shell(ssh_obj,cmd):
                return False
            cmd = "chown 777 %s"%path
            if self.execute_on_remote_shell(ssh_obj,cmd):
                self.response['extra-applets'] = path
                return path
        except Exception as e:
            _logger.info("Error: Creating data-dir %e"%e)
            raise e

    def lets_roll_back_everything(self,to_be_rolled_back = None):

        if 'server' in to_be_rolled_back:
            try:
                cont = self.dclient.containers.get(self.response['name']).id
                self.remove_container(cont)
            except docker.errors.NotFound as e:
                _logger.info("Error %r not found!!"%self.response['name'])
            except Exception as e:
                _logger.info("Error Dropping the SAAS server. %r"%self.response['name'])
                return False

        if 'directories' in to_be_rolled_back:
            try:
                path = self.tele_config+"/"+self.response['name']
                _logger.info("Deleting the Directory Created for %r"%self.response['name'])
                cmd = "rm -rf %r"%path
                if path.split("/")[-1] not in ["tele-data"]:
                    ssh_obj = self.login_remote()
                    return self.execute_on_remote_shell(ssh_obj,cmd)
            except Exception as e:
                _logger.info("Error: Deleting the Directory Created for %r %r"%(self.response['name'],e))
                return False
        return True
 
    def is_container_available(self,name):
        try:
            self.dclient.containers.get(name)
            return True
        except (docker.errors.ContainerError, docker.errors.ImageNotFound, docker.errors.APIError, Exception) as e:
            _logger.info("Container %s not available")
            return False

    def run_tele(self,name, db):
        self.response['name'] = name
        try:
            port = self.find_me_an_available_port_within(8000,9000)#find_me_an_available_port()  # Grepping an avialable port.
            if port == False:
                return False
            _logger.info("Port received %r"%port)
            lport = self.find_me_an_available_port_within(8000,9000, port)#find_me_an_available_port()  # Grepping an avialable port.
            if lport == False:
                return False

            path = self.mkdir_TeleConfig(name, "tele-server.conf") #Mounting the tele.conf file. Should ask user for the location.Assuming /root/Tele/config/$name for now.
            self.add_config_paramenter(self.tele_config+"/"+name+"/tele-server.conf","dbfilter = %s"%db) 
            self.add_config_paramenter(self.tele_config+"/"+name+"/tele-server.conf","db_user = %s"%self.db_user) 
            self.add_config_paramenter(self.tele_config+"/"+name+"/tele-server.conf","admin_passwd = %s"%self.container_master) 
            self.add_config_paramenter(self.tele_config+"/"+name+"/tele-server.conf","db_host = %s"%self.db_host) 
            self.add_config_paramenter(self.tele_config+"/"+name+"/tele-server.conf","db_port = %s"%self.db_port) 
            self.add_config_paramenter(self.tele_config+"/"+name+"/tele-server.conf","db_password = %s"%self.db_password) 
            extra_path = self.mkdir_mnt_extra_applets(name)
            _logger.info("FiLES CREATED AS NEEDED")
            _logger.info("%r %r"%(path,extra_path))
            self.dclient.containers.run(image=self.tele_image,name=name,detach=True,volumes={extra_path:{'bind':self.data_dir,"mode":"rw"}, path: {'bind': "/etc/tele/", 'mode': 'rw'},self.common_applets:{'bind': "/mnt/extra-applets", 'mode': 'rw'}},ports={8069:port, 8071 : lport },tty=True,restart_policy={"Name":"unless-stopped"}) #Start the container
            _logger.info("Let's give Tele 2s")
            time.sleep(2)
            self.response['container_id'] = self.response['name']
            _logger.info("Tele container with name %s started successfully. Hit http://localhost:%s"%(name,port))
            return { "port" : port, "longport" : lport }
        except (docker.errors.ContainerError, docker.errors.ImageNotFound, docker.errors.APIError, Exception) as e:
            _logger.info("Tele container with name %s couldn't be started. Error: %s"%(name,e))
            self.remove_container(self.dclient.containers.get(self.response['name']).id)  #Deleting the container that just got created but something seemingly went wrong with it.
        return False

    def add_config_paramenter(self,file_path,value):
        try:
            ssh_obj =  self.login_remote()
            cmd = "echo \"%s\" >> %s"%(value,file_path)
            return self.execute_on_remote_shell(ssh_obj,cmd)
        except Exception as e:
            _logger.info("Error appneding to file %r",e)
                
    
    def execute_on_shell(self,cmd):
        try:
            res = subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)
            _logger.info("-----------COMMAND RESULT--------%r", res)
            return True
        except Exception as e:
            _logger.info("+++++++++++++ERRROR++++%r",e)
            return False

    def write_saas_data(self,folder,data):
        path = self.tele_config + "/"+folder
        _logger.info("Writing data to %r"%path)
        with open(path+"/saas_data.conf",'w') as file:
            file.write("[options]\n")
            for each in data.items():
                file.write("%s = %s\n"%each)
 
    def login_remote(self):
        try:
            ssh_obj = paramiko.SSHClient()
            ssh_obj.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_obj.connect(hostname=self.remote_host, username=self.remote_user, password=self.remote_password,port=self.remote_port)
            return ssh_obj
        except Exception as e:
            _logger.info("Couldn't connect remote")
            return False

    def execute_on_remote_shell(self,ssh_obj,command):
        _logger.info(command)
        try:
            ssh_stdin, ssh_stdout, ssh_stderr = ssh_obj.exec_command(command)
            _logger.info(ssh_stdout.readlines())
            return True
        except Exception as e:
            _logger.info("+++ERROR++ %s",command)
            _logger.info("++++++++++ERROR++++%r",e)
            return False

    def cloning_db(self,url,source_db,new_db,admin_passwd):
        sock_db = xmlrpc.client.ServerProxy('{}/xmlrpc/2/db'.format(url))
        count = 0
        while count < 10:
            try:
                if source_db in sock_db.list():
                    result = sock_db.duplicate_database(admin_passwd, source_db, new_db)
                    return result
            except Exception as e:
                _logger.info("Error listing DB: %r"%e)
            count += 1
            time.sleep(5)

        return False

class nginx_vhost:

    def __init__(self,vhostTemplate="vhosttemplate.txt",sitesEnable = '/var/lib/tele/Tele-SAAS_Data/docker_vhosts/',sitesAvailable = '/etc/nginx/sites-available/'):    
        self.vhostTemplate=vhostTemplate
        self.sitesEnable=sitesEnable
        self.sitesAvailable=sitesAvailable


    def login_remote(self,remote_host,remote_user,remote_passwd):
        try:
            ssh_obj = paramiko.SSHClient()
            ssh_obj.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_obj.connect(hostname=remote_host, username=remote_user, password=remote_password)
            return ssh_obj
        except Exception as e:
            _logger.info("Couldn't connect remote")
            return False

    def exexute_on_remote_shell(self,ssh_obj,command):
        try:
            ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)
            _logger.info(ssh_stdout)
            return True
        except Exception as e:
            _logger.info("++++++++++ERROR++++%r",e)
            return False

    def execute_on_shell(self,cmd):
        try:
            res = subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)
            _logger.info("-----------COMMAND RESULT--------%r", res)
            return True
        except Exception as e:
            _logger.info("+++++++++++++ERRROR++++%r",e)
            return False

    def domainmapping(self,subdomain,backend,longbackend):
        _logger.info("++++%r   ======== %r++ %r"%(subdomain,backend,longbackend))

        new_conf = self.sitesEnable+str.lower(subdomain)+".conf"
        subdomain = str.lower(subdomain)

        cmd = "cp %s %s"%((self.sitesAvailable+self.vhostTemplate),new_conf)
        if not self.execute_on_shell(cmd):
            _logger.info("Couldn't Create Vhost file!!")
            return False

        cmd = "sed -i \"s/LONG_BACKEND_TO_BE_REPLACED/%s/g\" %s"%(longbackend,new_conf)
        if not self.execute_on_shell(cmd):
            _logger.info("Couldn't Replace Long Port!!")
            return False

        cmd = "sed -i \"s/BACKEND_TO_BE_REPLACED/%s/g\" %s"%(backend,new_conf)
        if not self.execute_on_shell(cmd):
            _logger.info("Couldn't Replace Port!!")
            return False


        cmd = "sed -i \"s/DOMAIN_TO_BE_REPLACED/%s/g\"  %s"%(subdomain,new_conf)
        if not self.execute_on_shell(cmd):
            _logger.info("Couldn't Replace Subdomain!!")
            return False

        if not self.execute_on_shell("sudo nginx -t"):
            _logger.info("Couldn't Replace Subdomain!!")
            return False

        if not self.execute_on_shell("sudo nginx -s reload"):
            _logger.info("Couldn't Replace Subdomain!!")
            return False

        return True 

def main(context=None):
    _logger.info(context)

    status_checks = {"server" : True, "dir" : True, "filestore" : True, "domain_mapping" : True, "db_clone" : True}

    db = context.get("db_name")
    db_template = context.get("db_template")
    modules = context.get('modules')
    host_domain = context.get("host_domain")

    _logger.info("++++++++++++%r++++++++++"%context)

    TeleObject = tele_remote_container(db = db,host_server = context['host_server'], db_server = context['db_server'],tele_config = context['config_path'])
    TeleObject.get_client()

    sitesEnable = TeleObject.tele_config+"/docker_vhosts/"
   
    if host_domain != db:
        raise Exception("Host Name should match the DB Name")

    port = TeleObject.run_tele(host_domain, db)
    if not port:
        status_checks['server'] = False
        raise Exception("No Available Port")
     
    try:
        src = "%s/%s/data-dir/filestore/%s"%(TeleObject.tele_config,TeleObject.tele_template,db_template)
        dest = "%s/%s/data-dir/filestore"%(TeleObject.tele_config,host_domain)
        ssh_obj = TeleObject.login_remote()
        try:
            TeleObject.execute_on_remote_shell(ssh_obj,"mkdir -p %s"%dest)
        except OSError as e:
            _logger.info("Could not create filestore %r",e)

        dest = dest+"/"+db
        _logger.info("SOURCE %r",src)
        _logger.info("DEST %r",dest)

#        _logger.info(TeleObject.execute_on_remote_shell(ssh_obj,"cp -r %s %s"%(src,dest)))
        _logger.info(TeleObject.execute_on_shell("sshpass -p %r rsync -var -e  \"ssh -o StrictHostKeyChecking=no\" %r/ %r@%r:%r"%(context['host_server']['password'],src,context['host_server']['user'],context['host_server']['host'],dest)))
        _logger.info(TeleObject.execute_on_remote_shell(ssh_obj,"chmod -R 777 %s"%dest))    #########----->>> do we really need it
    except OSError as e:
        _logger.info("Filestore couldnot be copied %r",e)

    time.sleep(1)
    _logger.info("http://{}:{}".format(TeleObject.remote_host, port['port']))
    result = TeleObject.cloning_db("http://{}:{}".format(TeleObject.remote_host, port['port']),db_template,db,TeleObject.container_master)

    _logger.info("Cloning Res %r"%result)
    time.sleep(1)
    if not result:
        TeleObject.lets_roll_back_everything(to_be_rolled_back = ['server','directories'])
        raise Exception("SAAS Clinet Could not be created!! Please follow logs for details")

    result = {'modules_installation': True, 'modules_missed': []}
    TeleObject.response['url'] = "{}:{}".format(str(host_domain), port['port'])

    _logger.info("-----------MAPPING DOMAIN-------- %r"%("{}:{}".format(str(TeleObject.remote_host), port)))
    NginxVhost = nginx_vhost(sitesAvailable=sitesEnable,sitesEnable=sitesEnable)
    resp = NginxVhost.domainmapping(str(host_domain),"{}:{}".format(str(TeleObject.remote_host), str(port['port'])),"{}:{}".format(str(TeleObject.remote_host), str(port['longport'])))
    _logger.info("----------MAPPING RESULT--------%r", resp)

    if resp:
        TeleObject.response['url']  = "http://{}".format(str.lower(host_domain))
    else:
        status_checks['domain_mapping'] = False
    TeleObject.response.update(result)

    _logger.info(TeleObject.response)

    #TeleObject.write_saas_data(host_domain, TeleObject.response)
    return TeleObject.response

def create_db_template(db_template=None,modules=None, config_path=None,host_server = None, db_server = None):
    _logger.info(locals())

    response = {}
    TeleObject = tele_remote_container(db=db_template,host_server = host_server,db_server = db_server,tele_config = config_path)
    TeleObject.get_client()

    response['tele_image'] = TeleObject.tele_image
    sitesEnable = TeleObject.tele_config+"/docker_vhosts/"
    host_domain = "db14_templates."+host_server['server_domain']
    response['port'] = TeleObject.template_tele_port
    response['lport'] = TeleObject.template_tele_lport
    response['name'] = TeleObject.tele_template

    if not TeleObject.is_container_available(TeleObject.tele_template):
        try:
            path = TeleObject.mkdir_TeleConfig(TeleObject.tele_template,"tele-template.conf") #Mounting the tele.conf file. Should ask user for the location.Assuming /root/Tele/config/$name for now. 
            extra_path = TeleObject.mkdir_mnt_extra_applets(TeleObject.tele_template)
            TeleObject.add_config_paramenter(TeleObject.tele_config+"/"+TeleObject.tele_template+"/tele-server.conf","db_user = %s"%TeleObject.db_user) 
            TeleObject.add_config_paramenter(TeleObject.tele_config+"/"+TeleObject.tele_template+"/tele-server.conf","admin_passwd = %s"%TeleObject.template_master) 
            TeleObject.add_config_paramenter(TeleObject.tele_config+"/"+TeleObject.tele_template+"/tele-server.conf","db_port = %s"%TeleObject.db_port) 
            TeleObject.add_config_paramenter(TeleObject.tele_config+"/"+TeleObject.tele_template+"/tele-server.conf","db_host = %s"%TeleObject.db_host) 
            TeleObject.add_config_paramenter(TeleObject.tele_config+"/"+TeleObject.tele_template+"/tele-server.conf","db_password = %s"%TeleObject.db_password)

            TeleObject.dclient.containers.run(image = TeleObject.tele_image, name = TeleObject.tele_template, detach = True, volumes = {extra_path:{'bind':TeleObject.data_dir,"mode":"rw"}, path: {'bind': "/etc/tele/", 'mode': 'rw'}, TeleObject.common_applets:{'bind': "/mnt/extra-applets", 'mode': 'rw'}}, ports = {8069:TeleObject.template_tele_port , 8071:TeleObject.template_tele_lport }, tty = True,restart_policy={"Name":"unless-stopped"}) #Start the container
            _logger.info("Let's give Tele 2s")
            time.sleep(2)

            NginxVhost = nginx_vhost(sitesAvailable = sitesEnable, sitesEnable = sitesEnable)
            if NginxVhost.domainmapping(str(host_domain),"{}:{}".format(TeleObject.remote_host,str(TeleObject.template_tele_port)),"{}:{}".format(TeleObject.remote_host,str(TeleObject.template_tele_lport))):
                response['url'] = "http://{}".format(str.lower(host_domain))

        except (docker.errors.ContainerError, docker.errors.ImageNotFound, docker.errors.APIError, Exception) as e:
            _logger.info("Tele container with name %s couldn't be started. Error: %s"%(TeleObject.tele_template,e))

            TeleObject.remove_container(TeleObject.dclient.containers.get(TeleObject.tele_template).id)
            response.update({ 'status': False, 'msg': e,})
            return response

    response['container_id'] = response['name']
    if TeleObject.create_db("http://%s:%s"%(TeleObject.remote_host,TeleObject.template_tele_port), db_template,TeleObject.template_master): #Creating a default DB.
        _logger.info("Tele container with name %s is available at http://localhost:%s"%(TeleObject.tele_template,TeleObject.template_tele_port))

        result = saas_client_db.create_saas_client(operation = "install", tele_url="http://{}:{}".format(TeleObject.remote_host, TeleObject.template_tele_port), tele_username = TeleObject.container_user ,tele_password = TeleObject.container_passwd, database_name=db_template,modules_list=modules,admin_passwd=TeleObject.template_master)
        response['result'] = result
        response['status'] = True
    else:
        response.update({'status': False,'msg': "Couldn't Create DB. Please ensure that template server is running, you may need to restart it once!!",})

    #TeleObject.write_saas_data(TeleObject.tele_template, response)
    return response



