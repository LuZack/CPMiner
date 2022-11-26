from functools import cmp_to_key
import json
import logging as log
import os
import platform
import re
import sys
import dateparser
from time import time as ts

import yaml

from szz.ag_szz import AGSZZ
from szz.b_szz import BaseSZZ
from szz.l_szz import LSZZ
from szz.ma_szz import MASZZ, DetectLineMoved
from szz.r_szz import RSZZ
from szz.ra_szz import RASZZ

log.basicConfig(level=log.INFO, format='%(levelname)s :: %(message)s')
log.getLogger('pydriller').setLevel(log.WARNING)


def main(input_json: str, out_json: str, conf: dict(), repos_dir: str, size: int, index: int):
    with open(input_json, 'r') as in_file:
        bugfix_commits = json.loads(in_file.read())

    tot = len(bugfix_commits)
    start_idx = int(index) * int(size)
    end_idx = (int(index) + 1) * int(size)
    # enumerate: latest commit to initial commit
    for i, commit in enumerate(bugfix_commits):
        if i < start_idx:
            continue
        if i >= end_idx:
            break
        bug_introducing_commits = set()
        repo_name = commit['repo_name']
        repo_url = f'https://test:test@github.com/{repo_name}.git'  # using test:test as git login to skip private repos during clone
        fix_commit = commit['fix_commit_hash']

        log.info(f'{i + 1} of {tot}: {repo_name} {fix_commit}')
        
        commit_issue_date = None
        if conf.get('issue_date_filter', None):
            commit_issue_date = (commit.get('earliest_issue_date', None) or commit.get('best_scenario_issue_date', None))
            commit_issue_date = dateparser.parse(commit_issue_date).timestamp()
        
        szz_name = conf['szz_name']
        if szz_name == 'b':
            b_szz = BaseSZZ(repo_full_name=repo_name, repo_url=repo_url, repos_dir=repos_dir)
            imp_files = b_szz.get_impacted_files(fix_commit_hash=fix_commit, file_ext_to_parse=conf.get('file_ext_to_parse'), only_deleted_lines=conf.get('only_deleted_lines', True))
            bug_introducing_commits = b_szz.find_bic(fix_commit_hash=fix_commit,
                                        impacted_files=imp_files,
                                        ignore_revs_file_path=conf.get('ignore_revs_file_path'),
                                        issue_date_filter=conf.get('issue_date_filter'),
                                        issue_date=commit_issue_date)

        elif szz_name == 'ag':
            ag_szz = AGSZZ(repo_full_name=repo_name, repo_url=repo_url, repos_dir=repos_dir)
            imp_files = ag_szz.get_impacted_files(fix_commit_hash=fix_commit, file_ext_to_parse=conf.get('file_ext_to_parse'), only_deleted_lines=conf.get('only_deleted_lines', True))
            bug_introducing_commits = ag_szz.find_bic(fix_commit_hash=fix_commit,
                                        impacted_files=imp_files,
                                        ignore_revs_file_path=conf.get('ignore_revs_file_path'),
                                        max_change_size=conf.get('max_change_size'),
                                        issue_date_filter=conf.get('issue_date_filter'),
                                        issue_date=commit_issue_date)

        elif szz_name == 'ma':
            ma_szz = MASZZ(repo_full_name=repo_name, repo_url=repo_url, repos_dir=repos_dir)
            imp_files = ma_szz.get_impacted_files(fix_commit_hash=fix_commit, file_ext_to_parse=conf.get('file_ext_to_parse'), only_deleted_lines=conf.get('only_deleted_lines', True))
            bug_introducing_commits = ma_szz.find_bic(fix_commit_hash=fix_commit,
                                        impacted_files=imp_files,
                                        ignore_revs_file_path=conf.get('ignore_revs_file_path'),
                                        max_change_size=conf.get('max_change_size'),
                                        detect_move_from_other_files=DetectLineMoved(conf.get('detect_move_from_other_files')),
                                        issue_date_filter=conf.get('issue_date_filter'),
                                        issue_date=commit_issue_date)

        elif szz_name == 'r':
            r_szz = RSZZ(repo_full_name=repo_name, repo_url=repo_url, repos_dir=repos_dir)
            imp_files = r_szz.get_impacted_files(fix_commit_hash=fix_commit, file_ext_to_parse=conf.get('file_ext_to_parse'), only_deleted_lines=conf.get('only_deleted_lines', True))
            bug_introducing_commits = r_szz.find_bic(fix_commit_hash=fix_commit,
                                        impacted_files=imp_files,
                                        ignore_revs_file_path=conf.get('ignore_revs_file_path'),
                                        max_change_size=conf.get('max_change_size'),
                                        detect_move_from_other_files=DetectLineMoved(conf.get('detect_move_from_other_files')),
                                        issue_date_filter=conf.get('issue_date_filter'),
                                        issue_date=commit_issue_date)

        elif szz_name == 'l':
            l_szz = LSZZ(repo_full_name=repo_name, repo_url=repo_url, repos_dir=repos_dir)
            imp_files = l_szz.get_impacted_files(fix_commit_hash=fix_commit, file_ext_to_parse=conf.get('file_ext_to_parse'), only_deleted_lines=conf.get('only_deleted_lines', True))
            bug_introducing_commits = l_szz.find_bic(fix_commit_hash=fix_commit,
                                        impacted_files=imp_files,
                                        ignore_revs_file_path=conf.get('ignore_revs_file_path'),
                                        max_change_size=conf.get('max_change_size'),
                                        detect_move_from_other_files=DetectLineMoved(conf.get('detect_move_from_other_files')),
                                        issue_date_filter=conf.get('issue_date_filter'),
                                        issue_date=commit_issue_date)
        elif szz_name == 'ra':
            ra_szz = RASZZ(repo_full_name=repo_name, repo_url=repo_url, repos_dir=repos_dir)
            imp_files = ra_szz.get_impacted_files(fix_commit_hash=fix_commit, file_ext_to_parse=conf.get('file_ext_to_parse'), only_deleted_lines=conf.get('only_deleted_lines', True))
            bug_introducing_commits = ra_szz.find_bic(fix_commit_hash=fix_commit,
                                        impacted_files=imp_files,
                                        ignore_revs_file_path=conf.get('ignore_revs_file_path'),
                                        max_change_size=conf.get('max_change_size'),
                                        detect_move_from_other_files=DetectLineMoved(conf.get('detect_move_from_other_files')),
                                        issue_date_filter=conf.get('issue_date_filter'),
                                        issue_date=commit_issue_date)
        else:
            log.info(f'SZZ implementation not found: {szz_name}')
            exit(-3)

        #log.info(f"result: {bug_introducing_commits}")
        bugfix_commits[i]["inducing_commit_hash"] = [bic.commit.hexsha for bic in bug_introducing_commits if bic]
        bugfix_commits[i]["inducing_commit_file"] = [bic.file_path for bic in bug_introducing_commits if bic]
        bugfix_commits[i]["inducing_commit_line"] = [bic.line_str for bic in bug_introducing_commits if bic]

    with open(out_json, 'w') as out:
        json.dump(bugfix_commits, out)

    log.info("+++ DONE +++")

{'tensorflow/tools/pip_package/setup.py': ['6bf47671443b66a65c4bff41b3ddc8ff9c00dbb8', ["_VERSION = '2.10.0'"]]}
if __name__ == "__main__":
    if (len(sys.argv) > 0 and '--help' in sys.argv[1]) or len(sys.argv) < 6:
        print('USAGE: python main.py <bugfix_commits.json> <conf_file path> <repos_directory> <size> <index>')
        print('If repos_directory is not set, pyszz will download each repository')
        exit(-1)
    input_json = sys.argv[1]
    conf_file = sys.argv[2]
    repos_dir = sys.argv[3]
    size = sys.argv[4]
    index = sys.argv[5]
    proj_name = re.split("_pc.json", input_json)[0]

    if platform.system() == 'Darwin':
        input_json = '_PC/' + sys.argv[1]
        out_dir = '_CPC'
    else:
        input_json = '/data/CGYW/CPMiner/_PC/' + sys.argv[1]
        out_dir = '/data/CGYW/CPMiner/_CPC'

    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    out_json = os.path.join(out_dir, f'{proj_name}_{index}_cpc.json')

    if not os.path.isfile(input_json):
        log.error('invalid input json', f'{input_json}')
        exit(-2)
    if not os.path.isfile(conf_file):
        log.error('invalid conf file')
        exit(-2)

    with open(conf_file, 'r') as f:
        conf = yaml.safe_load(f)

    log.info(f"parsed conf yml: {conf}")
    szz_name = conf['szz_name']

    if not szz_name:
        log.error('The configuration file does not define the SZZ name. Please, fix.')
        exit(-3)


    
    #log.info(f'Launching {szz_name}-szz')

    main(input_json, out_json, conf, repos_dir, size, index)
