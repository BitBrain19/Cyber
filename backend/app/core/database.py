import asyncio
from typing import Optional
import asyncpg
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from elasticsearch import AsyncElasticsearch
import redis.asyncio as redis
import structlog
from contextlib import asynccontextmanager

from app.core.config import settings

logger = structlog.get_logger()

# Database connections
postgres_pool: Optional[asyncpg.Pool] = None
influxdb_client: Optional[InfluxDBClient] = None
elasticsearch_client: Optional[AsyncElasticsearch] = None
redis_client: Optional[redis.Redis] = None

async def init_db():
    """Initialize all database connections"""
    global postgres_pool, influxdb_client, elasticsearch_client, redis_client
    
    try:
        # Initialize PostgreSQL connection pool
        postgres_pool = await asyncpg.create_pool(
            settings.POSTGRES_URL,
            min_size=5,
            max_size=20,
            command_timeout=60
        )
        logger.info("PostgreSQL connection pool initialized")
        
        # Initialize InfluxDB client
        influxdb_client = InfluxDBClient(
            url=settings.INFLUXDB_URL,
            token=settings.INFLUXDB_TOKEN,
            org=settings.INFLUXDB_ORG
        )
        logger.info("InfluxDB client initialized")
        
        # Initialize Elasticsearch client
        elasticsearch_client = AsyncElasticsearch(
            [settings.ELASTICSEARCH_URL],
            basic_auth=(settings.ELASTICSEARCH_USERNAME, settings.ELASTICSEARCH_PASSWORD),
            verify_certs=False,  # Set to True in production with proper certificates
            timeout=30
        )
        logger.info("Elasticsearch client initialized")
        
        # Initialize Redis client
        redis_client = redis.from_url(
            settings.REDIS_URL,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
        await redis_client.ping()
        logger.info("Redis client initialized")
        
        # Create database tables and indexes
        await create_tables()
        await create_elasticsearch_indexes()
        
    except Exception as e:
        logger.error("Failed to initialize database connections", error=str(e))
        raise

async def create_tables():
    """Create PostgreSQL tables if they don't exist"""
    async with postgres_pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'viewer',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                last_login TIMESTAMP WITH TIME ZONE,
                CONSTRAINT valid_role CHECK (role IN ('admin', 'analyst', 'viewer'))
            )
        """)
        
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(255) NOT NULL,
                type VARCHAR(50) NOT NULL,
                ip_address INET,
                mac_address MACADDR,
                location VARCHAR(255),
                department VARCHAR(100),
                risk_level VARCHAR(20) DEFAULT 'low',
                last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                CONSTRAINT valid_risk_level CHECK (risk_level IN ('low', 'medium', 'high', 'critical'))
            )
        """)
        
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                title VARCHAR(255) NOT NULL,
                description TEXT,
                severity VARCHAR(20) NOT NULL,
                category VARCHAR(100),
                source VARCHAR(100),
                threat_score DECIMAL(5,2),
                status VARCHAR(20) DEFAULT 'active',
                affected_assets TEXT[],
                remediation_suggestions TEXT[],
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                resolved_at TIMESTAMP WITH TIME ZONE,
                CONSTRAINT valid_severity CHECK (severity IN ('critical', 'high', 'medium', 'low')),
                CONSTRAINT valid_status CHECK (status IN ('active', 'investigating', 'resolved'))
            )
        """)
        
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS remediation_logs (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                alert_id UUID REFERENCES alerts(id),
                action VARCHAR(100) NOT NULL,
                description TEXT,
                executed_by UUID REFERENCES users(id),
                executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                success BOOLEAN DEFAULT TRUE,
                details JSONB
            )
        """)
        
        # Create indexes
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_assets_risk_level ON assets(risk_level)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_assets_last_seen ON assets(last_seen)")
        
        logger.info("PostgreSQL tables and indexes created")

async def create_elasticsearch_indexes():
    """Create Elasticsearch indexes if they don't exist"""
    try:
        # Security logs index
        logs_mapping = {
            "mappings": {
                "properties": {
                    "timestamp": {"type": "date"},
                    "source": {"type": "keyword"},
                    "message": {"type": "text"},
                    "level": {"type": "keyword"},
                    "asset_id": {"type": "keyword"},
                    "user_id": {"type": "keyword"},
                    "event_type": {"type": "keyword"},
                    "ip_address": {"type": "ip"},
                    "tags": {"type": "keyword"}
                }
            },
            "settings": {
                "number_of_shards": 3,
                "number_of_replicas": 1
            }
        }
        
        await elasticsearch_client.indices.create(
            index="security_logs",
            body=logs_mapping,
            ignore=400  # Ignore if index already exists
        )
        
        logger.info("Elasticsearch indexes created")
        
    except Exception as e:
        logger.error("Failed to create Elasticsearch indexes", error=str(e))

async def close_db():
    """Close all database connections"""
    global postgres_pool, influxdb_client, elasticsearch_client, redis_client
    
    if postgres_pool:
        await postgres_pool.close()
        logger.info("PostgreSQL connection pool closed")
    
    if influxdb_client:
        influxdb_client.close()
        logger.info("InfluxDB client closed")
    
    if elasticsearch_client:
        await elasticsearch_client.close()
        logger.info("Elasticsearch client closed")
    
    if redis_client:
        await redis_client.close()
        logger.info("Redis client closed")

# Database access functions
async def get_postgres_pool() -> asyncpg.Pool:
    """Get PostgreSQL connection pool"""
    if not postgres_pool:
        raise RuntimeError("Database not initialized")
    return postgres_pool

async def get_influxdb_client() -> InfluxDBClient:
    """Get InfluxDB client"""
    if not influxdb_client:
        raise RuntimeError("InfluxDB not initialized")
    return influxdb_client

async def get_elasticsearch_client() -> AsyncElasticsearch:
    """Get Elasticsearch client"""
    if not elasticsearch_client:
        raise RuntimeError("Elasticsearch not initialized")
    return elasticsearch_client

async def get_redis_client() -> redis.Redis:
    """Get Redis client"""
    if not redis_client:
        raise RuntimeError("Redis not initialized")
    return redis_client

@asynccontextmanager
async def get_db_connection():
    """Context manager for database connections"""
    pool = await get_postgres_pool()
    async with pool.acquire() as conn:
        yield conn

# InfluxDB helper functions
async def write_event_to_influxdb(event_data: dict):
    """Write security event to InfluxDB"""
    client = await get_influxdb_client()
    write_api = client.write_api(write_options=SYNCHRONOUS)
    
    point = Point("security_events") \
        .tag("asset_id", event_data.get("asset_id", "unknown")) \
        .tag("event_type", event_data.get("event_type", "unknown")) \
        .tag("severity", event_data.get("severity", "info")) \
        .field("bytes_transferred", event_data.get("bytes_transferred", 0)) \
        .field("login_attempts", event_data.get("login_attempts", 0)) \
        .field("duration", event_data.get("duration", 0)) \
        .time(event_data.get("timestamp", datetime.utcnow()))
    
    write_api.write(bucket=settings.INFLUXDB_BUCKET, record=point)
    write_api.close()

async def query_events_from_influxdb(start_time: str, end_time: str, asset_id: Optional[str] = None):
    """Query security events from InfluxDB"""
    client = await get_influxdb_client()
    query_api = client.query_api()
    
    query = f'''
    from(bucket: "{settings.INFLUXDB_BUCKET}")
        |> range(start: {start_time}, stop: {end_time})
    '''
    
    if asset_id:
        query += f'|> filter(fn: (r) => r["asset_id"] == "{asset_id}")'
    
    result = query_api.query(query)
    return result

# Elasticsearch helper functions
async def index_log_to_elasticsearch(log_data: dict):
    """Index security log to Elasticsearch"""
    client = await get_elasticsearch_client()
    
    await client.index(
        index="security_logs",
        body=log_data
    )

async def search_logs_in_elasticsearch(query: str, start_time: str, end_time: str, size: int = 100):
    """Search security logs in Elasticsearch"""
    client = await get_elasticsearch_client()
    
    search_body = {
        "query": {
            "bool": {
                "must": [
                    {"query_string": {"query": query}},
                    {"range": {"timestamp": {"gte": start_time, "lte": end_time}}}
                ]
            }
        },
        "sort": [{"timestamp": {"order": "desc"}}],
        "size": size
    }
    
    response = await client.search(
        index="security_logs",
        body=search_body
    )
    
    return response["hits"]["hits"]

# Redis helper functions
async def cache_data(key: str, data: dict, expire_seconds: int = 3600):
    """Cache data in Redis"""
    client = await get_redis_client()
    await client.setex(key, expire_seconds, str(data))

async def get_cached_data(key: str) -> Optional[dict]:
    """Get cached data from Redis"""
    client = await get_redis_client()
    data = await client.get(key)
    return eval(data) if data else None

async def invalidate_cache(pattern: str):
    """Invalidate cache entries matching pattern"""
    client = await get_redis_client()
    keys = await client.keys(pattern)
    if keys:
        await client.delete(*keys) 