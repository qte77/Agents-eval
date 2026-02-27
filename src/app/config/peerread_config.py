"""PeerRead dataset configuration model."""

from pydantic import BaseModel, Field

from app.config.config_app import DATASETS_PEERREAD_PATH


class PeerReadConfig(BaseModel):
    """Configuration for PeerRead dataset management."""

    base_url: str = Field(
        default="https://github.com/allenai/PeerRead/tree/master/data",
        description="Base URL for PeerRead dataset",
    )
    github_api_base_url: str = Field(
        default="https://api.github.com/repos/allenai/PeerRead/contents/data",
        description="Base URL for GitHub API to list PeerRead dataset contents",
    )
    raw_github_base_url: str = Field(
        default="https://raw.githubusercontent.com/allenai/PeerRead/master/data",
        description="Base URL for raw GitHub content of PeerRead dataset",
    )
    cache_directory: str = Field(
        default=DATASETS_PEERREAD_PATH,
        description="Local directory for caching downloaded data",
    )
    venues: list[str] = Field(
        default=["acl_2017", "conll_2016", "iclr_2017"],
        description="Available conference venues",
    )
    splits: list[str] = Field(default=["train", "test", "dev"], description="Available data splits")
    max_papers_per_query: int = Field(default=100, description="Maximum papers to return per query")
    download_timeout: int = Field(
        default=30, description="Timeout for download requests in seconds"
    )
    max_retries: int = Field(
        default=5, description="Maximum number of retry attempts for downloads"
    )
    retry_delay_seconds: int = Field(
        default=5, description="Delay in seconds between retry attempts"
    )
    similarity_metrics: dict[str, float] = Field(
        default={"cosine_weight": 0.6, "jaccard_weight": 0.4},
        description="Weights for similarity metrics",
    )
