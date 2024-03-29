import logging as log
from operator import attrgetter
from typing import List, Set, Dict, AnyStr

from git import Commit

from szz.core.abstract_szz import ImpactedFile, BlameData
from szz.ma_szz import MASZZ


class RSZZ(MASZZ):
    """
    Recent-SZZ implementation.
    """

    def __init__(self, repo_full_name: str, repo_url: str, repos_dir: str):
        super().__init__(repo_full_name, repo_url, repos_dir)

    # TODO: add parse and type check on kwargs
    def find_bic(self, fix_commit_hash: str, impacted_files: List['ImpactedFile'], **kwargs) -> BlameData:
        bic_candidates = super().find_bic(fix_commit_hash, impacted_files, **kwargs)
        bic_candidates_commit = set(bd.commit for bd in bic_candidates)
        latest_bic = None
        if len(bic_candidates) > 0:
            latest_bic_commit = max(bic_candidates_commit, key=attrgetter('committed_date'))
            for bd in bic_candidates:
                if bd.commit == latest_bic_commit:
                    latest_bic = bd
                    break
        
            #log.info(f"selected bug introducing commit: {latest_bic.commit.hexsha}")
        return latest_bic
