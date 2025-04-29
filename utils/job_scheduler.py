from typing import Any, Dict, List, Set


class DependencyResolver:
    def __init__(self) -> None:
        self.visited: Set[str] = set()
        self.ordered: List[Dict[str, Any]] = []
        self.job_map: Dict[str, Dict[str, Any]] = {}

    @staticmethod
    def get_jobs_for_schedule(config: dict, schedule_name: str) -> List[Dict[str, Any]]:
        """
        Retrieves jobs for a specific schedule from the configuration.
        """
        return config.get("schedule", {}).get(schedule_name, [])

    def resolve_dependencies(
        self, jobs: List[Dict[str, Any]], target_job_name: str
    ) -> List[Dict[str, Any]]:
        """
        Resolves job dependencies and returns an ordered list of jobs.
        """
        self.job_map = {job["name"]: job for job in jobs}
        self.visited.clear()
        self.ordered.clear()

        self.visit(target_job_name)
        return self.ordered

    def visit(self, name: str) -> None:
        """
        Visits a job and its dependencies recursively. Avoids cycles by checking if the job has already been visited.
        """
        if name in self.visited:
            return
        job = self.job_map.get(name)
        if not job:
            raise ValueError(f"Job '{name}' not found in schedule")
        dep = job.get("depends_on")
        if isinstance(dep, list):
            for d in dep:
                self.visit(d)
        elif isinstance(dep, str):
            self.visit(dep)

        self.visited.add(name)
        self.ordered.append(job)
