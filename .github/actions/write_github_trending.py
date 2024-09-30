import os
import json
import base64
import sys

def main():
    try:
        date = sys.argv[1]
        repo_data_str = sys.argv[2]
        repo_data_decoded_bytes = base64.urlsafe_b64decode(repo_data_str)
        repo_data = json.loads(repo_data_decoded_bytes.decode('utf-8'))
        repo_tables_map = {key: repos if key else 'All' for key, repos in repo_data.items()}

        # 创建目录
        target_dir = 'github-trending-repos'
        os.makedirs(target_dir, exist_ok=True)

        # 写入文件
        file_path = os.path.join(target_dir, f'github-trending-repos-{date}.json')
        # 直接覆盖写入
        with open(file_path, 'w') as f:
            json.dump(repo_tables_map, f)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise

if __name__ == '__main__':
    main()
