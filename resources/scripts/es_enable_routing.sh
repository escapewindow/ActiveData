
curl -XPUT http://localhost:9200/_cluster/settings -d "{\"transient\": {\"cluster.routing.allocation.disk.watermark.low\": \"80%\"}}"
curl -XPUT http://localhost:9200/_cluster/settings -d "{\"persistent\": {\"cluster.routing.allocation.balance.primary\": 1}}"
curl -XPUT http://localhost:9200/_cluster/settings -d "{\"persistent\": {\"cluster.routing.allocation.enable\": \"all\"}}"


curl -XPUT http://localhost:9200/_cluster/settings -d '{"persistent":{"indices.recovery.max_bytes_per_sec" : "1000mb"}}' -H "Content-Type: application/json"


curl -XPUT http://localhost:9200/_cluster/settings -d "{\"persistent\": {\"cluster.routing.use_adaptive_replica_selection\": true}}" -H "Content-Type: application/json"
