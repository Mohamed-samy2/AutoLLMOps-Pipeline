from .providers.postgres import postgres
from .DbEnums import PostgresDbEnums
from sqlalchemy.orm import sessionmaker


class DbFactory:
    def __init__(self,config, db_client : sessionmaker = None):
        self.config = config
        self.db_client = db_client
        
    def create(self, provider: str):

        if provider == PostgresDbEnums.POSTGRES.value:
            return postgres(
                db_client=self.db_client,
            )
        
        return None