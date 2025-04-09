from typing import Any, Dict, List


def get_jobs_for_schedule(config: dict, schedule_name: str) -> list:
    """
    Retrieves jobs for a specific schedule from the configuration.
    """
    return config.get("schedules", {}).get(schedule_name, [])


def resolve_dependencies(
    jobs: List[Dict[str, Any]], target_job_name: str
) -> List[Dict[str, Any]]:
    """
    Resolves job dependencies and returns an ordered list of jobs.
    """
    job_map = {job["name"]: job for job in jobs}
    visited = set()
    ordered: List[Dict[str, Any]] = []

    def visit(name: str) -> None:
        if name in visited:
            return
        job = job_map.get(name)
        if not job:
            raise ValueError(f"Job '{name}' not found in schedule")
        dep = job.get("depends_on")
        if dep:
            visit(dep)
        visited.add(name)
        ordered.append(job)

    visit(target_job_name)
    return ordered
