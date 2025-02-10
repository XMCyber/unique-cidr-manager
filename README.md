# Unique CIDR Manager

## Status Checks
[![Build Images](https://github.com/xmcyber/unique-cidr-manager/actions/workflows/build-image.yml/badge.svg)](https://github.com/xmcyber/unique-cidr-manager/actions/workflows/build-image.yml)
[![flake8 Linter](https://github.com/xmcyber/unique-cidr-manager/actions/workflows/python-lint.yml/badge.svg)](https://github.com/xmcyber/unique-cidr-manager/actions/workflows/python-lint.yml)
[![Run Unittest](https://github.com/xmcyber/unique-cidr-manager/actions/workflows/run-tests.yml/badge.svg)](https://github.com/xmcyber/unique-cidr-manager/actions/workflows/run-tests.yml)

## _A basic tool build to manage unique CIDR across networks_
<img src="https://github.com/XMCyber/unique-cidr-manager/blob/master/content/cidr-manager.png" width=40% height=40%>

This tool is built in order to manage the private range ip addresses in the organization network to avoid future potential routing conflicts. 

## How it Works

- An env file should be provided in order the set all the required parameters using '--env-file .env'  while running docker
Required parameter name and example values:

| name | description | value |
| ------ | ------ | ------ |
| access_token | your personal token for the repo that will contain the unique list of occupied CIDRs |  ghp_3KR4U7bxxxxxxxxxxxxx
| occupied_repo | the name of the owner+repo in github.com | xmcyber/infra |
| occupied_file | the name of the json file for keeping the occupied state | occupied-range.json |
| committer_email | committer email - will appear as commiter on github | xmcidr
| committer_name | committer name - will appear as commiter on github | xmcidr

- The tool will first clone a dedicated repo (your own repo) that will maintain the final and unique list of occupide ip ranges. 
- After getting the required major range, it will start choosing first subnet (cidr) in this range, for example 10.0.0.0/26
- Than it will read the already occupied ranges from 'occupied-range.json' file (which should be created in your repo, {} content should be enough) and check if that occupied, if its overlaping it will go to next available range.
- After getting the UNIQUE cidr, it will return the the CIDR to web browser.
- Last step, it will append the new CIDR to the occupied-range.json and will push the change to your repo 


## Docker

unique-cidr-manager is very easy to install and deploy in a Docker container.


```sh
docker build -t image:tag .
```

```sh
docker run -d -p 8000:8000 --env-file env -name unique-cidr-manager unique-cidr-manager:latest
```


Verify the deployment by navigating to your server address in
your preferred browser.

```sh
http://localhost:8000
```

Here are some examples for request 

Obtain new CIDR:
```sh
http://localhost:8000/get-cidr?subnet_size=${subnet_size}&requiredrange=${required_range}&reason=${reason}
```

Show all occupied CIDR list:
```sh
http://localhost:8000/get-occupied-list
```
Delete CIDR from list:
```sh
http://localhost:8000/delete-cidr-from-list?cidr_deletion=10.1.2.3/28
```

## License

MIT

**Free Software, Hell Yeah!**