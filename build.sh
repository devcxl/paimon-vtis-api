docker build -t registry.cn-shanghai.aliyuncs.com/devcxl/paimon-vits-api .
# docker rm -f paimon-vits-api
# docker run --network host --name paimon-vits-api -v /save/vits/models/:/save/vits/models/ -d registry.cn-shanghai.aliyuncs.com/devcxl/paimon-vits-api:latest
# docker logs --tail 1000 -f paimon-vits-api
docker system prune -f
docker push registry.cn-shanghai.aliyuncs.com/devcxl/paimon-vits-api:latest