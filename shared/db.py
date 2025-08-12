from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine  # 建立資料庫連線的工具（SQLAlchemy）
from sqlalchemy import (
    MetaData,
    select,
    Table,
    delete,
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
        self.metadata.reflect(bind=self.engine)

        self.jobs_table = self.metadata.tables.get("jobs")
        self.skills_table = self.metadata.tables.get("skills")
        self.categories_table = self.metadata.tables.get("categories")
        self.jobs_skills_table = self.metadata.tables.get("jobs_skills")
        self.jobs_categories_table = self.metadata.tables.get("jobs_categories")

        if any(
            table is None
            for table in [
                self.jobs_table,
                self.skills_table,
                self.categories_table,
                self.jobs_skills_table,
                self.jobs_categories_table,
            ]
        ):
            logger.error(
                "❌ 一或多個必要的資料表不存在，請先執行 `database/init_db.py`"
            )
            raise ValueError("資料表未被正確初始化")

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

    def _get_or_create_items(
        self, conn, names: set[str], table: Table
    ) -> dict[str, int]:
        name_to_id: dict[str, int] = {}
        if not names:
            return name_to_id

        # 1. 查詢已存在的項目
        stmt = select(table.c.id, table.c.name).where(table.c.name.in_(names))
        result = conn.execute(stmt)
        for row in result:
            # SQLAlchemy Core 的 row 物件可以像元組或字典一樣訪問
            name_to_id[row.name] = row.id

        # 2. 找出需要新增的項目
        new_names = names - set(name_to_id.keys())

        # 3. 批次新增新項目
        if new_names:
            new_items_data = [{"name": name} for name in new_names]
            # 使用 IGNORE 防止因平行處理造成的重複新增錯誤
            insert_stmt = insert(table).values(new_items_data).prefix_with("IGNORE")
            conn.execute(insert_stmt)

            # 重新查詢以取得所有（包含剛剛新增的）項目的 ID
            stmt_requery = select(table.c.id, table.c.name).where(
                table.c.name.in_(names)
            )
            result_requery = conn.execute(stmt_requery)
            for row in result_requery:
                name_to_id[row.name] = row.id

        return name_to_id

    def insert_jobs(self, jobs: list[dict]):
        if self.engine is None or not hasattr(self, "jobs_table"):
            logger.error("❌ 資料庫連接或資料表未初始化")
            return 0

        if not jobs:
            return 0

        # 1. 準備資料
        df = pd.DataFrame(jobs)
        # 儲存關聯資料，以 job_url 作為主鍵
        relations_map = df.set_index("job_url")[["skills", "categories"]].to_dict(
            "index"
        )
        # 取得所有唯一的技能與分類名稱
        all_skills = set(
            skill for sublist in df["skills"] for skill in sublist if skill
        )
        all_categories = set(
            category for sublist in df["categories"] for category in sublist if category
        )
        # 移除關聯欄位，準備主表插入
        jobs_df = df.drop(columns=["skills", "categories"])

        # 處理可能的空值與型別
        nullable_int_cols = ["salary_min", "salary_max", "experience_min"]
        for col in nullable_int_cols:
            if col in jobs_df.columns:
                jobs_df[col] = pd.to_numeric(jobs_df[col], errors="coerce").astype(
                    "Int64"
                )
        jobs_df = jobs_df.where(pd.notnull(jobs_df), None)

        update_dict = {
            col.name: col
            for col in self.jobs_table.c
            if col.name not in ["id", "created_at", "job_url"]
        }
        update_dict["updated_at"] = datetime.now()

        # 2. 批次新增/更新 `jobs` 表
        with self.engine.begin() as conn:
            try:
                insert_stmt = insert(self.jobs_table).values(
                    jobs_df.to_dict(orient="records")
                )
                upsert_stmt = insert_stmt.on_duplicate_key_update(update_dict)
                result = conn.execute(upsert_stmt)
                logger.info(f"批次新增/更新 {result.rowcount} 筆職缺資料到 `jobs` 表。")

                # 3. 批次取得或建立 `skills` 和 `categories`
                skill_name_to_id = self._get_or_create_items(
                    conn, all_skills, self.skills_table
                )
                category_name_to_id = self._get_or_create_items(
                    conn, all_categories, self.categories_table
                )

                # 4. 取得所有相關職缺的 ID
                job_urls = list(relations_map.keys())
                jobs_query = select(
                    self.jobs_table.c.id, self.jobs_table.c.job_url
                ).where(self.jobs_table.c.job_url.in_(job_urls))
                job_url_to_id = {
                    row.job_url: row.id for row in conn.execute(jobs_query)
                }
                job_ids = list(job_url_to_id.values())

                # 5. 更新關聯表
                if job_ids:
                    # 5a. 清除舊的關聯，確保更新時資料正確
                    conn.execute(
                        delete(self.jobs_skills_table).where(
                            self.jobs_skills_table.c.job_id.in_(job_ids)
                        )
                    )
                    conn.execute(
                        delete(self.jobs_categories_table).where(
                            self.jobs_categories_table.c.job_id.in_(job_ids)
                        )
                    )

                    # 5b. 準備並批次插入新的關聯
                    new_job_skills = []
                    new_job_categories = []
                    for url, job_id in job_url_to_id.items():
                        job_relations = relations_map[url]
                        for skill_name in job_relations.get("skills", []):
                            if skill_id := skill_name_to_id.get(skill_name):
                                new_job_skills.append(
                                    {"job_id": job_id, "skill_id": skill_id}
                                )
                        for cat_name in job_relations.get("categories", []):
                            if cat_id := category_name_to_id.get(cat_name):
                                new_job_categories.append(
                                    {"job_id": job_id, "category_id": cat_id}
                                )

                    if new_job_skills:
                        conn.execute(
                            insert(self.jobs_skills_table).values(new_job_skills)
                        )
                    if new_job_categories:
                        conn.execute(
                            insert(self.jobs_categories_table).values(
                                new_job_categories
                            )
                        )

                    logger.info(f"✅ 成功更新 {len(job_ids)} 筆職缺的技能與分類關聯。")

            except Exception as e:
                logger.error("❌ 寫入資料庫時發生錯誤: %s", e)
                # 由於 `with self.engine.begin() as conn:`，發生錯誤時會自動回滾
                return 0

        return len(jobs_df)
