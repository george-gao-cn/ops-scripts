#!/usr/bin/env python3
#coding=utf-8
__author__ = 'gao_hj@163.com'
'''This scripte use for zabbix to monitor redis cluster status and nodes info! 
used python 3.8, 
module info: redis-py-cluster==2.1.3, redis==3.5.3
'''
 
import os,sys,time,traceback
import json
import re
import redis
from rediscluster import RedisCluster as RCluster
 
cluster_nodes = [{"host":"192.168.101.126","port":"6379"},{"host":"192.168.102.22","port":"6379"},{"host":"192.168.101.128","port":"6379"}]
##cluster_nodes = [{"host":"Redis1.xxxxx.db","port":"7000"},{"host":"Redis1.xxxxx.db","port":"7001"},{"host":"Redis2.xxxxx.db","port":"7002"},
##{"host":"Redis2.xxxxx.db","port":"7003"},{"host":"Redis3.xxxxx.db","port":"7004"},{"host":"Redis3.xxxxx.db","port":"7005"}]
#try:
rc = RCluster(startup_nodes=cluster_nodes,decode_responses=True)
#except Exception:
#        #print (err)
#        print ('failed to connect redis cluster!')
#        sys.exit(0)
#print(rc) 
redis_node = []
master_node = []
slave_node = []

def getClusterStatus():
    cs =  rc.execute_command('cluster','info')
    clusterstatus = cs.split('\r')[0].split(':')
    print(clusterstatus)
    if clusterstatus[1] == 'ok':
        rediscluster = 0
    else:
        rediscluster = 1
    #print (rediscluster)
 
def getClusterNode():
    #query_str = sys.argv[1]
    cn = rc.execute_command('cluster','nodes')
    #print(cn.split("\n"))
    for i in cn.split("\n"):
        if (len(i)>0) and re.search(' connected',i):
                node_info = i.split(" ")
                redis_node.append(node_info[1].split('@')[0])
    data = []
    for ip in redis_node:
           data.append({'{#REDIS_NAME}':ip.split(':')[0]})
           #print(data)
       #print(slave_node)
    result = json.dumps({'data':data},indent=4,separators=(',',':'))
    print(result)


def getMasterNodeInfo():
    getClusterNode()
    query_str =str(sys.argv[2])
    for node in master_node:
        node_ip = node.split(':')[0]
        node_port = node.split(':')[1]
        r = redis.Redis(host=node_ip,port=node_port,decode_responses=True)
        result = r.info()
        node_role = result['role']
        node_used_memory = round(result['used_memory']/1024/1024,2)
        node_max_memory = round(result['maxmemory']/1024/1024,2)
        node_clients = result['connected_clients']
        node_ops = result['instantaneous_ops_per_sec']
        node_hits = result['keyspace_hits']
        node_miss = result['keyspace_misses']
        node_hit_rate = round(node_hits/(node_hits+node_miss)*100,2)
        node_keys = result['db0']['keys']
        node_keys_ttl = result['db0']['avg_ttl']
        node_info = {node_ip:{"node_role":node_role,
                              "used_memory":node_used_memory,
                              "max_memory":node_max_memory,
                              "client":node_clients,
                              "ops":node_ops,
                              "hit_rate":node_hit_rate,
                              "keys":node_keys,
                              "avg_ttl":node_keys_ttl}}
        #print(type(node_info))
        print(node_ip,node_info[node_ip][query_str])
def getNodeInfo():
    node_ip = str(sys.argv[1])
    node_port = "6379"
    query_str =str(sys.argv[2])
    #for node in master_node:
    r = redis.Redis(host=node_ip,port=node_port,decode_responses=True)
    result = r.info()
    # return 1 for master node, and 0 for slave node, this is for zabbix monitoring, if state change, can activate alarm
    if re.match("master",result['role']):
       node_role = 1
    else:
       node_role = 0
    #node_role = result['role']
    node_used_memory = round(result['used_memory']/1024/1024,2)
    node_max_memory = round(result['maxmemory']/1024/1024,2)
    node_clients = result['connected_clients']
    node_ops = result['instantaneous_ops_per_sec']
    node_hits = result['keyspace_hits']
    node_miss = result['keyspace_misses']
    node_hit_rate = round(node_hits/(node_hits+node_miss)*100,2)
    node_keys = int(result['db0']['keys'])
    node_keys_ttl = result['db0']['avg_ttl']
    node_info = {node_ip:{"node_role":node_role,
                          "used_memory":node_used_memory,
                          "max_memory":node_max_memory,
                          "client":node_clients,
                          "node_ops":node_ops,
                          "hit_rate":node_hit_rate,
                          "keys":node_keys,
                          "avg_ttl":node_keys_ttl}}
    #print(type(node_info))
    print(node_info[node_ip][query_str])
 
if __name__ == '__main__':
    #if  (str(sys.argv[1]) == 'master') or (str(sys.argv[1]) == "slave"):
    if  (len(sys.argv) == 1): #if no parameter, return all nodes's ip address
        getClusterNode()
    elif  str(sys.argv[1]) == 'status':
        getClusterStatus()
    elif  str(sys.argv[1]) == 'master_info':
        getMasterNodeInfo()
    else: # if other parameter, which is in the dict named "node_info", call getNodeInfo function
        getNodeInfo()
