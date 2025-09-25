import asyncio
import csv
import io
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.core.ioc_utils import detect_ioc_type
from app.models.bulk import BulkJob, JobStatus
from app.services.aggregator import FlashThreatAggregator
from app.services.cache import RedisCache

logger = logging.getLogger(__name__)


class BulkProcessor:
    """Service for processing bulk IOC jobs."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.cache = RedisCache()
        self.aggregator = FlashThreatAggregator(self.cache)
    
    async def parse_csv_file(self, file_content: bytes, filename: str) -> List[str]:
        """
        Parse CSV file and extract IOCs.
        
        Args:
            file_content: Raw file content
            filename: Original filename
            
        Returns:
            List of IOC strings
            
        Raises:
            ValueError: If file format is invalid
        """
        try:
            # Decode file content
            content = file_content.decode('utf-8')
            
            # Parse CSV
            csv_reader = csv.reader(io.StringIO(content))
            iocs = []
            
            for row_num, row in enumerate(csv_reader, 1):
                if not row or not row[0].strip():
                    continue  # Skip empty rows
                
                ioc = row[0].strip()
                if ioc:
                    iocs.append(ioc)
            
            if not iocs:
                raise ValueError("No valid IOCs found in CSV file")
            
            # Validate IOCs
            valid_iocs = []
            for ioc in iocs:
                ioc_type, error = detect_ioc_type(ioc)
                if not error:  # Valid IOC
                    valid_iocs.append(ioc)
                else:
                    logger.warning(f"Invalid IOC '{ioc}': {error}")
            
            if not valid_iocs:
                raise ValueError("No valid IOCs found after validation")
            
            return valid_iocs
            
        except UnicodeDecodeError:
            raise ValueError("File must be UTF-8 encoded")
        except Exception as e:
            raise ValueError(f"Error parsing CSV file: {str(e)}")
    
    async def create_bulk_job(
        self,
        file_content: bytes,
        filename: str,
        force_refresh: bool = False,
        user_id: Optional[str] = None
    ) -> BulkJob:
        """
        Create a new bulk job.
        
        Args:
            file_content: Raw file content
            filename: Original filename
            force_refresh: Whether to force refresh cache
            user_id: Optional user ID
            
        Returns:
            Created BulkJob instance
        """
        # Parse CSV file
        iocs = await self.parse_csv_file(file_content, filename)
        
        # Create bulk job
        bulk_job = BulkJob(
            user_id=user_id,
            total_iocs=len(iocs),
            original_filename=filename,
            file_size=len(file_content),
            ioc_list=iocs,
            force_refresh=force_refresh,
            status=JobStatus.PENDING
        )
        
        self.db.add(bulk_job)
        await self.db.commit()
        await self.db.refresh(bulk_job)
        
        logger.info(f"Created bulk job {bulk_job.id} with {len(iocs)} IOCs")
        return bulk_job
    
    async def process_bulk_job(self, job_id: str) -> None:
        """
        Process a bulk job in the background.
        
        Args:
            job_id: Job ID to process
        """
        try:
            # Get job from database
            result = await self.db.execute(
                select(BulkJob).where(BulkJob.id == job_id)
            )
            job = result.scalar_one_or_none()
            
            if not job:
                logger.error(f"Bulk job {job_id} not found")
                return
            
            if job.status != JobStatus.PENDING:
                logger.warning(f"Bulk job {job_id} is not in pending status: {job.status}")
                return
            
            # Update job status to processing
            await self.db.execute(
                update(BulkJob)
                .where(BulkJob.id == job_id)
                .values(
                    status=JobStatus.PROCESSING,
                    started_at=datetime.utcnow()
                )
            )
            await self.db.commit()
            
            logger.info(f"Started processing bulk job {job_id}")
            
            # Process each IOC
            results = []
            completed = 0
            failed = 0
            
            for i, ioc in enumerate(job.ioc_list):
                try:
                    # Process IOC
                    lookup_id, result = await self.aggregator.check_ioc(
                        ioc, 
                        force_refresh=job.force_refresh
                    )
                    
                    results.append({
                        "ioc": ioc,
                        "lookup_id": lookup_id,
                        "result": result,
                        "processed_at": datetime.utcnow().isoformat()
                    })
                    completed += 1
                    
                except Exception as e:
                    logger.error(f"Failed to process IOC '{ioc}': {str(e)}")
                    results.append({
                        "ioc": ioc,
                        "error": str(e),
                        "processed_at": datetime.utcnow().isoformat()
                    })
                    failed += 1
                
                # Update progress
                processed = i + 1
                await self.db.execute(
                    update(BulkJob)
                    .where(BulkJob.id == job_id)
                    .values(
                        processed_iocs=processed,
                        completed_iocs=completed,
                        failed_iocs=failed,
                        results=results
                    )
                )
                await self.db.commit()
                
                # Small delay to prevent overwhelming APIs
                await asyncio.sleep(0.1)
            
            # Mark job as completed
            await self.db.execute(
                update(BulkJob)
                .where(BulkJob.id == job_id)
                .values(
                    status=JobStatus.COMPLETED,
                    completed_at=datetime.utcnow()
                )
            )
            await self.db.commit()
            
            logger.info(f"Completed bulk job {job_id}: {completed} completed, {failed} failed")
            
        except Exception as e:
            logger.error(f"Error processing bulk job {job_id}: {str(e)}")
            
            # Mark job as failed
            try:
                await self.db.execute(
                    update(BulkJob)
                    .where(BulkJob.id == job_id)
                    .values(
                        status=JobStatus.FAILED,
                        error_message=str(e),
                        completed_at=datetime.utcnow()
                    )
                )
                await self.db.commit()
            except Exception as commit_error:
                logger.error(f"Failed to update job status: {str(commit_error)}")
    
    async def get_job_progress(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job progress information.
        
        Args:
            job_id: Job ID
            
        Returns:
            Job progress dictionary or None if not found
        """
        result = await self.db.execute(
            select(BulkJob).where(BulkJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            return None
        
        return job.to_dict()
    
    async def generate_results_csv(self, job_id: str) -> str:
        """
        Generate CSV results for a completed job.
        
        Args:
            job_id: Job ID
            
        Returns:
            CSV content as string
        """
        result = await self.db.execute(
            select(BulkJob).where(BulkJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job or not job.results:
            raise ValueError("Job not found or no results available")
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "IOC", "Type", "Verdict", "Score", "First Seen", "Last Seen", 
            "VirusTotal", "AbuseIPDB", "OTX", "Error"
        ])
        
        # Write results
        for result in job.results:
            if "error" in result:
                writer.writerow([
                    result["ioc"], "", "", "", "", "", "", "", "", result["error"]
                ])
            else:
                ioc_data = result["result"]
                summary = ioc_data.get("summary", {})
                ioc_info = ioc_data.get("ioc", {})
                
                # Get provider results
                providers = ioc_data.get("providers", [])
                vt_result = next((p for p in providers if p.get("provider") == "virustotal"), {})
                abuse_result = next((p for p in providers if p.get("provider") == "abuseipdb"), {})
                otx_result = next((p for p in providers if p.get("provider") == "otx"), {})
                
                writer.writerow([
                    result["ioc"],
                    ioc_info.get("type", ""),
                    summary.get("verdict", ""),
                    summary.get("score", ""),
                    summary.get("first_seen", ""),
                    summary.get("last_seen", ""),
                    "✓" if vt_result.get("success") else "✗",
                    "✓" if abuse_result.get("success") else "✗",
                    "✓" if otx_result.get("success") else "✗",
                    ""
                ])
        
        return output.getvalue()
