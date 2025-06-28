import asyncio
import json
from typing import Dict, List, Any, Optional
import structlog
from datetime import datetime, timedelta
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import pandas as pd
import redis.asyncio as redis

from app.core.config import settings
from app.core.database import get_redis_client, write_event_to_influxdb, index_log_to_elasticsearch

logger = structlog.get_logger()

class KafkaManager:
    """Kafka producer and consumer manager"""
    
    def __init__(self):
        self.producer = None
        self.consumers = {}
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize Kafka connections"""
        try:
            # Initialize producer
            self.producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',
                retries=3
            )
            
            # Initialize consumers for different topics
            topics = [
                settings.KAFKA_TOPIC_EVENTS,
                settings.KAFKA_TOPIC_LOGS,
                settings.KAFKA_TOPIC_THREAT_INTEL
            ]
            
            for topic in topics:
                consumer = KafkaConsumer(
                    topic,
                    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                    auto_offset_reset='latest',
                    enable_auto_commit=True,
                    group_id=f'securityai_{topic}_consumer'
                )
                self.consumers[topic] = consumer
            
            self.is_initialized = True
            logger.info("Kafka manager initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize Kafka manager", error=str(e))
            raise
    
    async def send_event(self, topic: str, event: Dict[str, Any], key: Optional[str] = None):
        """Send event to Kafka topic"""
        if not self.is_initialized:
            raise RuntimeError("Kafka manager not initialized")
        
        try:
            future = self.producer.send(topic, value=event, key=key)
            record_metadata = future.get(timeout=10)
            
            logger.debug(
                "Event sent to Kafka",
                topic=topic,
                partition=record_metadata.partition,
                offset=record_metadata.offset
            )
            
            return {
                "topic": topic,
                "partition": record_metadata.partition,
                "offset": record_metadata.offset
            }
            
        except KafkaError as e:
            logger.error("Failed to send event to Kafka", error=str(e))
            raise
    
    async def consume_events(self, topic: str, callback):
        """Consume events from Kafka topic"""
        if not self.is_initialized or topic not in self.consumers:
            raise RuntimeError(f"Consumer for topic {topic} not initialized")
        
        try:
            consumer = self.consumers[topic]
            
            for message in consumer:
                try:
                    await callback(message.value)
                except Exception as e:
                    logger.error("Error processing Kafka message", error=str(e))
                    
        except Exception as e:
            logger.error(f"Error consuming from topic {topic}", error=str(e))
            raise
    
    async def close(self):
        """Close Kafka connections"""
        try:
            if self.producer:
                self.producer.close()
            
            for consumer in self.consumers.values():
                consumer.close()
            
            logger.info("Kafka connections closed")
            
        except Exception as e:
            logger.error("Error closing Kafka connections", error=str(e))

class DataProcessor:
    """Data processing and transformation"""
    
    def __init__(self):
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize data processor"""
        try:
            self.is_initialized = True
            logger.info("Data processor initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize data processor", error=str(e))
            raise
    
    async def process_security_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process and enrich security event data"""
        try:
            # Add metadata
            processed_event = event.copy()
            processed_event["processed_at"] = datetime.utcnow().isoformat()
            processed_event["event_id"] = self._generate_event_id()
            
            # Enrich with threat intelligence
            threat_intel = await self._enrich_with_threat_intelligence(event)
            processed_event["threat_intelligence"] = threat_intel
            
            # Normalize data
            processed_event = self._normalize_event_data(processed_event)
            
            return processed_event
            
        except Exception as e:
            logger.error("Failed to process security event", error=str(e))
            raise
    
    async def process_log_entry(self, log_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Process and parse log entry"""
        try:
            processed_log = log_entry.copy()
            processed_log["processed_at"] = datetime.utcnow().isoformat()
            
            # Extract structured data from log message
            structured_data = self._parse_log_message(log_entry.get("message", ""))
            processed_log["structured_data"] = structured_data
            
            # Add log level if not present
            if "level" not in processed_log:
                processed_log["level"] = self._determine_log_level(log_entry.get("message", ""))
            
            return processed_log
            
        except Exception as e:
            logger.error("Failed to process log entry", error=str(e))
            raise
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        import uuid
        return str(uuid.uuid4())
    
    async def _enrich_with_threat_intelligence(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich event with threat intelligence data"""
        try:
            threat_intel = {
                "ip_reputation": "unknown",
                "domain_reputation": "unknown",
                "malware_family": None,
                "attack_techniques": [],
                "confidence": 0.0
            }
            
            # Check IP reputation
            source_ip = event.get("source_ip")
            if source_ip:
                ip_reputation = await self._check_ip_reputation(source_ip)
                threat_intel["ip_reputation"] = ip_reputation
            
            # Check domain reputation
            domain = event.get("domain")
            if domain:
                domain_reputation = await self._check_domain_reputation(domain)
                threat_intel["domain_reputation"] = domain_reputation
            
            return threat_intel
            
        except Exception as e:
            logger.error("Failed to enrich with threat intelligence", error=str(e))
            return {"error": str(e)}
    
    async def _check_ip_reputation(self, ip: str) -> str:
        """Check IP reputation (mock implementation)"""
        # In production, this would call VirusTotal, AlienVault OTX, etc.
        import random
        reputations = ["clean", "suspicious", "malicious"]
        return random.choice(reputations)
    
    async def _check_domain_reputation(self, domain: str) -> str:
        """Check domain reputation (mock implementation)"""
        # In production, this would call threat intelligence APIs
        import random
        reputations = ["clean", "suspicious", "malicious"]
        return random.choice(reputations)
    
    def _normalize_event_data(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize event data format"""
        try:
            normalized = event.copy()
            
            # Ensure required fields
            required_fields = ["timestamp", "event_type", "source_ip"]
            for field in required_fields:
                if field not in normalized:
                    normalized[field] = None
            
            # Convert timestamp to ISO format
            if normalized["timestamp"]:
                if isinstance(normalized["timestamp"], str):
                    # Already in string format
                    pass
                else:
                    normalized["timestamp"] = normalized["timestamp"].isoformat()
            
            # Normalize IP addresses
            if normalized["source_ip"]:
                normalized["source_ip"] = str(normalized["source_ip"])
            
            return normalized
            
        except Exception as e:
            logger.error("Failed to normalize event data", error=str(e))
            return event
    
    def _parse_log_message(self, message: str) -> Dict[str, Any]:
        """Parse log message and extract structured data"""
        try:
            structured_data = {}
            
            # Extract IP addresses
            import re
            ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
            ips = re.findall(ip_pattern, message)
            if ips:
                structured_data["ip_addresses"] = ips
            
            # Extract timestamps
            timestamp_pattern = r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}'
            timestamps = re.findall(timestamp_pattern, message)
            if timestamps:
                structured_data["timestamps"] = timestamps
            
            # Extract user names
            user_pattern = r'user[:\s]+([a-zA-Z0-9_]+)'
            user_match = re.search(user_pattern, message, re.IGNORECASE)
            if user_match:
                structured_data["user"] = user_match.group(1)
            
            # Extract actions
            action_keywords = ['login', 'logout', 'access', 'denied', 'blocked', 'failed']
            for keyword in action_keywords:
                if keyword in message.lower():
                    structured_data["action"] = keyword
                    break
            
            return structured_data
            
        except Exception as e:
            logger.error("Failed to parse log message", error=str(e))
            return {}
    
    def _determine_log_level(self, message: str) -> str:
        """Determine log level from message content"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['error', 'failed', 'denied', 'blocked']):
            return 'error'
        elif any(word in message_lower for word in ['warning', 'suspicious', 'unusual']):
            return 'warning'
        elif any(word in message_lower for word in ['info', 'success', 'allowed']):
            return 'info'
        else:
            return 'debug'

class DataPipeline:
    """Main data pipeline orchestrator"""
    
    def __init__(self):
        self.kafka_manager = KafkaManager()
        self.data_processor = DataProcessor()
        self.is_initialized = False
        self.processing_tasks = []
        
    async def initialize(self):
        """Initialize data pipeline"""
        try:
            # Initialize components
            await self.kafka_manager.initialize()
            await self.data_processor.initialize()
            
            # Start background processing tasks
            await self._start_background_tasks()
            
            self.is_initialized = True
            logger.info("Data pipeline initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize data pipeline", error=str(e))
            raise
    
    async def _start_background_tasks(self):
        """Start background data processing tasks"""
        try:
            # Start event processing
            event_task = asyncio.create_task(
                self._process_events()
            )
            self.processing_tasks.append(event_task)
            
            # Start log processing
            log_task = asyncio.create_task(
                self._process_logs()
            )
            self.processing_tasks.append(log_task)
            
            # Start threat intelligence processing
            intel_task = asyncio.create_task(
                self._process_threat_intelligence()
            )
            self.processing_tasks.append(intel_task)
            
            logger.info("Background processing tasks started")
            
        except Exception as e:
            logger.error("Failed to start background tasks", error=str(e))
            raise
    
    async def _process_events(self):
        """Process security events from Kafka"""
        try:
            await self.kafka_manager.consume_events(
                settings.KAFKA_TOPIC_EVENTS,
                self._handle_security_event
            )
        except Exception as e:
            logger.error("Error in event processing loop", error=str(e))
    
    async def _process_logs(self):
        """Process log entries from Kafka"""
        try:
            await self.kafka_manager.consume_events(
                settings.KAFKA_TOPIC_LOGS,
                self._handle_log_entry
            )
        except Exception as e:
            logger.error("Error in log processing loop", error=str(e))
    
    async def _process_threat_intelligence(self):
        """Process threat intelligence feeds"""
        try:
            await self.kafka_manager.consume_events(
                settings.KAFKA_TOPIC_THREAT_INTEL,
                self._handle_threat_intelligence
            )
        except Exception as e:
            logger.error("Error in threat intelligence processing loop", error=str(e))
    
    async def _handle_security_event(self, event: Dict[str, Any]):
        """Handle incoming security event"""
        try:
            # Process event
            processed_event = await self.data_processor.process_security_event(event)
            
            # Store in InfluxDB
            await write_event_to_influxdb(processed_event)
            
            # Cache for quick access
            redis_client = await get_redis_client()
            cache_key = f"event:{processed_event['event_id']}"
            await redis_client.setex(cache_key, 3600, json.dumps(processed_event))
            
            logger.debug("Security event processed", event_id=processed_event['event_id'])
            
        except Exception as e:
            logger.error("Failed to handle security event", error=str(e))
    
    async def _handle_log_entry(self, log_entry: Dict[str, Any]):
        """Handle incoming log entry"""
        try:
            # Process log entry
            processed_log = await self.data_processor.process_log_entry(log_entry)
            
            # Store in Elasticsearch
            await index_log_to_elasticsearch(processed_log)
            
            logger.debug("Log entry processed", log_id=processed_log.get('id'))
            
        except Exception as e:
            logger.error("Failed to handle log entry", error=str(e))
    
    async def _handle_threat_intelligence(self, intel_data: Dict[str, Any]):
        """Handle incoming threat intelligence data"""
        try:
            # Cache threat intelligence data
            redis_client = await get_redis_client()
            
            # Cache IP reputation
            if "ip" in intel_data:
                cache_key = f"ip_reputation:{intel_data['ip']}"
                await redis_client.setex(cache_key, 86400, json.dumps(intel_data))  # 24 hours
            
            # Cache domain reputation
            if "domain" in intel_data:
                cache_key = f"domain_reputation:{intel_data['domain']}"
                await redis_client.setex(cache_key, 86400, json.dumps(intel_data))  # 24 hours
            
            logger.debug("Threat intelligence data processed")
            
        except Exception as e:
            logger.error("Failed to handle threat intelligence", error=str(e))
    
    async def send_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Send event to data pipeline"""
        if not self.is_initialized:
            raise RuntimeError("Data pipeline not initialized")
        
        try:
            # Send to Kafka
            result = await self.kafka_manager.send_event(
                settings.KAFKA_TOPIC_EVENTS,
                event
            )
            
            return result
            
        except Exception as e:
            logger.error("Failed to send event to pipeline", error=str(e))
            raise
    
    async def send_log(self, log_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Send log entry to data pipeline"""
        if not self.is_initialized:
            raise RuntimeError("Data pipeline not initialized")
        
        try:
            # Send to Kafka
            result = await self.kafka_manager.send_event(
                settings.KAFKA_TOPIC_LOGS,
                log_entry
            )
            
            return result
            
        except Exception as e:
            logger.error("Failed to send log to pipeline", error=str(e))
            raise
    
    async def get_status(self) -> Dict[str, Any]:
        """Get data pipeline status"""
        return {
            "is_initialized": self.is_initialized,
            "kafka_status": self.kafka_manager.is_initialized,
            "processor_status": self.data_processor.is_initialized,
            "active_tasks": len(self.processing_tasks),
            "kafka_topics": list(self.kafka_manager.consumers.keys())
        }
    
    async def cleanup(self):
        """Cleanup data pipeline resources"""
        try:
            # Cancel background tasks
            for task in self.processing_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(*self.processing_tasks, return_exceptions=True)
            
            # Close Kafka connections
            await self.kafka_manager.close()
            
            logger.info("Data pipeline cleanup completed")
            
        except Exception as e:
            logger.error("Failed to cleanup data pipeline", error=str(e)) 