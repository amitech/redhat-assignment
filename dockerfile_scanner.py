#!/usr/bin/env python3

"""
This script returns a json with the aggregated information for all the repositories,
for a given list of github repositories, identifies all the Dockerfile files inside each repository,
extracts the image names from the FROM statement.

Ex. -
$ python dockerfile_scanner.py https://example.com/something/some_textfile.txt

some_textfile.txt format:
https://github.com/user1/repo1.git 40af65af14a2dce962df923446afff24dd8f123e
https://github.com/user2/repo2.git a260deaf135fc0efaab365ea234a5b86b3ead404
"""

import argparse
import json
import base64
import re
import logging
import requests
import validators

def url_validate(val):
    """Validate URL provided in argument"""
    if not validators.url(val):
        raise argparse.ArgumentTypeError('Invalid URL')
    return val

# Handle CLI arguments
parser = argparse.ArgumentParser(
    description='Enter valid url which contains github repo url and commit SHA'
)

parser.add_argument('url', help="URL which contains github repo url and commit SHA",
                    type=url_validate)
args = parser.parse_args()

def validate_github(github_data):
    """Validate github url & sha for each line in provided text file. Return True for valid repo"""
    if len(github_data.split()) == 2:
        # Generate github url with commit sha https://github.com/username/repo/commit_sha to verify
        github_url = github_data.replace(".git ", "/commit/")
        if requests.get(github_url).status_code == 200:
            return True
    return False

def scan_github(github_url, github_sha):
    """Returns repo_name and json response which contains all file path for a specific commit in a
    valid repo."""

    # repo_name along with username like username/repository_name
    repo_name = github_url.split('github.com/')[-1].split('.git')[0]
    url = f"https://api.github.com/repos/{repo_name}/git/trees/{github_sha}?recursive=1"
    try:
        response = requests.get(url)
        response.raise_for_status()

    # Client side errors based on status
    except requests.exceptions.HTTPError as http_err:
        raise SystemExit(http_err) from http_err
    except requests.exceptions.RequestException as request_exception:
        raise SystemExit(request_exception) from request_exception

    return repo_name, response.json()

def generate_json(repo_name, github_sha, response_json):
    """Returns json object for a specific repo."""

    # Initialize empty dic to store JSON object
    data = {}
    for line in response_json.get('tree'):
        if line['path'].split('/')[-1] == 'Dockerfile':
            docker_reg_list = []
            filepath = line['path']
            url = f"https://api.github.com/repos/{repo_name}/contents/{filepath}?ref={github_sha}"
            try:
                content = requests.get(url)
            except requests.exceptions.HTTPError as http_err:
                raise SystemExit(http_err) from http_err
            except requests.exceptions.RequestException as request_exception:
                raise SystemExit(request_exception) from request_exception
            content_json = content.json()

            # content key stores base64 encoded data, lets decode it.
            file_content = base64.urlsafe_b64decode(content_json.get('content')).decode()
            for part in file_content.splitlines():
                # Search FROM keyword in Dockerfile and append to JSON.
                if re.search(r'^FROM', part):
                    docker_registry = part.split()[1]
                    docker_reg_list.append(docker_registry)
            data.update({filepath: docker_reg_list})
    return data

def main():
    """Main function"""
    try:
    # Making a get request
        response = requests.get(args.url, timeout=3)
        response.raise_for_status()

    # Client side errors based on status
    except requests.exceptions.HTTPError as http_err:
        raise SystemExit(http_err) from http_err
    except requests.exceptions.RequestException as request_exception:
        raise SystemExit(request_exception) from request_exception

    output = {}
    # Initialize dict with "data" key in JSON.
    output['data'] = {}

    for line in response.iter_lines():
        line_decoded = line.decode()

        # Check whether provided format in url is correct, else skip that line
        if validate_github(line_decoded):
            github_url = line_decoded.split()[0]
            github_sha = line_decoded.split()[1]
            repo_name, data = scan_github(github_url, github_sha)
            final_json = generate_json(repo_name, github_sha, data)
            full_url = github_url + ":" + github_sha
            output['data'][full_url] = {}
            output['data'][full_url].update(final_json)
        else:
            logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                                level=logging.WARNING)
            logging.warning("Invalid Github URL and/or SHA. Skipping for line %s", line_decoded)

    # Dump final JSON
    print(json.dumps(output, indent=2))

if __name__ == '__main__':
    main()
