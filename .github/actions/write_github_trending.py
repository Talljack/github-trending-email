import os
import json
import base64

if __name__ == '__main__':
    import sys
    import json
    content = ''
    date = sys.argv[1]
    repo_data_str = sys.argv[2]
    repo_data_decoded_bytes = base64.urlsafe_b64decode(repo_data_str)
    repo_data = json.loads(repo_data_decoded_bytes.decode('utf-8'))
    repo_tables_map = {}
    repo_items = repo_data.items()
    for key, repos in repo_items:
        repo_tables_map[key] = repos
    # 在根目录下创建 github-trending-repos 目录，并写入文件
    if not os.path.exists('github-trending-repos'):
        os.makedirs('github-trending-repos')
    with open(f'github-trending-repos/github-trending-repos-{date}.json', 'w') as f:
        json.dump(repo_tables_map, f)
