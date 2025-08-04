from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine  # 建立資料庫連線的工具（SQLAlchemy）
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    String,
    Text,
    MetaData,
    String,
    Table,
    Integer,
)
from sqlalchemy.dialects.mysql import (
    insert,
)  # 專用於 MySQL 的 insert 語法，可支援 on_duplicate_key_update
from .config import (
    MYSQL_ACCOUNT,
    MYSQL_HOST,
    MYSQL_PASSWORD,
    MYSQL_PORT,
    MYSQL_DATABASE,
)
from .logger import logger


class Database:
    def __init__(self):
        self.engine = self.create_database_connection()
        if self.engine is None:
            logger.error("無法建立資料庫連接")
            return

        self.metadata = MetaData()
        self._create_tables()

    def create_database_connection(self):
        try:
            # 定義資料庫連線字串（MySQL 資料庫）
            # 格式：mysql+pymysql://使用者:密碼@主機:port/資料庫名稱
            # 上傳到 user 這個 db, 同學可切換成自己的 database
            address = f"mysql+pymysql://{MYSQL_ACCOUNT}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
            engine = create_engine(address)

            # 測試連接
            with engine.connect() as conn:
                conn.execute("SELECT 1")

            logger.info("✅ 資料庫連接成功")

            return engine
        except Exception as e:
            logger.warning("⚠️ 無法連接到資料庫 %s，嘗試自動創建: %s", MYSQL_DATABASE, e)

            try:
                server_address = f"mysql+pymysql://{MYSQL_ACCOUNT}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}"
                server_engine = create_engine(server_address)

                with server_engine.connect() as conn:
                    conn.execute(
                        f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DATABASE}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                    )
                    logger.info("✅ 資料庫 %s 創建成功", MYSQL_DATABASE)

                server_engine.dispose()

                address = f"mysql+pymysql://{MYSQL_ACCOUNT}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
                engine = create_engine(address)

                with engine.connect() as conn:
                    conn.execute("SELECT 1")

                logger.info("✅ 成功連接到新創建的資料庫: %s", MYSQL_DATABASE)
                return engine

            except Exception as create_error:
                logger.error("❌ 自動創建資料庫失敗: %s", create_error)
                return None

    def _create_tables(self):
        try:
            # 定義結構
            self.jobs_table = Table(
                "jobs",
                self.metadata,
                Column("id", BigInteger, primary_key=True, autoincrement=True),
                Column("job_title", String(200), nullable=False),
                Column("company_name", String(200), nullable=False),
                Column("job_description", Text),
                Column("work_type", String(100)),
                Column("required_skills", Text),
                Column("company_description", Text),
                Column("salary_min", Integer),
                Column("salary_max", Integer),
                Column("salary_type", String(20)),
                Column("salary_text", String(100)),
                Column("experience_text", String(100)),
                Column("experience_min", Integer),
                Column("city", String(20)),
                Column("district", String(20)),
                # Column("address", String(200)),
                Column("location", String(200)),
                Column("job_url", String(500), nullable=False, unique=True),
                Column("category", String(100)),
                Column("sub_category", String(100)),
                Column("platform", String(100)),
                Column("created_at", DateTime, default=datetime.now),
                Column(
                    "updated_at", DateTime, default=datetime.now, onupdate=datetime.now
                ),
            )

            self.categories_table = Table(
                "categories",
                self.metadata,
                Column("id", BigInteger, primary_key=True, autoincrement=True),
                Column("platform", String(200), nullable=False),
                Column("category_id", String(200), nullable=False),
                Column("category_name", Text),
                Column("sub_category_id", String(200), nullable=False),
                Column("sub_category_name", Text),
                Column("created_at", DateTime, default=datetime.now),
                Column(
                    "updated_at", DateTime, default=datetime.now, onupdate=datetime.now
                ),
            )

            # 創建表（如果不存在）
            self.metadata.create_all(self.engine)
            # logger.info("✅ 資料表建立/檢查完成")
        except Exception as e:
            logger.error("❌ 建立資料表失敗: %s", e)

    def insert_jobs(self, jobs):
        if self.engine is None:
            logger.error("❌ 資料庫連接未初始化")
            return False

        df = pd.DataFrame(jobs)
        
        # 將這些可能有缺值的整數欄轉成 nullable Int64 dtype
        nullable_int_cols = ["salary_min", "salary_max", "experience_min"]
        for col in nullable_int_cols:
            if col in df.columns:
                df[col] = df[col].astype("Int64")

        # 將 NaN 轉成 None（更保險）
        df = df.where(pd.notnull(df), None)

        success_count = 0
        insert_count = 0
        update_count = 0

        for _, row in df.iterrows():
            try:
                # 準備數據，排除 id 和 created_at
                job_data = row.to_dict()
                if "id" in job_data:
                    del job_data["id"]
                if "created_at" in job_data:
                    del job_data["created_at"]

                # 使用 SQLAlchemy 的 insert 語句建立插入語法
                insert_stmt = insert(self.jobs_table).values(**job_data)

                # 建立更新語句，使用 job_url 作為唯一鍵
                update_dict = {}
                for col in self.jobs_table.columns:
                    if col.name not in ["id", "created_at"]:
                        update_dict[col.name] = getattr(insert_stmt.inserted, col.name)

                # 手動設置 updated_at
                update_dict["updated_at"] = datetime.now()

                # 加上 on_duplicate_key_update 的邏輯
                update_stmt = insert_stmt.on_duplicate_key_update(**update_dict)

                # 執行 SQL 語句，寫入資料庫
                with self.engine.begin() as conn:
                    result = conn.execute(update_stmt)

                    # 判斷是插入還是更新
                    if result.rowcount == 1:
                        insert_count += 1
                        # print(f"✅ 新增職位: {job_data.get('job_title', 'Unknown')}")
                    else:
                        update_count += 1
                        # print(f"🔄 更新職位: {job_data.get('job_title', 'Unknown')}")

                success_count += 1

            except Exception as e:
                logger.error("❌ 處理職位資料失敗: %s", e)
                logger.error("   職位標題: %s", row.get("job_title", "Unknown"))
                logger.error("   job_url: %s", row.get("job_url", "Unknown"))
                logger.error(
                    "   job_salary: %s | %s",
                    row.get("salary_min", "Unknown"),
                    row.get("salary_max"),
                )
                continue

        logger.info("✅ 寫入資料庫完成:")
        logger.info("   總計: %s 筆", len(df))
        logger.info("   成功: %s 筆", success_count)
        logger.info("   新增: %s 筆", insert_count)
        logger.info("   更新: %s 筆", update_count)
        logger.info("   失敗: %s 筆", len(df) - success_count)

        return success_count
