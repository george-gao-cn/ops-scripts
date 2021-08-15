# zbx-RedisCluster
## rediscluster monitoring script for zabbix 3.4
## it can autodiscover all cluster's node, 
## and get clients, ops, memoryusage, hitrate, noderole, keys info per node.
## writen by python3 and rediscluster, redis module
Usage:
1. chk_redis.py  ,auto discover cluster nodes
2. chk_redis.py node_ip "client|used_memory|node_role|ops|hit_rate|keys" , get all node's info

