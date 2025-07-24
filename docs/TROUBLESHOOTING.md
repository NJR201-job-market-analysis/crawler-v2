## 本地包更名時，如何刪除舊的並安裝新包

# 1. 進入項目目錄
cd project_folder

# 2. 刪除舊包
pipenv uninstall package_name

# 3. 安裝新包
pipenv install -e .

pipenv install 會安裝所有的依賴，包含當前目錄的 Python 包
pipenv install -e . 不會安裝第三方庫，只安裝你的項目包

# 4. 驗證
pipenv run python -c "import package_name; print('成功！')"

---------------------------------------------------------------------