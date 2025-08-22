本地開發

可以不透過 docker 省去反覆構建的麻煩，快速測試程式碼邏輯 (要確保在執行前，RabbitMQ、MySQL等服務都已經成功打開。)

建立虛擬環境
```bash
pipenv --python ~/.pyenv/versions/3.8.10/bin/python
```

安裝依賴包
```bash
pipenv install
pipenv install -e .
```

產生 .env
```bash
ENV=DOCKER python3 genenv.py
```

啟動 worker
```bash
pipenv run celery -A crawlers.worker worker --loglevel=info --hostname=%h -Q jobmarket-worker-1
```

啟動 producer 爬取資料
```bash
pipenv run python -m crawlers.cake.producer
```

確認執行結果：
1. 訪問 `localhost:8080` 查看數據有沒有正確寫入
2. 查看 worker 日誌 `docker logs jobmarket-worker-1`，看看有沒有報錯

---------------------------------------------------------------------

shared 是共用的模組

- logger 可以寫入日誌，並存放在 logs 資料夾下
- db 用來將職缺資料寫入資料庫

可參考 crawlers/cake/tasks 的寫法。

---------------------------------------------------------------------

構建容器

構建指令
```bash
docker build -f Dockerfile -t xxx/jobmarket-crawler:0.0.1 .
```

推送到 Docker Hub
```bash
docker push your_username/jobmarket-crawler:0.0.1
```