"""
GitHub repository analyzer for direct analysis of GitHub-hosted projects.
Clones repositories and runs the full documentation consistency analysis.
"""

import os
import shutil
import tempfile
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
import subprocess

from analyzer.code_parser import CodeParser
from analyzer.doc_parser import DocumentationParser
from analyzer.comparator import Comparator

logger = logging.getLogger(__name__)


class GitHubAnalyzer:
    """Analyze Python projects directly from GitHub repositories."""

    def __init__(self, token: Optional[str] = None, timeout: int = 30):
        """
        Initialize GitHub analyzer.
        
        Parameters
        ----------
        token : Optional[str]
            GitHub personal access token for private repos
        timeout : int
            Git clone timeout in seconds
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.timeout = timeout
        self.temp_dir: Optional[Path] = None

    def _build_clone_url(self, repo: str) -> str:
        """
        Build git clone URL from repo identifier.
        
        Parameters
        ----------
        repo : str
            Repository in format "owner/repo" or full GitHub URL
            
        Returns
        -------
        str : Full git clone URL
        """
        # Handle full URLs
        if repo.startswith("http"):
            if self.token:
                # Insert token for HTTPS authentication
                repo = repo.replace("https://", f"https://x-access-token:{self.token}@")
            return repo
        
        # Handle owner/repo format
        if "/" in repo:
            if self.token:
                return f"https://x-access-token:{self.token}@github.com/{repo}.git"
            return f"https://github.com/{repo}.git"
        
        raise ValueError(f"Invalid repository format: {repo}. Use 'owner/repo' or full URL.")

    def _clone_repository(self, repo: str, target_dir: Path) -> bool:
        """
        Clone a GitHub repository to a local directory.
        
        Parameters
        ----------
        repo : str
            Repository identifier or URL
        target_dir : Path
            Target directory for cloning
            
        Returns
        -------
        bool : True if successful, False otherwise
        """
        clone_url = self._build_clone_url(repo)
        
        try:
            logger.info(f"Cloning repository: {repo}")
            result = subprocess.run(
                ["git", "clone", "--depth", "1", clone_url, str(target_dir)],
                timeout=self.timeout,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"Git clone failed: {result.stderr}")
                return False
            
            logger.info(f"Successfully cloned to {target_dir}")
            return True
            
        except FileNotFoundError:
            logger.error("Git not found. Install git or use 'pip install GitPython'")
            return False
        except subprocess.TimeoutExpired:
            logger.error(f"Clone operation timed out after {self.timeout}s")
            return False
        except Exception as e:
            logger.error(f"Clone failed: {str(e)}")
            return False

    def analyze_repository(
        self,
        repo: str,
        cleanup: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze a GitHub repository for documentation consistency.
        
        Parameters
        ----------
        repo : str
            GitHub repository (owner/repo format or full URL)
        cleanup : bool
            Whether to delete temporary files after analysis
            
        Returns
        -------
        Dict[str, Any] : Analysis result with status, issues, etc.
        """
        self.temp_dir = Path(tempfile.mkdtemp(prefix="github_analyzer_"))
        
        try:
            # Clone repository
            if not self._clone_repository(repo, self.temp_dir):
                return {
                    "status": "failed",
                    "error": "Failed to clone repository",
                    "issues": [],
                    "checked_samples": 0,
                    "mode": "github",
                    "repository": repo
                }
            
            # Run analysis
            from project_analyzer import analyze_project
            result = analyze_project(str(self.temp_dir))
            result["repository"] = repo
            result["mode"] = "github"
            
            logger.info(f"Analysis complete: {len(result.get('issues', []))} issues found")
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "issues": [],
                "checked_samples": 0,
                "mode": "github",
                "repository": repo
            }
        finally:
            if cleanup and self.temp_dir and self.temp_dir.exists():
                try:
                    shutil.rmtree(self.temp_dir)
                    logger.info(f"Cleaned up temporary directory: {self.temp_dir}")
                except Exception as e:
                    logger.warning(f"Failed to cleanup temp directory: {str(e)}")
                finally:
                    self.temp_dir = None

    def analyze_multiple_repositories(
        self,
        repos: List[str],
        cleanup: bool = True
    ) -> Dict[str, Dict[str, Any]]:
        """
        Analyze multiple repositories.
        
        Parameters
        ----------
        repos : List[str]
            List of repositories to analyze
        cleanup : bool
            Whether to delete temporary files after each analysis
            
        Returns
        -------
        Dict[str, Dict[str, Any]] : Results keyed by repository name
        """
        results = {}
        
        for repo in repos:
            logger.info(f"Starting analysis of {repo}")
            results[repo] = self.analyze_repository(repo, cleanup=cleanup)
            logger.info(f"Completed analysis of {repo}")
        
        return results

    @staticmethod
    def validate_github_url(repo: str) -> bool:
        """
        Validate GitHub repository format.
        
        Parameters
        ----------
        repo : str
            Repository identifier or URL
            
        Returns
        -------
        bool : True if valid format
        """
        if repo.startswith("http"):
            return "github.com" in repo
        
        # Check owner/repo format
        parts = repo.split("/")
        return len(parts) == 2 and all(p for p in parts)

    def get_repository_info(self, repo: str) -> Dict[str, Any]:
        """
        Get repository metadata without cloning.
        Requires GitHub API (not implemented here, would need requests library).
        
        Parameters
        ----------
        repo : str
            Repository identifier
            
        Returns
        -------
        Dict[str, Any] : Repository information
        """
        if not self.validate_github_url(repo):
            return {"error": "Invalid repository format"}
        
        # Extract owner/repo
        if repo.startswith("http"):
            parts = repo.rstrip("/").split("/")
            owner, repo_name = parts[-2], parts[-1].replace(".git", "")
        else:
            owner, repo_name = repo.split("/")
        
        return {
            "owner": owner,
            "name": repo_name,
            "url": f"https://github.com/{owner}/{repo_name}",
            "api_url": f"https://api.github.com/repos/{owner}/{repo_name}"
        }


class GitHubBatchAnalyzer:
    """Batch analyze multiple GitHub repositories with progress tracking."""

    def __init__(self, token: Optional[str] = None, max_concurrent: int = 1):
        """
        Initialize batch analyzer.
        
        Parameters
        ----------
        token : Optional[str]
            GitHub personal access token
        max_concurrent : int
            Maximum concurrent analyses (default 1 to avoid rate limits)
        """
        self.analyzer = GitHubAnalyzer(token=token)
        self.max_concurrent = max_concurrent
        self.results: Dict[str, Dict[str, Any]] = {}

    def analyze(self, repos: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Analyze multiple repositories sequentially.
        
        Parameters
        ----------
        repos : List[str]
            List of repositories
            
        Returns
        -------
        Dict[str, Dict[str, Any]] : Analysis results
        """
        logger.info(f"Starting batch analysis of {len(repos)} repositories")
        
        for i, repo in enumerate(repos, 1):
            logger.info(f"[{i}/{len(repos)}] Analyzing {repo}")
            self.results[repo] = self.analyzer.analyze_repository(repo)
        
        logger.info("Batch analysis complete")
        return self.results

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of all analyses.
        
        Returns
        -------
        Dict[str, Any] : Summary with totals and averages
        """
        if not self.results:
            return {"total_repos": 0, "total_issues": 0, "average_score": 0}
        
        total_issues = sum(
            len(r.get("issues", []))
            for r in self.results.values()
        )
        
        checked_samples = sum(
            r.get("checked_samples", 0)
            for r in self.results.values()
        )
        
        successful = sum(
            1 for r in self.results.values()
            if r.get("status") == "ok"
        )
        
        return {
            "total_repos": len(self.results),
            "successful_analyses": successful,
            "failed_analyses": len(self.results) - successful,
            "total_files_checked": checked_samples,
            "total_issues_found": total_issues,
            "average_issues_per_repo": (
                total_issues / len(self.results) if self.results else 0
            ),
            "results": self.results
        }
